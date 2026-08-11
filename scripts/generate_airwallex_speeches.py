#!/usr/bin/env python3
"""Generate + publish Airwallex 10-min agenda speech episodes from interview-speeches/*.md

Usage:
  python3 generate_airwallex_speeches.py --all
  python3 generate_airwallex_speeches.py --id 200
  python3 generate_airwallex_speeches.py --publish
  python3 generate_airwallex_speeches.py --all --publish
"""


from __future__ import annotations

# Frozen — see scripts/_legacy_guard.py. New episodes: build_episode.py
from _legacy_guard import warn_legacy
warn_legacy(__file__)

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from r2_utils import get_json, upload, upload_bytes, upload_json
from tts import get_duration_str, synthesize


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
SPEECH_DIR = os.path.join(
    os.path.expanduser("~"),
    "projects/job-hunter/applications/airwallex/interview-speeches",
)
BASE_URL = os.environ.get("BASE_URL", "https://podcast.mingli.world")
MANIFEST_LOCAL = os.path.join(SCRIPT_DIR, "manifest.json")
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# theme_key -> meta
EPISODES = [
    {"id": 200, "key": "q4w", "title": "Awx Speech: Distributed Wallet (Q4W)", "subtitle": "10-min agenda speech — Raft, SM, dedup, CQRS"},
    {"id": 201, "key": "q4l", "title": "Awx Speech: Double-Entry Ledger (Q4L)", "subtitle": "10-min agenda speech — journal SoT, outbox"},
    {"id": 202, "key": "q1", "title": "Awx Speech: Cross-Border Payment (Q1)", "subtitle": "10-min agenda speech — state machine, unknown timeout"},
    {"id": 203, "key": "q2", "title": "Awx Speech: Payment Gateway API (Q2)", "subtitle": "10-min agenda speech — idempotent accept, bulkheads"},
    {"id": 204, "key": "q9", "title": "Awx Speech: Webhook Delivery (Q9)", "subtitle": "10-min agenda speech — outbox, backoff, SSRF"},
    {"id": 205, "key": "q10", "title": "Awx Speech: AgentOS Assistant (Q10)", "subtitle": "10-min agenda speech — untrusted planner, policy tiers"},
    {"id": 206, "key": "q7", "title": "Awx Speech: Reconciliation (Q7)", "subtitle": "10-min agenda speech — match, case, repair journals"},
    {"id": 207, "key": "q5", "title": "Awx Speech: Fraud AML Sanctions (Q5)", "subtitle": "10-min agenda speech — hard then soft, fail closed"},
    {"id": 208, "key": "q3", "title": "Awx Speech: FX Quotes (Q3)", "subtitle": "10-min agenda speech — indicative vs executable"},
    {"id": 209, "key": "q12", "title": "Awx Speech: Multi-Region (Q12)", "subtitle": "10-min agenda speech — home cell, fence, HA vs C"},
    {"id": 210, "key": "q11", "title": "Awx Speech: KYC Onboarding (Q11)", "subtitle": "10-min agenda speech — case workflow, AI≠truth"},
    {"id": 211, "key": "q8", "title": "Awx Speech: Bulk Payouts (Q8)", "subtitle": "10-min agenda speech — item idempotency, rate limits"},
    {"id": 212, "key": "q6", "title": "Awx Speech: Card Authorization (Q6)", "subtitle": "10-min agenda speech — hot path hold, dedupe"},
    {"id": 213, "key": "job_scheduler", "title": "Awx Speech: Distributed Job Scheduler", "subtitle": "10-min agenda speech — claim, lease, workers"},
]


def extract_speech_text(md_path: str) -> str:
    text = open(md_path, encoding="utf-8").read()
    m = re.search(r"## Speech\n\n(.*?)(\n## |\Z)", text, re.S)
    body = m.group(1).strip() if m else text
    # strip markdown bold/backticks for TTS
    body = body.replace("**", "").replace("`", "")
    return body


