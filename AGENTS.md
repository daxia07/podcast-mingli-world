# AGENTS.md — podcast.mingli.world

Coding-agent guide to this repo. Read this before making changes.
For what is currently true — inventory, what works, what is broken — read
**`docs/STATUS.md`** first. This file is how to work here; that one is where
things stand.

## Adding content? Use the skills, not the legacy scripts

Episodes are authored as **blueprint JSON** in `content/blueprints/` and built
with one command. The `generate_*.py` scripts are frozen legacy — do not add to
them or copy their pattern.

| Task | Path |
|---|---|
| New episode | `.claude/skills/episode-new` — or `/new-episode` |
| Ingest a video as learning material | `.claude/skills/youtube-ingest` — or `/ingest` |
| New show / playlist | `.claude/skills/show-new` |
| Review a draft before building | `.claude/skills/content-review` |
| Publish | `.claude/skills/publish` — or `/publish-episode` |

```bash
npm test                                          # 165 tests, no deps, no network
npm run gates                                     # manifest, show registry, blueprint coverage
python3 -m scripts.lib.gates <blueprint>          # gate one blueprint
python3 scripts/build_episode.py <bp> --dry-run   # plan without TTS
gh workflow run build-episode.yml -f blueprint="a.json b.json"   # build + publish from CI
gh workflow run build-episode.yml -f show=<id>                   # rebuilds the whole show
```

**This is enforced, not just documented.** The 14 one-off generator and
batch-publish scripts that import `scripts/_legacy_guard.py` are frozen —
running one prints a banner and exits 2 (bypass: `--legacy-ok`, or
`PODCAST_ALLOW_LEGACY=1`). The guard is import-safe, so
`ingest_youtube.py --backfill` can still read from them. CI fails if any episode
outside `content/legacy-episodes.json` lacks a blueprint. The daily-cron scripts
(`generate.py`, `publish.py`, `arrange.py`, `curate.py`) are deliberately not
frozen.

**Traps that have already bitten, all now guarded by tests or gates:** episodes
must be uniform 48 kHz mono (mixed sample rates make browsers stop mid-file —
`scripts/lib/audio.py`); episode URLs carry a `?v=` content hash because rebuilds
happen in place; the manifest the app reads lives on R2 and only reaches it via
the deploy sync; a new show needs `mono` and `order` or it renders nowhere, and
registering one in `content/shows.json` without syncing it into the manifest's
`playlists` block kills the build mid-publish, after the audio has already
reached R2 (`gate_shows_synced`); CSS
additions must not redefine shared tokens, and must use tokens rather than raw
colours or dark mode breaks (`tests/test_theme.mjs`); and
`site/search-index.json` is a build artifact — rebuild it with
`scripts/build_search_index.py` after publishing, never hand-edit it.

**Batch CI builds into one run.** `cancel-in-progress: false` protects the
*executing* run; a concurrency group still holds only one *pending* run, so
dispatching N builds in a row cancels N−2 of them. Pass several paths to
`blueprint` instead. Roughly 12 min of wall clock per episode, so keep a batch
to three or it risks the 60-minute job timeout.

**Where things run:** build and test on this Mac; publish from CI or the `agent`
host — this Mac has no ffmpeg, no edge-tts and no Cloudflare credentials, by
design (`docs/UPGRADE-SPEC.md` §0b).

## What this project is

A self-hosted, $0/month audio learning platform for one listener. Cloudflare
Pages serves a vanilla-JS app and a handful of Functions; R2 holds the MP3s and
the JSON that stands in for a database. No server, no build step.

Shows are data — `content/shows.json` is the registry. Do not hardcode a show
list anywhere.

## Architecture at a glance

| Layer | Technology | Notes |
|---|---|---|
| Hosting | Cloudflare Pages (`podcast-landing`) | static `site/` + Pages Functions |
| Storage | Cloudflare R2 `podcast-mingli-world` | JSON files ARE the DB |
| Functions | Pages Functions (JS) | manifest, RSS, episode MP3s, feedback POST, auth middleware |
| Auth | `functions/_middleware.js` | hardcoded `ming` / `ping` + SHA-256 cookie |
| Content pipeline | `scripts/build_episode.py` + blueprints | gates → synth → timeline → upload |
| Daily cron | `arrange → curate → generate → publish` | `daily.yml`, unchanged by the upgrade |
| TTS | edge-tts (free, no key) | `scripts/tts.py`; unofficial endpoint, the biggest availability risk |
| R2 CLI | `npx wrangler r2 ... --remote` | wrapped by `scripts/r2_utils.py` |
| Vercel mirror | `vercel.json` + `api/` | alternative config; Cloudflare is live |

Live: `https://podcast.mingli.world` · RSS: `/rss.xml`

### The daily cron (`daily.yml`, not frozen)

