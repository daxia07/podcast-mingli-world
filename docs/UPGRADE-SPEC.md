# UPGRADE-SPEC — Content System, Learning Feeds, and Native Player

Status: **Phases 0–3 shipped and live; Phase 4 partial**  ·  Written: 2026-08-11  ·  Last updated: 2026-08-13

| Phase | State |
|---|---|
| §3.1b Range + cache headers | **live** — verified `206` in production; cache headers later corrected off `immutable` |
| Phase 0 foundations | **live** — lib package, gates, 165 tests, CI, deploy, `/healthz`, feedback-list |
| Phase 1 content system | **live** — 9 templates, show registry, `build_episode.py`, 5 skills, 81 blueprints migrated |
| Phase 2 ingestion | **built, unrun** — needs `yt-dlp`; `curate.py` and `ingest_youtube.py` never executed against a real channel |
| Phase 3 player | **live** — chapters, synced transcript, swipe-to-shelve, moment search, dark mode (restored 2026-08-13 behind a palette test) |
| Phase 4 backfill/prune | **partial** — cover art, symlinks and manifest sync done; whisper backfill and `prune.py` not started |

Shipped beyond the original spec: an Android APK build (`docs/ANDROID-APP.md`),
cover art generation, an MP3 frame scanner guarding audio uniformity, manifest
sync to R2 on deploy, four new shows (AWS AI Practitioner, Agentic AI investing,
Building Agentic Systems, plus the archived Airwallex set), and search across
what episodes actually say (`scripts/build_search_index.py` → `site/js/search.js`).

Remaining: run the ingestion pipeline once end to end, backfill transcripts for
the ~90 legacy episodes, storage pruning, and a real-device pass over the player.

**Search moments (added 2026-08-13).** Every episode with an exact transcript
contributes its lines and chapters, each with a start time, to a single static
`site/search-index.json` (~100 KB for 17 episodes). The app fetches it lazily on
the first keystroke in Search and ranks metadata and moments together, so a hit
can be "1:25 in Domain 2" rather than an episode title. It is rebuilt from the
public `/transcripts/` and `/chapters/` endpoints — no credentials — after every
publish and again on every deploy, with `--no-shrink` so a flaky fetch cannot
silently reduce coverage. Coverage grows only as blueprint-built episodes do:
the ~90 legacy episodes have no transcript and so remain title-searchable only.

---

Companion docs: `ENHANCEMENTS.md`, `docs/design-notes/01..03`. This spec supersedes the
"open questions" in those notes where they conflict — the decisions are recorded in §0.

---

## 0. Decisions already made (do not re-open)

| # | Decision | Rationale |
|---|---|---|
| D1 | **Agent-authored content + LLM fallback.** Episodes are authored as *blueprint JSON* committed to git, written either by a coding agent (via repo skills) or by `scripts/llm.py` (DeepSeek V4 Flash, ~$0.30/mo) for the unattended daily cron. Both paths emit the **same validated blueprint**. | Git stays the source of truth for what was said; cron still varies daily. |
| D2 | **YouTube → transcript → blueprint → original episode.** New YouTube material is ingested as text, distilled into a structured blueprint, and re-written as an original script in the show's own voice. Existing re-hosted YouTube audio episodes stay as they are, and gain transcripts. | Best learning value, no copyright grey area for new material. |
| D3 | **Native-feel polish on the existing vanilla SPA.** No React/Next rewrite, no Capacitor shell. Split `app.js` into ES modules (`<script type="module">`, still no build step). | Ships incrementally, zero deploy-config change, keeps $0/no-build ethos. |
| D4 | Keep the $0 constraint. No VPS. Cloudflare Pages + R2 remain the platform. | Existing ethos. |
| D5 | Chapters and transcripts are **generated at synthesis time** for TTS episodes (exact, free) and via faster-whisper **only** for imported audio. | See §3.3 — per-segment ffprobe gives sample-exact offsets. |

---

## 0b. Where things actually run (verified 2026-08-11)

This Mac (`daxia`) has **never been the pipeline host** and doesn't need to become one:

