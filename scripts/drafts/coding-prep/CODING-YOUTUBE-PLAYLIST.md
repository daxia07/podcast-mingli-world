# Coding YouTube — Audio-First Playlist

**Playlist id:** `coding-youtube`  
**Goal:** Commute / gym audio that trains **think + speak** for Airwallex-style LC easy/medium.  
**Sources:** Tier-A only (NeetCode short walkthroughs). No grind streams, no mega-courses.

## How to use (muscle memory loop)

For each day:

1. **Listen** to the NeetCode clip (audio OK — he narrates brute → optimal).  
2. **Pause and say back** the 8-step ritual without notes.  
3. **Listen** to the matching **Coding Prep** episode (your think-aloud, same problem).  
4. **Open app** deep drill / pattern unit — options cold.  
5. **Code once** without AI before sleep.

Do **not** treat YouTube as the final speech. YouTube is the model pattern; **your** episodes are the mouth muscle.

## Order (7-day schedule)

| Day | YouTube (audio-first) | Your Coding Prep ep | Tutor app |
|-----|----------------------|---------------------|-----------|
| 0 | — | ep00 Ritual | Interview Process |
| 1 | Two Sum (LC 1) | ep01 Two Sum | Two Sum Deep Drill |
| 2 | Contains Duplicate + Group Anagrams + Top K | ep02 HashMap family (planned) | HashMap Patterns |
| 3 | Longest Substring Without Repeating (LC 3) | ep03 Window | Longest Substring Deep Drill |
| 4 | Container With Most Water + 3Sum | ep04 Two pointers (planned) | Two Pointers |
| 5 | LRU Cache (LC 146) | ep05 LRU (planned) | LRU Deep Drill |
| 6 | Number of Islands + Level Order | ep06 BFS muscle (planned) | Trees & Graphs |
| 7 | (re-listen ritual + worst day) | ep07 Mock screen (planned) | Process + Complexity |

## Curated URLs (verified NeetCode)

| # | Theme | Title | URL | Audio fit | Pair with |
|---|--------|-------|-----|-----------|-----------|
| 1 | `yt-coding-two-sum` | Two Sum — HashMap | https://www.youtube.com/watch?v=KLlXCFG5TnA | Excellent — brute then one-pass spoken | ep01 |
| 2 | `yt-coding-contains-dup` | Contains Duplicate | https://www.youtube.com/watch?v=3OamzN90kPg | Excellent short set pattern | ep02 |
| 3 | `yt-coding-group-anagrams` | Group Anagrams | https://www.youtube.com/watch?v=vzdNOK2oB2E | Good; count-array story is verbalizable | ep02 |
| 4 | `yt-coding-top-k` | Top K Frequent Elements | https://www.youtube.com/watch?v=YPTqKIgVk-k | Good if you ignore heap drawing moments | ep02 |
| 5 | `yt-coding-longest-substr` | Longest Substring Without Repeating | https://www.youtube.com/watch?v=wiGpQwVHdE0 | Excellent window expand/shrink in words | ep03 |
| 6 | `yt-coding-water` | Container With Most Water | https://www.youtube.com/watch?v=UuiTKBwPgAo | Good two-pointer narrative | ep04 |
| 7 | `yt-coding-3sum` | 3Sum | https://www.youtube.com/watch?v=jzZsG8n2R9A | Good; skip pure board seconds | ep04 |
| 8 | `yt-coding-lru` | LRU Cache | https://www.youtube.com/watch?v=7ABFKPK2hD4 | Medium — list moves; still best audio of design problems | ep05 |
| 9 | `yt-coding-islands` | Number of Islands | https://www.youtube.com/watch?v=pV2kpPD66nE | Medium — grid is visual; restate as BFS/DFS steps | ep06 |
| 10 | `yt-coding-level-order` | Binary Tree Level Order | https://www.youtube.com/watch?v=6ZnyEApgFYg | Good BFS queue speech | ep06 |
| 11 | `yt-coding-two-sum-ii` | Two Sum II (sorted) | https://www.youtube.com/watch?v=cQ1Oz4ckceM | Excellent two-pointer contrast to Day 1 | bonus |

## Intentionally excluded (poor pure audio)

- Live multi-hour grind streams  
- 10h+ roadmap binge playlists as background noise  
- Pure code-along typing with little narration  
- Fiset / Bari long courses as commute audio (use sit-down when *why* is fuzzy)

## Pipeline

```bash
# Download + extract audio (personal study archive)
cd podcast-mingli-world/scripts
python3 publish_coding_youtube.py --download
# optional filters: --day 1   or   --id 401

# Publish into site playlist coding-youtube
python3 publish_coding_youtube.py --publish
# both: --download --publish
```

Config source of truth: `scripts/coding_youtube_playlist.json`  
Speech training design: `SPEECH-ENHANCEMENT.md`
