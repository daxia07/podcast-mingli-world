# Coding Prep Playlist — Series plan

**Status:** Full series ep00–ep07 scripted + published for Airwallex coding screen  
**Audience:** Commute / gym / walk — muscle memory under time pressure  
**Voice:** BrianNeural think-aloud  
**Companion app:** https://learn.mingli.world coding path  
**Companion YT:** playlist `coding-youtube`  
**Speech design:** `SPEECH-ENHANCEMENT.md`

## Listen order (test week)

| Ep | Title | App unit | Role |
|----|--------|----------|------|
| 0 | Airwallex Screen Ritual | Interview Process | Daily open / night-before |
| 1 | Two Sum | Two Sum Deep Drill | Day 1 |
| 2 | HashMap Family | HashMap Patterns | Day 2 |
| 3 | Longest Unique Substring | Longest Substring Deep Drill | Day 3 |
| 4 | Two Pointers | Two Pointers | Day 4 |
| 5 | LRU Cache | LRU Deep Drill | Day 5 |
| 6 | Islands + Level Order | Trees & Graphs | Day 6 |
| 7 | Mock Screen Dry Run | Process + Complexity | Day 7 / dress rehearsal |

**Plus:** Coding YouTube audio-first (11 NeetCode clips) same day order.

## Daily loop until the test

1. Morning: re-speak one **speed recap** (2 min)  
2. Commute: Coding Prep ep or Coding YouTube for that day + say-back  
3. Evening: app options cold + 15–25 min code **without AI**  
4. Night before: ep00 only, sleep  

## Generate / publish

```bash
cd scripts
python3 generate_coding_prep.py --all --force-tts --publish
python3 publish_coding_youtube.py --download --publish   # if YT audio missing
```

## Scripts

```
ep00-airwallex-coding-ritual.txt
ep01-two-sum-think-aloud.txt
ep02-hashmap-family.txt
ep03-longest-substring.txt
ep04-two-pointers.txt
ep05-lru-cache.txt
ep06-islands-bfs.txt
ep07-mock-screen.txt
```

Pure spoken prose only. Spoken count-out pauses for TTS.