- `data/` and `feedback/` symlink to `/Users/ding/workspace/podcast/…` — user `ding`, i.e.
  the `agent` host (`ding@192.168.31.170`, in `~/.ssh/config`). That is the machine where
  manual series runs have always happened.
- `npx wrangler whoami` on this Mac: **not authenticated**. No OAuth state, no token.
- The `pass` store on this Mac holds one unrelated entry; the real keys are on `agent`.
- The daily cron authenticates entirely through GitHub Actions —
  `daily.yml` passes `secrets.CLOUDFLARE_API_TOKEN` to the arrange, generate and publish
  steps, plus `vars.BASE_URL`.

**Therefore no new Cloudflare credential needs to be created for anything in this spec.**
Publishing already has working auth in the two places it happens: GitHub Actions (cron) and
`agent` (manual runs). Development work — the lib package, schemas, gates, tests, blueprint
authoring, and the entire frontend — needs no R2 access at all; only the publish step does.

Practical rule for goal mode: **build and test on this Mac, publish from `agent` or CI.**
Anything that needs R2 write access should be runnable on `agent` over SSH, or deferred to
a workflow run.

## 1. Why this work exists (current-state findings)

1. **There is no content system.** 157 episodes were produced by ~10 one-off generator
   scripts with the actual prose hardcoded inside `.py` modules
   (`scripts/mock_dialogues/*.py`, `scripts/coding_mocks/*.py`) or loose `.txt` drafts.
   Adding one episode means writing a new Python module, hand-picking a non-colliding ID,
   and hand-editing the manifest. Nothing is validated.
2. **Section structure is generated then thrown away.** Scripts contain `── Pattern 3 of 6 ──`
   markers; `tts.py::preprocess_text()` strips them (line 50) and no timings are recorded.
   Chapters are therefore *free* if captured during synthesis — we currently discard them.
3. **The YouTube pipeline downloads audio only.** `download_youtube.py` has 14 hardcoded URLs,
   no transcript, no text extraction, no derived content.
4. **The player is flat.** No chapters, no transcript, no gestures, no dark mode, no sleep
   timer, no lock-screen metadata, no offline downloads. `solutions.json` has boards for
   2 of 46 coding-prep episodes.
5. **Data hygiene debt.** Two manifest copies; 138/157 episodes missing `source`; two
   playlists (`behavioral-interview`, `infosec-interview`) registered with zero episodes;
   no ID-collision guard; no tests; no CI; no monitoring; `data/` and `feedback/` are
   broken symlinks to another machine.

---

## 2. Target architecture

```
content/                          # NEW — content is data, in git
  shows.json                      # show registry (single source for playlists + UI meta)
  templates/*.json                # episode format definitions
  blueprints/<show>/<slug>.json   # one file per episode (the authored artifact)
  sources/youtube/<video_id>.json # ingested transcript + extracted study blueprint
  notes/<slug>.md                 # study notes rendered in the app reading panel

schemas/                          # NEW — JSON Schema, used by gates + CI
  episode.schema.json
  template.schema.json
  source.schema.json
  shows.schema.json

scripts/
  lib/                            # NEW — the real codebase (importable, tested)
    __init__.py  blueprint.py  render.py  synth.py  chapters.py  transcript.py
    manifest.py  r2.py  llm.py  gates.py  ids.py  youtube.py  whisper.py
  build_episode.py                # NEW — blueprint -> mp3 + chapters + vtt + manifest
  ingest_youtube.py               # NEW — url -> content/sources/youtube/<id>.json
  blueprint_from_source.py        # NEW — source -> derived episode blueprint
  curate.py                       # UPGRADED — RSS + YouTube feeds -> data/candidates.json
  backfill_transcripts.py         # NEW — faster-whisper over legacy MP3s
  migrate_to_blueprints.py        # NEW — one-shot: legacy generators -> blueprints
  prune.py                        # NEW — storage hygiene
  (legacy generate_*.py kept, frozen, marked DEPRECATED in their docstrings)

tests/                            # NEW — pytest; the repo currently has zero tests

.claude/
  skills/{episode-new,youtube-ingest,show-new,content-review,publish}/SKILL.md
  commands/{new-episode,ingest,publish-episode}.md

site/js/*.js                      # app.js split into ES modules
```

