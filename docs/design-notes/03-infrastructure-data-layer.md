# Design Session — Round 3: Infrastructure, Data Layer & Operations

Research date: 2026-08-04. Inputs: `ENHANCEMENTS.md` §4–6, web research on GitHub
Actions scheduling limits, Cloudflare Workers cron triggers, and Cloudflare storage
options (KV / D1 / R2 / Durable Objects).
Companion docs: `docs/design-notes/01-content-script-pipeline.md`,
`docs/design-notes/02-tts-audio-stack.md`.

---

## Problem statement

The pipeline's weak points are **scheduling, monitoring, and the R2 client**:

1. **Scheduling is GitHub-Actions-only.** GH Actions cron: UTC-only (fits 18:00/19:00
   plan), min interval 5 min, runs can be delayed 5-15 min, and a workflow with **60 days
   of repo inactivity is auto-disabled** (a real outage risk for a personal project where
   the repo can go quiet). Pip-install + model download every run (no cache).
2. **Zero monitoring.** Nothing pings on failure — expired token, edge-tts breakage, R2
   incident all fail silently.
3. **R2 client is the wrangler CLI.** `scripts/r2_utils.py` shells `npx wrangler r2 object
   --remote` per op (~1-2 s each, spawns Node); no listing → feedback scan guesses keys.
   boto3 is in requirements.txt but unused.
4. **Data layer is JSON files on R2.** Fine at this scale, but queries (feedback
   aggregation in arrange.py) are manual JSON walks; no schema/consistency checks; no
   pruning of old episodes (10 GB free tier).

## Options

### Scheduling

#### Option A — Keep GH Actions, harden it (recommended)

Keep `daily.yml` cron. Mitigations: (a) monthly "keep-alive" workflow (touch or dispatch
a trivial job) to defeat the 60-day auto-disable; (b) `actions/cache` for pip deps;
(c) healthchecks.io ping after each job (see Monitoring).

**Pros:** zero cost, zero infra change, works today; the auto-disable is the only real
scheduler risk and the keep-alive defeats it; retries easy.
**Cons:** no sub-5-min runs (not needed), UTC-only (fine), still tied to GitHub.

#### Option B — Cloudflare Workers cron triggers (all-edge scheduling)

Move orchestration to Cloudflare Workers: `wrangler` cron triggers (min 1-min, 3 free
triggers, 10 ms CPU free / 30 s paid). Workers would call a pipeline… but the pipeline is
Python+TTS — a Worker cannot run edge-tts/Kokoro. Would only work for lightweight
steps (curl to trigger an external runner), so it doesn't replace the Python pipeline.

**Pros:** fully Cloudflare-native, no GitHub dependency, free 3 triggers.
**Cons:** can't run Python TTS; adds a second system for marginal benefit; the Python
pipeline still needs a host (Actions/VPS).

#### Option C — Cheap VPS (Hetzner ~€4-5/mo) self-hosted runner or cron

Host the whole pipeline on a small VPS: GH Actions self-hosted runner, or plain cron +
`systemd` timers; also enables local LLM + Kokoro-onnx with predictable hardware.

**Pros:** full control, no 60-day disable, no runner delays, can run local LLM/TTS; also
hosts the fallback engine; ~€4-5/mo.
**Cons:** breaks the $0 ethos (small but non-zero), new ops surface (SSH, updates,
certs), VPS uptime responsibility. **Overkill for a single daily episode** unless local
LLM/TTS becomes a hard requirement.

#### Option D — Hybrid: Workers health-probe + Actions pipeline

Workers hosts `/healthz` + uptime probe; Actions still runs the pipeline.

**Pros:** gets Cloudflare-native monitoring without moving the pipeline.
**Cons:** same as Option A plus a small extra function (already planned as `/healthz` in
ENHANCEMENTS §4).

### Data layer

#### Option E — Keep R2 JSON-as-DB (recommended for this scale)

Current model: manifest.json (source of truth) + per-episode/feedback JSON files.

**Pros:** simple, zero cost, already proven with ~157 episodes; versionable; the
frontend already reads it.
**Cons:** no SQL; feedback aggregation in arrange.py is a manual 7-day JSON walk;
consistency only guaranteed by convention.

#### Option F — Add Cloudflare D1 (SQLite) for structured data

Move feedback (+ optionally episode metadata) into D1 (free 5 GB, SQL).

