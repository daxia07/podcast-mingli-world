#!/usr/bin/env python3
"""transcript.py — WebVTT from a Timeline.

One cue per blueprint line. Because the text is what was *sent* to TTS rather
than what a recogniser guessed, these transcripts are exact: no hallucinated
words, no missing proper nouns, correct speaker attribution in the two-voice
mock-interview shows.

VTT (not SRT) because that is what `<podcast:transcript>` consumers and Apple
Podcasts prefer, and what the browser player parses in site/js/transcript.js.
"""

from __future__ import annotations

from .timeline import Timeline

# Voice role -> the label shown in the transcript panel and the <v> tag.
SPEAKER_LABELS = {
    "interviewer": "Interviewer",
    "candidate": "Candidate",
    "narrator": "Host",
    "estimation": "Host",
    "legacy": "Host",
}


def format_timestamp(seconds: float) -> str:
    """WebVTT wants HH:MM:SS.mmm, always with hours."""
    if seconds < 0:
        seconds = 0.0
    total_ms = int(round(seconds * 1000))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"


def build(timeline: Timeline, *, multi_voice: bool | None = None) -> str:
    """Render the timeline as a WebVTT document.

    Speaker tags are emitted only when the episode actually has more than one
    voice — tagging every cue "Host" in a solo narration is just noise.
    """
    if multi_voice is None:
        multi_voice = len({line.voice for line in timeline.lines}) > 1

    out = ["WEBVTT", ""]

    for index, line in enumerate(timeline.lines, start=1):
        # Hold each cue until the next one starts so the highlight never blinks
        # off during the silence between lines.
        end = line.end + line.gap_after if line.gap_after else line.end

        out.append(str(index))
        out.append(f"{format_timestamp(line.start)} --> {format_timestamp(end)}")

        text = " ".join(line.text.split())
        if multi_voice:
            label = SPEAKER_LABELS.get(line.voice, line.voice.title())
            out.append(f"<v {label}>{text}")
        else:
            out.append(text)
        out.append("")

    return "\n".join(out)


def parse(vtt: str) -> list[dict]:
    """Minimal VTT reader — {start, end, speaker, text}.

    Used by tests and by `backfill_transcripts.py` when normalising subtitle
    files that came from yt-dlp or whisper rather than from this module.
    """
    cues: list[dict] = []
    blocks = [b for b in vtt.replace("\r\n", "\n").split("\n\n") if b.strip()]

    for block in blocks:
        lines = [ln for ln in block.split("\n") if ln.strip()]
        if not lines or lines[0].startswith("WEBVTT"):
            continue

        timing_idx = next((i for i, ln in enumerate(lines) if "-->" in ln), None)
        if timing_idx is None:
            continue

        start_raw, _, end_raw = lines[timing_idx].partition("-->")
        text_lines = lines[timing_idx + 1 :]
        if not text_lines:
            continue

        text = " ".join(text_lines).strip()
        speaker = None
        if text.startswith("<v "):
            label, _, rest = text[3:].partition(">")
            speaker = label.strip()
            text = rest.strip()

        cues.append(
            {
                "start": _parse_timestamp(start_raw.strip()),
                "end": _parse_timestamp(end_raw.strip().split(" ")[0]),
                "speaker": speaker,
                "text": text,
            }
        )

    return cues


def _parse_timestamp(value: str) -> float:
    parts = value.replace(",", ".").split(":")
    if len(parts) == 3:
        hours, minutes, seconds = parts
    elif len(parts) == 2:
        hours, minutes, seconds = "0", parts[0], parts[1]
    else:
        return 0.0
    try:
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    except ValueError:
        return 0.0
