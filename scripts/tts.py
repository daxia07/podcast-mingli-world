#!/usr/bin/env python3
"""tts.py — TTS with edge-tts: better voices + natural text preprocessing.

Voices:
  - BrianNeural (casual, approachable) — default for think-aloud
  - AndrewNeural (warm, confident) — alternative narrator
  - AvaNeural (expressive, friendly) — interviewer in mock dialogues
  - EmmaNeural (cheerful, clear) — estimation narrator

Text preprocessing inserts natural pauses and verbal hesitations
that edge-tts reads as natural speech (not SSML — edge-tts doesn't support it).
"""

import os, sys, asyncio, subprocess, shutil, tempfile
import edge_tts

VOICE_MAP = {
    "narrator": "en-US-BrianNeural",
    "interviewer": "en-US-AvaNeural",
    "candidate": "en-US-AndrewNeural",
    "estimation": "en-US-EmmaNeural",
    "legacy": "en-US-ChristopherNeural",
}

DEFAULT_VOICE = "narrator"
DEFAULT_RATE = "-5%"

SCRIPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "script.txt")
MP3_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "episode.mp3")

MAX_CHARS_PER_CALL = 5000


def preprocess_text(text):
    """Convert think-aloud markers to natural speech text.

    Rules:
    - Double newlines become sentence breaks with pause markers
    - [pause] or ... becomes " ... " (edge-tts reads as brief pause)
    - [long-pause] becomes two sentences with "Hmm." between
    - Structural markers like ──, Key points:, bullet dashes are removed
    - Verbal connectors are preserved (Hmm, OK, So, Now, Well)
    """
    lines = text.split("\n")
    result = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("====") or stripped.startswith("──"):
            continue

        if stripped in ("[pause]", "[break]"):
            result.append(" ... ")
            continue

        if stripped in ("[long-pause]", "[thinking]"):
            result.append(" Hmm. ... ")
            continue

        if stripped.startswith("[") and stripped.endswith("]"):
            continue

        stripped = stripped.replace("**", "").replace("###", "").replace("`", "")
        stripped = stripped.replace("─", "")
        stripped = stripped.replace("Key points:", "Let me cover the key points.")
        stripped = stripped.replace("Key components:", "The main components are")
        stripped = stripped.replace("Key benefits:", "The benefits here are")
        stripped = stripped.replace("Common pitfalls:", "Now, some common mistakes.")
        stripped = stripped.replace("Trade-offs:", "The trade-off here is")
        stripped = stripped.replace("Real-world examples:", "Some real examples of this.")
        stripped = stripped.replace("When to use:", "You'd want to use this when")
        stripped = stripped.replace("Scale estimates:", "For scale, we're looking at")
        stripped = stripped.replace("Primary bottlenecks:", "The main bottleneck is")
        stripped = stripped.replace("Technologies:", "The typical technologies for this are")

        if stripped.startswith("- ") or stripped.startswith("  - "):
            stripped = stripped.lstrip("- ").lstrip()
            if result and result[-1].strip().endswith(","):
                result.append(stripped + ",")
            else:
                result.append(stripped + ".")

        elif stripped:
            result.append(stripped)

    text = " ".join(result)

    import re
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'\.\. \.', '...', text)

    return text


async def _edge_tts(text, output_path, voice_name, rate):
    communicate = edge_tts.Communicate(text, voice_name, rate=rate)
    await communicate.save(output_path)


def synthesize(text, output_path, voice="narrator", rate=DEFAULT_RATE, preprocess=True):
    """Synthesize speech from text using edge-tts.

    Args:
        text: Input text (plain or with think-aloud markers)
        output_path: Where to save the MP3
        voice: Voice key from VOICE_MAP or direct voice name
        rate: Speaking rate (e.g., "-5%", "+0%")
        preprocess: Whether to apply natural text preprocessing
    """
    if preprocess:
        text = preprocess_text(text)

    voice_name = VOICE_MAP.get(voice, voice)

    if len(text) <= MAX_CHARS_PER_CALL:
        asyncio.run(_edge_tts(text, output_path, voice_name, rate))
    else:
        _synthesize_long(text, output_path, voice_name, rate)

    if shutil.which("ffmpeg"):
        _postprocess(output_path)


