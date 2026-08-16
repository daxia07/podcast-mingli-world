# STATUS — where the project actually stands

A living snapshot, rewritten in place and edited by deletion. `UPGRADE-SPEC.md`
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

Every line is measured rather than transcribed, so chapter and transcript offsets
come from the same numbers that produced the audio.

## Where things run

| | Mac | CI (GitHub Actions) | `agent` host |
|---|---|---|---|
| Tests, gates, dry runs | ✅ | ✅ | ✅ |
| Build audio (ffmpeg, edge-tts) | ❌ not installed | ✅ | ✅ |
| Publish to R2 / deploy Pages | ❌ no credentials, by design | ✅ | ✅ |
| LLM calls | ✅ key resolved from `pass` at run time | ✅ | ✅ |

Build and reason locally; publish from CI. Deliberate, not an accident — see
UPGRADE-SPEC §0b.

## Inventory

| | Count |
|---|---|
| Episodes in the manifest | 200 |
| Shows | 18 — 15 active, 3 archived |
| Blueprints | 124 |
| Templates | 12 |
| Episodes with exact chapters + transcript | 43 |
| Search index | 2,355 lines + 220 chapters across 43 episodes (~385 KB) |
| Grandfathered legacy ids (blueprint not required) | 157 |
| Tests | 165 — 81 `node:test`, 84 `unittest` |
| Pages Functions | 11 |
| Skills / slash commands | 5 / 3 |
| Workflows | ci, deploy, build-episode, build-apk, daily |

## Live

- **Content system.** Blueprints, templates with authoring briefs, a show
  registry the frontend reads from the manifest, and five skills that are the
  supported way to add anything. The 14 legacy generator scripts are frozen.
- **Player.** Chapter rail on the seek bar, tap-to-seek synced transcript,
  solution boards, queue, sleep timer, lock-screen controls, offline shell cache.
- **Search inside episodes.** Titles, descriptions and boards for all 200; every
  spoken line and chapter for the 43 with transcripts. A result reads "1:25 in
  Domain 2" and starts playback 1.2 s early.
- **Swipe-to-shelve.** Left-swipe to hide, Undo toast, Shelved tab. Device-local
  in `localStorage` — nothing is deleted.
- **Appearance.** System / Light / Dark, applied before first paint.
- **Android.** A signed APK built in CI, no Play account needed (`ANDROID-APP.md`).
- **Delivery.** Push to `master` → tests, gates, deploy, manifest sync to R2,
  index refresh, then live checks of `/healthz`, a `206` range request and a
  non-empty index. Publishing dispatches the deploy itself.
- **AWS certification tracks.** All three exams Ming is sitting have over an hour
  of audio: AIF-C01 66:38 (9 eps), SAA-C03 69:41 (6), SCS-C03 70:04 (6). Roadmap
  and remaining episodes: `aws-cert-track.md`.

## Guardrails, and the bug each one remembers

Every row is a real failure that shipped once. The guard is why it cannot ship
twice.

| Guard | What it caught |
|---|---|
| `lib/audio.py` frame scanner | 48 kHz speech spliced with 24 kHz silence stopped playback at 13 s |
| `?v=<content-hash>` episode URLs | `immutable` caching meant the phone never re-fetched a rebuilt file |
| `classifyRange()` + deploy check | a range request returned 200 and the whole 10 MB, so every seek re-downloaded |
| `gate_show_registry` | a new show rendered nowhere, because `app.js` held a hardcoded show list |
| `gate_blueprint_required` | the only thing stopping a return to one-off generator scripts |
| `test_theme.mjs` | dark mode drawing white text on white cards |
| `test_assets.mjs` | a new HTML shell served with stale JS |
| `--no-shrink` on the index build | a flaky fetch silently shipping a thinner search index |
| `stdin=DEVNULL` everywhere | ffmpeg ate the blueprint list from stdin; 1 of 7 episodes built |
| `manifest_parity` | the app read an R2 manifest 102 episodes behind the repo |

## Known-broken and unrun

- **Phase 2 ingestion.** `ingest_youtube.py`, `curate.py` and
  `blueprint_from_source.py` are written and unit-tested at the edges, and have
  never been pointed at a real channel. Needs `yt-dlp`.
- **`daily.yml`.** The original daily-episode cron, untouched by the upgrade.
- **`data/` and `feedback/`** are symlinks to another machine, so they are broken
  here. Gitignored; `mkdir` them on a fresh checkout.

## Owed, and deliberately not done

- **Real-device pass.** Player, swipe thresholds and both themes are covered by
  unit tests and headless-Chrome screenshots. No phone has seen them.
- **Legacy transcripts.** 157 episodes predate the blueprint system, so they
  cannot be searched by what they say. A whisper backfill would roughly
  four-fold the searchable corpus; the largest remaining piece of work.
- **`prune.py`.** R2 is on a 10 GB free tier and nothing prunes yet.
- **Kokoro TTS fallback.** edge-tts is an unofficial endpoint and the single
  biggest availability risk (`ENHANCEMENTS.md` §1). Still unmitigated.
- **`boto3` R2 client.** Dropped on purpose — needs S3 credentials that do not
  exist; listing already works through the Pages R2 binding.

## Next

1. SCS-C03 Domain 6 (governance, 14%) — the one uncovered domain before Ming
   sits Security Specialty.
2. `aws-solutions-architect` and `aws-security-specialty` are still
   `featured: false` at order 11 and 12, so they do not appear on the home row.
   That was right at one episode each; they have six apiece now.
3. Whisper-backfill the legacy episodes so search covers everything.

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

---

Decisions and their tradeoffs: `../DECISIONS.md`. Design: `UPGRADE-SPEC.md`.
Working rules for agents: `../AGENTS.md`.
