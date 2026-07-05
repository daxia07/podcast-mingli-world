#!/usr/bin/env python3
"""generate.py — Build episode script from plan.json, run edge-tts."""

import json, os, sys, subprocess, shutil
from datetime import datetime, timezone

from r2_utils import get_json

VOICE = "en-US-ChristopherNeural"


def load_pattern(content_bank, pattern_id):
    for p in content_bank["patterns"]:
        if p["id"] == pattern_id:
            return p
    return content_bank["patterns"][0]


def load_tip(content_bank, tip_id):
    for t in content_bank["tips"]:
        if t["id"] == tip_id:
            return t
    return content_bank["tips"][0]


def build_script(plan, article, pattern, tip):
    today = datetime.now(timezone.utc)
    lines = [
        f"Welcome to Daily Interview English. Episode {plan['episode_id']}, {today.strftime('%B %d, %Y')}.",
        ""
    ]

    if article and article.get("source", {}).get("title", "") != "No article available today":
        lines.append(f"Today's episode draws from {article['source'].get('feed', 'an article')}: \"{article['source']['title']}\".")
        lines.append("")

    lines += [
        f"Today's pattern: \"{pattern['phrase']}\"",
        "",
        pattern['explanation'],
        "",
        "Here are three examples. Repeat each one out loud after me.",
        ""
    ]

    for i, example in enumerate(pattern["examples"], 1):
        lines.append(f"Example {i}. {example}")
        lines.append("")

    lines += [
        f"Today's interview tip: {tip['name']}.",
        "",
        tip['explanation'],
        ""
    ]

    for segment in tip.get("segments", []):
        lines.append(segment)
        lines.append("")

    lines += [
        "Your practice prompt for today.",
        "",
        plan['prompt_text'],
        "",
        "Pause this episode now and answer out loud. I'll wait five seconds.",
        "",
        f"That's it for today. The pattern again: \"{pattern['phrase']}\"",
        "Practice it out loud at least three times today.",
        "After you listen, go to the landing page and press thumbs up or thumbs down. Your feedback shapes tomorrow's episode.",
        "See you tomorrow."
    ]

    return "\n".join(lines)


def run_edge_tts(script_text, output_path):
    cmd = ["edge-tts", "--voice", VOICE, "--text", script_text, "--write-media", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Fallback: file-based approach
        script_path = "/tmp/episode_script.txt"
        with open(script_path, "w") as f:
            f.write(script_text)
        result2 = subprocess.run(
            ["edge-tts", "--voice", VOICE, "-f", script_path, "--write-media", output_path],
            capture_output=True, text=True
        )
        if result2.returncode != 0:
            raise RuntimeError(f"edge-tts failed: {result2.stderr}")

    # Post-process with ffmpeg if available
    if shutil.which("ffmpeg"):
        temp_path = output_path + ".temp.mp3"
        os.rename(output_path, temp_path)
        subprocess.run([
            "ffmpeg", "-y", "-i", temp_path,
            "-af", "loudnorm, silenceremove=stop_periods=-1:stop_duration=0.3:stop_threshold=-40dB",
            output_path
        ], capture_output=True)
        os.remove(temp_path)


def main():
    print("=== generate.py ===")

    # Load plan from R2
    print("Loading plan.json...")
    plan = get_json("plan.json")
    if not plan:
        print("ERROR: No plan.json found. Run arrange.py first.")
        sys.exit(1)
    print(f"  Episode #{plan['episode_id']}: '{plan['pattern_phrase']}' — {plan['tip_name']}")

    # Load today.json if available
    script_dir = os.path.dirname(os.path.abspath(__file__))
    today_json = os.path.join(os.path.dirname(script_dir), "data", "today.json")
    article = None
    if os.path.exists(today_json):
        with open(today_json) as f:
            article = json.load(f)

    # Load content bank
    with open(os.path.join(script_dir, "content_bank.json")) as f:
        content_bank = json.load(f)

    pattern = load_pattern(content_bank, plan["pattern_id"])
    tip = load_tip(content_bank, plan["tip_id"])
    print(f"  Pattern: '{pattern['phrase']}' ({pattern['category']})")
    print(f"  Tip: '{tip['name']}' ({tip['category']})")

    # Build script
    print("Building episode script...")
    script = build_script(plan, article, pattern, tip)
    print(f"  Script: {len(script)} chars, ~{len(script.split())} words")

    # Generate audio
    output_dir = os.path.join(os.path.dirname(script_dir), "data")
    os.makedirs(output_dir, exist_ok=True)
    mp3_path = os.path.join(output_dir, "episode.mp3")
    script_path = os.path.join(output_dir, "script.txt")

    with open(script_path, "w") as f:
        f.write(script)

    print("Generating audio with edge-tts...")
    run_edge_tts(script, mp3_path)

    size_kb = os.path.getsize(mp3_path) / 1024
    print(f"  MP3: {size_kb:.0f} KB")
    print("Done")


if __name__ == "__main__":
    main()
