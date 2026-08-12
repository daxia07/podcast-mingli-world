#!/usr/bin/env python3
"""sync_manifest.py — push the committed manifest to R2 and regenerate RSS.

    python3 scripts/sync_manifest.py [--dry-run]

R2 is what the app and podcast clients actually read; the committed copies are
just the reviewable version. Anything that edits the manifest without running a
publish — archiving a show, renaming one, editing shows.json — changes the repo
and leaves R2 untouched, so the change never reaches the app.

That is exactly what happened when the Airwallex shows were archived: the local
manifests said archived, the live site still served all fourteen shows. The
`manifest_parity` gate compares the two committed copies to each other and never
looks at R2, so it stayed green throughout.

Runs from CI on every deploy, where the Cloudflare token exists.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.lib import gates as gates_mod
from scripts.lib import manifest as manifest_mod


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv

    local = manifest_mod.load()

    # Never push a manifest that would break the app.
    errors = [
        f
        for f in gates_mod.run_manifest(local) + gates_mod.gate_show_registry(local)
        if f.level == gates_mod.ERROR
    ]
    if errors:
        for f in errors:
            print(f"  {f}")
        print("ERROR: refusing to sync an invalid manifest", file=sys.stderr)
        return 1

    shows = len(local.get("playlists", {}))
    archived = sum(1 for p in local.get("playlists", {}).values() if p.get("archived"))
    episodes = len(local.get("episodes", []))
    hidden = sum(1 for e in local.get("episodes", []) if e.get("archived"))
    print(f"  local: {episodes} episodes ({hidden} archived), {shows} shows ({archived} archived)")

    from scripts.lib import r2

    try:
        remote = r2.get_json("manifest.json")
    except Exception as exc:  # first run, or R2 unreachable
        print(f"  could not read the remote manifest ({exc}); will upload anyway")
        remote = None

    if remote == local:
        print("  R2 already matches — nothing to do")
        return 0

    if remote is not None:
        r_eps = len(remote.get("episodes", []))
        r_shows = len(remote.get("playlists", {}))
        print(f"  R2:    {r_eps} episodes, {r_shows} shows  -> out of date")

    if dry:
        print("  dry run — not uploading")
        return 0

    r2.upload_json("manifest.json", local)
    r2.upload_bytes("rss.xml", manifest_mod.generate_rss(local).encode("utf-8"))
    print("  uploaded manifest.json and rss.xml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
