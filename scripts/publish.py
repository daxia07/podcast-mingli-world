#!/usr/bin/env python3
"""publish.py — Upload episode MP3 to R2, update manifest.json, regenerate rss.xml."""

import json, os, sys
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from r2_utils import upload, get_json, upload_json, upload_bytes

BASE_URL = os.environ.get("BASE_URL", "https://podcast-landing-868.pages.dev")


def generate_rss(manifest):
    """Generate podcast RSS 2.0 XML from manifest.json."""
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


def main():
    print("=== publish.py ===")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), "data")
    mp3_path = os.path.join(data_dir, "episode.mp3")
    script_path = os.path.join(data_dir, "script.txt")

    if not os.path.exists(mp3_path):
        print("ERROR: No episode.mp3 found. Run generate.py first.")
        sys.exit(1)

    episode_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    mp3_key = f"episodes/{episode_date}.mp3"
    file_size = os.path.getsize(mp3_path)

    # Read script for description
    description = ""
    if os.path.exists(script_path):
        with open(script_path) as f:
            description = f.read()[:500].replace("\n", " ").strip()

    # Load existing manifest
    manifest = get_json("manifest.json")
    if not manifest:
        manifest = {
            "title": "Daily Interview English",
            "description": "Daily 5-minute episodes: English patterns, interview frameworks, and speaking practice for tech professionals.",
            "author": "Ming Li",
            "language": "en",
            "artwork_url": f"{BASE_URL}/artwork.jpg",
            "categories": ["Education", "Language Learning"],
            "episodes": []
        }

    existing_ids = {ep["id"] for ep in manifest["episodes"]}
    next_id = max(existing_ids) + 1 if existing_ids else 1

    # Read plan for metadata — local file first (selector.py output), then R2
    local_plan_path = os.path.join(data_dir, "plan.json")
    plan = {}
    if os.path.exists(local_plan_path):
        with open(local_plan_path) as f:
            plan = json.load(f)
    if not plan:
        plan = get_json("plan.json") or {}

    # Build title — support both selector.py format (topic + concepts) and
    # legacy format (pattern_phrase + tip_name)
    if "topic" in plan and "primary_concept_title" in plan:
        topic_label = plan["topic"].replace("-", " ").title()
        concept_title = plan["primary_concept_title"]
        title = f"{topic_label}: {concept_title}"
    else:
        title = f"{plan.get('pattern_phrase', 'Episode')} — {plan.get('tip_name', 'Tip')}"

    episode_entry = {
        "id": next_id,
        "date": episode_date,
        "title": title,
        "description": description,
        "duration": "5:00",
        "file_size_bytes": file_size,
        "file_url": f"{BASE_URL}/episodes/{episode_date}.mp3",
        "pattern": plan.get("pattern_phrase", plan.get("primary_concept_title", "")),
        "tip": plan.get("tip_name", ""),
        "pattern_id": plan.get("pattern_id", plan.get("primary_concept_id")),
        "tip_id": plan.get("tip_id", plan.get("topic", ""))
    }

    # Upload MP3
    print(f"Uploading episode #{next_id} MP3...")
    upload(mp3_key, mp3_path)
    print(f"  {mp3_key} uploaded")

    # Update manifest
    if next_id in existing_ids:
        for i, ep in enumerate(manifest["episodes"]):
            if ep["id"] == next_id:
                manifest["episodes"][i] = episode_entry
                break
    else:
        manifest["episodes"].append(episode_entry)

    print(f"Uploading manifest.json ({len(manifest['episodes'])} episodes)...")
    upload_json("manifest.json", manifest)

    # Generate and upload RSS
    print("Generating RSS...")
    rss_xml = generate_rss(manifest)
    upload_bytes("rss.xml", rss_xml.encode())

    # Save manifest locally for git push
    local_manifest_path = os.path.join(os.path.dirname(script_dir), "manifest.json")
    with open(local_manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Done — Episode #{next_id} published")


if __name__ == "__main__":
    main()
