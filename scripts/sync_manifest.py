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


def preservation_errors(local: dict, remote: dict | None) -> list[str]:
    """Refuse a stale checkout that would remove published identities or URLs.

    Archiving changes visibility metadata; it must not delete records. Rebuilds
    may update a cache-busting query string while retaining the published path.
    """
    if not isinstance(remote, dict) or not isinstance(remote.get("episodes"), list):
        return ["the current remote episode catalogue could not be verified"]
    remote_shows = remote.get("playlists")
    if not isinstance(remote_shows, dict):
        return ["the current remote show catalogue could not be verified"]

    local_episodes = {ep.get("id"): ep for ep in local.get("episodes", [])}
    errors = []
    for ep in remote["episodes"]:
        episode_id = ep.get("id")
        if episode_id is None or episode_id not in local_episodes:
            errors.append(f"published episode {episode_id!r} is absent locally")
            continue
        before = str(ep.get("file_url") or "").split("?", 1)[0]
        after = str(local_episodes[episode_id].get("file_url") or "").split("?", 1)[0]
        if before and before != after:
            errors.append(f"published episode {episode_id!r} would change its audio URL")
    for show_id in remote_shows:
        if show_id not in local.get("playlists", {}):
            errors.append(f"published show {show_id!r} is absent locally")
    return errors


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
    except Exception:
        print("ERROR: could not read the remote manifest; refusing to overwrite it", file=sys.stderr)
        return 1

    losses = preservation_errors(local, remote)
    if losses:
        for message in losses:
            print(f"ERROR: {message}", file=sys.stderr)
        print("ERROR: reconcile the current live catalogue before syncing; nothing uploaded", file=sys.stderr)
        return 1

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
