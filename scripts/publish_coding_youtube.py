#!/usr/bin/env python3
"""Download (optional) + publish Coding YouTube audio-first playlist.

Usage:
  python3 publish_coding_youtube.py --download          # yt-dlp only
  python3 publish_coding_youtube.py --download --publish
  python3 publish_coding_youtube.py --publish           # upload existing mp3s
  python3 publish_coding_youtube.py --id 401 --publish
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from r2_utils import get_json, upload, upload_bytes, upload_json
from tts import get_duration_str

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
YOUTUBE_DIR = os.path.join(DATA_DIR, "youtube")
PLAYLIST_PATH = os.path.join(SCRIPT_DIR, "coding_youtube_playlist.json")
BASE_URL = os.environ.get("BASE_URL", "https://podcast.mingli.world")
MANIFEST_LOCAL = os.path.join(SCRIPT_DIR, "manifest.json")
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def load_playlist() -> dict:
    with open(PLAYLIST_PATH, encoding="utf-8") as f:
        return json.load(f)


def check_deps() -> None:
    missing = []
    if not shutil.which("yt-dlp"):
        missing.append("yt-dlp")
    if not shutil.which("ffmpeg"):
        missing.append("ffmpeg")
    if missing:
        print(f"ERROR: missing {', '.join(missing)}")
        sys.exit(1)


def mp3_path_for(theme: str) -> str:
    return os.path.join(DATA_DIR, f"{theme}.mp3")


def download_one(video: dict, force: bool = False) -> str | None:
    theme = video["theme"]
    out = mp3_path_for(theme)
    if (not force) and os.path.exists(out) and os.path.getsize(out) > 100_000:
        print(f"  SKIP exists: {out} ({os.path.getsize(out) / 1e6:.1f} MB)")
        return out

    os.makedirs(YOUTUBE_DIR, exist_ok=True)
    temp = os.path.join(YOUTUBE_DIR, f"{theme}.%(ext)s")
    print(f"  Downloading: {video['title']}")
    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "--output",
        temp,
        "--no-playlist",
        video["url"],
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERROR yt-dlp: {r.stderr[:400]}")
        return None

    # yt-dlp may write theme.mp3
    found = os.path.join(YOUTUBE_DIR, f"{theme}.mp3")
    if not os.path.exists(found):
        # fallback: any new mp3 in youtube dir matching theme prefix
        for name in os.listdir(YOUTUBE_DIR):
            if name.startswith(theme) and name.endswith(".mp3"):
                found = os.path.join(YOUTUBE_DIR, name)
                break
    if not os.path.exists(found):
        print(f"  ERROR: no mp3 for {theme}")
        return None

    processed = found + ".norm.mp3"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            found,
            "-af",
            "loudnorm,silenceremove=stop_periods=-1:stop_duration=0.35:stop_threshold=-40dB",
            processed,
        ],
        capture_output=True,
    )
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(processed):
        shutil.move(processed, out)
        try:
            os.remove(found)
        except OSError:
            pass
    else:
        shutil.move(found, out)

    print(f"  → {out} ({os.path.getsize(out) / 1e6:.1f} MB)")
    return out


def generate_rss(manifest: dict) -> bytes:
    rss = Element("rss", version="2.0")
    rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
    rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = manifest.get("title", "Daily Interview English")
    SubElement(channel, "link").text = BASE_URL
    SubElement(channel, "description").text = manifest.get("description", "")
    SubElement(channel, "language").text = "en"
    SubElement(channel, "itunes:author").text = manifest.get("author", "Mingli")
    if manifest.get("artwork_url"):
        SubElement(channel, "itunes:image", href=manifest["artwork_url"])

    for ep in sorted(manifest.get("episodes", []), key=lambda e: e.get("id", 0), reverse=True):
        item = SubElement(channel, "item")
        SubElement(item, "title").text = ep.get("title", "")
        SubElement(item, "description").text = ep.get("description") or ep.get("subtitle", "")
        SubElement(item, "guid", isPermaLink="false").text = str(ep.get("id", ""))
        SubElement(item, "pubDate").text = ep.get("pub_date", TODAY)
        audio = ep.get("audio_url") or ep.get("file_url") or ""
        SubElement(
            item,
            "enclosure",
            url=audio,
            type="audio/mpeg",
            length=str(ep.get("file_size_bytes", 0)),
        )
        if ep.get("duration"):
            SubElement(item, "itunes:duration").text = ep["duration"]

    rough = tostring(rss, encoding="unicode")
    return minidom.parseString(rough).toprettyxml(indent="  ").encode("utf-8")


def publish(videos: list[dict], pl_meta: dict) -> None:
    print("=== publish coding-youtube → R2 + manifest ===")
    try:
        manifest = get_json("manifest.json")
    except Exception:
        manifest = None
    if not manifest:
        with open(MANIFEST_LOCAL, encoding="utf-8") as f:
            manifest = json.load(f)

    by_id = {e["id"]: e for e in manifest.get("episodes", [])}
    published_ids: list[int] = []

    for v in videos:
        path = mp3_path_for(v["theme"])
        if not os.path.exists(path):
            print(f"  SKIP missing mp3: {path}")
            continue
        fname = f"{v['theme']}.mp3"
        remote = f"episodes/{fname}"
        print(f"  upload {path} → {remote}")
        upload(remote, path)
        size = os.path.getsize(path)
        try:
            duration = get_duration_str(path)
        except Exception:
            duration = ""
        desc = (
            f"{v.get('subtitle', '')}. "
            f"Audio-fit: {v.get('audio_fit', 'good')}. "
            f"Pair: Coding Prep {v.get('pair_coding_prep', '')} + app {v.get('pair_app', '')}. "
            f"Source: {v['url']}"
        )
        entry = {
            "id": v["id"],
            "title": v["title"],
            "subtitle": v.get("subtitle", ""),
            "description": desc,
            "theme": v["theme"],
            "filename": fname,
            "file_url": f"{BASE_URL}/episodes/{fname}",
            "audio_url": f"{BASE_URL}/episodes/{fname}",
            "duration": duration,
            "file_size_bytes": size,
            "date": TODAY,
            "pub_date": TODAY,
            "playlist": pl_meta["playlist_id"],
            "playlist_ids": [pl_meta["playlist_id"], "coding-prep"],
            "source_url": v["url"],
            "day": v.get("day"),
            "audio_fit": v.get("audio_fit"),
        }
        by_id[v["id"]] = entry
        published_ids.append(v["id"])

    # keep any previously published coding-youtube ids in playlist order
    all_ids = [v["id"] for v in pl_meta["videos"] if v["id"] in by_id]
    manifest["episodes"] = sorted(by_id.values(), key=lambda e: e.get("id", 0), reverse=True)

    playlists = manifest.get("playlists") or {}
    if isinstance(playlists, list):
        playlists = {p["id"]: p for p in playlists if "id" in p}

    playlists[pl_meta["playlist_id"]] = {
        "title": pl_meta["title"],
        "description": pl_meta["description"],
        "episode_ids": all_ids,
        "icon": pl_meta.get("icon", "🎧"),
    }
    # ensure coding-prep still lists native eps only (don't swallow YT into it)
    if "coding-prep" in playlists:
        cp = playlists["coding-prep"]
        cp_ids = [i for i in cp.get("episode_ids", []) if i < 400]
        playlists["coding-prep"]["episode_ids"] = cp_ids

    manifest["playlists"] = playlists
    upload_json("manifest.json", manifest)
    with open(MANIFEST_LOCAL, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    rss = generate_rss(manifest)
    upload_bytes("rss.xml", rss)
    with open(os.path.join(SCRIPT_DIR, "rss.xml"), "wb") as f:
        f.write(rss)
    with open(os.path.join(PROJECT_DIR, "rss.xml"), "wb") as f:
        f.write(rss)

    print(f"  published {len(published_ids)} videos into playlist coding-youtube")
    print(f"  episode_ids: {all_ids}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--id", type=int)
    ap.add_argument("--day", type=int, help="Only videos for schedule day 1–6")
    args = ap.parse_args()

    if not args.download and not args.publish:
        print("Use --download and/or --publish")
        sys.exit(1)

    pl = load_playlist()
    videos = pl["videos"]
    if args.id:
        videos = [v for v in videos if v["id"] == args.id]
    if args.day is not None:
        videos = [v for v in videos if v.get("day") == args.day]
    if not videos:
        print("No videos matched filters")
        sys.exit(1)

    if args.download:
        check_deps()
        print(f"=== download {len(videos)} coding-youtube clips ===")
        for v in videos:
            print(f"\n--- #{v['id']}: {v['title']} ---")
            download_one(v, force=args.force)

    if args.publish:
        publish(videos, pl)


if __name__ == "__main__":
    main()
