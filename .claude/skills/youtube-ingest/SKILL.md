---
name: youtube-ingest
description: Turn a YouTube video into study notes and an original derived episode. Use when given a video or channel URL to learn from, or asked to expand the learning feeds.
---

# Ingest a video as learning material

Two stages, and the first is valuable on its own. We extract the *text*, distil
it into a study blueprint, and write an **original** episode in the show's own
voice. We do not re-host new source audio.

## 1. Ingest

```
python3 scripts/ingest_youtube.py <url>            # one video
python3 scripts/ingest_youtube.py --from-candidates # whatever curate.py queued
```

Pulls subtitles with yt-dlp (falling back to faster-whisper when a video has
none) and writes `content/sources/youtube/<video_id>.json`: title, channel,
duration, the video's own chapters, and a timestamped transcript.

Already-ingested videos are skipped via `sources/index.json`. Re-run with
`--force` to refresh one.

## 2. Distil into study notes

```
python3 scripts/blueprint_from_source.py <video_id> --notes
```

Produces `content/notes/<slug>.md`: the outline, the key claims **with their
timestamps**, a glossary, the eight to twelve questions an interviewer would
ask on this material, common misconceptions, and how it connects to
payments-domain systems.

Read the notes and sanity-check them against the transcript before going
further. If the source is thin or wrong, stop here and tell the user — a bad
source makes a bad episode, and the notes alone may still be worth keeping.

## 3. Compose an original episode

```
python3 scripts/blueprint_from_source.py <video_id> --episode --show <show>
```

Drafts a blueprint against the `youtube-derived` template. Then **read it and
rewrite it** — the generated draft is a starting point, not the deliverable.

Non-negotiable:

- **Our words.** Never reuse the source's phrasing beyond a short quoted
  definition, attributed out loud.
- **Credit the source** by name in the opening section.
- **Every factual claim carries a `sources[]` entry** pointing back to the
  timestamp it came from. The `claims` gate enforces this on any section marked
  `factual: true`.
- **Add the angle the source missed.** If the episode is just a summary, it
  isn't worth making — the value is the interview framing.

Then hand off to the `episode-new` skill from step 4 (gate, dry run, build).

## Adding a channel to the feeds

Edit `scripts/sources.yaml`. YouTube channel and playlist RSS needs no API key:

```yaml
youtube:
  - channel_id: UCxxxx      # from the channel page source
    name: ByteByteGo
    show: system-design
    max_per_run: 2
    min_minutes: 8
    keywords: [system design, scalability]
```

`curate.py` then queues matching new uploads into `data/candidates.json`.

## Existing re-hosted episodes

The 20 episodes already published as re-hosted source audio stay as they are.
They can gain transcripts without being rebuilt:

```
python3 scripts/ingest_youtube.py --backfill
```
