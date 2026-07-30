# Coding Prep Podcast — Master Index

**Canonical scripts (edit here):**  
`~/projects/podcast-mingli-world/scripts/drafts/coding-prep/`

**Generated audio + plain text copies:**  
`~/projects/podcast-mingli-world/data/coding-prep-{key}.mp3|.txt`

**Listening mirror (workspace):**  
`~/workspace/podcast/data/coding-prep-*.txt` (and mp3 when synced)

**Public URLs:**  
`https://podcast.mingli.world/episodes/coding-prep-{key}.mp3`  
Site: https://podcast.mingli.world  

**Tutor companion:**  
`~/workspace/generic-tutor-web/content/coding-prep/` · https://learn.mingli.world  

**Vault plan + checklist:**  
`~/vault` → `knowledge/airwallex/05-coding-prep/WEEK-PLAN-NEXT-WED.md`  
`knowledge/airwallex/05-coding-prep/PODCAST-INDEX.md` (this table, vault copy)

**Generate / publish:**
```bash
cd ~/projects/podcast-mingli-world/scripts
python3 generate_coding_prep.py --all --force-tts --publish
```

---

## Listen order for interview week (muscle memory)

| Priority | Ep | Loop for |
|----------|-----|----------|
| P0 daily | **19** | Clock 2/30/25 + dual AI |
| P0 daily | **22** | Interviewer Tianxiao fit (calm, infra frame, AI pilot) |
| P0 daily | **20** | Claude Code deep dive prompts |
| P0 | **00** | Eight-step ritual |
| P0 | **21** | AI scenario think-aloud (rate limiter) |
| P0 | **18** | Design-in-code primitives |
| P1 | **07**, **14** | Full mock scripts |
| P1 | Weak patterns | ep01–17 as needed |

**Rule:** Loop the same monologue until the speed recap is automatic. Then code without AI. Then short Claude Code deep dive on *your* file.

---

## Full catalog

| ID | Key | Title | Tutor sheet | Script file |
|----|-----|-------|-------------|-------------|
| 300 | ep00-ritual | Ritual | Interview Process 2026 | `ep00-airwallex-coding-ritual.txt` |
| 301 | ep01-two-sum | Two Sum | two-sum-deep-drill | `ep01-two-sum-think-aloud.txt` |
| 302 | ep02-hashmap-family | HashMap family | hashmap-patterns | `ep02-hashmap-family.txt` |
| 303 | ep03-longest-substring | Longest unique substring | longest-substring-deep-drill | `ep03-longest-substring.txt` |
| 304 | ep04-two-pointers | Two pointers | two-pointers | `ep04-two-pointers.txt` |
| 305 | ep05-lru | LRU cache | lru-cache-deep-drill | `ep05-lru-cache.txt` |
| 306 | ep06-islands-bfs | Islands + level order | trees-graphs | `ep06-islands-bfs.txt` |
| 307 | ep07-mock-screen | Mock dry run | interview-process + complexity | `ep07-mock-screen.txt` |
| 308 | ep08-stack | Parentheses + stack | stack-queue | `ep08-valid-parentheses-stack.txt` |
| 309 | ep09-intervals | Merge intervals | intervals-design | `ep09-merge-intervals.txt` |
| 310 | ep10-linked-list | Reverse + cycle | dp-search-list | `ep10-linked-list.txt` |
| 311 | ep11-binary-search | Binary search + rotated | dp-search-list | `ep11-binary-search.txt` |
| 312 | ep12-dp | DP fundamentals | dp-search-list | `ep12-dp-fundamentals.txt` |
| 313 | ep13-tree-dfs | Tree DFS | trees-graphs | `ep13-tree-dfs.txt` |
| 314 | ep14-mock-week2 | Mock week 2 | interview-process | `ep14-mock-screen-week2.txt` |
| 315 | ep15-monotonic | Monotonic stack | monotonic-stack-deep-drill | `ep15-monotonic-stack.txt` |
| 316 | ep16-fx-dijkstra | FX best rate | graph-paths-fx | `ep16-fx-dijkstra.txt` |
| 317 | ep17-fx-bellman | FX arbitrage | graph-paths-fx | `ep17-fx-bellman-ford.txt` |
| 318 | ep18-design-in-code | Design-in-code | design-in-code | `ep18-design-in-code.txt` |
| 319 | ep19-interview-clock | Clock + dual AI | interview-process | `ep19-interview-clock-dual-ai.txt` |
| 320 | ep20-ai-deep-dive | AI deep dive pilot | ai-deep-dive-pilot | `ep20-ai-deep-dive-pilot.txt` |
| 321 | ep21-ai-scenario | AI scenario think-aloud | ai-scenario-coding | `ep21-ai-scenario-think-aloud.txt` |
| 322 | ep22-interviewer-tianxiao | Interviewer fit Tianxiao | interviewer-tianxiao | `ep22-interviewer-tianxiao.txt` |
| 330 | mock-rate-limiter | **Two-voice** rate limiter | coding-mock-listen | `mocks/mock-rate-limiter.txt` |
| 331 | mock-currency-best-rate | **Two-voice** FX best rate | coding-mock-listen | `mocks/mock-currency-best-rate.txt` |
| 332 | mock-refund-rules | **Two-voice** refund rules | coding-mock-listen | `mocks/mock-refund-rules.txt` |
| 333 | mock-stream-topk | **Two-voice** stream top-K | coding-mock-listen | `mocks/mock-stream-topk.txt` |

### Two-voice coding mocks (preferred mock style)

Generate: `python3 generate_coding_mocks.py --all --publish`  
Builders: `scripts/coding_mocks/*.py`  
Voices: interviewer Ava · candidate Andrew · narrator Brian  

Each mock: problem → clarify → naive/improve → hand walk → **spoken pseudocode** → corners → complexity → speed recap.

---

## Quality bar (for re-listens)

Each monologue should:

1. Teach **thinking order**, not only the answer  
2. Keep the **eight-step ritual** language stable  
3. State **part one = no AI** for the solve  
4. Point to **deep dive practice** where relevant (ep19/20)  
5. End with **speed recap** and **app + code CTA**  
6. Stay pure spoken prose (TTS friendly)

Speech design: `SPEECH-ENHANCEMENT.md`  
Series plan: `SERIES.md`

---

## 2026-07 update notes

- Official PDF: 2 min intro / 30 min no AI / 25–30 min AI deep dive  
- ep00, ep07, ep14 rewritten for dual mode clock  
- ep01–18 closings: part one no AI + optional Claude Code on same file  
- ep19–21 spine for clock / deep dive / scenario  
- ep22 + tutor `interviewer-tianxiao.md` from `INTERVIEWER-PROFILE.md` (Tianxiao Huang EM)  
