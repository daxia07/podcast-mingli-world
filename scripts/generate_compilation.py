#!/usr/bin/env python3
"""generate_compilation.py — Build compilation episode scripts merging unique patterns.

Each compilation covers 3-4 patterns with their related tips, creating a focused
10-15 minute episode that replaces the repetitive individual episodes #1-16.
"""

import json, os, sys, subprocess, shutil
from datetime import datetime, timezone

VOICE = "en-US-ChristopherNeural"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_BANK_PATH = os.path.join(SCRIPT_DIR, "content_bank.json")

COMPILATIONS = [
    {
        "theme": "comp-opinions",
        "title": "Stating Opinions & Perspectives",
        "pattern_ids": ["the-way-i-see-it", "that-said", "id-argue-that"],
        "tip_ids": ["four-second-pause", "verbal-signposting"]
    },
    {
        "theme": "comp-self-desc",
        "title": "Self-Description & Career Narrative",
        "pattern_ids": ["what-clicked-for-me", "over-time-i-became", "what-im-looking-for"],
        "tip_ids": ["star-la", "structure-first"]
    },
    {
        "theme": "comp-emphasis",
        "title": "Emphasis & Elaboration",
        "pattern_ids": ["what-id-highlight", "to-put-a-finer-point-on-it", "to-give-you-a-concrete-example", "this-resulted-in"],
        "tip_ids": ["hook-flow-landing", "so-what-test"]
    },
    {
        "theme": "comp-bridging",
        "title": "Thinking Time & Bridging Gaps",
        "pattern_ids": ["thats-a-great-question", "i-havent-worked-with-that"],
        "tip_ids": ["i-dont-know-bridging", "pause-and-anchor", "acknowledge-reframe"]
    }
]


def load_content_bank():
    with open(CONTENT_BANK_PATH) as f:
        return json.load(f)


def find_patterns(content_bank, pattern_ids):
    found = []
    for pid in pattern_ids:
        for p in content_bank["patterns"]:
            if p["id"] == pid:
                found.append(p)
                break
        else:
            print(f"  WARNING: Pattern '{pid}' not found in content_bank")
    return found


def find_tips(content_bank, tip_ids):
    found = []
    for tid in tip_ids:
        for t in content_bank["tips"]:
            if t["id"] == tid:
                found.append(t)
                break
        else:
            print(f"  WARNING: Tip '{tid}' not found in content_bank")
    return found


def build_pattern_section(pat, index, total):
    lines = []
    lines.append(f"── Pattern {index} of {total}: \"{pat['phrase']}\" ──")
    lines.append("")
    lines.append(pat["explanation"])
    lines.append("")
    if pat.get("when_to_use"):
        lines.append(f"When to use: {pat['when_to_use']}.")
        lines.append("")

    examples = pat.get("examples", [])
    if examples:
        lines.append(f"Here are {min(3, len(examples))} examples. After each one, pause and repeat it out loud.")
        lines.append("")
        for j, ex in enumerate(examples[:3], 1):
            if isinstance(ex, dict):
                lines.append(f"Example {j}. {ex.get('q', str(ex))}")
            else:
                lines.append(f"Example {j}. {ex}")
            lines.append("")

    return lines


def build_tip_section(tip, index, total):
    lines = []
    lines.append(f"── Framework {index} of {total}: {tip['name']} ──")
    lines.append("")
    lines.append(tip["explanation"])
    lines.append("")

    segments = tip.get("segments", [])
    if segments:
        for j, seg in enumerate(segments, 1):
            lines.append(f"Step {j}. {seg}")
            lines.append("")

    return lines


