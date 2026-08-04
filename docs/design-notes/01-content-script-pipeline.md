# Design Session — Round 1: Content & Script Pipeline

Research date: 2026-08-04. Inputs: `ENHANCEMENTS.md` §2, web research on LLM podcast pipelines.
Companion docs: `docs/design-notes/02-tts-audio-stack.md`, `docs/design-notes/03-infrastructure-data-layer.md`.

---

## Problem statement

`scripts/generate.py::build_script()` assembles episodes from a **fixed template**: identical
phrasing every day ("I'll give you X examples..."), the curate.py article summary pasted
verbatim, hardcoded review/deep-dive sections, and a bare 500-char description. The quality
ceiling of the entire podcast is a string template in one Python function. Content bank
(`patterns`, `tips`, `prompts`) is rich (114 entries) but under-utilized.

What we want for a future design session:

1. Vary script style/flow per episode while **keeping the exact section structure** (TTS/ffmpeg/publish pipeline must not change).
2. Use the content bank more intelligently (pick related patterns, chain prompts, adapt difficulty).
3. Richer episode metadata: description, keywords, title.
4. Zero or near-zero cost; must work offline (no API key) as fallback.

## Options

### Option A — Status quo + template micro-improvements

Randomize template wordings in `build_script()` (phrase banks), expand description to
first-800-chars + keyword list from content bank.

**Pros:** zero cost, zero new deps, zero failure modes, ships in an hour.
**Cons:** still template-flavored; no real adaptation to the article; ceiling remains low; not
"smart" — descriptions stay generic.

### Option B — Cloud LLM script generation (DeepSeek/Gemini/Groq)

New `scripts/llm.py`: OpenAI-compatible client → prompt = content bank items + `plan.json` +
`today.json` → return a script with the same section markers. Existing template kept as
`--template` fallback when `DEEPSEEK_API_KEY` absent. Optionally also generate description,
keywords, chapter titles.

**Pros:**
- Real linguistic variety and article adaptation (uses today's article properly).
- Cheapest verified pricing (July 2026): DeepSeek V4 Flash $0.14/$0.28 per 1M tokens
  (~$0.001–0.01/episode ≈ $0.30/mo for daily); Groq Llama 3.1 8B $0.05/$0.08; Gemini 3.1
  Flash-Lite $0.125/$0.75. All OpenAI-compatible clients.
- Structured output possible (JSON script with markers) → validation before TTS.
- Also solves metadata generation (description/keywords) in the same call.
**Cons:**
- Network dependency + API key → new failure mode (mitigate: template fallback, retries).
- Hallucination risk in "facts" sections → needs guardrails or a fact-check pass.
- Latency adds a few seconds–minutes to the pipeline (fine for daily cron, fine for manual).
- Key management (GH secret) — trivial but new.

### Option C — Local LLM (Ollama, e.g. Qwen3-8B / Qwen3-4B)

Run a local model for script generation; no API key, no network.

**Pros:** fully offline, $0 forever, no privacy leak of the user's content.
**Cons:**
- Needs a machine with RAM/CPU (Qwen3-8B ~5-6 GB RAM; 4B ~3 GB) — GitHub Actions runners
  are 7 GB RAM x64, so feasible but slow (minutes for a 3000-word script, risky in cron).
- Quality noticeably below DeepSeek-class models for this length of coherent output.
- Adds a ~4 GB model download in CI or requires a local always-on machine for manual runs.

### Option D — Hybrid: local draft + cloud polish

Local cheap model (or template) produces a draft; cloud LLM (DeepSeek) rewrites/polishes
only when key present; final fallback = template.

**Pros:** every degradation level works: full cloud quality → local draft → template.
**Cons:** most moving parts to build and test; three code paths to maintain.

### Option E — Agentic pipeline (multi-step: research → writer → reviewer)

Inspired by 2026 local-first "AI podcast studio" approaches (Microsoft Agent Framework +
Ollama, LFM Podcast Studio). A planner agent decides episode structure from content bank,
a writer agent drafts, a reviewer agent checks structure markers + claims (claim ledger),
retry loop on failure.

**Pros:** highest quality ceiling; adaptive per day; the claim-ledger pattern (from LFM)
covers the hallucination risk of Option B.
**Cons:** heaviest build (LLM infra, tool calling, loops); overkill for a 3000-word daily
script; latency and cost multiply; most code to maintain in a $0 side project.

### Sub-option — structured JSON output everywhere

Regardless of engine, have the LLM return JSON `{sections: [{marker, text}], description,
keywords}` and validate with a schema before TTS. (Pattern seen in multiple 2026 podcast
pipelines — e.g. Deer Flow, LFM.)

**Pros:** validation-before-TTS catches malformed scripts; chapters/description come free.
**Cons:** one extra validation layer to write (~50 lines).

---

## Recommendation for the design session

**Start with Option B + sub-option** (DeepSeek V4 Flash, structured JSON, template fallback,
retry ×2). It's ~1 day of work, ~$0.30/mo, no infra change. Keep Option E (agentic) as a
stretch goal only if quality after B is unsatisfying. If B's network dependency is
unacceptable, fall back to Option D (local Qwen3-4B draft + cloud polish when key present).

## Open questions for the session

1. Is an API key + GH secret acceptable, or must the pipeline stay fully local?
2. Should the LLM ever invent "facts" about the article, or only paraphrase
   `today.json` content? (Determines whether we need a claim-ledger/guardrail pass.)
3. Where does script generation run — GitHub Actions (cron) or local manual runs?
4. Do we want per-episode chapter titles generated too (feeds Round-2 chapters/RSS work)?

## Files touched (when approved)

- `scripts/llm.py` (new)
- `scripts/generate.py` (call llm.py, keep `--template`)
- `scripts/requirements.txt` (openai or anthropic client)
- `.github/workflows/daily.yml` (env: `DEEPSEEK_API_KEY`)
