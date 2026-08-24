"""Music bed and sound effects for bedtime-story episodes.

Everything here is synthesised from first principles with the stdlib —
no audio files in the repo, nothing downloaded, no licensing questions.
The bed is a slow music-box lullaby figure; the effects are soft and
cartoonish on purpose, so they sit under narration without ever startling
a sleepy listener.

All rendering is 48 kHz mono 16-bit PCM WAV, matching the pinned episode
format (scripts/tts.py OUTPUT_*), so the mix step needs no resampling and
`audio.is_uniform` keeps passing after the ffmpeg mix.
"""

import math
import os
import random
import struct
import wave

SAMPLE_RATE = 48_000

# Mix levels, relative to the already-normalised voice track.
BED_GAIN_DB = -27.0
SFX_GAIN_DB = -13.0
BED_FADE_S = 6.0


def _write_wav(path, samples):
    frames = b"".join(
        struct.pack("<h", max(-32767, min(32767, int(s * 32767)))) for s in samples
    )
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(frames)


def _note(freq, seconds, tau=0.9, velocity=1.0):
    """A struck music-box tine: sine partials with exponential ring-out."""
    n = int(seconds * SAMPLE_RATE)
    out = [0.0] * n
    for k, amp in ((1, 1.0), (2, 0.30), (3, 0.12), (4, 0.05)):
        w = 2 * math.pi * freq * k
        for i in range(n):
            t = i / SAMPLE_RATE
            env = min(t / 0.012, 1.0) * math.exp(-t / tau)
            out[i] += amp * math.sin(w * t) * env
    peak = max(abs(s) for s in out) or 1.0
    return [s / peak * velocity for s in out]


def render_bed(seconds: float, path):
    """A slow lullaby figure that loops for the whole episode and fades out."""
    rng = random.Random(20260824)
    root = 261.63  # C4
    # Gentle phrase in scale degrees, held long enough to feel like rocking.
    melody = [
        0, 0, 4, 0, 0, 4, 0, 4, 7, 5, 5, 4,
        4, 5, 7, 5, 4, 2, 0, -1, 0,
    ]
    eighth = 0.55
    lengths = [2, 1, 2, 2, 1, 2, 2, 1, 2, 2, 1, 4, 2, 1, 2, 2, 1, 2, 2, 1, 6]

    total = int(seconds * SAMPLE_RATE)
    buf = [0.0] * total
    pos = 0
    idx = 0
    while pos < total:
        semis = melody[idx % len(melody)]
        dur = lengths[idx % len(lengths)] * eighth
        freq = root * (2 ** (semis / 12))
        note = _note(freq, min(dur * 2.2, 4.0), velocity=0.75 + rng.random() * 0.15)
        for i, s in enumerate(note):
            j = pos + i
            if j < total:
                buf[j] += s
        pos += int(dur * SAMPLE_RATE)
        idx += 1
        if idx % len(melody) == 0:
            pos += int(0.8 * SAMPLE_RATE)

    # Two-tap echo gives the box a little room without any reverb impulse.
    delay = int(0.31 * SAMPLE_RATE)
    echoed = buf[:]
    for i in range(total):
        if i >= delay:
            echoed[i] += 0.28 * buf[i - delay]
        if i >= 2 * delay:
            echoed[i] += 0.10 * buf[i - 2 * delay]

    peak = max(abs(s) for s in echoed) or 1.0
    gain = 0.42 / peak
    fade_n = int(BED_FADE_S * SAMPLE_RATE)
    for i in range(total):
        s = echoed[i] * gain
        remain = total - i
        if remain < fade_n:
            s *= remain / fade_n
        echoed[i] = s
    _write_wav(path, echoed)
    return path


# ---------------------------------------------------------------------------
# Sound effects — each is short, soft, and named for a story beat.
# ---------------------------------------------------------------------------


def _noise_burst(n, attack=0.005, tau=0.25):
    # Seeded so a rebuild produces the same episode byte-for-byte.
    rng = random.Random(7)
    return [
        (rng.random() * 2 - 1) * min(i / (attack * SAMPLE_RATE), 1.0)
        * math.exp(-i / (tau * SAMPLE_RATE))
        for i in range(n)
    ]


def _lowpass(samples, alpha):
    out, acc = [], 0.0
    for s in samples:
        acc += alpha * (s - acc)
        out.append(acc)
    return out


def _sfx_splash():
    n = int(0.8 * SAMPLE_RATE)
    out = _lowpass(_noise_burst(n, attack=0.004, tau=0.18), 0.35)
    for start, f0, f1 in ((0.10, 900, 300), (0.22, 700, 250), (0.38, 500, 200)):
        base = int(start * SAMPLE_RATE)
        dur = int(0.09 * SAMPLE_RATE)
        for i in range(dur):
            t = i / SAMPLE_RATE
            f = f0 + (f1 - f0) * t / 0.09
            if base + i < n:
                out[base + i] += 0.5 * math.sin(2 * math.pi * f * t) * math.exp(-t / 0.03)
    return _normalise(out, 0.5)


def _sfx_buzz():
    n = int(1.4 * SAMPLE_RATE)
    out = []
    for i in range(n):
        t = i / SAMPLE_RATE
        tremolo = 0.6 + 0.4 * math.sin(2 * math.pi * 22 * t)
        saw = 2 * ((140 * t) % 1.0) - 1
        env = min(t / 0.05, 1.0) * min((n - i) / (0.2 * SAMPLE_RATE), 1.0)
        out.append(saw * tremolo * env)
    return _normalise(out, 0.28)