```
18:00 UTC  arrange.py   feedback from R2 → plan.json to R2
                        (≥80% good → the pattern appears more; <40% → dropped)
19:00 UTC  curate.py    3 RSS feeds → keyword-scored → data/today.json
19:00 UTC  generate.py  plan + content_bank + article → data/episode.mp3
19:00 UTC  publish.py   upload MP3, append to manifest.json, regenerate rss.xml
```

`scripts/content_bank.json` is the source data for these: `patterns`,
`tips`, `prompts`, plus `system_design`, `coding_interview` and `info_security`
sections. Blueprint episodes do not use it.

## Repo layout

```
site/          static SPA — index.html, app.js, style.css, sw.js, search-index.json
functions/     Pages Functions — _middleware.js (auth), manifest, rss, episodes/[file]
api/           Vercel mirror of functions/
content/       blueprints/, templates/, shows.json, legacy-episodes.json, sources/, notes/
scripts/       pipeline; scripts/lib/ is the current code, generate_*.py is frozen legacy
tests/         node:test (*.mjs) + unittest (test_*.py)
docs/          STATUS.md, UPGRADE-SPEC.md, podcast-craft.md, ANDROID-APP.md, aws-cert-track.md
data/ feedback/  BROKEN symlinks to another machine — gitignored, recreate with mkdir
```

## R2 object layout (the database)

```
manifest.json                # source of truth: metadata + episodes[] + playlists{}
rss.xml  plan.json  artwork.jpg
episodes/{slug}.mp3          # series;  episodes/{date}.mp3 for daily
chapters/  transcripts/  boards/
feedback/{date}_ep{id}.json  # one file per vote
```

Manifest episode fields: `id`, `slug`, `title`, `description`, `duration`,
`file_size_bytes`, `file_url` (carries `?v=`), `playlist`, `source`
(`legacy` | `tts` | `youtube`), `has_transcript`, `has_chapters`, `keywords`,
`sources[]`. `playlists` maps show id → `{title, description, mono, icon, order,
featured, episode_ids[]}` and is synced from `content/shows.json`.

## Frontend notes

- 4 tabs: Home, Library, Search, Me. Data comes from `GET /manifest.json`.
- Shows come from the manifest's `playlists`. `SHOW_META` in `app.js` is only a
  **fallback** for shows the manifest does not describe — register shows in
  `content/shows.json`, never by editing `app.js`.
- `sw.js` app-shell cache is `CACHE_V`; bump it and the `?v=` query strings in
  `index.html` together, or a new shell is served with stale JS
  (`tests/test_assets.mjs` catches this).
- `_headers`: `app.js`, `style.css`, `sw.js`, `index.html` are no-cache.

## Auth

The whole site is password-gated except public paths. `POST /api/login` with
hardcoded `ming` / `ping` returns cookie `mingli_auth` = SHA-256 of
`user:pass:env.AUTH_SECRET`. Public: `/rss.xml`, `/episodes/`, `/manifest.json`,
`/api/manifest`, `/api/rss`, `/artwork`, `/sw.js`, `/manifest.webmanifest`,
`/solutions.json`, `/.well-known/`, `/login`. Hardcoding is intentional for a
single-user site — keep the pattern if you change it.

## Env / secrets

| Var | Where | Used by |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` | GH secrets, `agent` host | all R2 ops via wrangler |
| `BASE_URL` | GH vars | RSS generation (defaults to the live domain) |
| `AUTH_SECRET` | Pages env | middleware token (default `tutor-local-dev`) |
| `COOKIE_DOMAIN` | Pages env | optional, cross-subdomain cookie |
| `TUTOR_DB_PATH` / `KNOWLEDGE_DIR_PATH` | local | `selector.py` |

## Gotchas

1. **Two manifest copies in git** — `scripts/manifest.json` and
   `site/manifest.json`. The R2 copy is authoritative at runtime; `npm run
   gates` checks parity. Never hand-edit either.
2. **Episode ids are allocated at build time** from the manifest and written
   back into the blueprint. Never pick one yourself.
3. **`npm run test:*` are not tests** — they execute pipeline scripts. The test
   suite is `npm test`.
4. **Two deploy configs** — Cloudflare (live) and Vercel (mirror). Update both
   if you change endpoints.
5. **Two TTS paths** — `generate.py` shells out to the edge-tts CLI; `scripts/
   tts.py` is the library used by everything new. Prefer `tts.py`.
6. **R2 listing is avoided** — scripts iterate known keys by convention.
7. **R2 free tier is 10 GB** and nothing prunes yet.

---

Design: `docs/UPGRADE-SPEC.md` · Decisions and tradeoffs: `DECISIONS.md` ·
Writing craft: `docs/podcast-craft.md` · Android: `docs/ANDROID-APP.md`
