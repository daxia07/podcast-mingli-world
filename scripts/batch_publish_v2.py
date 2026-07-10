#!/usr/bin/env python3
"""batch_publish_v2.py — Upload all new think-aloud, estimation, and mock interview episodes to R2.
Update manifest with new playlists, regenerate RSS.
"""

import json, os, sys
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from r2_utils import upload, get_json, upload_json, upload_bytes
from tts import get_duration_str

BASE_URL = "https://podcast.mingli.world"
BUCKET = "podcast-mingli-world"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

NEW_PLAYLISTS = [
    {
        "id": "compilations",
        "name": "Pattern Compilations",
        "episode_ids": [19, 20, 21, 22]
    },
    {
        "id": "self-intro",
        "name": "Self-Introduction",
        "episode_ids": [17]
    },
    {
        "id": "prepared-qa",
        "name": "Prepared Q&A",
        "episode_ids": [18]
    },
    {
        "id": "sd-think-aloud",
        "name": "SD: Think-Aloud",
        "episode_ids": [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]
    },
    {
        "id": "sd-estimation",
        "name": "SD: Estimation Practice",
        "episode_ids": [44, 45]
    },
    {
        "id": "sd-mock-interviews",
        "name": "SD: Mock Interviews",
        "episode_ids": [46, 47, 48]
    },
    {
        "id": "sd-deep-dive",
        "name": "SD: Deep Dive Listening",
        "episode_ids": [35, 36, 37, 38, 39, 40, 41, 42, 43]
    },
    {
        "id": "interview-patterns",
        "name": "Interview Patterns (Archive)",
        "episode_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    },
]

SD_EPISODES_V2 = [
    {"id": 23, "theme": "sd-fundamentals", "title": "SD Fundamentals Think-Aloud", "subtitle": "CAP, ACID vs BASE, Consensus", "playlist_id": "sd-think-aloud"},
    {"id": 24, "theme": "sd-infrastructure", "title": "Infrastructure Think-Aloud", "subtitle": "Load Balancing, Caching, CDN, Message Queues", "playlist_id": "sd-think-aloud"},
    {"id": 25, "theme": "sd-data", "title": "Data Architecture Think-Aloud", "subtitle": "Sharding, Replication, Partitioning", "playlist_id": "sd-think-aloud"},
    {"id": 26, "theme": "sd-api-microservices", "title": "API & Microservices Think-Aloud", "subtitle": "API Design, Microservices Architecture", "playlist_id": "sd-think-aloud"},
    {"id": 27, "theme": "sd-reliability", "title": "Reliability Think-Aloud", "subtitle": "Idempotency, Rate Limiting, Observability", "playlist_id": "sd-think-aloud"},
    {"id": 28, "theme": "sd-classic-1", "title": "URL Shortener Think-Aloud", "subtitle": "Full walkthrough with estimation", "playlist_id": "sd-think-aloud"},
    {"id": 29, "theme": "sd-classic-2", "title": "Chat System Think-Aloud", "subtitle": "Real-time messaging, WebSocket vs polling", "playlist_id": "sd-think-aloud"},
    {"id": 30, "theme": "sd-classic-3", "title": "News Feed Think-Aloud", "subtitle": "Fan-out, caching, ranking", "playlist_id": "sd-think-aloud"},
    {"id": 31, "theme": "sd-fintech-payment", "title": "Payment System Think-Aloud", "subtitle": "Fintech: idempotency, double-charge, reconciliation", "playlist_id": "sd-think-aloud"},
    {"id": 32, "theme": "sd-fintech-ledger", "title": "Ledger System Think-Aloud", "subtitle": "Fintech: double-entry, append-only, ACID, audit", "playlist_id": "sd-think-aloud"},
    {"id": 33, "theme": "sd-fintech-trading", "title": "Trading Platform Think-Aloud", "subtitle": "Fintech: order matching, real-time feeds, FIFO", "playlist_id": "sd-think-aloud"},
    {"id": 34, "theme": "sd-fintech-fraud", "title": "Fraud Detection Think-Aloud", "subtitle": "Fintech: stream processing, feature stores, rules vs ML", "playlist_id": "sd-think-aloud"},
]

EST_EPISODES = [
    {"id": 44, "theme": "estimation-1", "title": "Estimation Practice I", "subtitle": "Twitter QPS, Google storage, WhatsApp bandwidth", "playlist_id": "sd-estimation"},
    {"id": 45, "theme": "estimation-2", "title": "Estimation Practice II", "subtitle": "Payment TPS, Netflix CDN, Uber location writes", "playlist_id": "sd-estimation"},
]

MOCK_EPISODES = [
    {"id": 46, "theme": "mock-payment-system", "title": "Mock Interview: Payment System", "subtitle": "Full mock system design interview", "playlist_id": "sd-mock-interviews"},
    {"id": 47, "theme": "mock-url-shortener", "title": "Mock Interview: URL Shortener", "subtitle": "Full mock system design interview", "playlist_id": "sd-mock-interviews"},
    {"id": 48, "theme": "mock-news-feed", "title": "Mock Interview: News Feed", "subtitle": "Full mock system design interview", "playlist_id": "sd-mock-interviews"},
]


def generate_rss(manifest):
    rss = Element("rss", version="2.0")
    rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
    rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")

    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = manifest.get("title", "Daily Interview English")
    SubElement(channel, "link").text = BASE_URL
    SubElement(channel, "description").text = manifest.get("description", "")
    SubElement(channel, "language").text = "en"

    img = SubElement(channel, "itunes:image")
    img.set("href", f"{BASE_URL}/artwork.jpg")
    SubElement(channel, "itunes:category", text="Education")
    SubElement(channel, "itunes:explicit").text = "false"
    SubElement(channel, "itunes:author").text = manifest.get("author", "Daily Interview English")

    active_eps = [ep for ep in manifest.get("episodes", []) if not ep.get("archived")]
    for ep in sorted(active_eps, key=lambda e: e["id"], reverse=True):
        item = SubElement(channel, "item")
        SubElement(item, "title").text = ep["title"]
        SubElement(item, "description").text = ep.get("description", "")
        SubElement(item, "itunes:summary").text = ep.get("description", "")
        enc = SubElement(item, "enclosure")
        enc.set("url", ep["file_url"])
        enc.set("length", str(ep.get("file_size_bytes", 0)))
        enc.set("type", "audio/mpeg")
        SubElement(item, "guid").text = ep["file_url"]
        SubElement(item, "pubDate").text = f"{ep['date']}T06:00:00+10:00"
        SubElement(item, "duration").text = ep.get("duration", "5:00")

    raw = tostring(rss, encoding="unicode")
    dom = minidom.parseString(raw)
    return dom.toprettyxml(indent="  ")


def get_description_from_script(script_path):
    if not os.path.exists(script_path):
        return ""
    with open(script_path) as f:
        return f.read()[:500].replace("\n", " ").strip()


def main():
    print("=== batch_publish_v2.py ===")
    print(f"Date: {TODAY}")

    manifest = get_json("manifest.json")
    if not manifest:
        print("ERROR: Could not load manifest.json from R2")
        sys.exit(1)

    existing_ids = {ep["id"] for ep in manifest["episodes"]}
    print(f"Current episodes: {len(manifest['episodes'])}, next ID would be: {max(existing_ids) + 1 if existing_ids else 1}")

    new_episodes = []
    prefix_map = {"sd": "sd", "est": "est", "mock": "mock"}

    all_eps = SD_EPISODES_V2 + EST_EPISODES + MOCK_EPISODES

    for ep_config in all_eps:
        ep_id = ep_config["id"]
        theme = ep_config["theme"]

        # Determine file prefix
        if theme.startswith("mock-"):
            prefix = "mock"
        elif theme.startswith("estimation-"):
            prefix = "est"
        else:
            prefix = "sd"

        mp3_path = os.path.join(DATA_DIR, f"{prefix}-{theme}.mp3")
        script_path = os.path.join(DATA_DIR, f"{prefix}-{theme}.txt")

        if not os.path.exists(mp3_path):
            print(f"  SKIP #{ep_id}: {mp3_path} not found")
            continue

        r2_key = f"episodes/{TODAY}-{theme}.mp3"
        file_url = f"{BASE_URL}/{r2_key}"
        file_size = os.path.getsize(mp3_path)
        duration = get_duration_str(mp3_path)
        description = get_description_from_script(script_path)

        print(f"  Uploading #{ep_id}: {ep_config['title']} ({duration}, {file_size/(1024*1024):.1f}MB)")
        upload(r2_key, mp3_path)

        ep_entry = {
            "id": ep_id,
            "date": TODAY,
            "title": f"{ep_config['title']} — {ep_config['subtitle']}",
            "description": description,
            "duration": duration,
            "file_size_bytes": file_size,
            "file_url": file_url,
            "pattern": "Think-Aloud" if prefix == "sd" else ("Estimation" if prefix == "est" else "Mock Interview"),
            "tip": "RESHADED Framework" if prefix == "sd" else ("Back-of-Envelope" if prefix == "est" else "Interview Practice"),
            "playlist_id": ep_config.get("playlist_id", ""),
        }
        new_episodes.append(ep_entry)

    print(f"\nUploaded {len(new_episodes)} new episodes")

    for ep in manifest["episodes"]:
        if ep["id"] <= 16:
            ep["archived"] = True
            ep["playlist_id"] = "interview-patterns"

    for ep in new_episodes:
        existing = [i for i, e in enumerate(manifest["episodes"]) if e["id"] == ep["id"]]
        if existing:
            manifest["episodes"][existing[0]] = ep
        else:
            manifest["episodes"].append(ep)

    manifest["episodes"].sort(key=lambda e: e["id"])

    manifest["playlists"] = NEW_PLAYLISTS

    total = len(manifest["episodes"])
    active = len([e for e in manifest["episodes"] if not e.get("archived")])
    print(f"Manifest: {total} total episodes, {active} active")

    print("Uploading manifest.json...")
    upload_json("manifest.json", manifest)

    print("Generating RSS...")
    rss_xml = generate_rss(manifest)
    upload_bytes("rss.xml", rss_xml.encode())

    local_manifest_path = os.path.join(PROJECT_DIR, "manifest.json")
    with open(local_manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Saved local manifest to {local_manifest_path}")

    print(f"\nDone — Published {len(new_episodes)} new episodes")


if __name__ == "__main__":
    main()