**R2 layout additions** (existing keys unchanged):

```
chapters/{slug}.json      # Podcasting 2.0 chapters
transcripts/{slug}.vtt    # WebVTT, cue-per-line, speaker-labelled
notes/{slug}.md           # study notes (reading panel)
boards/{slug}.json        # solution board (migrated out of site/solutions.json)
sources/index.json        # ingested YouTube video ids -> dedupe
```

---

## 3. Phase 0 — Foundations (do first; everything else depends on it)

### 3.1 R2 access — listing via the existing binding, **not** boto3 (revised 2026-08-11)

The original plan was a boto3 rewrite of `r2_utils.py`. That needs **R2 S3 credentials**
(Access Key ID + Secret Access Key), which are a *different* credential from the
`CLOUDFLARE_API_TOKEN` the pipeline already has, and which Cloudflare displays exactly
once at creation — the existing ones cannot be recovered from the dashboard, the API, or
a browser session. Creating a new pair is a 30-second manual step, but it is a new secret
to manage for a benefit that turns out to be obtainable for free.

**Revised plan.** The only capability actually missing is *listing* — `arrange.py`
currently guesses `feedback/{date}_ep{id}.json` keys for 7 days because the wrangler CLI
can't list. Pages Functions already hold an R2 binding (`FEEDBACK_BUCKET` in
`wrangler.toml`), and bindings expose `.list()`. So:

- Add `functions/api/feedback-list.js` — auth-gated `GET`, returns
  `{keys: [...], truncated: bool}` from `env.FEEDBACK_BUCKET.list({prefix, cursor})`,
  paging through the cursor.
- `arrange.py` calls that endpoint (auth cookie from the existing middleware) instead of
  guessing keys. Real listing, zero new credentials.
- Keep `scripts/r2_utils.py` on wrangler for read/write. It is slow (~1-2 s/op, spawns
  Node) but correct, and the daily pipeline does a handful of ops per run.

**Revisit boto3 only if** per-op latency starts to hurt (bulk backfill in Phase 4 is the
likely trigger). At that point create an R2 API token in the dashboard and store the pair
in `pass` — resolved at run time the same way `scripts/lib/llm.py` does (§3.5), never in a
`.env` file beside the code.

### 3.5 `scripts/lib/llm.py` — DONE (2026-08-11)

Already written and verified against a live call. Resolution order follows the convention
in `convfinqa-agent/src/convfinqa/llm.py` and `job-hunter`:
`LLM_API_KEY` → `DEEPSEEK_API_KEY` → `OPENAI_API_KEY` → `pass show $LLM_PASS_ENTRY`
(default `deepseek/api_key`) → `ssh $LLM_PASS_SSH_HOST pass show …`.
Endpoint/model from `LLM_ENDPOINT` / `LLM_MODEL`, defaulting to
`https://api.deepseek.com/v1` and `deepseek-v4-flash`.

Two roles — `writer` (episode prose) and `distiller` (transcript → study blueprint) —
both defaulting to the same model, overridable via `PODCAST_WRITER_MODEL` /
`PODCAST_DISTILLER_MODEL`. Callers **must** catch `LlmUnavailable` and fall back to the
template path. Verify a setup with `python3 -m scripts.lib.llm --check` (prints key
*origin*, never the value).

**Local dev needs `export LLM_PASS_SSH_HOST=agent`** — the password store lives on that
host, not on this Mac.

**Acceptance:** `python3 -c "from scripts.lib.r2 import list_prefix; print(len(list_prefix('episodes/')))"`
returns ≥157; `arrange.py` produces identical `plan.json` to a wrangler run.

### 3.1b `functions/episodes/[file].js` — Range support (P0, blocks §6.1)

