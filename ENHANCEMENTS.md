# ENHANCEMENTS.md — Research: what to improve, what's on the web, how

Research date: 2026-08-04. Goal: keep the $0/month ethos, list concrete upgrades with
real packages, prices, and exact integration points in this repo.

---

## 1. TTS — biggest single risk in the whole project

**Current:** `scripts/tts.py` + `scripts/generate.py` use edge-tts (unofficial scraping of
Microsoft Edge's free endpoint). It works in 2026 but is a moving target: Microsoft
migrated endpoints (`speech.platform.bing.com` → `api.msedgeservices.com`), added DRM
tokens (`Sec-MS-GEC`), and changes browser emulation versions periodically. When MS
breaks it, **the daily episode silently doesn't publish** and there is no fallback.

**Actions:**

1. **Pin + auto-update edge-tts**: requirements.txt pins `edge-tts>=6.1.0`; the current
   maintained version is 7.2.x+. Update it and re-verify monthly (the DRM/cookie work
   lives in the package). This alone derisks most breakage.
2. **Add a fallback engine** so a broken edge-tts can't kill the daily run:
   - **Kokoro-82M** (Apache 2.0, 82M params, runs on CPU, ~2-3 GB RAM, RTF ~0.03 on GPU,
     54 voices incl. high-quality English) — the strongest open-weight TTS of 2026,
     naturalness Elo 1424 (highest open-weight), fully offline, $0 forever.
     `pip install kokoro` / `pip install kokoro-onnx`. Swap in via the existing
     `tts.py` interface (keep the same `synthesize()` signature).
   - **Piper** (MIT weights, CPU, <100 MB) — more robotic but instant; good third fallback.
   - **Azure Speech F0** (500K chars/month free, never expires) — a free API fallback that
     covers ~10 daily episodes/month; `$16/1M` chars beyond that.
3. **If you ever want paid quality** (optional, not needed):
   - OpenAI `gpt-4o-mini-tts` / `tts-1`: $15/1M chars ≈ **$0.015/min**. A 28-min daily
     episode (~45K chars) ≈ **$0.68/mo**. Negligible.
   - Google Neural2: $16/1M with 1M free chars/month. Azure Neural: $16/1M + 500K free.
   - ElevenLabs: best quality but ~$60-300/1M — not worth it for a personal podcast.
   - **Chatterbox** (MIT, 0.5B, zero-shot cloning) — the "self-hosted ElevenLabs"; needs
     ~4-6 GB VRAM. Overkill for narration, great if you want a consistent cloned host voice.

**Recommendation:** keep edge-tts as primary, add Kokoro (`kokoro-onnx`, CPU) as the
automatic fallback in `tts.py` when edge-tts raises; wire a voice-rotation option
(Kokoro has multiple strong English voices: am_michael, am_fenrir, bf_emma, ...).

---

## 2. LLM-generated scripts instead of fixed templates (≈ $0.01/episode)

**Current:** `generate.py::build_script()` concatenates a fixed template. Every episode
has identical phrasing ("I'll give you X examples..."), the article summary is pasted
verbatim, and there's zero adaptation. The "review" section and deep-dive scenarios are
hardcoded strings.

**Cheapest LLM APIs (July 2026, verified):**

| Provider / model | Input $/1M | Output $/1M | Notes |
|---|---|---|---|
| DeepSeek V4 Flash | $0.14 ($0.0028 cached) | $0.28 | 1M ctx, OpenAI-compatible, thinking mode |
| Gemini 3.1 Flash-Lite | $0.125 | $0.75 | 1M ctx |
| Groq Llama 3.1 8B | $0.05 | $0.08 | 128K ctx, very fast |
| GPT-5.4 nano | $0.20 | $1.25 | OpenAI budget tier |

A ~3,000-word script ≈ 4K output tokens → **~$0.001-0.01 per episode** at DeepSeek/Groq
rates. That's ~$0.30/mo for daily episodes.

**How to use it here:**
- New `scripts/llm.py` (DeepSeek API, `openai`-compatible client, `DEEPSEEK_API_KEY` env):
  prompt = content_bank pattern/tip/prompt + plan.json + today.json → varied script that
  keeps the exact section structure (the TTS/ffmpeg pipeline doesn't change).
- Pass the generated script through existing `tts.py` — zero downstream changes.
- Bonus: LLM can write the **rich per-episode description** (currently first-500-chars of
  script), suggest 3 search keywords, and expand the article discussion when curate.py
  falls back to "No article available today" (generate a mini-essay from the pattern
  theme instead of skipping the section).
- Keep the template as `--template` fallback when the API key is absent (offline mode).

---

## 3. Transcripts + chapters in RSS (Podcasting 2.0) — highest listener-value win

**Current:** no transcripts, no chapters. RSS is bare iTunes-namespace. The daily script
**already contains section markers** (`── Pattern 1 of 6: ... ──`), so chapter metadata is
nearly free.

**On the web (2026):**
- **`podcast:transcript`** tag (PodcastIndex namespace): Apple Podcasts uses your VTT/SRT
  instead of auto-generating its own (better accuracy, speaker names, no hallucinations);
  Pocket Casts, Castro, AntennaPod, Podcast Addict, PlayerFM all display RSS-linked
  transcripts. Format: VTT (`text/vtt`) is the safest single choice.
- **`podcast:chapters`**: JSON chapters file per episode → chapter markers in Apple
  Podcasts (iOS 17+), most other apps. Apple best practices: ≥3 chapters, ≤6/hr,
  titles ≤45 chars, ≥2 min each — the daily episode's section structure fits naturally.
- **Transcription engine (free, local):** faster-whisper (Python, CTranslate2, INT8,
  ~4× faster than reference, MIT, built-in VAD). On the GitHub Actions ubuntu runner
  (CPU, int8, large-v3-turbo) a 28-min episode transcribes in a few minutes. On your Mac:
  whisper.cpp (Metal). WhisperX adds word-level timestamps + speaker diarization if you
  want per-speaker labels in mock-interview episodes.
- Cost: $0, fully local. Storage: VTT is a few hundred KB per episode on R2.

**Implementation sketch:** `scripts/transcribe.py` — run after generate.py, upload
`transcripts/{date}.vtt` (+ `transcripts/{date}.json` chapters) to R2, and
`publish.py::generate_rss()` adds `<podcast:transcript url=... type="text/vtt" language="en">`
and `<podcast:chapters url=... type="application/json+chapters">` to each item.
Also add `podcast:person` (host name), `itunes:episode`, `itunes:season`, per-episode
`itunes:image` — all trivial XML additions that improve Apple/Spotify surfaces.
Validate the feed with the Cast Feed Validator (podcastindex.org/validator) after.

---

## 4. Monitoring & alerting — the daily cron is currently a silent failure

**Current:** nothing pings when arrange/generate/publish fails (expired token, edge-tts
breakage, R2 incident). The daily workflow logs to GitHub but nobody looks unless an
episode is missing.

**Free options (2026):**
- **healthchecks.io** — free 20 checks, cron heartbeat (dead-man's switch). Add
  `curl -fsS https://hc-ping.com/<uuid>` after each `daily.yml` job step; alert on
  missing ping. Simplest, recommended.
- **CronAlert** — free 25 monitors, 3-min intervals, checks URLs from outside
  Cloudflare (catches DNS/edge issues, binding failures).
- **Cloudflare-native `/healthz`**: add a `functions/healthz.js` that does
  `env.FEEDBACK_BUCKET.head('manifest.json')` + validates JSON, returns 200/503. Point
  any uptime monitor at it. ~15 lines of code. (This was already flagged in README's
  technical-debt table — do it.)
- **Cloudflare Web Analytics** — free, cookieless, one `<script>` tag in `index.html`:
  gives visitor/play counts without breaking the "no analytics" gap. Optional since this
  is a single-user site.
- **Velprove** — free plan, multi-step R2 write-then-read probes if you ever want
  deep platform-level checks (probably overkill here).

---

## 5. R2 client: use boto3, not the wrangler CLI

**Current:** `scripts/r2_utils.py` shells out to `npx wrangler r2 object ... --remote` per
operation (~1-2 s each, spawns Node each time). `requirements.txt` already lists boto3 —
it's just never used. There is **no listing** capability, which is why feedback is scanned
by guessing `feedback/{date}_ep{id}.json` keys for 7 days (arrange.py).

**Fix:** rewrite `r2_utils.py` on boto3 with the S3-compatible endpoint
(`https://<account_id>.r2.cloudflarestorage.com`) — the exact pattern `api/r2.js` already
uses. Same function signatures (`upload`, `upload_json`, `get_json`, `download`), so all
scripts keep working unchanged. Gains:
- **ListObjectsV2** → arrange.py can list ALL feedback files properly; any other
  "iterate known keys" hack becomes robust.
- head_object (existence checks), multipart uploads (bigger MP3s), faster ops (no npx).
- Removes the Node dependency from the pipeline (`npm install` step in daily.yml).

---

## 6. Pipeline robustness & CI (cheap insurance)

- **CI job** in `.github/workflows/` (runs on every push): `python3 -m json.tool` on
  `scripts/manifest.json` + `site/manifest.json`; duplicate-ID check across episodes;
  consistency check that every `file_url` matches naming convention (`episodes/{theme or
  date}.mp3`, no date-prefix bug — gotcha #8); verify playlists reference existing
  episode IDs. ~30 lines, catches the most common manual-series mistakes.
- **episode ID collision guard**: `publish.py`/batch scripts should assert
  `next_id`/hardcoded IDs don't exist in manifest before uploading.
- **Storage pruning**: R2 free tier is 10 GB. Add a `scripts/prune.py` (or fold into
  publish.py) that deletes daily `episodes/{date}.mp3` older than 90 days from R2
  (keep series episodes — they're evergreen). Already noted as an idea in AGENTS.md.
- **Cache pip deps** in `daily.yml` (`actions/cache` on `~/.cache/pip`) — trivial speedup.
- **Run generation locally with a smoke check**: ffprobe duration > 0 and file size >
  1 MB before uploading (publish.py currently doesn't validate the MP3 at all).

---

## 7. Frontend (site/) — small, high-value additions

- **Transcript panel in the player**: fetch `transcripts/{theme or date}.vtt`, render
  clickable captions synced to playback (`audio.currentTime` seek on tap). The player
  already has the queue/solutions panel pattern to copy. Also great for the
  "reading practice" goal in README.
- **Chapter markers on the seek bar** (from the same JSON chapters file).
- **Offline transcripts** via the existing service worker (sw.js) — cache VTT files.
- Otherwise the vanilla-JS SPA is fine at this scale; no framework migration warranted.
- Keep bumping `?v=` + `CACHE_V` together (gotcha #6) whenever assets change.

---

## 8. YouTube pipeline — already good

`download_youtube.py` + `publish_coding_youtube.py` already use **yt-dlp** (the correct,
actively maintained tool; the older youtube_dl is deprecated). Minor ideas: pull YouTube
chapter data (`--write-info-json`) to reuse as podcast chapters; add description/links to
RSS items; prune old downloads from `data/youtube/`.

---

## 9. Cost ledger (all upgrades are ≈ $0)

| Upgrade | Cost |
|---|---|
| Pin edge-tts 7.2+ | $0 |
| Kokoro fallback (CPU) | $0 (open weights) |
| DeepSeek V4 Flash scripts | ~$0.30/mo (daily eps) |
| faster-whisper transcripts | $0 (local) |
| healthchecks.io + /healthz | $0 |
| boto3 R2 client | $0 |
| CI validation job | $0 (GH Actions free tier) |
| Cloudflare Web Analytics | $0 |
| Azure F0 TTS emergency fallback | $0 (500K chars/mo) |

---

## Priority order

1. **P0 (do first, 1-2 hrs)**: boto3 rewrite of `r2_utils.py`; CI validation job;
   healthchecks.io pings in `daily.yml`; bump edge-tts to 7.2.x.
2. **P1 (week)**: `scripts/llm.py` script generation (DeepSeek ~$0.01/ep) with template
   fallback; `scripts/transcribe.py` (faster-whisper) + `podcast:transcript` +
   `podcast:chapters` + richer iTunes tags in `publish.py`; `/healthz` function.
3. **P2 (whenever)**: Kokoro fallback in `tts.py`; transcript panel + chapter seek bar in
   the player; `scripts/prune.py` storage pruning; RSS feed validation run.
