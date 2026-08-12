#!/usr/bin/env python3
"""audio.py — MP3 frame inspection, in pure Python.

Exists because of a real failure: episodes built by `synth.py` played for about
eleven seconds and then stopped dead in the browser. `ffprobe` reported the full
duration and the file looked healthy, because ffmpeg happily decodes a stream
whose parameters change mid-file. Browser decoders do not — they stop at the
first change.

The cause was that speech segments came out of `tts.py` at 48 kHz (ffmpeg's
`loudnorm` filter resamples) while the silence inserted between them was
generated at 24 kHz. Concatenating them with `-c copy` produced a file that
alternated formats 45 times.

`scan()` walks the frame headers and reports every parameter change, so the
build can refuse to publish a file no player will finish. No ffmpeg needed,
which also means it runs in tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Layer III bitrate tables, in kbps, indexed by the header's 4-bit field.
_BITRATES_V1 = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]
_BITRATES_V2 = [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0]

_RATES = {
    3: {0: 44100, 1: 48000, 2: 32000},  # MPEG 1
    2: {0: 22050, 1: 24000, 2: 16000},  # MPEG 2
    0: {0: 11025, 1: 12000, 2: 8000},   # MPEG 2.5
}

_CHANNELS = ["stereo", "joint", "dual", "mono"]


@dataclass(frozen=True)
class FrameFormat:
    version: str
    sample_rate: int
    bitrate: int
    channel_mode: str

    def __str__(self) -> str:
        return f"{self.version} {self.sample_rate} Hz {self.bitrate} kbps {self.channel_mode}"


@dataclass
class Run:
    """A stretch of frames sharing one format."""

    fmt: FrameFormat
    first_frame: int
    byte_offset: int
    seconds: float


def _skip_id3(data: bytes) -> int:
    if data[:3] != b"ID3":
        return 0
    # Syncsafe 28-bit size, excluding the 10-byte header.
    size = (data[6] << 21) | (data[7] << 14) | (data[8] << 7) | data[9]
    return 10 + size


def scan(path: str | Path) -> list[Run]:
    """Format runs through an MP3, in order. One run means a uniform file."""
    data = Path(path).read_bytes()
    i = _skip_id3(data)

    runs: list[Run] = []
    frames = 0
    elapsed = 0.0

    while i < len(data) - 4:
        if data[i] != 0xFF or (data[i + 1] & 0xE0) != 0xE0:
            i += 1
            continue

        version = (data[i + 1] >> 3) & 0x03
        layer = (data[i + 1] >> 1) & 0x03
        bitrate_idx = (data[i + 2] >> 4) & 0x0F
        rate_idx = (data[i + 2] >> 2) & 0x03
        padding = (data[i + 2] >> 1) & 0x01
        channel = (data[i + 3] >> 6) & 0x03

        # layer==1 is Layer III; version==1 is reserved.
        if layer != 1 or version == 1 or rate_idx == 3 or bitrate_idx in (0, 15):
            i += 1
            continue

        sample_rate = _RATES.get(version, {}).get(rate_idx)
        table = _BITRATES_V1 if version == 3 else _BITRATES_V2
        bitrate = table[bitrate_idx]
        if not sample_rate or not bitrate:
            i += 1
            continue

        samples = 1152 if version == 3 else 576
        size = int((samples / 8) * bitrate * 1000 / sample_rate) + padding

        fmt = FrameFormat(
            version="MPEG1" if version == 3 else "MPEG2",
            sample_rate=sample_rate,
            bitrate=bitrate,
            channel_mode=_CHANNELS[channel],
        )
        if not runs or runs[-1].fmt != fmt:
            runs.append(Run(fmt=fmt, first_frame=frames, byte_offset=i, seconds=elapsed))

        frames += 1
        elapsed += samples / sample_rate
        i += max(size, 4)

    return runs


def is_uniform(path: str | Path) -> bool:
    return len(scan(path)) <= 1


def describe(path: str | Path, limit: int = 6) -> str:
    runs = scan(path)
    if not runs:
        return "no MP3 frames found"
    if len(runs) == 1:
        return f"uniform: {runs[0].fmt}"

    lines = [f"{len(runs)} format changes — players will stop at the first one:"]
    for run in runs[:limit]:
        lines.append(f"    {run.seconds:7.2f}s  frame {run.first_frame:6d}  {run.fmt}")
    if len(runs) > limit:
        lines.append(f"    ... {len(runs) - limit} more")
    return "\n".join(lines)
