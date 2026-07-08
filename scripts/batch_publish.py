#!/usr/bin/env python3
"""batch_publish.py — Upload all new episodes to R2, update manifest with playlists, regenerate RSS."""

import json, os, sys
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from r2_utils import upload, get_json, upload_json, upload_bytes

BASE_URL = "https://podcast.mingli.world"
BUCKET = "podcast-mingli-world"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

PLAYLISTS = [
    {
        "id": "interview-patterns",
        "name": "Interview Patterns",
        "icon": "comment",
        "episode_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    },
    {
        "id": "compilations",
        "name": "Pattern Compilations",
        "icon": "target",
        "episode_ids": [19, 20, 21, 22]
    },
    {
        "id": "self-intro",
        "name": "Self-Introduction",
        "icon": "mic",
        "episode_ids": [17]
    },
    {
        "id": "prepared-qa",
        "name": "Prepared Q&A",
        "icon": "question",
        "episode_ids": [18]
    },
    {
        "id": "sd-concepts",
        "name": "SD: Core Concepts",
        "icon": "compass",
        "episode_ids": [23, 24, 25, 26, 27]
    },
    {
        "id": "sd-cases",
        "name": "SD: Case Studies",
        "icon": "building",
        "episode_ids": [28, 29, 30, 31, 32]
    },
    {
        "id": "sd-patterns",
        "name": "SD: Architecture Patterns",
        "icon": "link",
        "episode_ids": [33, 34]
    }
]

COMP_EPISODES = [
    {"id": 19, "theme": "comp-opinions", "title": "Stating Opinions & Perspectives", "subtitle": "Opinion Patterns + Verbal Signposting", "pattern": "The way I see it is... / That said... / I'd argue that...", "tip": "4-Second Pause + Verbal Signposting", "playlist_id": "compilations", "pattern_ids": ["the-way-i-see-it", "that-said", "id-argue-that"], "tip_ids": ["four-second-pause", "verbal-signposting"]},
    {"id": 20, "theme": "comp-self-desc", "title": "Self-Description & Career Narrative", "subtitle": "Self-Description Patterns + STAR-LA", "pattern": "What clicked for me was... / Over time I became the... / What I'm really looking for is...", "tip": "STAR-LA + Structure-First", "playlist_id": "compilations", "pattern_ids": ["what-clicked-for-me", "over-time-i-became", "what-im-looking-for"], "tip_ids": ["star-la", "structure-first"]},
    {"id": 21, "theme": "comp-emphasis", "title": "Emphasis & Elaboration", "subtitle": "Impact Patterns + Hook-Flow-Landing", "pattern": "What I'd really highlight is... / To put a finer point on it... / To give you a concrete example... / This resulted in...", "tip": "Hook-Flow-Landing + So What Test", "playlist_id": "compilations", "pattern_ids": ["what-id-highlight", "to-put-a-finer-point-on-it", "to-give-you-a-concrete-example", "this-resulted-in"], "tip_ids": ["hook-flow-landing", "so-what-test"]},
    {"id": 22, "theme": "comp-bridging", "title": "Thinking Time & Bridging Gaps", "subtitle": "Bridging Patterns + Three Ways to Say I Don't Know", "pattern": "That's a great question. Let me think... / I haven't worked directly with that. What I can tell you is...", "tip": "Three Ways to Say I Don't Know + Pause-and-Anchor", "playlist_id": "compilations", "pattern_ids": ["thats-a-great-question", "i-havent-worked-with-that"], "tip_ids": ["i-dont-know-bridging", "pause-and-anchor", "acknowledge-reframe"]}
]

SD_EPISODES = [
    {"id": 23, "theme": "sd-fundamentals", "title": "System Design Fundamentals", "subtitle": "CAP, ACID vs BASE, Consensus", "playlist_id": "sd-concepts", "sd_items": ["cap-theorem", "acid-vs-base", "consensus"]},
    {"id": 24, "theme": "sd-infrastructure", "title": "Infrastructure Essentials", "subtitle": "Load Balancing, Caching, CDN, Message Queues", "playlist_id": "sd-concepts", "sd_items": ["load-balancing", "caching", "cdn", "message-queues"]},
    {"id": 25, "theme": "sd-data", "title": "Data Architecture", "subtitle": "Sharding, Replication, Partitioning", "playlist_id": "sd-concepts", "sd_items": ["database-sharding", "replication", "data-partitioning"]},
    {"id": 26, "theme": "sd-api-microservices", "title": "API & Microservices", "subtitle": "API Design, Microservices Architecture", "playlist_id": "sd-concepts", "sd_items": ["api-design", "microservices"]},
    {"id": 27, "theme": "sd-reliability", "title": "Reliability Engineering", "subtitle": "Idempotency, Rate Limiting, Observability", "playlist_id": "sd-concepts", "sd_items": ["idempotency", "rate-limiting", "observability"]},
    {"id": 28, "theme": "sd-classic-1", "title": "Classic System Design I", "subtitle": "URL Shortener + Chat System", "playlist_id": "sd-cases", "sd_items": ["design-url-shortener", "design-chat-system"]},
    {"id": 29, "theme": "sd-classic-2", "title": "Classic System Design II", "subtitle": "News Feed + Search Autocomplete", "playlist_id": "sd-cases", "sd_items": ["design-news-feed", "design-search-autocomplete"]},
    {"id": 30, "theme": "sd-classic-3", "title": "Classic System Design III", "subtitle": "Notification System + Web Crawler", "playlist_id": "sd-cases", "sd_items": ["design-notification-system", "design-web-crawler"]},
    {"id": 31, "theme": "sd-advanced-1", "title": "Advanced System Design I", "subtitle": "Object Storage + Key-Value Store", "playlist_id": "sd-cases", "sd_items": ["design-object-storage", "design-key-value-store"]},
    {"id": 32, "theme": "sd-advanced-2", "title": "Advanced System Design II", "subtitle": "Location Service + Video Streaming", "playlist_id": "sd-cases", "sd_items": ["design-location-service", "design-video-streaming"]},
    {"id": 33, "theme": "sd-arch-patterns-1", "title": "Architecture Patterns I", "subtitle": "Event-Driven, CQRS, Sidecar", "playlist_id": "sd-patterns", "sd_items": ["event-driven", "cqrs", "sidecar"]},
    {"id": 34, "theme": "sd-arch-patterns-2", "title": "Architecture Patterns II", "subtitle": "Circuit Breaker, Bulkhead, Saga, Strangler Fig, Backpressure", "playlist_id": "sd-patterns", "sd_items": ["circuit-breaker", "bulkhead", "saga", "strangler-fig", "backpressure"]}
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


def get_duration_str(mp3_path):
    import subprocess, shutil
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


def get_description_from_script(script_path):
    if not os.path.exists(script_path):
        return ""
    with open(script_path) as f:
        return f.read()[:500].replace("\n", " ").strip()


def main():
    print("=== batch_publish.py ===")
    print(f"Date: {TODAY}")

    manifest = get_json("manifest.json")
    if not manifest:
        print("ERROR: Could not load manifest.json from R2")
        sys.exit(1)

    existing_ids = {ep["id"] for ep in manifest["episodes"]}
    next_id = max(existing_ids) + 1 if existing_ids else 1
    print(f"Current episodes: {len(manifest['episodes'])}, next ID would be: {next_id}")

    new_episodes = []

    for comp in COMP_EPISODES:
        ep_id = comp["id"]
        theme = comp["theme"]
        mp3_path = os.path.join(DATA_DIR, f"comp-{theme}.mp3")
        script_path = os.path.join(DATA_DIR, f"comp-{theme}.txt")

        if not os.path.exists(mp3_path):
            print(f"  SKIP #{ep_id}: {mp3_path} not found")
            continue

        r2_key = f"episodes/{TODAY}-{theme}.mp3"
        file_url = f"{BASE_URL}/{r2_key}"
        file_size = os.path.getsize(mp3_path)
        duration = get_duration_str(mp3_path)
        description = get_description_from_script(script_path)

        print(f"  Uploading #{ep_id}: {comp['title']} ({duration}, {file_size/(1024*1024):.1f}MB)")
        upload(r2_key, mp3_path)

        ep_entry = {
            "id": ep_id,
            "date": TODAY,
            "title": f"{comp['title']} — {comp['subtitle']}",
            "description": description,
            "duration": duration,
            "file_size_bytes": file_size,
            "file_url": file_url,
            "pattern": comp.get("pattern", ""),
            "tip": comp.get("tip", ""),
            "playlist_id": comp.get("playlist_id", ""),
            "pattern_ids": comp.get("pattern_ids", []),
            "tip_ids": comp.get("tip_ids", [])
        }
        new_episodes.append(ep_entry)

    for sd in SD_EPISODES:
        ep_id = sd["id"]
        theme = sd["theme"]
        mp3_path = os.path.join(DATA_DIR, f"sd-{theme}.mp3")
        script_path = os.path.join(DATA_DIR, f"sd-{theme}.txt")

        if not os.path.exists(mp3_path):
            print(f"  SKIP #{ep_id}: {mp3_path} not found")
            continue

        r2_key = f"episodes/{TODAY}-{theme}.mp3"
        file_url = f"{BASE_URL}/{r2_key}"
        file_size = os.path.getsize(mp3_path)
        duration = get_duration_str(mp3_path)
        description = get_description_from_script(script_path)

        print(f"  Uploading #{ep_id}: {sd['title']} ({duration}, {file_size/(1024*1024):.1f}MB)")
        upload(r2_key, mp3_path)

        ep_entry = {
            "id": ep_id,
            "date": TODAY,
            "title": f"{sd['title']} — {sd['subtitle']}",
            "description": description,
            "duration": duration,
            "file_size_bytes": file_size,
            "file_url": file_url,
            "pattern": "System Design",
            "tip": "RESHADED Framework",
            "playlist_id": sd.get("playlist_id", ""),
            "sd_items": sd.get("sd_items", [])
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

    manifest["playlists"] = PLAYLISTS

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
