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
import re
import sys
from copy import deepcopy
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
    count = (str(sum(len(re.findall(r'[\u3400-\u9fff]', line.text)) for section in bp.sections for line in section.lines)) + ' Han characters'
             if bp.language.startswith('zh') else str(bp.word_count()) + ' words')
    print(f"  {bp.line_count()} chunks, {count}, ~{bp.estimate_minutes():.1f} min (estimate)\n")

    width = max(len(s.id) for s in bp.sections)
    for section in bp.sections:
        est = bp.section_speech_seconds(section)
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
        # Completed local builds reserve IDs too; --no-publish does not yet
        # append to the live catalogue, so repeated builds otherwise collide.
        reservations = deepcopy(manifest)
        known = {ep['id'] for ep in reservations.get('episodes', [])}
        for path in Path('content/blueprints').rglob('*.json'):
            item = json.loads(path.read_text())
            if item.get('id') is not None and item['id'] not in known:
                reservations.setdefault('episodes', []).append({'id':item['id']})
                known.add(item['id'])
        bp.id = ids_mod.next_id(reservations)
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

    if getattr(args, 'publish_built', False):
        if args.dry_run or args.no_publish:
            fail('--publish-built cannot be combined with --dry-run or --no-publish')
        return publish_built(bp, manifest, args)

    run_gates(bp, manifest, args.force)
    print_plan(bp, gates_mod.load_template(bp.template))

    if args.dry_run:
        print("  dry run — no audio synthesised, nothing uploaded")
        return 0

    # --force may override editorial warnings; never source alignment.
    if bp.language.startswith('zh') or bp.tts:
        from scripts.lib.local_mandarin import validate_source
        try:
            validate_source(bp)
        except (ValueError, OSError) as exc:
            fail(str(exc))
    allocate(bp, manifest)

    # Imported here so --dry-run works on a machine with no ffmpeg installed.
    from scripts.lib import synth as synth_mod

    output_dir = Path(getattr(args, 'output_dir', None) or DATA_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    mp3_path = output_dir / f"{bp.slug}.mp3"

    print("  synthesising...")
    try:
        timeline = synth_mod.synthesize(bp, mp3_path,
            workdir=getattr(args, 'workdir', None), model_dir=getattr(args, 'model_dir', None))
    except synth_mod.SynthError as exc:
        fail(str(exc))

    size = mp3_path.stat().st_size
    if size < MIN_MP3_BYTES:
        fail(f"{mp3_path} is only {size} bytes — refusing to publish a truncated episode")

    chapter_doc = chapters_mod.dumps(timeline, title=bp.title)
    vtt = transcript_mod.build(timeline)
    has_chapters = bool(chapters_mod.build(timeline))

    (output_dir / f"{bp.slug}.chapters.json").write_text(chapter_doc, encoding="utf-8")
    (output_dir / f"{bp.slug}.vtt").write_text(vtt, encoding="utf-8")

    duration = f"{int(timeline.total // 60)}:{int(timeline.total % 60):02d}"
    print(f"  {duration}  {size / 1e6:.1f} MB  chapters={'yes' if has_chapters else 'no'}")

    if args.no_publish:
        print(f"  wrote {mp3_path} (not published)")
        save(bp)
        return 0

    return publish(bp, manifest, mp3_path, chapter_doc, vtt, timeline, duration, size, has_chapters,
                   listening_review=getattr(args, 'listening_review', None))


def publish_built(bp, manifest, args):
    """Publish exact locally reviewed Mandarin artifacts on an existing publisher.

    The publishing host needs ffmpeg and its existing storage access, not a
    second speech model or a copied account credential. No synthesis occurs.
    """
    from scripts.lib.local_mandarin import validate_source, require_listening_review
    from scripts.lib.timeline import Timeline, TimedLine, TimedSection, flatten
    if not bp.language.startswith('zh') or bp.id is None:
        fail('--publish-built requires an allocated Mandarin blueprint')
    run_gates(bp, manifest, False)
    folder = Path(getattr(args, 'output_dir', None) or DATA_DIR)
    path = folder / f'{bp.slug}.mp3'
    try:
        validate_source(bp)
        require_listening_review(bp, path, getattr(args, 'listening_review', None))
        receipt = json.loads(path.with_suffix('.build.json').read_text())
        raw = receipt['timeline']
        timeline = Timeline([TimedLine(**line) for line in raw['lines']],
            [TimedSection(**section) for section in raw['sections']], raw['total'])
        if [line.text for line in timeline.lines] != [line.text for _, _, line in flatten(bp)]:
            fail('built timeline does not preserve every source chunk')
        chapter_doc = chapters_mod.dumps(timeline, title=bp.title)
        vtt = transcript_mod.build(timeline)
        if ((folder / f'{bp.slug}.chapters.json').read_text() != chapter_doc
                or (folder / f'{bp.slug}.vtt').read_text() != vtt):
            fail('built chapter or transcript sidecar changed after rendering')
    except (ValueError, OSError, KeyError, TypeError) as exc:
        fail(str(exc))
    size = path.stat().st_size
    if size < MIN_MP3_BYTES:
        fail('built MP3 is unexpectedly small')
    duration = f'{int(timeline.total // 60)}:{int(timeline.total % 60):02d}'
    return publish(bp, manifest, path, chapter_doc, vtt, timeline, duration, size,
        bool(chapters_mod.build(timeline)), listening_review=getattr(args, 'listening_review', None))


def _content_hash(path, length: int = 8) -> str:
    import hashlib

    digest = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()[:length]


def publish(bp, manifest, mp3_path, chapter_doc, vtt, timeline, duration, size, has_chapters, *, listening_review=None) -> int:
    if bp.language.startswith('zh') or bp.tts:
        from scripts.lib.local_mandarin import validate_source, require_listening_review
        try:
            validate_source(bp)
            require_listening_review(bp, mp3_path, listening_review)
        except (ValueError, OSError) as exc:
            fail(str(exc))
    entry = {
        "id": bp.id,
        "slug": bp.slug,
        "title": bp.title,
        "description": bp.description,
        "duration": duration,
        "file_size_bytes": size,
        # Content hash in the URL: episodes are rebuilt in place when a bug is
        # fixed, and without this a client that cached the broken build would
        # keep playing it. The Worker ignores the query when resolving the key.
        "file_url": f"{manifest_mod.BASE_URL}/episodes/{bp.slug}.mp3?v={_content_hash(mp3_path)}",
        "filename": f"{bp.slug}.mp3",
        "playlist": bp.show,
        "source": "tts",
        "has_transcript": True,
        "has_chapters": has_chapters,
        "keywords": bp.keywords,
    }
    if bp.language != 'en':
        entry['language'] = bp.language
    reader_url = bp.source_document.get('reader_url')
    if reader_url:
        if not re.fullmatch(r'/novel/[a-z0-9-]+\.html', reader_url):
            fail('reader URL must identify a local novel HTML page')
        entry['reader_url'] = reader_url
    if bp.sources:
        entry["sources"] = bp.sources

    candidate = deepcopy(manifest)
    manifest_mod.add_or_update(candidate, entry)
    try:
        manifest_mod.attach_to_playlist(candidate, bp.show, bp.id)
    except KeyError as exc:
        fail(str(exc))
    show = candidate['playlists'][bp.show]
    if show.get('draft_chapters'):
        show['draft_chapters'] = [chapter for chapter in show['draft_chapters'] if chapter.get('slug') != bp.slug]

    findings = [f for f in gates_mod.run_manifest(candidate) + gates_mod.gate_show_registry(candidate) if f.level == gates_mod.ERROR]
    if findings:
        for finding in findings:
            print(f"  {finding}")
        fail("manifest would be invalid after this publish — not uploading it")

    from scripts.lib import r2
    from scripts.sync_manifest import preservation_errors
    try:
        remote = r2.get_json('manifest.json')
        losses = preservation_errors(candidate, remote)
    except Exception:
        fail('current remote catalogue could not be verified; nothing uploaded')
    if losses:
        fail('; '.join(losses))
    print("  uploading...")
    r2.upload(f"episodes/{bp.slug}.mp3", str(mp3_path))
    r2.upload_bytes(f"transcripts/{bp.slug}.vtt", vtt.encode("utf-8"))
    if has_chapters:
        r2.upload_bytes(f"chapters/{bp.slug}.json", chapter_doc.encode("utf-8"))
    if bp.board:
        r2.upload_json(f"boards/{bp.slug}.json", bp.board)

    r2.upload_json("manifest.json", candidate)
    r2.upload_bytes("rss.xml", manifest_mod.generate_rss(candidate).encode("utf-8"))
    manifest_mod.save_local(candidate)
    save(bp)

    print(f"  published #{bp.id} {bp.title}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("blueprint", help="path to a blueprint JSON file")
    parser.add_argument("--dry-run", action="store_true", help="gates + plan only")
    parser.add_argument("--no-publish", action="store_true", help="build audio locally, don't upload")
    parser.add_argument("--force", action="store_true", help="build despite gate errors")
    parser.add_argument('--model-dir', help='existing pinned local model snapshot; never downloaded automatically')
    parser.add_argument('--workdir', help='persistent chunk cache directory')
    parser.add_argument('--output-dir', help='local build outputs; defaults to data/')
    parser.add_argument('--publish-built', action='store_true', help='publish exact reviewed Mandarin build artifacts without loading a speech model')
    parser.add_argument('--audio-review', '--listening-review', dest='listening_review',
        help='explicit listening or disclosed objective review bound to final MP3/source hashes; never generated by the builder')
    return build(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