def _sfx_wind():
    n = int(4.0 * SAMPLE_RATE)
    out = _lowpass(_noise_burst(n, attack=1.2, tau=3.0), 0.08)
    for i in range(n):
        t = i / SAMPLE_RATE
        swell = 0.55 + 0.45 * math.sin(2 * math.pi * t / 3.4 - math.pi / 2)
        out[i] *= swell
    return _normalise(out, 0.4)


def _sfx_chirp():
    out = [0.0] * int(0.9 * SAMPLE_RATE)
    for k, start in enumerate((0.05, 0.42)):
        base = int(start * SAMPLE_RATE)
        for i in range(int(0.16 * SAMPLE_RATE)):
            t = i / SAMPLE_RATE
            f = 3100 - 1200 * t
            env = math.exp(-t / 0.06)
            j = base + i
            if j < len(out):
                out[j] += 0.9 * math.sin(2 * math.pi * f * t + 3 * math.sin(2 * math.pi * 40 * t)) * env
    return _normalise(out, 0.5)


def _sfx_wingflap():
    out = [0.0] * int(1.3 * SAMPLE_RATE)
    for start in (0.02, 0.36, 0.70):
        base = int(start * SAMPLE_RATE)
        burst = _lowpass(_noise_burst(int(0.12 * SAMPLE_RATE), attack=0.006, tau=0.05), 0.15)
        for i, s in enumerate(burst):
            j = base + i
            if j < len(out):
                out[j] += s
    return _normalise(out, 0.5)


def _sfx_sparkle():
    out = [0.0] * int(1.6 * SAMPLE_RATE)
    for k, semi in enumerate((0, 4, 7, 12, 16)):
        f = 1046.5 * (2 ** (semi / 12))
        note = _note(f, 0.7, tau=0.35, velocity=0.8)
        base = int((0.04 + k * 0.11) * SAMPLE_RATE)
        for i, s in enumerate(note):
            j = base + i
            if j < len(out):
                out[j] += s
    return _normalise(out, 0.5)


SFX = {
    "splash": _sfx_splash,
    "buzz": _sfx_buzz,
    "wind": _sfx_wind,
    "chirp": _sfx_chirp,
    "wingflap": _sfx_wingflap,
    "sparkle": _sfx_sparkle,
}


def _normalise(samples, peak_target):
    peak = max(abs(s) for s in samples) or 1.0
    return [s / peak * peak_target for s in samples]


def has_story_audio(bp) -> bool:
    return bool(getattr(bp, "music", False)) or any(
        line.sfx for section in bp.sections for line in section.lines
    )


def mix(mp3_path, total_seconds: float, want_music: bool, events, *, progress=print):
    """Mix the voice track with the bed and any per-line effects.

    `events` is [(offset_seconds, name)]. The output replaces mp3_path at the
    pinned format (48 kHz mono 64k), so every downstream check still applies.
    """
    import subprocess
    import tempfile
    from pathlib import Path

    workdir = Path(tempfile.mkdtemp(prefix="story_audio_"))
    inputs = ["-i", str(mp3_path)]
    chains = []
    sfx_labels = []

    next_idx = 1
    if want_music:
        bed_path = workdir / "bed.wav"
        render_bed(total_seconds + 0.2, bed_path)
        inputs += ["-i", str(bed_path)]
        fade_start = max(total_seconds - BED_FADE_S, 0.0)
        chains.append(
            f"[{next_idx}:a]volume={BED_GAIN_DB}dB,"
            f"afade=t=in:st=0:d=2,afade=t=out:st={fade_start:.3f}:d={BED_FADE_S}[bed]"
        )
        next_idx += 1

    for offset, name in events:
        sfx_path = workdir / f"sfx_{next_idx}_{name}.wav"
        _write_wav(sfx_path, SFX[name]())
        inputs += ["-i", str(sfx_path)]
        ms = int(offset * 1000)
        chains.append(
            f"[{next_idx}:a]volume={SFX_GAIN_DB}dB,adelay={ms}:all=1[e{next_idx}]"
        )
        sfx_labels.append(f"[e{next_idx}]")
        next_idx += 1

    if len(chains) == 0:
        return mp3_path

    mixed = "[0:a]" + ("[bed]" if want_music else "") + "".join(sfx_labels)
    # Inputs consumed: the voice file at index 0, then one per chain.
    n_inputs = next_idx
    # ffmpeg refuses an output path that is also an input, so mix to a sibling.
    out_path = Path(str(mp3_path) + ".mixed.mp3")
    filtergraph = (
        ";".join(chains)
        + f";{mixed}amix=inputs={n_inputs}:normalize=0,alimiter=limit=0.95[out]"
    )

    result = subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            *inputs,
            "-filter_complex", filtergraph,
            "-map", "[out]",
            "-ar", "48000", "-ac", "1", "-b:a", "64k",
            str(out_path),
        ],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
    )
    if result.returncode != 0 or not out_path.exists():
        raise RuntimeError(
            f"story-audio mix failed: {result.stderr.strip()[:400]}"
        )
    os.replace(out_path, mp3_path)
    progress(
        f"  mixed story audio: {'music bed' if want_music else 'voice only'}"
        f"{' + ' + str(len(events)) + ' effects' if events else ''}"
    )
    return mp3_path