def build_script(comp_config, content_bank):
    today = datetime.now(timezone.utc)
    patterns = find_patterns(content_bank, comp_config["pattern_ids"])
    tips = find_tips(content_bank, comp_config["tip_ids"])

    if not patterns:
        print(f"  WARNING: No patterns found for {comp_config['theme']}")
        return ""

    lines = []

    lines.append(f"Welcome to Interview Pattern Practice. {today.strftime('%B %d, %Y')}.")
    lines.append("")
    lines.append(f"Today's compilation: {comp_config['title']}.")
    lines.append("")
    lines.append(f"We're covering {len(patterns)} English patterns and {len(tips)} interview frameworks in one focused session. These patterns work together — use them in combination and your answers will sound more structured and confident.")
    lines.append("")

    for i, pat in enumerate(patterns, 1):
        lines.extend(build_pattern_section(pat, i, len(patterns)))

    if tips:
        lines.append("── Supporting Frameworks ──")
        lines.append("")
        lines.append("Now let's look at the interview frameworks that complement these patterns.")
        lines.append("")
        for i, tip in enumerate(tips, 1):
            lines.extend(build_tip_section(tip, i, len(tips)))

    lines.append("── Practice ──")
    lines.append("")
    lines.append("Now it's your turn. I'll give you a prompt. Pause this episode and answer out loud, using at least one of today's patterns.")
    lines.append("")
    lines.append(f"Prompt: Tell me about a time you had to {comp_config['title'].lower().split('&')[0].strip()} in a professional setting.")
    lines.append("")
    lines.append("Pause now and practice your answer out loud.")
    lines.append("")

    lines.append("── Quick Review ──")
    lines.append("")
    for pat in patterns:
        lines.append(f"\"{pat['phrase']}\" — {pat['explanation'][:80]}")
    lines.append("")
    for tip in tips:
        lines.append(f"{tip['name']} — {tip['explanation'][:80]}")
    lines.append("")

    lines.append("── Outro ──")
    lines.append("")
    lines.append("Remember: these patterns are tools, not scripts. Use them naturally, one per conversation. The goal is fluency, not performance.")
    lines.append("")
    lines.append("Great work today. See you next time.")
    lines.append("")

    return "\n".join(lines)


def run_edge_tts(script_text, output_path):
    script_path = "/tmp/comp_episode_script.txt"
    with open(script_path, "w") as f:
        f.write(script_text)

    cmd = ["edge-tts", "--voice", VOICE, "--rate=-15%", "--text", script_text, "--write-media", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        cmd2 = ["edge-tts", "--voice", VOICE, "--rate=-15%", "-f", script_path, "--write-media", output_path]
        result2 = subprocess.run(cmd2, capture_output=True, text=True)
        if result2.returncode != 0:
            raise RuntimeError(f"edge-tts failed: {result2.stderr[:500]}")

    if shutil.which("ffmpeg"):
        temp_path = output_path + ".temp.mp3"
        os.rename(output_path, temp_path)
        subprocess.run([
            "ffmpeg", "-y", "-i", temp_path,
            "-af", "loudnorm, silenceremove=stop_periods=-1:stop_duration=0.3:stop_threshold=-40dB",
            output_path
        ], capture_output=True)
        os.remove(temp_path)


def get_duration_str(mp3_path):
    if not shutil.which("ffprobe"):
        return "~12 min"
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
        return "~12 min"


def main():
    print("=== generate_compilation.py ===")

    content_bank = load_content_bank()
    data_dir = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
    os.makedirs(data_dir, exist_ok=True)

    theme = sys.argv[1] if len(sys.argv) > 1 else None

    if theme:
        configs = [c for c in COMPILATIONS if c["theme"] == theme]
        if not configs:
            print(f"ERROR: Unknown theme '{theme}'. Available: {[c['theme'] for c in COMPILATIONS]}")
            sys.exit(1)
    else:
        configs = COMPILATIONS

    results = []

    for config in configs:
        print(f"\n--- {config['title']} ---")

        script = build_script(config, content_bank)
        if not script:
            continue

        word_count = len(script.split())
        print(f"  Script: {word_count} words, ~{word_count / 140:.0f} min estimated")

        script_path = os.path.join(data_dir, f"comp-{config['theme']}.txt")
        with open(script_path, "w") as f:
            f.write(script)

        mp3_path = os.path.join(data_dir, f"comp-{config['theme']}.mp3")
        print(f"  Generating audio...")
        run_edge_tts(script, mp3_path)

        size_mb = os.path.getsize(mp3_path) / (1024 * 1024)
        dur = get_duration_str(mp3_path)
        print(f"  MP3: {size_mb:.1f} MB, {dur}")

        results.append({
            "theme": config["theme"],
            "title": config["title"],
            "pattern_ids": config["pattern_ids"],
            "tip_ids": config["tip_ids"],
            "script_path": script_path,
            "mp3_path": mp3_path,
            "file_size_bytes": os.path.getsize(mp3_path),
            "duration": dur
        })

    results_path = os.path.join(data_dir, "comp_episodes.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDone — {len(results)} compilation episodes generated")
    print(f"Results saved to {results_path}")


if __name__ == "__main__":
    main()
