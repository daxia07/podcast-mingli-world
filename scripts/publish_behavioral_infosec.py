#!/usr/bin/env python3
"""publish_behavioral_infosec.py — Upload behavioral + infosec episodes to R2, update manifest + RSS.

Uploads both TTS-generated episodes and YouTube-extracted audio.
"""

import argparse, json, os, sys
from datetime import datetime, timezone
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from r2_utils import get_json, upload, upload_bytes, upload_json
from tts import get_duration_str

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
MANIFEST_LOCAL = os.path.join(SCRIPT_DIR, "manifest.json")
BASE_URL = os.environ.get("BASE_URL", "https://podcast.mingli.world")
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

BEHAVIORAL_EPISODES = [
    {"id": 450, "theme": "behavioral-why-leaving-weakness", "title": "Behavioral: Why Leaving + Biggest Weakness", "playlist": "behavioral-interview", "source": "tts"},
    {"id": 451, "theme": "behavioral-deadline-feedback", "title": "Behavioral: Tight Deadlines + Critical Feedback", "playlist": "behavioral-interview", "source": "tts"},
    {"id": 452, "theme": "behavioral-unpopular-difficult", "title": "Behavioral: Unpopular Decisions + Difficult People", "playlist": "behavioral-interview", "source": "tts"},
    {"id": 453, "theme": "behavioral-ambiguity-standards", "title": "Behavioral: Navigating Ambiguity + Driving Standards", "playlist": "behavioral-interview", "source": "tts"},
    {"id": 454, "theme": "behavioral-quality-incident", "title": "Behavioral: Quality vs Speed + Production Incidents", "playlist": "behavioral-interview", "source": "tts"},
]

INFOSEC_EPISODES = [
    {"id": 460, "theme": "infosec-owasp-auth", "title": "Infosec: OWASP Top 10 + Authentication Patterns", "playlist": "infosec-interview", "source": "tts"},
    {"id": 461, "theme": "infosec-encryption-threatmodel", "title": "Infosec: Encryption + Threat Modeling", "playlist": "infosec-interview", "source": "tts"},
    {"id": 462, "theme": "infosec-incident-secrets", "title": "Infosec: Incident Response + Secrets Management", "playlist": "infosec-interview", "source": "tts"},
    {"id": 463, "theme": "infosec-supplychain-compliance", "title": "Infosec: Supply Chain Security + Compliance", "playlist": "infosec-interview", "source": "tts"},
    {"id": 464, "theme": "infosec-zero-trust-api", "title": "Infosec: Zero Trust Architecture + API Security", "playlist": "infosec-interview", "source": "tts"},
]

