#!/usr/bin/env python3
"""Generate + publish Coding Prep playlist from drafts/coding-prep/*.txt

Usage:
  python3 generate_coding_prep.py --all
  python3 generate_coding_prep.py --all --publish
  python3 generate_coding_prep.py --id 300 --publish
"""


from __future__ import annotations

# Frozen — see scripts/_legacy_guard.py. New episodes: build_episode.py
from _legacy_guard import warn_legacy
warn_legacy(__file__)

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from r2_utils import get_json, upload, upload_bytes, upload_json
from tts import get_duration_str, synthesize


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
DRAFT_DIR = os.path.join(SCRIPT_DIR, "drafts", "coding-prep")
BASE_URL = os.environ.get("BASE_URL", "https://podcast.mingli.world")
MANIFEST_LOCAL = os.path.join(SCRIPT_DIR, "manifest.json")
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

EPISODES = [
    {
        "id": 300,
        "key": "ep00-ritual",
        "script": "ep00-airwallex-coding-ritual.txt",
        "title": "Coding Prep 0: Airwallex Screen Ritual",
        "subtitle": "Clarify → naive → optimize → edges → complexity. No AI in live rounds.",
    },
    {
        "id": 301,
        "key": "ep01-two-sum",
        "script": "ep01-two-sum-think-aloud.txt",
        "title": "Coding Prep 1: Two Sum Think-Aloud",
        "subtitle": "Map complement, cold open, speed recap. Pair with app deep drill.",
    },
    {
        "id": 302,
        "key": "ep02-hashmap-family",
        "script": "ep02-hashmap-family.txt",
        "title": "Coding Prep 2: HashMap Family",
        "subtitle": "Duplicate · Anagrams · Top K. Seen-before muscle memory.",
    },
    {
        "id": 303,
        "key": "ep03-longest-substring",
        "script": "ep03-longest-substring.txt",
        "title": "Coding Prep 3: Longest Unique Substring",
        "subtitle": "Sliding window expand/shrink. Pair with deep drill.",
    },
    {
        "id": 304,
        "key": "ep04-two-pointers",
        "script": "ep04-two-pointers.txt",
        "title": "Coding Prep 4: Two Pointers",
        "subtitle": "Container water + 3Sum moves. Move the shorter line.",
    },
    {
        "id": 305,
        "key": "ep05-lru",
        "script": "ep05-lru-cache.txt",
        "title": "Coding Prep 5: LRU Cache Design",
        "subtitle": "Map + doubly linked list for O(1) get/put.",
    },
    {
        "id": 306,
        "key": "ep06-islands-bfs",
        "script": "ep06-islands-bfs.txt",
        "title": "Coding Prep 6: Islands + Level Order",
        "subtitle": "Flood fill + BFS queue batches. Trees & graphs muscle.",
    },
    {
        "id": 307,
        "key": "ep07-mock-screen",
        "script": "ep07-mock-screen.txt",
        "title": "Coding Prep 7: Mock Screen Dry Run",
        "subtitle": "60-minute narration script. Brackets + merge intervals. Test week recap.",
    },
    {
        "id": 308,
        "key": "ep08-stack",
        "script": "ep08-valid-parentheses-stack.txt",
        "title": "Coding Prep 8: Valid Parentheses + Stack",
        "subtitle": "Week 2 · Nesting muscle · Min stack note. Pair with Stack & Queue.",
    },
    {
        "id": 309,
        "key": "ep09-intervals",
        "script": "ep09-merge-intervals.txt",
        "title": "Coding Prep 9: Merge Intervals",
        "subtitle": "Sort by start, sweep merge. Calendar/range muscle.",
    },
    {
        "id": 310,
        "key": "ep10-linked-list",
        "script": "ep10-linked-list.txt",
        "title": "Coding Prep 10: Linked List Reverse + Cycle",
        "subtitle": "Three-pointer reverse · Floyd fast/slow.",
    },
    {
        "id": 311,
        "key": "ep11-binary-search",
        "script": "ep11-binary-search.txt",
        "title": "Coding Prep 11: Binary Search + Rotated",
        "subtitle": "Closed interval · sorted half on rotated array.",
    },
    {
        "id": 312,
        "key": "ep12-dp",
        "script": "ep12-dp-fundamentals.txt",
        "title": "Coding Prep 12: DP Fundamentals",
        "subtitle": "Define the cell · stairs · robber · coin change.",
    },
    {
        "id": 313,
        "key": "ep13-tree-dfs",
        "script": "ep13-tree-dfs.txt",
        "title": "Coding Prep 13: Tree DFS",
        "subtitle": "Depth · invert · same tree. Complements BFS week 1.",
    },
    {
        "id": 314,
        "key": "ep14-mock-week2",
        "script": "ep14-mock-screen-week2.txt",
        "title": "Coding Prep 14: Mock Screen Week 2",
        "subtitle": "Min stack · cycle · stairs · full pattern checklist.",
    },
]