**Verified broken 2026-08-11.** The function sends `Accept-Ranges: bytes` but never reads
the request's `Range` header — it always does a full `env.FEEDBACK_BUCKET.get(key)` and
returns 200 with the whole body. Live check against `/episodes/2026-07-06.mp3` with
`Range: bytes=1000000-1000100` returned `HTTP 200, content-length: 10109520`.

Consequence: **every seek re-downloads the episode from byte 0.** On the 102 MB / 60-min
episodes, tapping a chapter at minute 45 pulls the entire file. The chapter rail and
tap-to-seek transcript in §6.1–6.2 are unusable until this is fixed.

Fix (~10 lines): parse `Range`, pass `{range: {offset, length}}` to `.get()`, return
`206 Partial Content` with `Content-Range: bytes start-end/total`, and fall through to 200
when the header is absent. Handle `HEAD` by returning headers with no body.

Also missing: **no `Cache-Control` and no `ETag`** on the response, so every play re-fetches
through the Worker — no browser cache, no edge cache. Published episodes are immutable, so
add `Cache-Control: public, max-age=31536000, immutable` and echo `obj.httpEtag`.

### 3.2 Schemas + gates
`schemas/episode.schema.json` (see §4.1 for the shape) and `scripts/lib/gates.py` with
one function per gate, each returning `(ok, [messages])`:

