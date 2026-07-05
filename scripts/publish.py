#!/usr/bin/env python3
"""publish.py — Upload episode MP3 to R2, update manifest.json, regenerate rss.xml.

Runs at 5 AM AEST (19:00 UTC) via GitHub Actions, after generate.py.
"""

import json, os, sys
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

import boto3

R2_ENDPOINT = os.environ["R2_ENDPOINT"]
R2_ACCESS_KEY = os.environ["R2_ACCESS_KEY"]
R2_SECRET_KEY = os.environ["R2_SECRET_KEY"]
BUCKET = "podcast-mingli-world"
BASE_URL = "https://podcast.mingli.world"


def load_json_from_r2(s3, key):
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=key)
        return json.loads(obj["Body"].read().decode())
    except s3.exceptions.NoSuchKey:
        return None


def save_json_to_r2(s3, key, data):
    s3.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(data, indent=2), ContentType="application/json")


def upload_file_to_r2(s3, local_path, r2_key, content_type):
    with open(local_path, "rb") as f:
        s3.put_object(Bucket=BUCKET, Key=r2_key, Body=f.read(), ContentType=content_type)
    print(f"  Uploaded: {r2_key}")


def generate_rss(manifest):
    """Generate podcast RSS 2.0 XML from manifest.json."""
    rss = Element("rss", version="2.0")
    rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
    rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")

    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = manifest.get("title", "Daily Interview English")
    SubElement(channel, "link").text = BASE_URL
    SubElement(channel, "description").text = manifest.get("description", "Daily 5-minute episodes: English patterns, interview frameworks, and speaking practice for tech professionals.")
    SubElement(channel, "language").text = manifest.get("language", "en")

    itunes_image = SubElement(channel, "itunes:image")
    itunes_image.set("href", manifest.get("artwork_url", f"{BASE_URL}/artwork.jpg"))

    SubElement(channel, "itunes:category", text="Education")
    SubElement(channel, "itunes:explicit").text = "false"
    SubElement(channel, "itunes:author").text = manifest.get("author", "Ming Li")

    for ep in sorted(manifest.get("episodes", []), key=lambda e: e["id"], reverse=True):
        item = SubElement(channel, "item")
        SubElement(item, "title").text = ep["title"]
        SubElement(item, "description").text = ep.get("description", "")
        SubElement(item, "itunes:summary").text = ep.get("description", "")

        enclosure = SubElement(item, "enclosure")
        enclosure.set("url", ep["file_url"])
        enclosure.set("length", str(ep.get("file_size_bytes", 0)))
        enclosure.set("type", "audio/mpeg")

        SubElement(item, "guid").text = ep["file_url"]
        SubElement(item, "pubDate").text = f"{ep['date']}T00:00:00+10:00"
        SubElement(item, "duration").text = ep.get("duration", "5:00")

    # Pretty-print XML
    raw = tostring(rss, encoding="unicode")
    dom = minidom.parseString(raw)
    return dom.toprettyxml(indent="  ")


def main():
    print("=== publish.py ===")

    s3 = boto3.client("s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY
    )

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), "data")
    mp3_path = os.path.join(data_dir, "episode.mp3")
    script_path = os.path.join(data_dir, "script.txt")

    if not os.path.exists(mp3_path):
        print("ERROR: No episode.mp3 found. Run generate.py first.")
        sys.exit(1)

    # Load plan for episode metadata
    plan = load_json_from_r2(s3, "plan.json")
    if not plan:
        print("ERROR: No plan.json found.")
        sys.exit(1)

    episode_date = plan.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    episode_id = plan["episode_id"]
    file_size = os.path.getsize(mp3_path)
    file_url = f"{BASE_URL}/episodes/{episode_date}.mp3"

    # Load script for description
    description = ""
    if os.path.exists(script_path):
        with open(script_path) as f:
            script_text = f.read()
            # Use first 500 chars as description
            description = script_text[:500].replace("\n", " ").strip()

    # Build episode entry
    episode_entry = {
        "id": episode_id,
        "date": episode_date,
        "title": f"{plan['pattern_phrase']} — {plan['tip_name']}",
        "description": description,
        "duration": "5:00",
        "file_size_bytes": file_size,
        "file_url": file_url,
        "pattern": plan["pattern_phrase"],
        "tip": plan["tip_name"],
        "pattern_id": plan.get("pattern_id"),
        "tip_id": plan.get("tip_id")
    }

    # Upload MP3
    print(f"Uploading episode #{episode_id}...")
    r2_mp3_key = f"episodes/{episode_date}.mp3"
    upload_file_to_r2(s3, mp3_path, r2_mp3_key, "audio/mpeg")

    # Update manifest
    print("Updating manifest.json...")
    manifest = load_json_from_r2(s3, "manifest.json")
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

    # Check if episode already exists (idempotent)
    existing_ids = {ep["id"] for ep in manifest["episodes"]}
    if episode_id in existing_ids:
        # Update existing entry
        for i, ep in enumerate(manifest["episodes"]):
            if ep["id"] == episode_id:
                manifest["episodes"][i] = episode_entry
                break
    else:
        manifest["episodes"].append(episode_entry)

    save_json_to_r2(s3, "manifest.json", manifest)
    print(f"  Total episodes: {len(manifest['episodes'])}")

    # Regenerate RSS
    print("Regenerating rss.xml...")
    rss_xml = generate_rss(manifest)
    s3.put_object(Bucket=BUCKET, Key="rss.xml", Body=rss_xml, ContentType="application/rss+xml")
    print("  rss.xml updated")

    # Save manifest.json locally for git push (triggers Pages deploy)
    local_manifest_path = os.path.join(os.path.dirname(script_dir), "manifest.json")
    with open(local_manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  manifest.json saved locally for git push")

    print("✓")


if __name__ == "__main__":
    main()
