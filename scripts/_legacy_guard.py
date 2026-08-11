#!/usr/bin/env python3
"""_legacy_guard.py — make running a frozen generator a deliberate act.

The one-off series generators (`generate_sd.py`, `generate_mock_interview.py`,
…) each reimplemented id allocation, manifest editing and RSS regeneration
slightly differently. That is what produced colliding ids, date-prefixed URLs
and a manifest that drifted from its own copy.

They are kept for reference and because they still document how existing
episodes were made, but new content goes through `build_episode.py`. This guard
stops someone — human or agent — reaching for the old path by habit.

Import-safe: it only fires when the file is executed directly, so
`ingest_youtube.py --backfill` can still import `download_youtube.YOUTUBE_VIDEOS`.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

BYPASS_FLAG = "--legacy-ok"
BYPASS_ENV = "PODCAST_ALLOW_LEGACY"

BANNER = """
────────────────────────────────────────────────────────────────────────────
  {name} is FROZEN.

  New episodes are authored as blueprints and built with one command:

      .claude/skills/episode-new          (or /new-episode)
      python3 scripts/build_episode.py <blueprint.json> --dry-run

  That path validates the script before spending a TTS run, allocates a
  non-colliding id, and emits chapters and a synced transcript. This script
  does none of that.

  Reference only: docs/UPGRADE-SPEC.md §4, AGENTS.md.

  To run it anyway (you almost certainly should not):
      {name} {flag}          or   {env}=1
────────────────────────────────────────────────────────────────────────────
"""


def warn_legacy(file_path: str) -> None:
    """Abort if this file is the script being run, unless explicitly bypassed."""
    name = Path(file_path).name

    # Import, not execution — stay out of the way.
    if Path(sys.argv[0]).name != name:
        return

    if BYPASS_FLAG in sys.argv or os.environ.get(BYPASS_ENV):
        print(f"  [legacy] running frozen {name} with an explicit bypass", file=sys.stderr)
        if BYPASS_FLAG in sys.argv:
            sys.argv.remove(BYPASS_FLAG)
        return

    print(BANNER.format(name=name, flag=BYPASS_FLAG, env=BYPASS_ENV), file=sys.stderr)
    raise SystemExit(2)
