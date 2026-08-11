#!/usr/bin/env python3
"""synth.py — render a blueprint to audio while recording exact offsets.

Each line becomes its own MP3, is post-processed, then measured with ffprobe.
Concatenation uses the ffmpeg concat demuxer with `-c copy`, which rewrites no
frames, so the measured durations really are the playback offsets.

Two rules make the timings trustworthy, and breaking either silently corrupts
every chapter marker:

1. **Measure after post-processing.** loudnorm and silence trimming change
   length. Measuring the raw TTS output would drift by seconds over an episode.
2. **Never crossfade timed segments.** `acrossfade` overlaps audio, so the
   total is shorter than the sum of the parts and every offset after the first
   fade is wrong. Gaps are explicit silence segments of known length instead.

ffmpeg and edge-tts are imported lazily so the rest of the library stays
importable (and testable) on a machine without them.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from .blueprint import Blueprint
from .timeline import Timeline, build as build_timeline, calibrate, flatten, gaps_for

# edge-tts emits 24 kHz mono. Silence must match, or the concat demuxer
# produces a file whose duration doesn't match the sum of its parts.
SILENCE_RATE = 24000
SILENCE_CHANNELS = 1
SILENCE_BITRATE = "48k"


class SynthError(RuntimeError):
    pass


def require_tools() -> None:
    missing = [t for t in ("ffmpeg", "ffprobe") if not shutil.which(t)]
    if missing:
        raise SynthError(
            f"missing required tool(s): {', '.join(missing)}. "
            "Install with `brew install ffmpeg`."
        )


def probe_duration(path: str | Path) -> float:
    """Exact duration in seconds. Raises rather than guessing — a wrong
    duration here corrupts every offset that follows it."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SynthError(f"ffprobe failed on {path}: {result.stderr.strip()[:200]}")
    try:
        return float(result.stdout.strip())
    except ValueError:
        raise SynthError(f"ffprobe returned no duration for {path}") from None


def make_silence(seconds: float, out_path: Path) -> Path:
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-f", "lavfi",
            "-i", f"anullsrc=r={SILENCE_RATE}:cl=mono",
            "-t", f"{seconds:.3f}",
            "-ar", str(SILENCE_RATE), "-ac", str(SILENCE_CHANNELS),
            "-b:a", SILENCE_BITRATE,
            str(out_path),
        ],
        capture_output=True,
    )
    if not out_path.exists():
        raise SynthError(f"could not generate {seconds}s of silence")
    return out_path


def concat(paths: list[Path], out_path: Path) -> Path:
    """Stream-copy concatenation — no re-encode, so offsets stay additive."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as listing:
        for path in paths:
            escaped = str(path).replace("'", r"'\''")
            listing.write(f"file '{escaped}'\n")
        listing_path = listing.name

    result = subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-f", "concat", "-safe", "0",
            "-i", listing_path,
            "-c", "copy",
            str(out_path),
        ],
        capture_output=True,
        text=True,
    )
    Path(listing_path).unlink(missing_ok=True)

    if result.returncode != 0 or not out_path.exists():
        raise SynthError(f"concat failed: {result.stderr.strip()[:300]}")
    return out_path


def synthesize(
    bp: Blueprint,
    out_path: str | Path,
    *,
    workdir: str | Path | None = None,
    rate: str | None = None,
    progress=print,
) -> Timeline:
    """Render `bp` to `out_path` and return the Timeline of what was produced.

    The returned Timeline drives chapters.py and transcript.py, so the audio
    and its metadata can never disagree — they come from the same measurement.
    """
    require_tools()

    # Imported here: edge_tts is a heavy optional dependency and the caller may
    # only want the pure helpers above.
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import tts as tts_module  # scripts/tts.py

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    temp_root = Path(workdir) if workdir else Path(tempfile.mkdtemp(prefix="synth_"))
    temp_root.mkdir(parents=True, exist_ok=True)

    flat = flatten(bp)
    gaps = gaps_for(bp)

    segments: list[Path] = []
    durations: list[float] = []

    for index, ((section_id, _, line), gap) in enumerate(zip(flat, gaps)):
        segment = temp_root / f"{index:04d}_{section_id}.mp3"
        voice = bp.voice_for(line.voice)

        progress(f"  [{index + 1}/{len(flat)}] {section_id} ({voice}) {line.text[:48]!r}")

        kwargs = {"voice": voice}
        if rate:
            kwargs["rate"] = rate
        tts_module.synthesize(line.text, str(segment), **kwargs)

        if not segment.exists() or segment.stat().st_size == 0:
            raise SynthError(f"TTS produced nothing for line {index} in {section_id!r}")

        # Measured after tts.synthesize's own loudnorm/silence pass — see rule 1.
        durations.append(probe_duration(segment))
        segments.append(segment)

        if gap > 0:
            silence = make_silence(gap, temp_root / f"{index:04d}_gap.mp3")
            segments.append(silence)

    concat(segments, out_path)

    timeline = build_timeline(bp, durations)

    # MP3 frames are fixed-size, so each segment is padded to a frame boundary
    # and the joins accumulate a small drift — around 40ms per segment. The
    # measured durations are right; the error is in the gaps, so calibrate
    # against the real file rather than trusting the computed total.
    actual = probe_duration(out_path)
    drift = actual - timeline.total

    # Beyond a few percent this is not frame padding, it is a real fault —
    # a dropped segment or a re-encode — and publishing would misplace chapters.
    if abs(drift) > max(5.0, actual * 0.02):
        raise SynthError(
            f"timeline drift {drift:.2f}s (computed {timeline.total:.2f}s, "
            f"actual {actual:.2f}s) — too large to be frame padding; "
            "a segment is probably missing"
        )

    timeline = calibrate(timeline, actual)
    per_join = drift / max(len(timeline.lines) - 1, 1)
    progress(
        f"  total {actual:.1f}s (drift {drift * 1000:+.0f} ms over "
        f"{len(timeline.lines)} segments, {per_join * 1000:+.0f} ms/join, calibrated)"
    )

    return timeline