def generate_one(ep: dict) -> dict | None:
    md_path = os.path.join(SPEECH_DIR, f"speech-{ep['key']}.md")
    if not os.path.exists(md_path):
        print(f"  SKIP missing {md_path}")
        return None
    body = extract_speech_text(md_path)
    words = len(body.split())
    print(f"  {ep['key']}: {words} words")

    os.makedirs(DATA_DIR, exist_ok=True)
    mp3_path = os.path.join(DATA_DIR, f"awx-speech-{ep['key']}.mp3")
    txt_path = os.path.join(DATA_DIR, f"awx-speech-{ep['key']}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(body)

    if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 1000:
        print(f"  MP3 exists, reusing: {mp3_path}")
    else:
        print(f"  TTS synthesizing…")
        synthesize(body, mp3_path, voice="narrator", preprocess=True)

    duration = get_duration_str(mp3_path)
    size = os.path.getsize(mp3_path)
    print(f"  → {size/1024/1024:.1f} MB, {duration}")
    return {
        **ep,
        "mp3_path": mp3_path,
        "txt_path": txt_path,
        "file_size_bytes": size,
        "duration": duration,
        "words": words,
        "theme": f"awx-speech-{ep['key']}",
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
        audio = ep.get("audio_url") or f"{BASE_URL}/episodes/{ep.get('filename', '')}"
        SubElement(item, "enclosure", url=audio, type="audio/mpeg", length=str(ep.get("file_size_bytes", 0)))
        if ep.get("duration"):
            SubElement(item, "itunes:duration").text = ep["duration"]

    rough = tostring(rss, encoding="unicode")
    pretty = minidom.parseString(rough).toprettyxml(indent="  ")
    return pretty.encode("utf-8")


def publish(results: list[dict]) -> None:
    print("=== publish to R2 + manifest ===")
    try:
        manifest = get_json("manifest.json")
    except Exception:
        with open(MANIFEST_LOCAL, encoding="utf-8") as f:
            manifest = json.load(f)

    by_id = {e["id"]: e for e in manifest.get("episodes", [])}

    for r in results:
        fname = f"awx-speech-{r['key']}.mp3"
        remote = f"episodes/{fname}"
        print(f"  upload {r['mp3_path']} → {remote}")
        upload(remote, r["mp3_path"])

        entry = {
            "id": r["id"],
            "title": r["title"],
            "subtitle": r["subtitle"],
            "description": (
                f"Agenda-aligned ~10 minute monologue for Airwallex system design prep. "
                f"{r['subtitle']}. Source: applications/airwallex/interview-speeches/speech-{r['key']}.md"
            ),
            "theme": r["theme"],
            "filename": fname,
            "audio_url": f"{BASE_URL}/episodes/{fname}",
            "duration": r["duration"],
            "file_size_bytes": r["file_size_bytes"],
            "pub_date": TODAY,
            "playlist_ids": ["awx-10min-speeches"],
            "words": r.get("words"),
        }
        by_id[r["id"]] = entry

    manifest["episodes"] = sorted(by_id.values(), key=lambda e: e["id"])

    playlists = manifest.get("playlists") or {}
    if isinstance(playlists, list):
        # legacy list form — convert not expected
        playlists = {p["id"]: p for p in playlists if "id" in p}

    playlists["awx-10min-speeches"] = {
        "title": "Airwallex SD — 10-Min Agenda Speeches",
        "description": (
            "Compact monologues for each Airwallex prep problem (Q4W–Q12 bank + job scheduler). "
            "Structured for the design interview agenda: requirements first, simple→iterate, "
            "trade-offs, DS theory, HA vs consistency. Pair with Whimsical practice."
        ),
        "episode_ids": [e["id"] for e in EPISODES],
        "icon": "🎯",
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
    print(f"  playlist: awx-10min-speeches ({len(EPISODES)} episodes)")
    print(f"  site: {BASE_URL}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--id", type=int, help="single episode id")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--skip-existing-mp3", action="store_true", default=True)
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
        print("=== generate_airwallex_speeches ===")
        for ep in configs:
            print(f"\n[{ep['id']}] {ep['title']}")
            r = generate_one(ep)
            if r:
                results.append(r)
        # save local index of generated
        idx_path = os.path.join(DATA_DIR, "awx-speech-index.json")
        with open(idx_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nIndex: {idx_path}")

    if args.publish:
        if not results:
            # load from existing mp3s
            for ep in EPISODES:
                mp3 = os.path.join(DATA_DIR, f"awx-speech-{ep['key']}.mp3")
                if os.path.exists(mp3) and os.path.getsize(mp3) > 1000:
                    results.append({
                        **ep,
                        "mp3_path": mp3,
                        "duration": get_duration_str(mp3),
                        "file_size_bytes": os.path.getsize(mp3),
                        "words": 0,
                        "theme": f"awx-speech-{ep['key']}",
                    })
        if not results:
            print("Nothing to publish — generate first")
            sys.exit(1)
        publish(results)

    print("DONE")


if __name__ == "__main__":
    main()
