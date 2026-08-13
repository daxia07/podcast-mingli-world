#!/usr/bin/env python3
"""build_search_index.py — a searchable index of what is *said* in each episode.

Until now Search matched titles, descriptions and solution boards: it could find
an episode about vector databases, but not the ninety seconds inside a different
episode where vector databases actually get explained. Every blueprint-built
episode already ships an exact transcript and chapter list (both measured during
synthesis, not transcribed afterwards), so the moments are there — they were
simply never indexed.

This walks the manifest, pulls `transcripts/<slug>.vtt` and
`chapters/<slug>.json` for every episode flagged as having them, and writes a
single `site/search-index.json`. It is a static file deployed with the site, not
an R2 object: it needs no credentials to read, no Function to serve, and it is
diffable in git, so a bad build is visible in review rather than at run time.

Sources, in order of preference per episode:

  1. `data/<slug>.vtt` — the local build output, if this machine built it.
  2. `https://podcast.mingli.world/transcripts/<slug>.vtt` — public, no auth
     (podcast clients fetch these, so `_middleware.js` whitelists them).

Usage:
    python3 scripts/build_search_index.py              # fetch, write, report
    python3 scripts/build_search_index.py --offline    # local data/ only
    python3 scripts/build_search_index.py --check      # fail if out of date
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.lib import transcript as transcript_mod  # noqa: E402

BASE_URL = os.environ.get("BASE_URL", "https://podcast.mingli.world")
DATA_DIR = ROOT / "data"
OUT_PATH = ROOT / "site" / "search-index.json"
MANIFEST_PATHS = (ROOT / "scripts" / "manifest.json", ROOT / "site" / "manifest.json")

# A cue shorter than this is a fragment — "Right." — and only ever adds noise to
# the result list. Chapters are exempt: a short chapter title is still a landmark.
MIN_LINE_CHARS = 24
INDEX_VERSION = 1


# ——— sources ———————————————————————————————————————————————————————————————


def load_manifest() -> dict:
    for path in MANIFEST_PATHS:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    raise SystemExit("no manifest found — expected scripts/manifest.json")


# Cloudflare answers the default `Python-urllib/3.x` agent with a 403 before the
# request ever reaches the Function. Identifying ourselves honestly gets through.
USER_AGENT = "podcast-mingli-world/search-index (+https://podcast.mingli.world)"


def fetch(url: str, timeout: int = 20) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError, UnicodeDecodeError):
        return None


def read_artifact(slug: str, kind: str, *, offline: bool) -> str | None:
    """kind is 'vtt' or 'chapters.json'; local build output wins over the site."""
    local = DATA_DIR / f"{slug}.{kind}"
    if local.exists():
        return local.read_text(encoding="utf-8")
    if offline:
        return None
    path = "transcripts" if kind == "vtt" else "chapters"
    suffix = "vtt" if kind == "vtt" else "json"
    return fetch(f"{BASE_URL}/{path}/{slug}.{suffix}")


# ——— shaping ———————————————————————————————————————————————————————————————


def moments_from_vtt(vtt: str) -> list[list]:
    """[[start_seconds, text], ...] — one entry per cue worth surfacing."""
    out: list[list] = []
    for cue in transcript_mod.parse(vtt):
        text = " ".join(cue["text"].split())
        if len(text) < MIN_LINE_CHARS:
            continue
        out.append([round(cue["start"], 1), text])
    return out


def chapters_from_doc(doc: str) -> list[list]:
    try:
        parsed = json.loads(doc)
    except json.JSONDecodeError:
        return []
    out: list[list] = []
    for ch in parsed.get("chapters", []):
        title = " ".join(str(ch.get("title", "")).split())
        if not title:
            continue
        out.append([round(float(ch.get("startTime", 0)), 1), title])
    return out


def build(manifest: dict, *, offline: bool = False, verbose: bool = True) -> dict:
    episodes: dict[str, dict] = {}
    missing: list[str] = []

    for ep in manifest.get("episodes", []):
        slug = ep.get("slug")
        if not slug or not (ep.get("has_transcript") or ep.get("has_chapters")):
            continue

        entry: dict[str, object] = {"s": slug}

        if ep.get("has_chapters"):
            doc = read_artifact(slug, "chapters.json", offline=offline)
            if doc:
                chapters = chapters_from_doc(doc)
                if chapters:
                    entry["c"] = chapters

        if ep.get("has_transcript"):
            vtt = read_artifact(slug, "vtt", offline=offline)
            if vtt:
                lines = moments_from_vtt(vtt)
                if lines:
                    entry["l"] = lines

        if len(entry) == 1:  # slug only — nothing was fetchable
            missing.append(slug)
            continue

        episodes[str(ep["id"])] = entry

    if verbose and missing:
        print(f"  {len(missing)} episode(s) claimed artifacts we could not read:")
        for slug in missing[:5]:
            print(f"    - {slug}")

    return {"version": INDEX_VERSION, "episodes": episodes}


# ——— entry point ———————————————————————————————————————————————————————————


def render(index: dict) -> str:
    # Compact separators: this ships to a phone on mobile data. Sorted keys so a
    # rebuild with no content change produces no diff.
    return json.dumps(index, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="use data/ only, never the network")
    parser.add_argument("--check", action="store_true", help="exit 1 if the committed index is stale")
    parser.add_argument(
        "--no-shrink",
        action="store_true",
        help="keep the existing index if this build covers fewer episodes",
    )
    parser.add_argument("--out", default=str(OUT_PATH))
    args = parser.parse_args()

    manifest = load_manifest()
    index = build(manifest, offline=args.offline)
    payload = render(index)

    eps = index["episodes"]
    moments = sum(len(e.get("l", [])) + len(e.get("c", [])) for e in eps.values())
    size_kb = len(payload.encode("utf-8")) / 1024
    print(f"  {len(eps)} episodes · {moments} moments · {size_kb:.0f} KB")

    out = Path(args.out)
    if args.check:
        current = out.read_text(encoding="utf-8") if out.exists() else ""
        if current != payload:
            print("  search index is stale — run scripts/build_search_index.py", file=sys.stderr)
            return 1
        print("  search index is up to date")
        return 0

    # A network wobble during the deploy build would otherwise quietly ship an
    # index covering fewer episodes than the one already committed, and search
    # would lose moments nobody deleted.
    if args.no_shrink and out.exists():
        try:
            existing = json.loads(out.read_text(encoding="utf-8")).get("episodes", {})
        except json.JSONDecodeError:
            existing = {}
        if len(eps) < len(existing):
            print(
                f"  refusing to shrink the index: {len(eps)} < {len(existing)} episodes"
                " — keeping the committed one",
                file=sys.stderr,
            )
            return 0

    out.write_text(payload, encoding="utf-8")
    shown = out.relative_to(ROOT) if out.is_relative_to(ROOT) else out
    print(f"  wrote {shown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