**Pros:** real SQL for arrange.py aggregation (SELECT rating WHERE episode=...), schema
enforced, still $0, served via Pages Functions.
**Cons:** new binding + migration path + sync problem (manifest remains JSON/R2 —
two sources of truth); D1 free tier fine but adds moving parts.

#### Option G — Add KV for hot metadata (episode list, playlists)

KV for the manifest blob the frontend reads (faster reads than R2 fetch).

**Pros:** cheap, fast reads at the edge.
**Cons:** manifest is small; R2 fetch via Pages Function already works — no measurable
win; extra state to keep in sync.

**Design note:** D1/KV are real options but only pay off when JSON walks hurt. At one
episode/day they don't. Keep R2 JSON as primary; revisit D1 only if feedback analysis
grows (e.g., per-pattern stats dashboards).

### R2 client

#### Option H — boto3 rewrite of r2_utils.py (recommended)

Same function signatures (`upload`, `upload_json`, `get_json`, `download`) over
S3-compatible endpoint (`https://<account_id>.r2.cloudflarestorage.com`, the pattern
`api/r2.js` already uses). Gains: ListObjectsV2 (fix the feedback-key guessing),
head_object, multipart uploads, no npx/Node spawn per op; **removes the `npm install`
step from daily.yml**.

**Pros:** strictly better ops, less CI time, enables robust feedback scan; API is stable.
**Cons:** one-time rewrite + cred setup (CLOUDFLARE_API_TOKEN already exists; needs the
S3 endpoint + account ID).

### Monitoring

#### Option I — healthchecks.io heartbeats (recommended)

Free 20 checks; `curl -fsS https://hc-ping.com/<uuid>` after each `daily.yml` job step;
alert (email) on missing ping. Dead-man's switch semantics — catches "job ran but step
died silently" and "job never ran".

**Pros:** 5-min setup, $0, catches the silent-failure class precisely.
**Cons:** another account; pings only (no R2/edge checks).

#### Option J — Cloudflare `/healthz` + external uptime monitor

`functions/healthz.js`: `env.FEEDBACK_BUCKET.head('manifest.json')` + JSON validity,
return 200/503; point CronAlert (free 25 monitors) or similar at it.

**Pros:** checks the actual data path from outside Cloudflare; catches binding/DNS
issues; ~15 lines.
**Cons:** doesn't detect "pipeline failed but site is up" — pairs with Option I.

#### Option K — CI validation job (cheap insurance)

On every push: `python3 -m json.tool` on both manifests, duplicate-ID check, file_url
naming-convention check, playlists reference existing IDs.

**Pros:** catches the most common manual-series mistakes before publish; ~30 lines.
**Cons:** none worth mentioning.

### Storage hygiene

#### Option L — prune daily episodes > 90 days

`scripts/prune.py` (or fold into publish.py): delete `episodes/{date}.mp3` older than
90 days on R2 (keep series episodes — evergreen). 10 GB free tier headroom.

**Pros:** bounded storage, $0.
**Cons:** loses old daily episodes (acceptable for practice material; feedback files are
tiny and retained); note: RSS/manifest history references would 404 — decide whether to
remove from manifest or leave.

---

## Recommendation for the design session

1. **Scheduling:** Option A (keep Actions + keep-alive workflow + pip cache).
2. **R2 client:** Option H (boto3) — highest ops win per hour of work.
3. **Monitoring:** Option I + Option J (healthchecks.io pings AND `/healthz`).
4. **CI:** Option K (validation job on push).
5. **Data layer:** keep Option E (JSON/R2); treat D1/KV (F/G) as deferred.
6. **Pruning:** Option L, decided together with manifest-history handling.

## Open questions for the session

1. VPS (Option C) — is a €4-5/mo Hetzner box acceptable if it enables local LLM+TTS
   everywhere? Or does $0 stay a hard constraint?
2. Pruning: remove pruned episodes from manifest/RSS, or leave stale links?
3. Do we want the keep-alive workflow, or is the 60-day auto-disable risk acceptable
   given the repo is actively committed to?

## Files touched (when approved)

- `scripts/r2_utils.py` (boto3 rewrite; same signatures)
- `scripts/arrange.py` (real feedback listing via ListObjectsV2)
- `.github/workflows/daily.yml` (healthchecks pings, pip cache, drop npm install)
- `.github/workflows/keepalive.yml` (new), `.github/workflows/ci.yml` (new)
- `functions/healthz.js` (new), `functions/_middleware.js` (public path for /healthz)
- `scripts/prune.py` (new)