| Gate | Checks |
|---|---|
| `schema` | Blueprint validates against JSON Schema |
| `template_coverage` | Every required section id of the template is present, in order |
| `duration` | Estimated minutes (words ÷ 145 wpm, + inter-line gaps) inside the template's `target_minutes` range |
| `tts_safety` | No characters/patterns edge-tts mangles: `===`, code blocks, bare `O(n^2)`, URLs, `&`, unexpanded acronyms, emoji, markdown |
| `voice_roles` | Every line's `voice` exists in the template's role list |
| `id_unique` | Episode id and slug not already in manifest |
| `url_convention` | `file_url` = `{BASE}/episodes/{slug}.mp3`, no date prefix (gotcha #8) |
| `manifest_integrity` | Both manifests parse; every playlist `episode_ids` entry exists; no duplicate ids; every episode has `source` |
| `banned_phrases` | Configurable filler list (e.g. "I'll give you X examples", "delve", "in today's fast-paced") |
| `claims` | Blueprint sections marked `factual: true` must carry a `sources[]` entry (hallucination guard for LLM/derived content) |

`scripts/gates.py` CLI: `python3 -m scripts.lib.gates <blueprint.json>` and `--manifest`
mode for repo-wide checks.

### 3.3 `scripts/lib/synth.py` — synthesis with exact timings (the key enabler)

Per blueprint **line**: synthesize → post-process (loudnorm + silenceremove) → `ffprobe`
duration → append. Concatenate with `ffmpeg -f concat -c copy` **only** (no `acrossfade`
between timed segments — crossfade destroys offset additivity; if a fade is wanted, use a
generated silence segment of known length instead). Cumulative offsets are then exact.

Returns:
```python
{"mp3": path,
 "total_seconds": 1683.4,
 "lines": [{"section":"clarify","voice":"candidate","text":"...","start":42.1,"end":49.8}, ...],
 "sections": [{"id":"clarify","title":"Clarify first","start":40.0,"end":180.2}, ...]}
```
From that, `chapters.py` writes Podcasting 2.0 JSON and `transcript.py` writes WebVTT
(one cue per line, `<v Interviewer>` speaker tags for multi-voice shows). **No whisper
needed for TTS episodes.** Apply Apple's chapter guidance: ≥3 chapters, titles ≤45 chars,
merge sections shorter than 45s into the previous chapter.

Add a **Kokoro (`kokoro-onnx`, CPU) fallback** behind the same `synthesize()` signature,
used automatically when edge-tts raises (ENHANCEMENTS §1) — the daily cron must not die
when Microsoft moves the endpoint.

### 3.4 Tests + CI
`tests/` with pytest covering: blueprint validation (valid + each failing gate), chapter
math (merging, boundary rounding), VTT formatting, manifest add/update idempotency, id
allocation, slug rules, YouTube VTT normalisation. Mock TTS/R2 — no network in tests.

`.github/workflows/ci.yml` on every push: `pytest -q` + `python3 -m scripts.lib.gates --manifest`.
`.github/workflows/keepalive.yml` monthly (defeats the 60-day Actions auto-disable).
`daily.yml`: add healthchecks.io pings per job, `actions/cache` for pip, drop `npm install`
once boto3 lands. Add `functions/healthz.js` (R2 `head('manifest.json')` + JSON parse →
200/503) and whitelist `/healthz` in `_middleware.js`.

**Phase 0 acceptance:** CI green on a push; `/healthz` returns 200 in production; a
deliberately broken blueprint fails the right gate with a readable message.

---

## 4. Phase 1 — The content system

### 4.1 Episode blueprint (the authored artifact)

`content/blueprints/<show>/<slug>.json`:

```jsonc
{
  "schema": 1,
  "id": 320,                       // allocated by scripts/lib/ids.py, never by hand
  "slug": "ep20-topological-sort", // == mp3 filename, chapter/vtt/board key
  "show": "coding-prep",
  "template": "think-aloud-coding",
  "title": "Topological Sort — Think Aloud",
  "description": "...",            // 2–4 sentences, shown in app + RSS
  "keywords": ["graph", "dag", "kahn"],
  "voices": { "narrator": "narrator" },   // role -> VOICE_MAP key
  "sections": [
    { "id": "cold-open", "title": "Cold open", "target_minutes": 1.5,
      "lines": [ { "voice": "narrator", "text": "..." } ] },
    { "id": "clarify", "title": "Clarify first", "target_minutes": 2,
      "lines": [ ... ] }
  ],
  "board": { "tabs": [ { "title": "Clarify", "content": "..." } ], "tutorUrl": "..." },
  "notes_md": "content/notes/ep20-topological-sort.md",
  "sources": [ { "type": "youtube", "id": "abc123", "url": "...", "used_for": ["outline"] } ],
  "publish": { "pub_date": null, "explicit": false }
}
```

Rules: `lines[].text` is **spoken text only** — no markdown, no symbols; `[pause]`,
`[long-pause]` markers are allowed and honoured by `render.py`. Sections are the chapter
boundaries. `board` (when present) is written to `boards/{slug}.json` on R2, replacing the
hand-maintained `site/solutions.json`.

### 4.2 Templates

`content/templates/<name>.json` defines a show format: required + optional section ids in
order, per-section `target_minutes` and an **authoring brief** (what belongs in the
section, what to avoid, an example paragraph) that the agent skill and the LLM prompt both
read. Ship these six, derived from the formats already in use:

| Template | Derived from | Roles | Target |
|---|---|---|---|
| `think-aloud-coding` | `drafts/coding-prep/*.txt` | narrator | 12–18 min |
| `mock-interview-2voice` | `mock_dialogues/*.py` | interviewer, candidate | 25–45 min |
| `coding-mock-drill` | `coding_mocks/*.py` | narrator, interviewer, candidate | 15–25 min |
| `concept-explainer` | `generate_sd.py` | narrator | 10–20 min |
| `estimation-drill` | `generate_estimation.py` | estimation | 8–15 min |
| `daily-english` | `generate.py::build_script()` | legacy | 25–30 min |
| `youtube-derived` | NEW (§5) | narrator | 10–20 min |

### 4.3 `scripts/build_episode.py`

```
python3 scripts/build_episode.py content/blueprints/coding-prep/ep20-topological-sort.json \
        [--dry-run] [--no-publish] [--force]
```
Steps: load → gates → allocate id/slug if missing → render → synth (§3.3) → chapters →
VTT → notes → board → validate MP3 (`ffprobe` duration > 0, size > 1 MB, duration within
±20% of estimate) → upload `episodes/`, `chapters/`, `transcripts/`, `notes/`, `boards/` →
`manifest.add_or_update()` → regenerate RSS → upload both manifest copies → write local
`scripts/manifest.json` + `site/manifest.json`.

`--dry-run` runs everything except TTS and upload and prints the section/duration plan.

**RSS additions** in `manifest.py::generate_rss()`: `podcast:transcript` (VTT),
`podcast:chapters`, `podcast:person`, `itunes:episode`, `itunes:season`, per-episode
`itunes:image`. Validate once against podcastindex.org/validator.

### 4.4 Show registry

`content/shows.json` becomes the single source for: playlist id, title, description, icon,
mono badge, sort order, default template, default voices. `publish` writes the `playlists`
block of the manifest from it, and the frontend reads it from the manifest — deleting the
duplicated `SHOW_META` + `SHOW_ORDER` constants in `app.js`. Fix the two empty playlists
while doing this (either populate or remove).

### 4.5 Migration (one-shot, `scripts/migrate_to_blueprints.py`)

Convert every existing generator into blueprints without re-synthesising audio:
`mock_dialogues/*.py` and `coding_mocks/*.py` expose `build() -> [(voice, text)]` — import
each, map tuples to sections using the `# SECTION n:` comments already present; parse
`drafts/coding-prep/*.txt` into sections on blank-line + heading heuristics; emit blueprint
JSON with the existing manifest id/slug and `"audio": "existing"` so `build_episode.py`
skips synthesis. Backfill `source` on all 138 episodes, dedupe ids, normalise `file_url`.

**Phase 1 acceptance:** a new episode can be created end to end with one blueprint file and
one command; `migrate_to_blueprints.py` produces a blueprint for every existing episode and
the manifest gates pass; `git diff` on the manifest after a no-op rebuild is empty.

### 4.6 Agent workflow — skills and commands

`.claude/skills/`, each with a SKILL.md that is *procedural*, not descriptive:

- **`episode-new`** — pick show → load its template → interview the user for the topic and
  angle (≤3 questions) → draft each section against the template's authoring brief →
  write the blueprint → run gates → `--dry-run` → show the section/duration plan → on
  approval, build and publish. Explicitly instructs: allocate ids via `ids.py`, never edit
  the manifest by hand, spoken-text-only rules, run `content-review` before publishing.
- **`youtube-ingest`** — §5. URL(s) → transcript → source JSON → proposed derived episodes.
- **`show-new`** — register a show in `content/shows.json`, pick or create a template,
  seed the first 3 blueprints, verify the frontend renders it.
- **`content-review`** — run all gates, then a human-quality pass: reads the blueprint
  aloud-style for filler, repetition against the last 5 episodes of the same show, claim
  checking for `factual: true` sections, and duration balance across sections.
- **`publish`** — pre-flight (id collision, R2 head checks, manifest parse), publish,
  post-flight (fetch the live manifest and MP3 headers, bump `?v=` + `CACHE_V` together —
  gotcha #6 — and confirm `/healthz`).

`.claude/commands/`: `/new-episode`, `/ingest <url>`, `/publish-episode <slug>` as thin
wrappers. Update `AGENTS.md` so "how to add content" points at the skills as the *only*
supported path, and mark the legacy generators DEPRECATED.

---

## 5. Phase 2 — Feeds as learning material

### 5.1 Source registry — `scripts/sources.yaml` (create it; today it's a hardcoded default)

```yaml
rss:
  - {url: "...", name: "Changelog", keywords: [...], show: daily-english}
youtube:
  # channel/playlist RSS is free and needs no API key:
  # https://www.youtube.com/feeds/videos.xml?channel_id=UC...  |  ?playlist_id=PL...
  - {channel_id: "UC...", name: "ByteByteGo", show: system-design, max_per_run: 2,
     min_minutes: 8, max_minutes: 60, keywords: [system design, scalability]}
curation:
  prefer_recent_hours: 168
  min_score: 2
```

`curate.py` upgraded: pull both source kinds, score, **dedupe against `sources/index.json`
on R2**, write `data/candidates.json` (ranked, with reasons). It no longer picks exactly
one article — it produces a candidate queue the daily pipeline and the agent both consume.

### 5.2 `scripts/ingest_youtube.py`

`yt-dlp --skip-download --write-info-json --write-subs --write-auto-subs --sub-lang en
--sub-format vtt` → if no subtitles exist, download audio and run **faster-whisper**
(`large-v3-turbo`, int8, CPU) → normalise into:

```jsonc
// content/sources/youtube/<video_id>.json
{"id":"abc123","url":"...","title":"...","channel":"...","published":"2026-..",
 "duration_seconds":1820,
 "chapters":[{"start":0,"title":"Intro"}],        // from info.json when present
 "transcript":[{"start":12.4,"end":17.9,"text":"..."}],
 "text":"full plain text",
 "license_note":"transcript stored for personal study; audio not re-hosted"}
```

Also `--keep-audio` flag for the legacy re-hosting path, and `--backfill` to run whisper
over the 14 existing YouTube episodes so they gain transcripts and chapters too.

### 5.3 `scripts/blueprint_from_source.py` — the blueprint extraction

Two stages, both available to agent *and* LLM:

1. **Distil** — source → study blueprint: outline (topic tree), key claims with
   timestamps, glossary of terms, the 8–12 questions an interviewer would ask on this
   material, common misconceptions, and a "what this means for Airwallex-style systems"
   angle. Saved to `content/notes/<slug>.md` and embedded in the source JSON.
2. **Compose** — study blueprint + `youtube-derived` template → an **original** episode
   blueprint in the show's voice. Hard rule enforced by the `claims` gate: every factual
   claim carries a `sources[]` reference back to the source timestamp; no verbatim reuse
   beyond short quoted definitions.

Output of stage 1 is valuable on its own — the notes render in the app's reading panel
(§6.4) even when no episode is produced.

**Phase 2 acceptance:** `/ingest <youtube-url>` produces a source JSON with transcript, a
notes markdown, and a proposed derived blueprint that passes all gates; the daily cron can
run `curate.py` and surface a candidate queue without human input.

---

## 6. Phase 3 — Player and UI

Split `site/app.js` into ES modules under `site/js/` (`state.js`, `data.js`, `player.js`,
`chapters.js`, `transcript.js`, `ui-home.js`, `ui-library.js`, `ui-show.js`, `sheets.js`,
`gestures.js`). `<script type="module" src="/js/main.js?v=N">` — no bundler. Keep the
single `?v=N` constant in sync with `CACHE_V` in `sw.js` (gotcha #6); add a
`scripts/bump_assets.py` so this can't be forgotten.

### 6.1 Chapters in the player (headline feature)
- Fetch `chapters/{slug}.json` on load.
- **Segmented seek bar**: one segment per chapter, gaps between, the current segment
  filled and elevated. Tapping a segment seeks to its start.
- **Current section label** under the episode title, updating live.
- **Chapter list sheet**: title, duration, progress tick; tap to jump; the active row
  highlighted and auto-scrolled into view.
- **Skip-to-next-section** button replacing nothing — added beside ±15s.

### 6.2 Synced transcript panel
- Fetch `transcripts/{slug}.vtt`, parse client-side (~40 lines, no library).
- Active cue highlighted, container auto-scrolls (suspended for 4s after a manual scroll).
- Tap any line to seek there. Speaker labels styled per voice in 2-voice shows.
- In-transcript search with match jump. Transcript text also feeds the global Search tab,
  so search finally covers what was actually said.

### 6.3 Panel model
Replace the single "Solutions" toggle with a bottom sheet holding four tabs:
**Chapters · Transcript · Board · Notes** — each hidden when the episode lacks that asset,
which finally makes the 44 board-less coding episodes read as intentional rather than broken.

### 6.4 Native feel
- Full player becomes a **draggable sheet**: swipe down to dismiss with velocity-based
  spring (`pointer` events + `transform`, no library), rubber-banding at the top.
- Bottom sheets for queue, speed, sleep timer, chapter list — same primitive, one
  `sheets.js`.
- **Media Session API**: title, artwork, show name, chapter metadata on the lock screen;
  `seekbackward`/`seekforward`/`previoustrack`/`nexttrack`/`seekto` handlers.
- Sleep timer (5/10/15/30/end-of-episode) and per-show playback-rate memory.
- iOS-style **large title that collapses** into the top bar on scroll; `env(safe-area-inset-*)`
  everywhere; `overscroll-behavior: contain`; no rubber-band on the body.
- **Dark mode**: `prefers-color-scheme` + a manual override in Account, tokens in `style.css`.
- Haptics via `navigator.vibrate` on primary actions (no-op on iOS, harmless).
- Skeleton placeholders instead of empty flashes; `content-visibility` on long lists.
- View Transitions API for tab and show-detail navigation where supported, CSS fallback.
- **Offline downloads**: a download button per episode caches MP3 + VTT + chapters through
  the SW into a dedicated cache; a "Downloaded" section in Library with size and a clear
  action. Bump the SW to a versioned multi-cache strategy (app shell / data / media).

### 6.5 Home as a learning surface
Home gains a **"Continue learning"** block above Shows: resume card, then today's ingested
candidates (from `sources/index.json`) as reading cards with their notes, so new material
is visible before it becomes an episode.

**Phase 3 acceptance:** on an iPhone, the app opens full-screen from the home screen,
plays with lock-screen chapter metadata, the seek bar shows sections, the transcript
follows playback and is tappable, the player dismisses with a swipe, and a downloaded
episode plays in airplane mode.

---

## 7. Phase 4 — Backfill and hygiene

- `scripts/backfill_transcripts.py`: faster-whisper over all legacy MP3s (batch, resumable,
  writes `transcripts/` + auto-chapters where the blueprint has no sections). ~157 episodes;
  run locally on the Mac (whisper.cpp/Metal is much faster than the CI runner).
- `scripts/prune.py`: delete daily `episodes/{date}.mp3` older than 90 days (series episodes
  are evergreen and kept); **also remove the pruned entries from the manifest and RSS** so
  no dead links remain.
- Fix the broken `data/`/`feedback/` symlinks (replace with real gitignored dirs created by
  the scripts).
- Delete `site/manifest.json` duplication in favour of a build step that copies it, or
  document it as generated-only.

---

## 8. Execution order and estimates

| Phase | Content | Rough size |
|---|---|---|
| 0 | boto3 R2, schemas, gates, synth-with-timings, Kokoro fallback, tests, CI, healthz | 1–1.5 days |
| 1 | templates, blueprints, build_episode, shows.json, migration, skills + commands | 2 days |
| 2 | sources.yaml, curate upgrade, ingest_youtube, blueprint_from_source, llm.py | 1.5 days |
| 3 | module split, chapters, transcript, sheets, gestures, media session, dark mode, downloads | 2–3 days |
| 4 | whisper backfill, prune, cleanup | 0.5 day |

Phases 0→1 are strictly sequential. Phase 3 can start after Phase 0 lands §3.3 (it only
needs the chapter/VTT format, not the whole content system) — the frontend can be built
against a hand-written fixture.

## 9. Non-goals

No framework rewrite. No native app store build. No paid infrastructure. No multi-user
support or real auth change (hardcoded `ming`/`ping` stays, per AGENTS.md #4). No D1/KV
migration. No re-synthesis of existing episode audio.

## 10. Risks

| Risk | Mitigation |
|---|---|
| edge-tts breaks mid-migration | Kokoro fallback lands in Phase 0, before any bulk synthesis |
| ffmpeg concat drift makes chapter offsets wrong | `-c copy` only, per-segment ffprobe, a test asserting Σ segments == total ±0.5s |
| LLM invents facts in derived episodes | `claims` gate requires a source reference on factual sections; `content-review` skill checks them |
| Migration corrupts the manifest | Migration is read-only w.r.t. audio; manifest written via `manifest.py` with gates + a git-committed backup before the first run |
| R2 free tier (10 GB) | `prune.py` in Phase 4; transcripts are a few hundred KB each |