def load_script(filename: str) -> str:
    path = os.path.join(DRAFT_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def generate_one(ep: dict, force: bool = False) -> dict | None:
    body = load_script(ep["script"])
    words = len(body.split())
    print(f"  {ep['key']}: {words} words")

    os.makedirs(DATA_DIR, exist_ok=True)
    mp3_path = os.path.join(DATA_DIR, f"coding-prep-{ep['key']}.mp3")
    txt_path = os.path.join(DATA_DIR, f"coding-prep-{ep['key']}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(body)

    if (not force) and os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 1000:
        print(f"  MP3 exists, reusing: {mp3_path}")
    else:
        print("  TTS synthesizing…")
        synthesize(body, mp3_path, voice="narrator", preprocess=True, rate="-5%")

    duration = get_duration_str(mp3_path)
    size = os.path.getsize(mp3_path)
    print(f"  → {size / 1024 / 1024:.1f} MB, {duration}")
    return {
        **ep,
        "mp3_path": mp3_path,
        "txt_path": txt_path,
        "file_size_bytes": size,
        "duration": duration,
        "words": words,
        "theme": f"coding-prep-{ep['key']}",
        "description": body[:480].replace("\n", " ").strip() + "…",
    }


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

    episodes = sorted(manifest.get("episodes", []), key=lambda e: e.get("id", 0), reverse=True)
    for ep in episodes:
        item = SubElement(channel, "item")
        SubElement(item, "title").text = ep.get("title", "")
        SubElement(item, "description").text = ep.get("description") or ep.get("subtitle", "")
        SubElement(item, "guid", isPermaLink="false").text = str(ep.get("id", ""))
        SubElement(item, "pubDate").text = ep.get("pub_date", TODAY)
        audio = ep.get("audio_url") or ep.get("file_url") or f"{BASE_URL}/episodes/{ep.get('filename', '')}"
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
    pretty = minidom.parseString(rough).toprettyxml(indent="  ")
    return pretty.encode("utf-8")


def publish(results: list[dict]) -> None:
    print("=== publish coding-prep to R2 + manifest ===")
    try:
        manifest = get_json("manifest.json")
    except Exception:
        manifest = None
    if not manifest:
        with open(MANIFEST_LOCAL, encoding="utf-8") as f:
            manifest = json.load(f)

    by_id = {e["id"]: e for e in manifest.get("episodes", [])}

    for r in results:
        fname = f"coding-prep-{r['key']}.mp3"
        remote = f"episodes/{fname}"
        print(f"  upload {r['mp3_path']} → {remote}")
        upload(remote, r["mp3_path"])

        entry = {
            "id": r["id"],
            "title": r["title"],
            "subtitle": r["subtitle"],
            "description": r.get("description") or r["subtitle"],
            "theme": r["theme"],
            "filename": fname,
            "file_url": f"{BASE_URL}/episodes/{fname}",
            "audio_url": f"{BASE_URL}/episodes/{fname}",
            "duration": r["duration"],
            "file_size_bytes": r["file_size_bytes"],
            "date": TODAY,
            "pub_date": TODAY,
            "playlist": "coding-prep",
            "playlist_ids": ["coding-prep"],
            "tip_id": "coding-prep-playlist",
            "words": r.get("words"),
        }
        by_id[r["id"]] = entry

    # Newest first so site hero + lists surface coding-prep immediately
    manifest["episodes"] = sorted(by_id.values(), key=lambda e: e.get("id", 0), reverse=True)

    playlists = manifest.get("playlists") or {}
    if isinstance(playlists, list):
        playlists = {p["id"]: p for p in playlists if "id" in p}

    # Keep full series order even if this publish only regenerates a subset
    all_cp_ids = [e["id"] for e in EPISODES]
    existing_cp = []
    if "coding-prep" in playlists and isinstance(playlists["coding-prep"], dict):
        existing_cp = [
            i
            for i in playlists["coding-prep"].get("episode_ids", [])
            if isinstance(i, int) and 300 <= i < 400
        ]
    for i in all_cp_ids:
        if i not in existing_cp:
            existing_cp.append(i)
    # Prefer canonical series order
    id_order = {e["id"]: idx for idx, e in enumerate(EPISODES)}
    existing_cp = sorted(existing_cp, key=lambda x: id_order.get(x, x))

    playlists["coding-prep"] = {
        "title": "Coding Prep — Airwallex Muscle Memory",
        "description": (
            "Think-aloud coding interviews: clarify → naive → optimize → edges → complexity. "
            "Cold open, dead-end recovery, speed recap. Pair with tutor deep drills + Coding YouTube."
        ),
        "episode_ids": existing_cp,
        "icon": "💻",
    }
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

    print("  manifest + rss updated")
    print(f"  playlist: coding-prep ({len(EPISODES)} episodes)")
    for r in results:
        print(f"  → {BASE_URL}/episodes/coding-prep-{r['key']}.mp3")
    print(f"  site: {BASE_URL}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--id", type=int)
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--force-tts", action="store_true")
    args = ap.parse_args()

    configs = EPISODES
    if args.id:
        configs = [e for e in EPISODES if e["id"] == args.id]
        if not configs:
            print("Unknown id", args.id)
            sys.exit(1)
    elif not args.all and not args.publish:
        print("Use --all and/or --id N and/or --publish")
        sys.exit(1)

    results = []
    if args.all or args.id:
        for ep in configs:
            r = generate_one(ep, force=args.force_tts)
            if r:
                results.append(r)

    if args.publish:
        if not results:
            # rebuild metadata from existing mp3s
            for ep in configs:
                r = generate_one(ep, force=False)
                if r:
                    results.append(r)
        publish(results)


if __name__ == "__main__":
    main()
