# STATUS — where the project actually stands

Last updated: **2026-08-13**. A living snapshot, kept honest: what is live, what
exists but has never run, and what is deliberately not done. `UPGRADE-SPEC.md`
says what was planned; this says what is true.

---

## The shape of it

A $0/month audio learning platform for one listener. Cloudflare Pages serves a
vanilla-JS app and a handful of Functions; R2 holds the MP3s and the JSON that
stands in for a database. There is no server and no build step.

Content is **data**: an episode is a blueprint JSON in git, and one command turns
it into audio, chapters, a transcript, a manifest entry and an RSS item.

```
content/blueprints/<show>/<slug>.json
        │
        ├─ gates  ────────────── slug, voices, TTS safety, template coverage,
        │                        duration, claims, board, id uniqueness
        │
        ├─ synth  ────────────── one TTS call per line, each ffprobe'd, then
        │                        concatenated with -c copy (48 kHz mono, pinned)
        │
        ├─ timeline ──────────── measured offsets → chapters + WebVTT
        │
        └─ upload ────────────── episodes/ chapters/ transcripts/ boards/
                                 manifest.json + rss.xml → R2
                                 search-index.json → git → Pages
```

Because every line is measured rather than transcribed, chapter and transcript
offsets come from the same numbers that produced the audio.

## Where things run

| | Mac | CI (GitHub Actions) | `agent` host |
|---|---|---|---|
| Tests, gates, dry runs | ✅ | ✅ | ✅ |
| Build audio (ffmpeg, edge-tts) | ❌ not installed | ✅ | ✅ |
| Publish to R2 / deploy Pages | ❌ no credentials, by design | ✅ | ✅ |
| LLM calls | ✅ key resolved from `pass` at run time | ✅ | ✅ |

Build and reason locally; publish from CI. This is a deliberate split, not an
accident — see UPGRADE-SPEC §0b.

## Inventory

| | Count |
|---|---|
| Episodes in the manifest | 174 |
| Shows | 14 — 11 active, 3 archived |
| Blueprints | 98 |
| Templates | 10 |
| Episodes with exact chapters + transcript | 17 |
| Moments in the search index | 485 across 17 episodes (~99 KB) |
| Grandfathered legacy ids (blueprint not required) | 157 |
| Tests | 165 — 81 `node:test`, 84 `unittest` |
| Pages Functions | 11 |
| Skills / slash commands | 5 / 3 |
| Workflows | ci, deploy, build-episode, build-apk, daily |

## Live

**Content system.** Blueprints, templates with authoring briefs, a show registry
the frontend reads from the manifest, and five skills that are the supported way
to add anything. The 14 one-off `generate_*.py` scripts are frozen: running one
prints a banner and exits 2.

**Player.** Chapter rail on the seek bar, synced transcript you can tap to seek,
solution boards, queue, sleep timer, lock-screen controls, offline shell caching.

**Search inside episodes.** Titles, descriptions and solution boards for all 174;
every spoken line and chapter for the 17 with transcripts. A result is "1:25 in
Domain 2", with the line quoted and the match highlighted; tapping it starts
playback 1.2 s early.

**Swipe-to-shelve.** Left-swipe any row to hide it, with an Undo toast and a
Shelved tab. Device-local, stored in `localStorage` — nothing is deleted, and
archived shows can be restored per device.

**Appearance.** System / Light / Dark, applied before first paint so a dark phone
never flashes white.

**Android.** A signed APK built in CI, installable without a Play developer
account. See `ANDROID-APP.md`.

**Delivery.** Push to `master` → tests, gates, deploy, manifest sync to R2,
search index refresh, then live verification of `/healthz`, a `206` range
request, and a non-empty index. Publishing episodes dispatches the deploy itself.

## Guardrails, and the bug each one remembers

Every row here is a real failure that shipped once. The guard is the reason it
cannot ship twice.

| Guard | What it caught |
|---|---|
| `lib/audio.py` frame scanner | 45 format changes mid-file (48 kHz speech spliced with 24 kHz silence) stopped playback at 13 s |
| `?v=<content-hash>` episode URLs | `Cache-Control: immutable` meant the phone never re-fetched a rebuilt file — the fix for the above was invisible for a day |
| `classifyRange()` + deploy check | `Accept-Ranges` was a lie: a range request returned 200 and the whole 10 MB, so every chapter seek re-downloaded from byte 0 |
| `gate_show_registry` | a new show rendered nowhere, because `app.js` still held a hardcoded show list |
| `gate_blueprint_required` | the only thing stopping a return to one-off generator scripts |
| `test_theme.mjs` | dark mode drawing white text on white cards — ~40 hardcoded light colours that did not flip |
| `test_assets.mjs` | a new HTML shell served with stale JS, because `?v=` and `CACHE_V` were bumped separately |
| `--no-shrink` on the index build | a flaky fetch during deploy silently shipping a thinner search index |
| `stdin=DEVNULL` everywhere | ffmpeg ate the blueprint list from stdin; 1 of 7 episodes built |
| `manifest_parity` | the app read an R2 manifest 102 episodes behind the repo |

## Built but never run

- **Phase 2 ingestion.** `ingest_youtube.py`, `curate.py` and
  `blueprint_from_source.py` are written and unit-tested at the edges, and have
  never been pointed at a real channel. Needs `yt-dlp`.
- **`daily.yml`.** The original daily-episode cron, untouched by the upgrade.

## Owed, and deliberately not done

- **Real-device pass.** The player, swipe thresholds and both themes are covered
  by unit tests and headless-Chrome screenshots. No phone has seen them.
- **Legacy transcripts.** ~90 episodes predate the blueprint system, so they have
  no chapters, no transcript, and cannot be searched by what they say. A whisper
  backfill would roughly six-fold the searchable corpus; it is the largest single
  piece of remaining work.
- **`prune.py`.** R2 is on a 10 GB free tier and nothing prunes yet.
- **Kokoro TTS fallback.** edge-tts is an unofficial endpoint and the single
  biggest availability risk (`ENHANCEMENTS.md` §1). Still unmitigated.
- **`boto3` R2 client.** Dropped on purpose — it needs S3 credentials that do not
  exist, and listing already works through the Pages R2 binding.

## Verifying

```bash
npm test            # 165 tests, no deps, no network
npm run gates       # manifest parity, show registry, blueprint coverage
python3 scripts/build_episode.py <blueprint> --dry-run
python3 scripts/build_search_index.py           # rebuild the moment index
curl -s https://podcast.mingli.world/healthz
```

Visual checks run against a local `python3 -m http.server` plus headless Chrome —
the browser-automation tooling cannot reach this machine's localhost.

## Open questions for the listener

1. Are the swipe thresholds right on a real phone (56 px to reveal, 160 px to
   commit)? Should shelving also hide an episode on its own show page?
2. Is the *Reading Codex* teardown pitched at the right level?
3. Whisper-backfill the ~90 legacy episodes so search covers everything?

---

Decisions and their tradeoffs: `../DECISIONS.md`. Design: `UPGRADE-SPEC.md`.
Working rules for agents: `../AGENTS.md`.
