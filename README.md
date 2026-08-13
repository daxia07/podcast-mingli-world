# podcast.mingli.world

A personal audio learning platform. 174 episodes across 11 shows — coding
interviews, system design, behavioural, AWS certification, agentic AI — served
as a mobile web app and a podcast feed, for about zero dollars a month.

**Live:** https://podcast.mingli.world · **RSS:** `/rss.xml` · **Android:** see
[docs/ANDROID-APP.md](docs/ANDROID-APP.md)

## Adding content

Episodes are **data**, not code. One blueprint JSON in, one command out.

```bash
/new-episode                 # the episode-new skill: interview → blueprint → build
/ingest <youtube-url>        # transcript → study notes → original episode
/publish-episode <slug>      # pre-flight, publish, verify
```

The `generate_*.py` scripts are frozen — running one exits 2 and points here.
CI fails if any episode outside `content/legacy-episodes.json` lacks a blueprint,
so the format can't quietly decay. Full guide: **[AGENTS.md](AGENTS.md)**.

```bash
npm test                                   # 165 tests, no deps, no network
npm run gates                              # manifest + show registry + blueprint coverage
python3 scripts/build_episode.py <bp> --dry-run    # plan without spending a TTS run
```

## Architecture

| Layer | Technology | Notes |
|---|---|---|
| Hosting | Cloudflare Pages | static `site/` + Pages Functions |
| Storage | Cloudflare R2 | JSON files and MP3s are the database |
| Content | blueprint JSON in git | `content/blueprints/**`, validated by gates |
| TTS | edge-tts | pinned to 48 kHz mono; Kokoro fallback planned |
| LLM | DeepSeek (optional) | key resolved at run time, never stored in repo |
| CI | GitHub Actions | test, deploy, build episodes, build APK |

No backend server, no database.

```
content/          blueprints, templates, show registry, source notes
scripts/lib/      the pipeline: blueprint, timeline, chapters, transcript, gates, synth
scripts/          build_episode, ingest_youtube, curate, migrate, sync_manifest,
                  build_search_index
site/             vanilla-JS app; js/ holds chapters, transcript, search, shelf,
                  theme, player UI
functions/        Pages Functions: episodes, chapters, transcripts, artwork, healthz
tests/            126 tests — node:test for JS, unittest for Python
docs/             STATUS (where things stand), UPGRADE-SPEC (design),
                  ANDROID-APP (install), design-notes
.claude/skills/   the supported ways to add content
```

## The app

Four tabs — Home, Library, Search, Account — plus a full player with:

- **chapter rail** on the seek bar, tap a segment to jump
- **synced transcript**, tap a line to seek, searchable
- **search inside episodes** — every spoken line is indexed with its timestamp,
  so a result is "4:12 in Domain 2", not just an episode title
- **swipe-to-shelve** on any episode row, with an Undo toast and a Shelved tab
- **light / dark / system** appearance, set in Account
- solution boards, queue, sleep timer, lock-screen controls, offline caching

Chapters and transcripts are exact rather than transcribed: each line is
synthesised separately and measured, so offsets come from the same measurement
that produced the audio.

## Operations

| Task | How |
|---|---|
| Deploy | push to `master` — CI runs gates, deploys, syncs the manifest to R2, verifies `206` and `/healthz` |
| Build episodes | `gh workflow run build-episode.yml -f show=<id>` |
| Build the APK | `gh workflow run build-apk.yml` |
| Health | `curl https://podcast.mingli.world/healthz` |

**Where things run:** build and test on the Mac; publish from CI or the `agent`
host. This Mac has no Cloudflare credentials, by design.

## Shows

11 active, 3 archived. The registry is `content/shows.json`; the frontend reads
titles, badges, ordering and featured status from the manifest, so adding a show
needs no frontend change.

Archived shows stay in the manifest and the RSS feed — nothing is deleted — and
can be restored per-device from the app's Shelved tab.

## Known gaps

Full picture — inventory, guardrails and what is owed — in
**[docs/STATUS.md](docs/STATUS.md)**.

- ~90 legacy episodes have no blueprint, so they have neither chapters nor a
  transcript, and therefore cannot be searched by what they say. Deliberate.
- `boto3` R2 rewrite dropped; listing goes through the Pages R2 binding instead.
- The player UI has unit-tested logic and headless-Chrome screenshots, but no
  pass on a real phone.
