#!/usr/bin/env python3
"""generate.py — Build episode script from plan.json + today.json, run edge-tts.

Runs at 5 AM AEST (19:00 UTC) via GitHub Actions.
Reads plan.json from R2 and today.json from local data/, fills the script
template, and generates the MP3 via edge-tts.
"""

import json, os, sys, subprocess, shutil
from datetime import datetime, timezone

import boto3

R2_ENDPOINT = os.environ["R2_ENDPOINT"]
R2_ACCESS_KEY = os.environ["R2_ACCESS_KEY"]
R2_SECRET_KEY = os.environ["R2_SECRET_KEY"]
BUCKET = "podcast-mingli-world"
VOICE = "en-US-ChristopherNeural"


def load_json_from_r2(s3, key):
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=key)
        return json.loads(obj["Body"].read().decode())
    except s3.exceptions.NoSuchKey:
        return None


def load_pattern_details(content_bank, pattern_id):
    for p in content_bank["patterns"]:
        if p["id"] == pattern_id:
            return p
    return content_bank["patterns"][0]


def load_tip_details(content_bank, tip_id):
    for t in content_bank["tips"]:
        if t["id"] == tip_id:
            return t
    return content_bank["tips"][0]


def build_script(plan, article, pattern, tip):
    """Build the episode script from the plan and content bank data."""
    today = datetime.now(timezone.utc)

    lines = []

    # Intro
    lines.append(f"Welcome to Daily Interview English. Episode {plan['episode_id']}, {today.strftime('%B %d, %Y')}.")
    lines.append("")

    # Article tie-in
    if article and article["source"]["title"] != "No article available today":
        lines.append(f"Today's pattern was inspired by an article from {article['source']['feed']}: \"{article['source']['title']}\".")
        lines.append("")

    # Pattern section
    lines.append(f"Today's pattern: \"{pattern['phrase']}\"")
    lines.append("")
    lines.append(f"{pattern['explanation']}")
    lines.append("")
    lines.append("Here are three examples. Repeat each one out loud after me.")
    lines.append("")

    for i, example in enumerate(pattern["examples"], 1):
        lines.append(f"Example {i}. {example}")
        lines.append("")

    # Tip section
    lines.append(f"Today's interview tip: {tip['name']}.")
    lines.append("")
    lines.append(f"{tip['explanation']}")
    lines.append("")
    for segment in tip.get("segments", []):
        lines.append(f"{segment}")
        lines.append("")

    # Practice prompt
    lines.append("Your practice prompt for today.")
    lines.append("")
    lines.append(f"{plan['prompt_text']}")
    lines.append("")
    lines.append("Pause this episode now and answer out loud. I'll wait five seconds.")
    lines.append("")

    # Outro
    lines.append(f"That's it for today. The pattern again: \"{pattern['phrase']}\"")
    lines.append(f"Practice it out loud at least three times today.")
    lines.append(f"And don't forget to press the thumbs up or thumbs down button on the landing page — your feedback directly shapes tomorrow's episode.")
    lines.append("See you tomorrow.")

    return "\n".join(lines)


def run_edge_tts(script_text, output_path, rate="+0%"):
    """Generate MP3 using Microsoft edge-tts (free, no API key)."""
    # Write script to temp file
    script_path = "/tmp/episode_script.txt"
    with open(script_path, "w") as f:
        f.write(script_text)

    cmd = [
        "edge-tts",
        "--voice", VOICE,
        "--rate", rate,
        "--text", script_text,
        "--write-media", output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"edge-tts error: {result.stderr}")
        # Fallback: try with the file-based approach
        cmd_file = [
            "edge-tts",
            "--voice", VOICE,
            "--rate", rate,
            "-f", script_path,
            "--write-media", output_path
        ]
        result2 = subprocess.run(cmd_file, capture_output=True, text=True)
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
        print("  ffmpeg post-processing applied")
    else:
        print("  ffmpeg not found — skipping post-processing")


def main():
    print("=== generate.py ===")

    s3 = boto3.client("s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY
    )

    # Load inputs
    print("Loading plan.json from R2...")
    plan = load_json_from_r2(s3, "plan.json")
    if not plan:
        print("ERROR: No plan.json found in R2. Run arrange.py first.")
        sys.exit(1)
    print(f"  Episode #{plan['episode_id']}: pattern='{plan['pattern_phrase']}', tip='{plan['tip_name']}'")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    today_json_path = os.path.join(os.path.dirname(script_dir), "data", "today.json")
    article = None
    if os.path.exists(today_json_path):
        with open(today_json_path) as f:
            article = json.load(f)
        print(f"  Article: {article['source']['title'][:80]}")

    with open(os.path.join(script_dir, "content_bank.json")) as f:
        content_bank = json.load(f)

    # Look up content
    pattern = load_pattern_details(content_bank, plan["pattern_id"])
    tip = load_tip_details(content_bank, plan["tip_id"])
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
    print("✓")


if __name__ == "__main__":
    main()
