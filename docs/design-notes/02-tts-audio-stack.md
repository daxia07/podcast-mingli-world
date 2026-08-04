# Design Session — Round 2: TTS & Audio Production

Research date: 2026-08-04. Inputs: `ENHANCEMENTS.md` §1, web research on Kokoro-82M
(`kokoro` / `kokoro-onnx` PyPI, v2.3.1) and podcast loudness/mastering standards.
Companion docs: `docs/design-notes/01-content-script-pipeline.md`,
`docs/design-notes/03-infrastructure-data-layer.md`.

---

## Problem statement

TTS is the **single biggest risk** in the project: `scripts/tts.py` + `generate.py` use
edge-tts (unofficial scraping of Microsoft's free endpoint — migrated hosts, DRM tokens,
browser-emulation churn). When MS breaks it, the daily episode silently fails with **no
fallback**. Secondary issues:

- Single voice family (en-US-ChristopherNeural at -15% rate) — flat delivery, no
  host-variety option; multi-voice series hardcode voices in each script.
- No mastering: raw edge-tts output, no loudness normalization (podcast apps vary volume
  wildly between episodes), no silence trimming.
- All series generators duplicate TTS glue (some use `tts.py`, some their own logic).

## Options

### Engine choice

#### Option A — Harden edge-tts (keep primary)

Pin `edge-tts>=6.1.0` in requirements.txt (current maintained: 7.2.x+), bump in CI
monthly, add retries + graceful error surfacing.

**Pros:** $0, zero new deps, best-in-class naturalness among free options, works today.
**Cons:** still a moving target (DRM/cookies live in the package); vendor may kill the
endpoint at any time; out of our control — this is exactly the single point of failure.

#### Option B — Kokoro-82M as automatic fallback (recommended)

Add `kokoro-onnx` (PyPI, Apache 2.0, 82M params, CPU-only, ~2-3 GB RAM, RTF ~0.03 on
GPU, ~54 voices incl. strong English: am_michael, am_fenrir, bf_emma, ...). In `tts.py`
wrap `synthesize()`: try edge-tts, on any exception fall back to Kokoro, log which engine
ran. Same signature → all scripts unchanged.

**Pros:** fully local, $0 forever, no vendor risk; naturalness Elo 1424 (highest
open-weight); runs in CI runner and on the Mac; clean swap via existing interface; also
solves the "voice rotation" idea (multiple strong voices). v2.3.1 supports voice
blending, chapter splitting, EPUB/PDF input, WAV/MP3 out.
**Cons:** on CPU a 28-min episode takes a while (RTF ~0.03 needs GPU; on Mac M-series
CPU it's slower but OK for a once-a-day batch); adds ~1 GB model download; quality
slightly below edge-tts top voices for some users.

#### Option C — Piper as second fallback (or lightweight-only path)

MIT weights, <100 MB, CPU instant, very fast.

**Pros:** tiny, fastest CPU path, robust.
**Cons:** noticeably more robotic — fine as a 3rd tier, bad as primary; fewer English
voice options.

#### Option D — Cloud API fallback (Azure F0)

Azure Speech F0 free tier: 500K chars/month (≈10 daily episodes), $16/1M beyond.
E.g. `en-US-ChristopherNeural` exists there too.

**Pros:** same voice as current primary (consistency), zero vendor-scrape risk, free tier
is genuinely free.
**Cons:** needs an Azure account + key (another secret); overage costs; F0 quota could
run out mid-month for daily episodes (45K chars × 30 ≈ 1.3M chars).

#### Option E — Paid quality (optional, not needed)

- OpenAI `gpt-4o-mini-tts` / `tts-1`: $15/1M chars ≈ $0.015/min → ~$0.68/mo for daily.
- Google Neural2: $16/1M (1M free chars/mo).
- Chatterbox (MIT, 0.5B, zero-shot cloning, 4-6 GB VRAM): self-hosted ElevenLabs — only
  interesting for a consistent cloned host voice; overkill for narration.
- ElevenLabs: best quality, $60-300/1M — not worth it here.

**Pros:** best quality / consistent cloned host voice.
**Cons:** costs money, needs GPU for Chatterbox, adds secrets; contradicts $0 ethos.

### Voice strategy

#### Option F — Single host voice (current)

**Pros:** brand consistency, simplest.
**Cons:** long episodes get monotonous; no way to do two-host dynamics for daily eps.

#### Option G — Multi-voice rotation (Kokoro enables this cheaply)

Rotate between 2-3 voices per day or per section (e.g., pattern host + tip host), and
use distinct voices in mock-interview dialogues (already done in series scripts with
Ava/Brian) — standardize via `tts.py` `VOICE_MAP`.

**Pros:** listener engagement, matches series pattern, $0 with Kokoro.
**Cons:** consistency tradeoff (host identity), more config.

### Audio mastering (post-TTS, ffmpeg)

#### Option H — loudnorm single-pass (current: none)

Run `ffmpeg loudnorm` (EBU R128) on the concatenated episode.

**Pros:** free, one ffmpeg call, fixes episode-to-episode volume variance.
**Cons:** single-pass loudnorm compresses dynamics slightly; not "loudness-matched" to a
specific LUFS target by itself.

#### Option I — Two-pass loudnorm to target (recommended)

Podcast standard is ~-16 LUFS (Apple Podcasts target is -16; Spotify ~-14). Two-pass
loudnorm: measure → apply with `I=-16:TP=-1.5:LRA=11`, then optional EQ/compression/
limiter chain. `ffmpeg-normalize` wrapper if desired. Also add silence trimming
(`silenceremove`) and a final MP3 encode (mono 96-128k for speech, or stereo 128k).

**Pros:** consistent volume across all ~157 episodes; industry-standard loudness; $0.
**Cons:** a couple of minutes extra processing per episode; series generators also need
the same post-step (centralize in `tts.py::concatenate_mp3()`/`master_episode()`).

---

## Recommendation for the design session

1. **Primary:** keep edge-tts, pinned to 7.2.x, with retries.
2. **Fallback:** Kokoro-82M via `kokoro-onnx` inside `tts.py` (Option B) — this removes
   the single point of failure for ~$0 and is the biggest derisking move in the repo.
3. **Mastering:** add two-pass loudnorm targeting -16 LUFS + silence trim as a single
   `master_episode()` in `tts.py`, used by the daily pipeline AND series generators
   (removes duplicated ffmpeg glue across generate_*.py).
4. Defer voice rotation (G) and cloud/paid engines (D/E) — nice-to-haves, not needed to
   fix the risk.

## Open questions for the session

1. CI runner CPU budget: is Kokoro-onnx on the GH Actions x64 runner acceptable for a
   28-min episode, or should fallback only run on manual/local runs?
2. Target loudness: -16 LUFS (Apple standard) vs -14 (Spotify loudness) — one number
   for all episodes?
3. Do we standardize on mono or stereo for speech episodes?
4. Voice rotation — yes/no, and if yes: host + guest pattern for daily episodes?

## Files touched (when approved)

- `scripts/tts.py` (fallback wrapper + `master_episode()`)
- `scripts/requirements.txt` (kokoro-onnx, maybe ffmpeg-normalize)
- `scripts/generate.py` + series `generate_*.py` (call master_episode; remove local ffmpeg glue)
- `.github/workflows/daily.yml` (no change needed if kokoro-onnx is in requirements)
