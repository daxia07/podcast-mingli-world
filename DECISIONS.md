# DECISIONS.md — podcast.mingli.world

Agent-made and user-confirmed decisions. Newest first.
Architecture-significant entries carry options → decision → tradeoff.

---

- [2026-08-14] **Seeded `aws-security-specialty` with its exam-map episode, beyond the two SAA episodes asked for** — decided-by: agent · confidence: 0.8 · why: `show-new` records that two shows once sat at zero episodes for months and rendered as dead tiles, and the build workflow publishes straight to production R2, so shipping the registration without an episode would have repeated exactly that · revert: delete the blueprint and the show entry, re-sync the manifest
- [2026-08-13] **`cert-prep-2voice` added rather than changing `cert-prep`** — decided-by: user · confidence: 0.85 · why: the seven published AIF-C01 episodes were authored single-narrator and cannot grow a second voice retroactively; a sibling template lets SAA and SCS use the cold-open-and-disagreement format while the AIF series stays untouched, and gives an honest comparison of whether the format plays better · revert: delete `content/templates/cert-prep-2voice.json` and point the two new shows at `cert-prep`
- [2026-08-13] **The two AWS cert shows are registered unfeatured at order 11 and 12** — decided-by: agent · confidence: 0.8 · why: `show-new` warns that a show with one episode renders as a dead tile, and promoting them next to `aws-ai-practitioner` at order 3 would renumber four existing shows for content that is not seeded yet · revert: set `featured` and `order` in `content/shows.json`, re-sync the manifest
- [2026-08-13] **Episode craft rules live in the template's `authoring_brief`, not in a doc** — decided-by: agent · confidence: 0.85 · why: the brief is the only text an author or an LLM reliably reads before writing; craft guidance parked in `docs/` gets written once and consulted never · revert: trim the brief back to the `cert-prep` original
- [2026-08-13] **Shelving is device-local; server archiving stays the source of truth** — decided-by: agent · confidence: 0.85 · why: there is no write API for the manifest, and hiding an episode is a per-device preference; a local override can restore an archived show without reversing the decision for the feed · revert: delete the two localStorage keys
- [2026-08-13] **Two-stage swipe with an Undo toast rather than a confirmation** — decided-by: agent · confidence: 0.85 · why: a confirm on a reversible action is friction, and a one-stage swipe makes accidental shelving trivial · revert: thresholds in `site/js/shelf.js`
- [2026-08-13] **Codex checkout kept at `~/git-resources/codex`, pinned at 9ca0337** — decided-by: user · why: the teardown notes cite line counts from that commit; pulling will drift them · revert: re-clone
- [2026-08-12] **Episode URLs carry a content hash; episodes are no longer cached immutably** — decided-by: agent · confidence: 0.9 · why: `immutable` meant a phone that cached a broken build would never ask for the fix; episodes are rebuilt in place, so the header was a lie · revert: `functions/episodes/[file].js`
- [2026-08-12] **Audio format pinned to 48 kHz mono 64 kbps, verified by a frame scanner** — decided-by: agent · confidence: 0.95 · why: speech at 48 kHz spliced with 24 kHz silence made browsers stop decoding eleven seconds in, while ffprobe reported the file as fine · revert: `scripts/lib/audio.py`
- [2026-08-12] **Dark mode removed rather than fixed** — decided-by: agent · confidence: 0.85 · why: 41 hardcoded light colours elsewhere in the stylesheet do not flip, so it rendered white text on white; re-adding needs those converted to tokens and checked in a browser · revert: git revert the removal commit
- [2026-08-12] **APK built in CI, not locally** — decided-by: agent · confidence: 0.85 · why: the runners already have a JDK and the Android SDK; installing that toolchain locally is about half a gigabyte · revert: delete `.github/workflows/build-apk.yml`
- [2026-08-12] **Cover art generated in pure Python** — decided-by: agent · confidence: 0.8 · why: `artwork.jpg` was referenced everywhere and never existed; no image tooling on this machine, and PNG is simple enough to encode directly · revert: delete `scripts/make_artwork.py` and the PNGs
- [2026-08-12] **Legacy generators frozen; new episodes gated on having a blueprint** — decided-by: agent · confidence: 0.9 · why: documentation alone doesn't stop the old habit — the 14 one-off scripts now exit 2 unless bypassed, and CI fails on any episode outside the grandfathered set without a blueprint · revert: delete `scripts/_legacy_guard.py` imports and the `blueprint_required` gate
- [2026-08-12] **Deploy moved to GitHub Actions** — decided-by: agent · confidence: 0.85 · why: the Cloudflare token exists in CI and on `agent` but not on the dev Mac, so laptop deploys fail; CI also runs the gates and verifies 206/healthz after shipping · revert: delete `.github/workflows/deploy.yml`
- [2026-08-13] **Search indexes what episodes *say*, via a static `site/search-index.json`** — decided-by: agent · confidence: 0.85 · why: the exact transcripts already existed but were unsearchable, and a 99 KB static file needs no R2 write, no Function, and diffs in review — unlike an R2 object or a query-time API · revert: delete `scripts/build_search_index.py`, `site/js/search.js` and the CI steps
- [2026-08-13] **The moment index is built from the public site, not from R2 credentials** — decided-by: agent · confidence: 0.9 · why: `/transcripts/` and `/chapters/` are already public for podcast clients, so the builder runs anywhere, including this Mac, with no secret · revert: switch `read_artifact` to `r2.get_text`
- [2026-08-13] **`/search-index.json` is public** — decided-by: agent · confidence: 0.8 · why: it is derived wholly from `/transcripts/`, which is already whitelisted, so gating it would protect nothing while breaking the deploy verification · revert: drop the path from `PUBLIC_PATHS` in `functions/_middleware.js`
- [2026-08-13] **Dark mode restored, with the palette enforced by a test** — decided-by: agent · confidence: 0.85 · why: the 2026-08-12 removal was about ~40 hardcoded light colours, not the palette; those are now tokens and `tests/test_theme.mjs` fails the build if a raw colour reappears or the two dark blocks drift · revert: git revert; the tokens can stay
- [2026-08-13] **Appearance is a three-state setting, defaulting to System** — decided-by: agent · confidence: 0.9 · why: a phone that flips at sunset should not override a deliberate choice, and an inline pre-paint snippet avoids the white flash a JS-only toggle causes · revert: delete `site/js/theme.js` and the Account card
- [2026-08-13] **`build-episode` now dispatches Deploy explicitly** — decided-by: agent · confidence: 0.8 · why: the publish commit carries `[skip ci]`, so new episodes would have stayed unsearchable until an unrelated push touched `site/**` · revert: drop the last step of `build-episode.yml`
- [2026-08-12] **Legacy backfill stopped at 81 blueprints (user decision)** — decided-by: user · why: the remaining ~90 episodes live in monolithic generators and keep working as-is; they simply never gain chapters · revert: extend `migrate_to_blueprints.py`
- [2026-08-12] **Legacy blueprints graded as `audio: existing` — coverage and TTS gates downgrade to warnings** — decided-by: agent · confidence: 0.85 · why: published audio cannot grow a missing section or lose a slash, and blocking on it made 20 episodes unmigratable for unfixable reasons · revert: drop the `bp.audio` check in `gates.py`
- [2026-08-12] **Migrated blueprints adopt the published slug, not their source filename** — decided-by: agent · confidence: 0.9 · why: the slug is the key for `episodes/<slug>.mp3` and every side artifact; keeping the source name would make a rebuild upload to a key the manifest doesn't reference · revert: `migrate_to_blueprints.py` `link_existing_ids`
- [2026-08-12] **Range support added to the episode Function; `Accept-Ranges` was a lie** — decided-by: agent · confidence: 0.95 · why: verified live that a range request returned 200 with the full 10 MB, so every chapter seek would re-download from byte 0 · revert: git revert `functions/episodes/[file].js`
- [2026-08-11] **Dropped the boto3/R2 rewrite; list feedback via the existing Pages R2 binding instead** — decided-by: agent · confidence: 0.85 · why: boto3 needs S3 credentials that don't exist yet and can never be re-read once created, while `env.FEEDBACK_BUCKET.list()` gives the one missing capability with zero new secrets · revert: spec §3.1 keeps the boto3 path as a documented Phase-4 option
- [2026-08-11] **LLM provider = DeepSeek (`deepseek-v4-flash`), verified working** — decided-by: agent · confidence: 0.95 · why: it is the house convention across convfinqa-agent / job-hunter / generic-tutor-web, the key already exists at `deepseek/api_key`, and a live call succeeded · revert: `export LLM_MODEL=…` / `LLM_ENDPOINT=…`
- [2026-08-11] **Keys resolved at runtime by `scripts/lib/llm.py`, never stored in the repo** — decided-by: agent · confidence: 0.9 · why: env → local `pass` → remote `pass` over SSH, mirroring `convfinqa-agent/src/convfinqa/llm.py`; the secret never enters git, a transcript, or shell history · revert: delete `scripts/lib/llm.py`
- [2026-08-11] **Scope the upgrade as docs/UPGRADE-SPEC.md, 5 phases** — decided-by: agent · confidence: 0.85 · why: the ask spans content tooling, ingestion, and UI; a phased spec lets goal mode execute without re-deciding · revert: delete the spec file

