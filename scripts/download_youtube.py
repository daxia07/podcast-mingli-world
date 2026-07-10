#!/usr/bin/env python3
"""download_youtube.py — Download curated YouTube mock interview audio.

Uses yt-dlp to download, ffmpeg to extract audio and post-process.
Downloads are saved to data/youtube/ directory.
"""

import os, sys, subprocess, shutil
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
YOUTUBE_DIR = os.path.join(DATA_DIR, "youtube")

YOUTUBE_VIDEOS = [
    {
        "id": 49, "theme": "yt-exponent-payment",
        "title": "Exponent: Design a Payment System",
        "url": "https://www.youtube.com/watch?v=WI8y-5PDBQM",
        "playlist_id": "sd-youtube",
    },
    {
        "id": 50, "theme": "yt-exponent-instagram",
        "title": "Exponent: Design Instagram",
        "url": "https://www.youtube.com/watch?v=VJxfZ3jMeps",
        "playlist_id": "sd-youtube",
    },
    {
        "id": 51, "theme": "yt-jordan-chat",
        "title": "Jordan: Design a Chat System",
        "url": "https://www.youtube.com/watch?v=B7w0wIN4mRQ",
        "playlist_id": "sd-youtube",
    },
    {
        "id": 52, "theme": "yt-exponent-url-shortener",
        "title": "Exponent: Design a URL Shortener",
        "url": "https://www.youtube.com/watch?v=4v6dWQO8vCE",
        "playlist_id": "sd-youtube",
    },
    {
        "id": 53, "theme": "yt-gaurav-sd-prep",
        "title": "Gaurav Sen: System Design Interview Prep",
        "url": "https://www.youtube.com/watch?v=mFM0O8QN3A8",
        "playlist_id": "sd-youtube",
    },
]


def check_dependencies():
    missing = []
    if not shutil.which("yt-dlp"):
        missing.append("yt-dlp (pip install yt-dlp)")
    if not shutil.which("ffmpeg"):
        missing.append("ffmpeg (brew install ffmpeg)")
    if missing:
        print(f"ERROR: Missing dependencies: {', '.join(missing)}")
        sys.exit(1)


def download_and_extract(video_config):
    """Download YouTube video and extract audio as MP3."""
    os.makedirs(YOUTUBE_DIR, exist_ok=True)

    mp3_path = os.path.join(DATA_DIR, f"yt-{video_config['theme']}.mp3")

    if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 100000:
        print(f"  SKIP: {mp3_path} already exists ({os.path.getsize(mp3_path)/(1024*1024):.1f} MB)")
        return mp3_path

    temp_path = os.path.join(YOUTUBE_DIR, f"{video_config['theme']}.mp3")

    print(f"  Downloading: {video_config['title']}")
    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--output", temp_path,
        "--no-playlist",
        video_config["url"],
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: yt-dlp failed: {result.stderr[:500]}")
        return None

    if not os.path.exists(temp_path):
        print(f"  ERROR: Download file not found at {temp_path}")
        return None

    # Post-process with ffmpeg (loudnorm + silence removal)
    print(f"  Post-processing with ffmpeg...")
    temp2 = temp_path + ".processed.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-i", temp_path,
        "-af", "loudnorm, silenceremove=stop_periods=-1:stop_duration=0.3:stop_threshold=-40dB",
        temp2
    ], capture_output=True)

    if os.path.exists(temp2):
        shutil.move(temp2, mp3_path)
        os.remove(temp_path)
    else:
        shutil.move(temp_path, mp3_path)

    size_mb = os.path.getsize(mp3_path) / (1024 * 1024)

    # Get duration
    dur = "~30 min"
    if shutil.which("ffprobe"):
        result = subprocess.run([
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", mp3_path
        ], capture_output=True, text=True)
        try:
            seconds = float(result.stdout.strip())
            m = int(seconds // 60)
            s = int(seconds % 60)
            dur = f"{m}:{s:02d}"
        except (ValueError, TypeError):
            pass

    print(f"  Done: {size_mb:.1f} MB, {dur}")

    return mp3_path


def main():
    print("=== download_youtube.py ===")
    check_dependencies()

    theme = sys.argv[1] if len(sys.argv) > 1 else None
    videos = YOUTUBE_VIDEOS
    if theme:
        videos = [v for v in videos if v["theme"] == theme]
        if not videos:
            print(f"ERROR: Unknown theme '{theme}'")
            sys.exit(1)

    results = []
    for video in videos:
        print(f"\n--- #{video['id']}: {video['title']} ---")
        mp3_path = download_and_extract(video)
        if mp3_path:
            results.append({
                "id": video["id"],
                "theme": video["theme"],
                "title": video["title"],
                "playlist_id": video["playlist_id"],
                "mp3_path": mp3_path,
                "file_size_bytes": os.path.getsize(mp3_path),
            })

    print(f"\nDone — {len(results)} YouTube audio files downloaded")


if __name__ == "__main__":
    main()
