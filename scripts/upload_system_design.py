#!/usr/bin/env python3
"""Upload system-design learning materials as podcast episodes, grouped in a playlist."""

import json, os, sys
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from r2_utils import upload, get_json, upload_json, upload_bytes

BASE_URL = os.environ.get("BASE_URL", "https://podcast-landing-868.pages.dev")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "system-design")

EPISODES = [
    {
        "file": "se704-system-design-interviews.mp3",
        "title": "System Design Interviews — The Complete Framework",
        "description": "Sriram Panyam (ex-Google, ex-LinkedIn) breaks down the system design interview: 5-phase approach, 25 canonical problems, what interviewers look for at each level, and the key mindset shift from buzzword-driven to requirement-driven design. The single best SDI resource.",
        "concept": "scalability",
        "source": "SE Radio #704",
        "source_url": "https://se-radio.net/2026/01/se-radio-704-sriram-panyam-on-system-design-interviews/",
        "order": 1,
    },
    {
        "file": "se720-eventsourcing.mp3",
        "title": "Event Sourcing & CQRS — Architecture Deep Dive",
        "description": "Martin Dilger (author of Understanding Event Sourcing) explains event stores, projections, CQRS, event versioning, and why Kafka is NOT an event store. Practical adoption strategy: 2-day modeling workshop + 1-day build.",
        "concept": "cqrs-event-sourcing",
        "source": "SE Radio #720",
        "source_url": "https://se-radio.net/2026/05/se-radio-720-martin-dilger-on-understanding-eventsourcing/",
        "order": 2,
    },
    {
        "file": "se700-waiting-rooms-high-traffic.mp3",
        "title": "Rate Limiting & High-Traffic Systems — Real Incident Walkthrough",
        "description": "Mojtaba Sarooghi (Queue-it) on handling flash traffic: 100K to 100M requests in one minute, cold-start failures, DynamoDB at 200K TPS, rate limiting algorithms, and bot detection (98% of traffic is bots during ticket drops).",
        "concept": "rate-limiting",
        "source": "SE Radio #700",
        "source_url": "https://se-radio.net/2025/12/se-radio-700-mojtaba-sarooghi-on-waiting-rooms-for-high-traffic-events/",
        "order": 3,
    },
    {
        "file": "se654-event-driven-message-queues.mp3",
        "title": "Message Queues & Event-Driven Architecture — Patterns & Tradeoffs",
        "description": "Chris Patterson (MassTransit creator) on message brokers vs event streaming, sagas vs routing slips, transactional outbox pattern, dead-letter queues. Transport-agnostic architectural patterns for distributed systems.",
        "concept": "message-queues",
        "source": "SE Radio #654",
        "source_url": "https://se-radio.net/2025/02/se-radio-654-chris-patterson-on-masstransit-and-event-driven-systems/",
        "order": 4,
    },
    {
        "file": "bytebytego-consistent-hashing.mp3",
        "title": "Consistent Hashing Explained (ByteByteGo)",
        "description": "Visual explainer on consistent hashing — how distributed systems assign keys to nodes and minimize redistribution when nodes are added or removed. Core concept for sharding and distributed caches.",
        "concept": "consistent-hashing",
        "source": "ByteByteGo YouTube",
        "source_url": "https://www.youtube.com/watch?v=UF9Iqmg94tk",
        "order": 5,
    },
    {
        "file": "bytebytego-cap-theorem.mp3",
        "title": "CAP Theorem Simplified (ByteByteGo)",
        "description": "Why distributed systems must choose between Consistency, Availability, and Partition Tolerance. Clear explanation with real-world database examples (CP vs AP systems).",
        "concept": "cap-theorem",
        "source": "ByteByteGo YouTube",
        "source_url": "https://www.youtube.com/watch?v=BHqjEjzAicA",
        "order": 6,
    },
    {
        "file": "bytebytego-rate-limiter.mp3",
        "title": "Rate Limiter Design — Token Bucket & Leaky Bucket (ByteByteGo)",
        "description": "Token bucket, leaky bucket, fixed window, sliding window — the four rate limiting algorithms explained. How to scale rate limiters in a distributed system.",
        "concept": "rate-limiting",
        "source": "ByteByteGo YouTube",
        "source_url": "https://www.youtube.com/watch?v=YXkOdWBwqaA",
        "order": 7,
    },
    {
        "file": "bytebytego-url-shortener.mp3",
        "title": "How a URL Shortener Works — System Design Walkthrough (ByteByteGo)",
        "description": "End-to-end system design for a URL shortener: hash functions, base62 encoding, database schema, caching strategy, and scaling to millions of URLs.",
        "concept": "scalability",
        "source": "ByteByteGo YouTube",
        "source_url": "https://www.youtube.com/watch?v=HHUi8F_qAXM",
        "order": 8,
    },
    {
        "file": "bytebytego-api-gateway.mp3",
        "title": "API Gateway Explained (ByteByteGo)",
        "description": "What an API gateway does: authentication, rate limiting, request routing, protocol translation, and service discovery. How it fits into a microservices architecture.",
        "concept": "api-gateway",
        "source": "ByteByteGo YouTube",
        "source_url": "https://www.youtube.com/watch?v=6ULyxuHKxg8",
        "order": 9,
    },
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

    for ep in sorted(manifest.get("episodes", []), key=lambda e: e["id"], reverse=True):
        item = SubElement(channel, "item")
        SubElement(item, "title").text = ep["title"]
        desc = ep.get("description", "")
        SubElement(item, "description").text = desc[:4000]
        SubElement(item, "itunes:summary").text = desc[:4000]
        enc = SubElement(item, "enclosure")
        enc.set("url", ep["file_url"])
        enc.set("length", str(ep.get("file_size_bytes", 0)))
        enc.set("type", "audio/mpeg")
        SubElement(item, "guid").text = ep["file_url"]
        SubElement(item, "pubDate").text = f"{ep['date']}T06:00:00+10:00"
        dur = ep.get("duration", "5:00")
        SubElement(item, "duration").text = dur

    raw = tostring(rss, encoding="unicode")
    dom = minidom.parseString(raw)
    return dom.toprettyxml(indent="  ")


def main():
    print("=== Uploading System Design Learning Materials ===\n")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    manifest = get_json("manifest.json") or {"episodes": []}

    # Add playlist support to manifest if not present
    if "playlists" not in manifest:
        manifest["playlists"] = {}

    existing_ids = {ep["id"] for ep in manifest["episodes"]}
    next_id = max(existing_ids) + 1 if existing_ids else 1

    uploaded = []
    for ep_meta in EPISODES:
        filepath = os.path.join(DATA_DIR, ep_meta["file"])
        if not os.path.exists(filepath):
            print(f"  SKIP: {ep_meta['file']} not found")
            continue

        file_size = os.path.getsize(filepath)
        # Use a date-offset key to avoid collisions (one per episode)
        episode_date = f"2026-07-{8 + ep_meta['order']:02d}"
        mp3_key = f"episodes/system-design/{ep_meta['file']}"

        print(f"Uploading: {ep_meta['title'][:70]}...")
        upload(mp3_key, filepath)

        episode_entry = {
            "id": next_id,
            "date": episode_date,
            "title": ep_meta["title"],
            "description": ep_meta["description"],
            "duration": "60:00" if "se" in ep_meta["file"] else "10:00",
            "file_size_bytes": file_size,
            "file_url": f"{BASE_URL}/{mp3_key}",
            "pattern": ep_meta["concept"],
            "tip": ep_meta["source"],
            "pattern_id": ep_meta["concept"],
            "tip_id": "system-design-playlist",
            "playlist": "system-design",
            "order": ep_meta["order"],
        }

        if next_id in existing_ids:
            for i, ep in enumerate(manifest["episodes"]):
                if ep["id"] == next_id:
                    manifest["episodes"][i] = episode_entry
                    break
        else:
            manifest["episodes"].append(episode_entry)
            existing_ids.add(next_id)

        uploaded.append(episode_entry)
        print(f"  → Episode #{next_id}: {episode_entry['title']}")
        next_id += 1

    # Update playlist metadata
    manifest["playlists"]["system-design"] = {
        "title": "System Design — Spaced Repetition Learning",
        "description": "Curated audio materials for system design interview prep. SE Radio deep dives + ByteByteGo visual explainers. Mapped to SM-2 spaced repetition concepts in the generic-tutor.",
        "episode_ids": [ep["id"] for ep in uploaded],
        "concepts": list(set(ep["concept"] for ep in EPISODES if ep["concept"])),
    }

    print(f"\nUploading manifest ({len(manifest['episodes'])} total episodes)...")
    upload_json("manifest.json", manifest)

    print("Generating RSS...")
    rss_xml = generate_rss(manifest)
    upload_bytes("rss.xml", rss_xml.encode())

    # Save locally
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    for filename, data in [
        ("manifest.json", json.dumps(manifest, indent=2).encode()),
        ("rss.xml", rss_xml.encode()),
    ]:
        with open(os.path.join(project_dir, filename), "wb") as f:
            f.write(data)

    print(f"\n✓ Uploaded {len(uploaded)} episodes to 'System Design' playlist")
    print(f"  Playlist URL: {BASE_URL}")
    for ep in uploaded:
        print(f"  #{ep['id']}: {ep['title']}")


if __name__ == "__main__":
    main()