YOUTUBE_EPISODES = [
    {"id": 88, "theme": "yt-behavioral-star-answers", "title": "Behavioral Interview — STAR Technique Answers (YouTube)", "playlist": "behavioral-youtube", "source": "youtube"},
    {"id": 89, "theme": "yt-behavioral-top10-questions", "title": "Top 10 Behavioral SE Interview Questions (YouTube)", "playlist": "behavioral-youtube", "source": "youtube"},
    {"id": 90, "theme": "yt-behavioral-cracking", "title": "Cracking the Behavioral Interview for Developers (YouTube)", "playlist": "behavioral-youtube", "source": "youtube"},
    {"id": 91, "theme": "yt-behavioral-meta-amazon", "title": "Behavioral Interview — Ex-Meta & Amazon Managers (YouTube)", "playlist": "behavioral-youtube", "source": "youtube"},
    {"id": 92, "theme": "yt-behavioral-uncomplicated", "title": "Answering Behavioral Questions — Shockingly Uncomplicated (YouTube)", "playlist": "behavioral-youtube", "source": "youtube"},
    {"id": 93, "theme": "yt-infosec-owasp-2025", "title": "OWASP Top 10 2025 — Complete Guide (YouTube)", "playlist": "infosec-youtube", "source": "youtube"},
    {"id": 94, "theme": "yt-infosec-zero-trust-4min", "title": "Zero Trust Explained in 4 Minutes (YouTube)", "playlist": "infosec-youtube", "source": "youtube"},
    {"id": 95, "theme": "yt-infosec-owasp-explained", "title": "OWASP Top 10 Web App Security Risks Explained (YouTube)", "playlist": "infosec-youtube", "source": "youtube"},
    {"id": 96, "theme": "yt-infosec-zero-trust-nist", "title": "Zero Trust Architecture — NIST 800-207 (YouTube)", "playlist": "infosec-youtube", "source": "youtube"},
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
    SubElement(channel, "itunes:author").text = manifest.get("author", "Mingli")
    if manifest.get("artwork_url"):
        SubElement(channel, "itunes:image", href=manifest["artwork_url"])

    for ep in sorted(manifest.get("episodes", []), key=lambda e: e.get("id", 0), reverse=True):
        item = SubElement(channel, "item")
        SubElement(item, "title").text = ep.get("title", "")
        SubElement(item, "description").text = ep.get("description", "")
        SubElement(item, "guid", isPermaLink="false").text = str(ep.get("id", ""))
        SubElement(item, "pubDate").text = ep.get("pub_date", TODAY)
        audio = ep.get("audio_url") or ep.get("file_url") or ""
        SubElement(item, "enclosure", url=audio, type="audio/mpeg", length=str(ep.get("file_size_bytes", 0)))
        if ep.get("duration"):
            SubElement(item, "itunes:duration").text = ep["duration"]

    rough = tostring(rss, encoding="unicode")
    return minidom.parseString(rough).toprettyxml(indent="  ").encode("utf-8")


def publish_episodes(episodes):
    print("=== publish_behavioral_infosec.py ===")

    try:
        manifest = get_json("manifest.json")
    except Exception:
        manifest = None
    if not manifest:
        with open(MANIFEST_LOCAL, encoding="utf-8") as f:
            manifest = json.load(f)

    by_id = {e["id"]: e for e in manifest.get("episodes", [])}
    published = []

    for ep_cfg in episodes:
        mp3_path = os.path.join(DATA_DIR, f"{ep_cfg['theme']}.mp3")
        if not os.path.exists(mp3_path):
            alt = os.path.join(DATA_DIR, f"yt-{ep_cfg['theme']}.mp3")
            if os.path.exists(alt):
                mp3_path = alt
            else:
                print(f"  SKIP missing: {mp3_path}")
                continue

        fname = f"{ep_cfg['theme']}.mp3"
        remote_key = f"episodes/{fname}"
        print(f"  Upload {fname}...")
        upload(remote_key, mp3_path)

        size = os.path.getsize(mp3_path)
        dur = get_duration_str(mp3_path)

        desc = ""
        if ep_cfg["source"] == "youtube":
            desc = f"YouTube-extracted expert interview audio."
        else:
            desc = f"TTS-generated practice episode for behavioral interview preparation."

        entry = {
            "id": ep_cfg["id"],
            "title": ep_cfg["title"],
            "description": desc,
            "theme": ep_cfg["theme"],
            "filename": fname,
            "file_url": f"{BASE_URL}/episodes/{fname}",
            "audio_url": f"{BASE_URL}/episodes/{fname}",
            "duration": dur,
            "file_size_bytes": size,
            "date": TODAY,
            "pub_date": TODAY,
            "playlist": ep_cfg["playlist"],
            "source": ep_cfg["source"],
        }
        by_id[ep_cfg["id"]] = entry
        published.append(ep_cfg["id"])

    manifest["episodes"] = sorted(by_id.values(), key=lambda e: e.get("id", 0), reverse=True)

    playlists = manifest.get("playlists", {})
    if isinstance(playlists, list):
        playlists = {p["id"]: p for p in playlists if "id" in p}

    playlist_configs = {
        "behavioral-interview": {"title": "Behavioral Interview Practice", "icon": "🎯", "description": "TTS practice episodes for behavioral interview questions"},
        "infosec-interview": {"title": "Info Security Interview Prep", "icon": "🔒", "description": "TTS practice episodes for infosec interview questions"},
        "behavioral-youtube": {"title": "Behavioral Interview — Expert Audio", "icon": "🎬", "description": "YouTube-extracted expert behavioral interview advice"},
        "infosec-youtube": {"title": "InfoSec — Expert Audio", "icon": "🎬", "description": "YouTube-extracted infosec and security interview content"},
    }

    for pl_id, pl_cfg in playlist_configs.items():
        ep_ids = [ep["id"] for ep in episodes if ep.get("playlist") == pl_id and ep["id"] in by_id]
        playlists[pl_id] = {
            "title": pl_cfg["title"],
            "description": pl_cfg["description"],
            "episode_ids": ep_ids,
            "icon": pl_cfg["icon"],
        }

    manifest["playlists"] = playlists

    print(f"  Uploading manifest ({len(manifest['episodes'])} episodes)...")
    upload_json("manifest.json", manifest)
    with open(MANIFEST_LOCAL, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    rss = generate_rss(manifest)
    upload_bytes("rss.xml", rss)
    with open(os.path.join(PROJECT_DIR, "rss.xml"), "wb") as f:
        f.write(rss)

    print(f"  Published {len(published)} episodes: {published}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--what", default="all", choices=["behavioral", "infosec", "youtube", "behavioral-youtube", "infosec-youtube", "all"])
    args = ap.parse_args()

    episodes = []
    if args.what in ("behavioral", "all"):
        episodes += BEHAVIORAL_EPISODES
    if args.what in ("infosec", "all"):
        episodes += INFOSEC_EPISODES
    if args.what in ("youtube", "behavioral-youtube", "infosec-youtube", "all"):
        if args.what in ("youtube", "all", "behavioral-youtube"):
            episodes += [e for e in YOUTUBE_EPISODES if e["playlist"] == "behavioral-youtube"]
        if args.what in ("youtube", "all", "infosec-youtube"):
            episodes += [e for e in YOUTUBE_EPISODES if e["playlist"] == "infosec-youtube"]

    if not episodes:
        print("No episodes matched filter")
        sys.exit(1)

    publish_episodes(episodes)


if __name__ == "__main__":
    main()