## 2026-08-11 — Content authoring engine

**Options considered**
- A. Agent-authored blueprints only (templates in git, no API key)
- B. Runtime LLM for every episode
- C. Agent-authored blueprints **+** `scripts/llm.py` fallback for the unattended daily cron

**Decision: C** — user-confirmed. Both paths emit the same validated *episode blueprint*
JSON; git remains the record of what was said, while the daily cron still produces varied
scripts without a human.

**Tradeoff accepted:** one API key (DeepSeek, ~$0.30/mo) and a second code path to keep
working, in exchange for the cron not degrading to a fixed template.

## 2026-08-11 — YouTube material

**Options considered**
- A. Keep re-hosting source audio, add transcripts only
- B. Transcript → study blueprint → **original** episode in our own voice
- C. Both, for every video

**Decision: B** — user-confirmed. New material is ingested as text and re-written; the 14
existing re-hosted episodes stay and gain transcripts.

**Tradeoff accepted:** more pipeline work per video and a dependency on transcript quality,
in exchange for original content, better learning artifacts (notes, question sets), and no
copyright grey area for anything new.

## 2026-08-11 — Frontend direction

**Options considered**
- A. Native-feel polish on the existing vanilla SPA, split into ES modules (no build step)
- B. Rewrite in React/Next
- C. Capacitor native shell

**Decision: A** — user-confirmed.

**Tradeoff accepted:** hand-written gestures, sheets and state instead of a component
framework, in exchange for zero build pipeline, no Cloudflare Pages config change, and
incremental shipping. B/C remain open later; A is a prerequisite for C regardless.

## 2026-08-11 — Chapters and transcripts are captured at synthesis time

Per-line TTS segments are ffprobe'd and concatenated with `-c copy` (never `acrossfade`),
so cumulative offsets are exact. TTS episodes therefore get sample-accurate chapters and a
line-synced VTT for free; faster-whisper is used **only** for imported audio.

**Tradeoff accepted:** no crossfades between timed segments (silence segments of known
length instead), in exchange for exact timings and no transcription cost.
