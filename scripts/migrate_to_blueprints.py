#!/usr/bin/env python3
"""migrate_to_blueprints.py — legacy scripts -> blueprint JSON.

Recovers structure from content that predates the blueprint format, without
re-synthesising any audio. Migrated blueprints carry `"audio": "existing"`, so
`build_episode.py` will regenerate their chapters and transcript metadata but
leave the published MP3 alone.

Two sources, two strategies:

* `scripts/drafts/coding-prep/*.txt` — prose. Sections are recovered from the
  phrases the drafts consistently open each movement with ("Naive approach",
  "Better idea", "Edges checklist"). Anything unmatched joins the section
  above it, so no text is ever dropped.
* `scripts/mock_dialogues/*.py`, `scripts/coding_mocks/*.py` — these expose
  `build() -> [(voice, text)]` and mark movements with `# SECTION n: Title`
  comments. The comments are read from the source text and matched positionally
  to the tuples, since importing the module discards them.

    python3 scripts/migrate_to_blueprints.py --coding-prep --dry-run
    python3 scripts/migrate_to_blueprints.py --dialogues --write
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.lib import gates as gates_mod
from scripts.lib import ids as ids_mod
from scripts.lib.blueprint import from_dict, save

# Opening phrases that reliably start a movement in the coding-prep drafts,
# mapped to the think-aloud-coding template's section ids.
CODING_PREP_MARKERS: list[tuple[str, str, str]] = [
    ("attempt", "Your attempt", r"^(Before I give you anything|Pause here and attempt)"),
    ("clarify", "Clarify first", r"^(Here are the clarifiers|The clarifiers I always ask)"),
    ("naive", "Naive approach", r"^Naive approach"),
    ("improve", "Better idea", r"^(Better idea|Improved approach)"),
    ("walk", "Hand walk", r"^(Concrete example|Hand walk|In my head, the code)"),
    ("complexity", "Complexity", r"^(Time: O of|Complexity\.)"),
    ("edges", "Edges", r"^(Edges checklist|Mistake one)"),
    ("wrap", "Wrap", r"^(Pattern cue card|Speed recap|Transfer\.)"),
]

SECTION_COMMENT = re.compile(r"#\s*SECTION\s*\d*\s*:?\s*(.+?)\s*(?:\(|$)", re.I)


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def migrate_coding_prep(path: Path) -> dict | None:
    paragraphs = split_paragraphs(path.read_text(encoding="utf-8"))
    if not paragraphs:
        return None

    sections: list[dict] = [{"id": "cold-open", "title": "Cold open", "lines": []}]

    for para in paragraphs:
        for sid, title, pattern in CODING_PREP_MARKERS:
            if re.match(pattern, para, re.I) and sid not in {s["id"] for s in sections}:
                sections.append({"id": sid, "title": title, "lines": []})
                break
        sections[-1]["lines"].append({"voice": "narrator", "text": para})

    stem = path.stem  # e.g. ep01-two-sum-think-aloud
    title = stem.split("-", 1)[-1].replace("-", " ").title()

    return {
        "schema": 1,
        "slug": f"coding-prep-{stem}",
        "show": "coding-prep",
        "template": "think-aloud-coding",
        "title": title,
        "description": f"Think-aloud walkthrough: {title}.",
        "voices": {"narrator": "narrator"},
        "audio": "existing",
        "sections": sections,
    }


def section_titles_from_source(source: str) -> list[tuple[int, str]]:
    """(append_index, section_title) for each `# SECTION` comment.

    Counts `.append(` calls textually so the comment positions line up with the
    tuples `build()` returns.
    """
    marks: list[tuple[int, str]] = []
    appends = 0
    for line in source.split("\n"):
        match = SECTION_COMMENT.search(line)
        if match:
            marks.append((appends, match.group(1).strip()))
        appends += line.count(".append((")
    return marks


def migrate_module(path: Path, show: str, template: str) -> dict | None:
    source = path.read_text(encoding="utf-8")

    # Import through the package so relative imports inside the module resolve.
    module_name = f"scripts.{path.parent.name}.{path.stem}"
    try:
        __import__(module_name)
        module = sys.modules[module_name]
        pairs = module.build()
    except Exception as exc:  # a legacy module that no longer imports
        print(f"  SKIP {path.name}: {type(exc).__name__}: {exc}")
        return None

    if not pairs:
        return None

    marks = section_titles_from_source(source)
    if not marks or marks[0][0] > 0:
        marks.insert(0, (0, "Opening"))

    sections: list[dict] = []
    for i, (start, title) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(pairs)
        chunk = pairs[start:end]
        if not chunk:
            continue
        sections.append(
            {
                "id": ids_mod.slugify(title, max_length=32) or f"section-{i}",
                "title": title,
                "lines": [{"voice": voice, "text": text} for voice, text in chunk],
            }
        )

    if not sections:
        return None

    # Section ids must be unique; two "Deep dive" comments would otherwise clash.
    seen: dict[str, int] = {}
    for section in sections:
        base = section["id"]
        if base in seen:
            seen[base] += 1
            section["id"] = f"{base}-{seen[base]}"
        else:
            seen[base] = 1

    title = path.stem.replace("_", " ").title()
    return {
        "schema": 1,
        "slug": ids_mod.slugify(f"{show}-{path.stem}"),
        "show": show,
        "template": template,
        "title": title,
        "description": f"{title} — migrated from {path.name}.",
        "audio": "existing",
        "sections": sections,
    }


def link_existing_ids(candidates: list[dict]) -> int:
    """Adopt the published id for any episode already in the manifest.

    Without this a migrated blueprint looks new, `build_episode` allocates a
    fresh id, and republishing would duplicate an episode that already exists.
    Matching is by slug against the manifest's slug / theme / filename stem.
    """
    from scripts.lib import manifest as manifest_mod

    manifest = manifest_mod.load()

    by_key: dict[str, int] = {}
    by_episode_no: dict[tuple[str, str], int] = {}

    for ep in manifest.get("episodes", []):
        keys = [
            ep.get("slug"),
            ep.get("theme"),
            (ep.get("filename") or "").removesuffix(".mp3"),
        ]
        for key in keys:
            if not key:
                continue
            by_key[key] = ep["id"]

            # Draft episodes are numbered; the published slug often abbreviates
            # the title ('ep15-monotonic' vs the draft's 'ep15-monotonic-stack'),
            # so the number plus the show is the reliable join key.
            match = re.search(r"ep(\d{1,3})", key)
            if match:
                by_episode_no.setdefault(
                    (ep.get("playlist") or "", match.group(1).lstrip("0") or "0"), ep["id"]
                )

    # Each published episode may be claimed once. Without this two blueprints
    # normalising to the same core both adopt the same id, and the second
    # publish silently overwrites the first.
    claimed: set[int] = set()

    # The published slug is the key every artifact of that episode already uses
    # (episodes/<slug>.mp3). A migrated blueprint must adopt it, or a rebuild
    # would upload to a new key while the manifest still points at the old one.
    published_slug: dict[int, str] = {}
    for ep in manifest.get("episodes", []):
        slug = ep.get("slug") or (ep.get("filename") or "").removesuffix(".mp3")
        if slug:
            published_slug[ep["id"]] = slug

    def claim(episode_id: int | None) -> int | None:
        if episode_id is None or episode_id in claimed:
            return None
        claimed.add(episode_id)
        return episode_id

    by_core: dict[str, int] = {}
    for ep in manifest.get("episodes", []):
        for key in (
            ep.get("slug"),
            ep.get("theme"),
            (ep.get("filename") or "").removesuffix(".mp3"),
        ):
            if key:
                by_core.setdefault(_core(key, ep.get("playlist") or ""), ep["id"])

    linked = 0
    for data in candidates:
        slug = data["slug"]
        show = data["show"]

        found = claim(by_key.get(slug))
        if found is None:
            found = claim(by_core.get(_core(slug, show)))
        if found is None:
            match = re.search(r"ep(\d{1,3})", slug)
            if match:
                found = claim(
                    by_episode_no.get((show, match.group(1).lstrip("0") or "0"))
                )

        if found is not None:
            data["id"] = found
            if published_slug.get(found):
                data["slug"] = published_slug[found]
            linked += 1
    return linked


# Prefixes the various batch publishers stamped onto filenames over the years.
_PREFIXES = ("mock-v2-mock-", "mock-v2-", "coding-prep-mock-", "mock-")
_SUFFIXES = re.compile(r"-(think-aloud|walkthrough|drill|dialogue)$")


def _core(key: str, show: str) -> str:
    """Reduce a key to the part that identifies the episode.

    `mock-v2-mock-reconciliation`, `sd-mock-interviews-reconciliation` and
    `reconciliation` all reduce to `reconciliation`, which is what lets the
    three historical naming schemes join up.
    """
    core = key
    if show and core.startswith(f"{show}-"):
        core = core[len(show) + 1 :]
    changed = True
    while changed:
        changed = False
        for prefix in _PREFIXES:
            if core.startswith(prefix):
                core = core[len(prefix) :]
                changed = True
    return _SUFFIXES.sub("", core)


def prune(written: set[Path]) -> int:
    """Delete blueprint files this run didn't produce.

    Adopting a published slug renames a file; without pruning the old name
    stays behind, and two blueprints then claim the same episode id.
    """
    removed = 0
    for path in sorted((ROOT / "content" / "blueprints").rglob("*.json")):
        if path.resolve() not in written:
            print(f"  pruned orphan {path.relative_to(ROOT)}")
            path.unlink()
            removed += 1
    return removed


def process(candidates: list[dict], write: bool, do_prune: bool = False) -> int:
    linked = link_existing_ids(candidates)
    print(f"  linked {linked}/{len(candidates)} to published episode ids\n")

    # Two source files can normalise to the same slug — `ep03-longest-substring`
    # and its `-excerpt` variant both do. Silently writing both to one path
    # loses content, so the unlinked one is suffixed and reported.
    seen_slugs: dict[str, dict] = {}
    for data in sorted(candidates, key=lambda d: (d.get("id") is None, d["slug"])):
        slug = data["slug"]
        if slug not in seen_slugs:
            seen_slugs[slug] = data
            continue
        n = 2
        while f"{slug}-{n}" in seen_slugs:
            n += 1
        data["slug"] = f"{slug}-{n}"
        seen_slugs[data["slug"]] = data
        print(f"  NOTE slug collision: {slug!r} -> {data['slug']!r} ({data['title']})")

    written: set[Path] = set()
    ok = failed = 0
    for data in candidates:
        try:
            bp = from_dict(data)
        except Exception as exc:
            print(f"  INVALID {data.get('slug')}: {exc}")
            failed += 1
            continue

        findings = gates_mod.run_blueprint(bp, gates_mod.load_template(bp.template))
        errors = [f for f in findings if f.level == gates_mod.ERROR]

        status = "ok " if not errors else "GATE"
        print(
            f"  {status} {bp.slug:<44} {len(bp.sections):2d} sections "
            f"{bp.line_count():4d} lines ~{bp.estimate_minutes():5.1f} min"
        )
        for finding in errors[:3]:
            print(f"        {finding}")

        if errors:
            failed += 1
            continue

        if write:
            target = ROOT / "content" / "blueprints" / bp.show / f"{bp.slug}.json"
            save(bp, target)
            written.add(target.resolve())
        ok += 1

    removed = prune(written) if (write and do_prune) else 0
    suffix = f", {removed} orphan(s) pruned" if removed else ""
    print(f"\n  {ok} migrated, {failed} needing attention{suffix}")
    return 0 if not failed else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coding-prep", action="store_true")
    parser.add_argument("--dialogues", action="store_true")
    parser.add_argument("--mocks", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--write", action="store_true", help="write files (default: dry run)")
    parser.add_argument("--prune", action="store_true", help="delete blueprints this run did not produce")
    args = parser.parse_args()

    if not (args.coding_prep or args.dialogues or args.mocks):
        parser.error("pick at least one of --coding-prep / --dialogues / --mocks")

    candidates: list[dict] = []

    if args.coding_prep:
        paths = sorted((ROOT / "scripts/drafts/coding-prep").glob("ep*.txt"))
        print(f"coding-prep drafts: {len(paths)}")
        candidates += [d for d in (migrate_coding_prep(p) for p in paths) if d]

    if args.dialogues:
        paths = sorted((ROOT / "scripts/mock_dialogues").glob("*.py"))
        paths = [p for p in paths if not p.name.startswith("__")]
        print(f"mock dialogues: {len(paths)}")
        candidates += [
            d
            for d in (
                migrate_module(p, "sd-mock-interviews", "mock-interview-2voice") for p in paths
            )
            if d
        ]

    if args.mocks:
        paths = sorted((ROOT / "scripts/coding_mocks").glob("*.py"))
        paths = [p for p in paths if not p.name.startswith("__")]
        print(f"coding mocks: {len(paths)}")
        candidates += [
            d for d in (migrate_module(p, "coding-prep", "coding-mock-drill") for p in paths) if d
        ]

    if args.limit:
        candidates = candidates[: args.limit]

    print()
    return process(candidates, args.write, args.prune)


if __name__ == "__main__":
    raise SystemExit(main())