def _synthesize_long(text, output_path, voice_name, rate):
    """Split long text into chunks and concatenate with ffmpeg."""
    chunks = _split_text(text, MAX_CHARS_PER_CALL)
    temp_dir = tempfile.mkdtemp(prefix="tts_chunks_")
    chunk_paths = []

    for i, chunk in enumerate(chunks):
        chunk_path = os.path.join(temp_dir, f"chunk_{i:04d}.mp3")
        asyncio.run(_edge_tts(chunk, chunk_path, voice_name, rate))
        chunk_paths.append(chunk_path)

    if len(chunk_paths) == 1:
        import shutil as sh
        sh.move(chunk_paths[0], output_path)
    else:
        list_path = os.path.join(temp_dir, "concat.txt")
        with open(list_path, "w") as f:
            for cp in chunk_paths:
                f.write(f"file '{cp}'\n")

        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", list_path, "-c", "copy", output_path
        ], capture_output=True)

    import shutil as sh
    sh.rmtree(temp_dir, ignore_errors=True)


def _split_text(text, max_chars):
    """Split text at sentence boundaries to stay under max_chars."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    current = ""
    sentences = text.replace(". ", ".\n").replace("? ", "?\n").replace("! ", "!\n").split("\n")

    for sentence in sentences:
        if len(current) + len(sentence) + 1 > max_chars and current:
            chunks.append(current.strip())
            current = sentence
        else:
            current = current + " " + sentence if current else sentence

    if current.strip():
        chunks.append(current.strip())

    return chunks


def _postprocess(mp3_path):
    """Apply loudnorm + silence removal via ffmpeg."""
    temp_path = mp3_path + ".temp.mp3"
    os.rename(mp3_path, temp_path)
    subprocess.run([
        "ffmpeg", "-y", "-i", temp_path,
        "-af", "loudnorm, silenceremove=stop_periods=-1:stop_duration=0.3:stop_threshold=-40dB",
        mp3_path
    ], capture_output=True)
    if os.path.exists(temp_path):
        os.remove(temp_path)


def get_duration_minutes(mp3_path):
    if not shutil.which("ffprobe"):
        return 0
    result = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", mp3_path
    ], capture_output=True, text=True)
    try:
        seconds = float(result.stdout.strip())
        return int(seconds / 60)
    except (ValueError, TypeError):
        return 0


def get_duration_str(mp3_path):
    if not shutil.which("ffprobe"):
        return "~10 min"
    result = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", mp3_path
    ], capture_output=True, text=True)
    try:
        seconds = float(result.stdout.strip())
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m}:{s:02d}"
    except (ValueError, TypeError):
        return "~10 min"


def concatenate_mp3(mp3_paths, output_path):
    """Concatenate multiple MP3 files using ffmpeg."""
    temp_dir = tempfile.mkdtemp(prefix="tts_concat_")
    list_path = os.path.join(temp_dir, "concat.txt")
    with open(list_path, "w") as f:
        for p in mp3_paths:
            f.write(f"file '{p}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_path, "-c", "copy", output_path
    ], capture_output=True)

    import shutil as sh
    sh.rmtree(temp_dir, ignore_errors=True)


def crossfade_mp3(mp3_paths, output_path, fade_ms=300):
    """Concatenate MP3s with crossfade between segments."""
    if len(mp3_paths) == 1:
        import shutil as sh
        sh.copy2(mp3_paths[0], output_path)
        return

    inputs = []
    filter_parts = []
    for i, p in enumerate(mp3_paths):
        inputs.extend(["-i", p])

    n = len(mp3_paths)
    if n == 2:
        filter_str = f"[0][1]acrossfade=d={fade_ms/1000}:c1=tri:c2=tri[a]"
    else:
        filter_parts = []
        for i in range(n - 1):
            if i == 0:
                inp_a = f"[{i}]"
            else:
                inp_a = f"[t{i-1}]"
            inp_b = f"[{i+1}]"
            if i == n - 2:
                out = "[a]"
            else:
                out = f"[t{i}]"
            filter_parts.append(f"{inp_a}{inp_b}acrossfade=d={fade_ms/1000}:c1=tri:c2=tri{out}")
        filter_str = ";".join(filter_parts)

    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_str, "-map", "[a]", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        concatenate_mp3(mp3_paths, output_path)


def main():
    if not os.path.exists(SCRIPT_PATH):
        print(f"ERROR: {SCRIPT_PATH} not found. Run selector.py first.")
        sys.exit(1)

    with open(SCRIPT_PATH) as f:
        text = f.read()

    clean_text = preprocess_text(text)
    word_count = len(clean_text.split())
    estimated_minutes = word_count / 140

    print(f"Script: {word_count} words (~{estimated_minutes:.1f} min)")
    print(f"Voice: {VOICE_MAP[DEFAULT_VOICE]}")
    print(f"Generating MP3...")

    synthesize(text, MP3_PATH, voice=DEFAULT_VOICE)

    size_kb = os.path.getsize(MP3_PATH) / 1024
    print(f"Done: {MP3_PATH} ({size_kb:.0f} KB)")
    print(f"\nNext: python3 scripts/publish.py")


if __name__ == "__main__":
    main()
