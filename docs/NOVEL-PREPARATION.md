# V3 opening release

The user selected the September 27 V3 opening and delegated the voice choice,
completion of these three audio chapters, and publication on the existing
`podcast.mingli.world`. This is **开篇三章**, with the provisional title
**向后兼容**. It is not a completed 23-chapter novel. Older editions remain intact.

| Chapter | Source chunks | Scene sections | Episode |
|---|---:|---:|---:|
| 还没有收到 | 15 | 4 | 439 |
| 借来的时间 | 21 | 8 | 440 |
| 题目之外 | 23 | 8 | 441 |

Original chapter text and the complete opening are in
`content/sources/novel-opening-v3/`. Exact text downloads and HTML readers are
in `site/novel/`. The three blueprints preserve all words and source hashes.
The setting is 2004; the characters are 陈默、周启、罗宁 and 回声.

## Narration and review

The offline production adapter uses Qwen3-TTS 1.7B CustomVoice MLX 4-bit,
revision `f35faf19b0cc2160865af64ecf0f22f83d335135`, preset Serena,
temperature 0.7, base seed 142, mlx-audio 0.5.7 and mlx 0.32.3. It uses the
existing local model snapshot without paid APIs, accounts, or voice cloning.

Source and spoken text are separate. Documented speech adaptations retain the
manuscript: a pause in 本轮采集，已结束, bounded ellipsis punctuation,
the date's 〇 spoken as 零, and `aqi/local` read as letters, slash, local.
Seed overrides identify exact chunks so a targeted retry preserves other audio.

Each chunk is committed to cache only after PCM validation. Cache identity binds
source, spoken text, render parameters, seed and audio hashes. Changed settings
cannot reuse an old chunk. Corrupt caches, token-limit output, silence, clipping
and decoding failures stop the build. Initial rejected takes remain outside the
release package; no rejected take is silently substituted into a final chapter.

Measured PCM chunks and pauses are assembled once and encoded as **48 kHz mono
64 kbps MP3**. Strict full decoding, actual frame uniformity, and encoder drift
below 150 ms are checked. VTT and chapter timestamps use that measured timeline.

There is no audio-listening tool in this execution environment. An objective
review must explicitly record `listening_performed: false`, the method and its
limitations, and an assessment for every exact PCM/source pair. Each assessment
binds a saved offline ASR report by hash. Short-window recognition resolves
ambiguous full-chunk results; material omissions or garbled passages require
targeted retries. ASR is not proof of pronunciation or listening comfort.
No actual listening is claimed, and no human listening signoff is fabricated.

```bash
python3 scripts/build_episode.py content/blueprints/novel-opening-v3/opening-v3-ch01.json \
  --no-publish --output-dir ../production-build \
  --workdir ../production-build/chunks/opening-v3-ch01 --model-dir <pinned-local-snapshot>

# On the existing authorized publisher, with the exact reviewed artifacts:
python3 scripts/build_episode.py content/blueprints/novel-opening-v3/opening-v3-ch01.json \
  --publish-built --output-dir release-audio \
  --audio-review release-audio/opening-v3-ch01.review.json
```

`--publish-built` needs codecs and existing storage authorization, not a second
speech model. It rechecks review hashes, blueprint, source, transcript and
chapters before using the existing publisher. The builder never grants approval.

## Catalogue and source preservation

Production is Cloudflare Pages `podcast-landing` with R2
`podcast-mingli-world`. The snapshot has 249 episodes and 26 shows, ten more
episodes than the source base. All 249 records and all 26 shows, including IDs
500–509, are preserved exactly. Only the three new episodes and their collection
are added. Recheck the current live catalogue immediately before release.

Publishing refuses stale catalogues, missing published identities and changed
canonical audio paths before uploading. An unreadable catalogue fails closed.
This is a preservation guard, not an atomic cross-publisher lock.

The original MacBook and publisher checkouts contain unrelated dirty work;
neither is edited. Release work uses an isolated checkout. Authentication and
Functions source are unchanged. Existing normal browser sign-in was verified.
The older rejected Vercel mapping action is not retried; publication uses the
independently verified existing Cloudflare service.

## Reversible UI changes

The source adds 1.1× playback, remembers its setting, restores archived shows
with ordered and tag-only episodes, and prevents a hidden System Design fallback
from reappearing. Novel entries link to exact original text. Direct
`/?episode=439` links open the collection and focus the chapter without autoplay.

`content/duplicate-display-proposal.json` records a deterministic comparison of
exact complete media URLs. Representatives are 3, 13 and 15. Thirteen alternate
entries are hidden only in browsing by `display_aliases`; their records, IDs,
URLs, RSS items, queues and progress remain intact. Visible Restore and Undo
controls use separate per-device storage. Removing the mapping reverses it.
This chooses a display representative; it does not verify historical titles
against the shared audio. The coordinated app-shell version is 30.

## Verification

The source suite currently passes 90 Node and 132 Python tests, including real
codec, resumable-cache, targeted-retry, exact-evidence and stale-publish checks.
Tests use synthetic codec fixtures where appropriate, and never make hidden
production writes. Use Node 20 or newer.

Earlier local UI tests used an explicitly labelled audition fixture. They do
not establish production acceptance. The final production report must cover
normal sign-in, all three actual chapter entries, playback, seeking, 1.1×,
next chapter, persisted progress/resume, HTTP 206, full deployed artifact hashes,
and unchanged original catalogue records. Publication and acceptance status
are recorded separately from immutable render receipts.
