# DECISIONS.md — podcast.mingli.world

Agent-made and user-confirmed decisions. Newest first.
Architecture-significant entries carry options → decision → tradeoff.

---

- [2026-08-12] **Legacy generators frozen; new episodes gated on having a blueprint** — decided-by: agent · confidence: 0.9 · why: documentation alone doesn't stop the old habit — the 14 one-off scripts now exit 2 unless bypassed, and CI fails on any episode outside the grandfathered set without a blueprint · revert: delete `scripts/_legacy_guard.py` imports and the `blueprint_required` gate
- [2026-08-12] **Deploy moved to GitHub Actions** — decided-by: agent · confidence: 0.85 · why: the Cloudflare token exists in CI and on `agent` but not on the dev Mac, so laptop deploys fail; CI also runs the gates and verifies 206/healthz after shipping · revert: delete `.github/workflows/deploy.yml`
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
