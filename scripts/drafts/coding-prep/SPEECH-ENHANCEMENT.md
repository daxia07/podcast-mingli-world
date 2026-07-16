# Speech enhancement — think + muscle memory

**Goal:** Audio that makes you *solve under your breath*, not just nod along.  
**Target loop:** cold attempt → model path → mistake recovery → say-back → transfer → app options.

## What’s already good (keep)

| In ep00 / ep01 today | Why keep |
|----------------------|----------|
| 8-step ritual fixed order | Interview script muscle |
| Naive → optimize spoken | Airwallex process |
| Concrete hand-walk examples | Ears can simulate board |
| Mistake list mid-episode | Error inoculation |
| End “say it back” + app CTA | Close the loop |

## What’s missing for real muscle memory

Current scripts are excellent **demonstrations**. They under-train **retrieval**.

| Gap | Effect | Fix |
|-----|--------|-----|
| Solution starts too fast | Passive listening | **Cold open** — problem only, then timed attempt |
| No forced silence | Brain never commits | **Count-out pauses** (TTS-safe: “One… five…”) |
| One pass only | Weak spaced retrieval | **90-second speed recap** at end |
| No wrong path | You don’t practice recovery | **Deliberate dead-end** then pivot speech |
| No transfer | Pattern stuck to one LC# | **20-second sibling problem** |
| Abstract “think” | Not motor | **Say-then-type cue**: “mouth says X before fingers” |
| No daily micro-rep | Long ep once | **Drill card** — 5 lines you re-speak every morning |

## Canonical episode skeleton (use for all ep01+)

Word budget ~1.8–2.4k (~12–16 min at −5% rate).

### 1. Hook + stakes (20–30s)
- Name problem + why Airwallex cares (process, not optimal only).
- Explicit: “No AI. You will speak before I solve.”

### 2. Cold open (60–90s) — NEW
- State full problem once.
- Clarifiers as *questions you must ask*, not answers yet.
- **Attempt block:**  
  “Pause with me. I’ll count to eight. In that time, say out loud your naive idea and its Big-O. One. Two. … Eight.  
  If you said nested loops O of n squared — good. If you froze, that’s the muscle we’re building.”

### 3. Ritual lock (30s)
- Restate the 8 steps in under 20 words each. Same wording every episode (ritual = anchor).

### 4. Naive path full (60–90s)
- Speak nested / brute with a tiny example.
- Complexity. “Ship this if time is dying.”

### 5. Dead-end (45–60s) — NEW
- One plausible wrong idea (e.g. sort without index tracking; insert-before-lookup self-match).
- Walk why it fails on a 3-element case.
- Recovery line: “I’d say: that breaks indices — switching to map.”

### 6. Optimal path (3–4 min)
- Name structure + invariant in one sentence.
- Hand-walk primary example step by step (no code syntax soup).
- Second micro-example for the edge the dead-end hit.
- Pseudocode in full words.

### 7. Edges + complexity checklist (60s)
- Empty / one / all equal / negatives / capacity — as a *spoken checklist*, not a lecture.

### 8. Pattern cue card (30s) — NEW
- “When I hear *pair / complement / seen before* → hash map.  
  When I hear *contiguous max under constraint* → window.  
  Say the cue with me…”

### 9. Transfer (45–60s) — NEW
- Sibling problem in one sentence (e.g. after Two Sum → Contains Duplicate).
- “Twenty seconds: approach only, not code. One… five.  
  Model answer: set of seen values, true if insert collides.”

### 10. Speed recap (60–90s) — NEW
- Entire solution in compressed interview voice (what you’d say in the first 3 minutes of a real screen).
- This is the clip you re-play daily at 1.25×.

### 11. Say-back challenge (45s)
- Numbered list, no notes. Same structure every ep.

### 12. App + code CTA (20s)
- Open deep drill options cold. Then code once without AI.

## Phrase bank (drop into every ep)

**Commit before reveal**
- “Don’t wait for me. Commit to a sentence.”
- “Wrong out loud beats silent perfect.”

**Process under pressure**
- “If stuck: two options I’m between, and which constraint decides.”
- “I’m stating naive first even though I know the optimal.”

**Motor memory**
- “Mouth first: clarify, naive, structure, example, then code.”
- “If I can’t walk the example, I don’t type.”

**No AI**
- “Live round: no copilot. This audio is the copilot you’re replacing.”

## TTS / audio production rules

1. Pure spoken prose only — no `[INTRO]`, no stage banners.  
2. Pauses = spoken counts or “take a breath” — not silent stage directions.  
3. Numbers: “O of n squared”, “ten to the five”, not `O(n²)`.  
4. Avoid “as you can see on the board” — describe state in words.  
5. One problem per deep ep; family eps (ep02) get 3× shorter cold opens.

## Enhancement plan for existing scripts

| Script | Priority changes |
|--------|------------------|
| **ep00 ritual** | Add cold open: “I’ll name a fake problem — you run the 8 steps in 30s.” Add morning drill card. |
| **ep01 Two Sum** | Insert cold open + dead-end (insert-before-lookup) earlier; add transfer (Contains Duplicate); add 90s speed recap; tighten middle. |
| **ep03 excerpt** | Expand to full skeleton or retire as fragment. |
| **ep02–ep07** | Write from skeleton; each ends with transfer to next day’s pattern. |

## Success criteria (you as listener)

After one enhanced ep + app drill you can:

1. Run the 8-step ritual without prompting  
2. State naive + optimal + one edge in under 90 seconds (speed recap)  
3. Recover from one named mistake without freezing  
4. Transfer the pattern to the sibling problem in one sentence  
5. Score cold options on the deep drill without rewinding  

## Decision

- **A (recommended):** Rewrite ep00 + ep01 to skeleton now; generate TTS with `--force-tts`; keep YT playlist as input model, not replacement.  
- **B:** Keep current audio; use SPEECH-ENHANCEMENT only as template for ep02+.  
- **C:** Add short “drill card” micro-eps (2–3 min) per problem for daily re-speak, plus long think-alouds.

Default recommendation: **A + optional C later** (micro drill cards after full ep series exists).
