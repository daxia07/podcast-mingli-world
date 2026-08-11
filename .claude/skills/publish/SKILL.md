---
name: publish
description: Publish a built episode to R2 and update the manifest and RSS. Use when asked to publish, ship, or release an episode.
---

# Publish an episode

Publishing writes to production storage and to a public RSS feed. It is the
one irreversible step in the pipeline — confirm with the user before running it.

## Where it can run

`CLOUDFLARE_API_TOKEN` exists in **GitHub Actions** and on the **`agent` host**
(`ding@192.168.31.170`). It is *not* on this Mac — `wrangler whoami` here says
not authenticated. Build locally, publish from `agent` or CI. See
`docs/UPGRADE-SPEC.md` §0b.

## Pre-flight

1. `python3 -m scripts.lib.gates --manifest` — must be zero errors *before* you
   start. Publishing on top of a broken manifest compounds the damage.
2. Confirm the id is not already taken. `build_episode.py` checks, but if the
   blueprint carries a hand-written id, verify it yourself.
3. Check the MP3 is real: over 500 KB and the duration roughly matches the
   blueprint estimate. A silent or truncated file passes every other check.

## Publish

```
python3 scripts/build_episode.py content/blueprints/<show>/<slug>.json
```

Uploads the MP3, VTT, chapters and board; updates the manifest and RSS; writes
both committed manifest copies. It re-runs the manifest gates on the *result*
and aborts before uploading the manifest if the outcome would be invalid.

## Post-flight

1. `curl -sI https://podcast.mingli.world/episodes/<slug>.mp3` — expect `200`
   and `accept-ranges: bytes`.
2. `curl -s https://podcast.mingli.world/healthz` — expect `{"ok":true}` with
   the new episode count.
3. Confirm a range request works, since the player's chapter seek depends on it:
   `curl -si -H 'Range: bytes=1000-1100' <url> | head -1` must be `206`.
4. Commit the manifest changes and the blueprint.

## Shipping frontend changes

Assets are cached hard. Bump **both** together or users get a broken mix:

- the `?v=N` query on `style.css` and the module entry in `site/index.html`
- `CACHE_V` in `site/sw.js`

Then `npm run deploy`. Ask before deploying — it is a production change.
