#!/usr/bin/env python3
"""build_episode.py — blueprint in, published episode out.

    python3 scripts/build_episode.py content/blueprints/coding-prep/ep20.json --dry-run
    python3 scripts/build_episode.py content/blueprints/coding-prep/ep20.json --no-publish
    python3 scripts/build_episode.py content/blueprints/coding-prep/ep20.json

Replaces the per-series generator scripts (`generate_sd.py`,
`generate_coding_prep.py`, …), which each reimplemented id allocation, manifest
editing and RSS regeneration slightly differently. One path now, gated.

Stages: load -> gates -> allocate -> synth -> chapters + transcript -> verify
-> upload -> manifest + RSS.

`--dry-run` stops after the gates and prints the section plan, so a draft can be
reviewed without spending a TTS run. It needs neither ffmpeg nor credentials.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib import chapters as chapters_mod
from scripts.lib import gates as gates_mod
from scripts.lib import ids as ids_mod
from scripts.lib import manifest as manifest_mod
from scripts.lib import transcript as transcript_mod
from scripts.lib.blueprint import Blueprint, BlueprintError, load as load_blueprint, save

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Below this the upload is almost certainly a truncated or silent file. The old
# publish.py uploaded whatever it found without looking.
MIN_MP3_BYTES = 500_000


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def print_plan(bp: Blueprint, template: dict | None) -> None:
    print(f"\n  {bp.title}")
    print(f"  show={bp.show}  template={bp.template}  slug={bp.slug}  id={bp.id or 'unallocated'}")
    print(f"  {bp.line_count()} lines, {bp.word_count()} words, ~{bp.estimate_minutes():.1f} min\n")

    width = max(len(s.id) for s in bp.sections)
    for section in bp.sections:
        est = section.word_count() / 145 * 60
        target = f" (target {section.target_minutes}m)" if section.target_minutes else ""
        flag = " [factual]" if section.factual else ""
        print(
            f"    {section.id:<{width}}  {len(section.lines):3d} lines "
            f"{est / 60:5.1f} min{target}{flag}"
        )

    if template:
        low, high = template.get("target_minutes", [None, None])
        print(f"\n  template range: {low}-{high} min")
    print()


def run_gates(bp: Blueprint, manifest: dict, force: bool) -> None:
    template = gates_mod.load_template(bp.template)
    findings = gates_mod.run_blueprint(bp, template, manifest)
    errors = [f for f in findings if f.level == gates_mod.ERROR]

    for finding in findings:
        print(f"  {finding}")

    if errors and not force:
        fail(f"{len(errors)} gate error(s) — fix them, or re-run with --force")
    if errors:
        print(f"  ...{len(errors)} error(s) overridden by --force")


def allocate(bp: Blueprint, manifest: dict) -> None:
    if bp.id is None:
        bp.id = ids_mod.next_id(manifest)
        print(f"  allocated id {bp.id}")
    if not ids_mod.is_valid_slug(bp.slug):
        fail(f"invalid slug {bp.slug!r}")


def build(args: argparse.Namespace) -> int:
    try:
        bp = load_blueprint(args.blueprint)
    except BlueprintError as exc:
        fail(str(exc))

    print(f"=== build_episode: {bp.slug} ===")
    manifest = manifest_mod.load()

    run_gates(bp, manifest, args.force)
    allocate(bp, manifest)
    print_plan(bp, gates_mod.load_template(bp.template))

    if args.dry_run:
        print("  dry run — no audio synthesised, nothing uploaded")
        return 0

    # Imported here so --dry-run works on a machine with no ffmpeg installed.
    from scripts.lib import synth as synth_mod

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    mp3_path = DATA_DIR / f"{bp.slug}.mp3"

    print("  synthesising...")
    try:
        timeline = synth_mod.synthesize(bp, mp3_path)
    except synth_mod.SynthError as exc:
        fail(str(exc))

    size = mp3_path.stat().st_size
    if size < MIN_MP3_BYTES:
        fail(f"{mp3_path} is only {size} bytes — refusing to publish a truncated episode")

    chapter_doc = chapters_mod.dumps(timeline, title=bp.title)
    vtt = transcript_mod.build(timeline)
    has_chapters = bool(chapters_mod.build(timeline))

    (DATA_DIR / f"{bp.slug}.chapters.json").write_text(chapter_doc, encoding="utf-8")
    (DATA_DIR / f"{bp.slug}.vtt").write_text(vtt, encoding="utf-8")

    duration = f"{int(timeline.total // 60)}:{int(timeline.total % 60):02d}"
    print(f"  {duration}  {size / 1e6:.1f} MB  chapters={'yes' if has_chapters else 'no'}")

    if args.no_publish:
        print(f"  wrote {mp3_path} (not published)")
        save(bp)
        return 0

    return publish(bp, manifest, mp3_path, chapter_doc, vtt, timeline, duration, size, has_chapters)


def publish(bp, manifest, mp3_path, chapter_doc, vtt, timeline, duration, size, has_chapters) -> int:
    from scripts.lib import r2  # wrangler-backed; needs CLOUDFLARE_API_TOKEN

    print("  uploading...")
    r2.upload(f"episodes/{bp.slug}.mp3", str(mp3_path))
    r2.upload_bytes(f"transcripts/{bp.slug}.vtt", vtt.encode("utf-8"))
    if has_chapters:
        r2.upload_bytes(f"chapters/{bp.slug}.json", chapter_doc.encode("utf-8"))
    if bp.board:
        r2.upload_json(f"boards/{bp.slug}.json", bp.board)

    entry = {
        "id": bp.id,
        "slug": bp.slug,
        "title": bp.title,
        "description": bp.description,
        "duration": duration,
        "file_size_bytes": size,
        "file_url": f"{manifest_mod.BASE_URL}/episodes/{bp.slug}.mp3",
        "filename": f"{bp.slug}.mp3",
        "playlist": bp.show,
        "source": "tts",
        "has_transcript": True,
        "has_chapters": has_chapters,
        "keywords": bp.keywords,
    }
    if bp.sources:
        entry["sources"] = bp.sources

    manifest_mod.add_or_update(manifest, entry)
    manifest_mod.attach_to_playlist(manifest, bp.show, bp.id)

    findings = [f for f in gates_mod.run_manifest(manifest) if f.level == gates_mod.ERROR]
    if findings:
        for finding in findings:
            print(f"  {finding}")
        fail("manifest would be invalid after this publish — not uploading it")

    r2.upload_json("manifest.json", manifest)
    r2.upload_bytes("rss.xml", manifest_mod.generate_rss(manifest).encode("utf-8"))
    manifest_mod.save_local(manifest)
    save(bp)

    print(f"  published #{bp.id} {bp.title}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("blueprint", help="path to a blueprint JSON file")
    parser.add_argument("--dry-run", action="store_true", help="gates + plan only")
    parser.add_argument("--no-publish", action="store_true", help="build audio locally, don't upload")
    parser.add_argument("--force", action="store_true", help="build despite gate errors")
    return build(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
