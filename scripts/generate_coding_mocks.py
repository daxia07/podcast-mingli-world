#!/usr/bin/env python3
"""Two-voice Airwallex coding mock interviews (part one, no AI).

Interviewer: AvaNeural · Candidate: AndrewNeural · Narrator: BrianNeural

Usage:
  python3 generate_coding_mocks.py --all --publish
  python3 generate_coding_mocks.py --theme coding-mock-rate-limiter --publish
"""


from __future__ import annotations

# Frozen — see scripts/_legacy_guard.py. New episodes: build_episode.py
from _legacy_guard import warn_legacy
warn_legacy(__file__)

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from coding_mocks import BUILDERS
from r2_utils import get_json, upload, upload_bytes, upload_json
from tts import concatenate_mp3, get_duration_str, synthesize


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
DRAFT_DIR = os.path.join(SCRIPT_DIR, "drafts", "coding-prep", "mocks")
MANIFEST_LOCAL = os.path.join(SCRIPT_DIR, "manifest.json")
BASE_URL = os.environ.get("BASE_URL", "https://podcast.mingli.world")
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

EPISODES = [
    {
        "id": 330,
        "theme": "coding-mock-rate-limiter",
        "key": "mock-rate-limiter",
        "title": "Coding Mock: Rate Limiter (Agent API)",
        "subtitle": "~19 min problem · two-voice · token bucket. No AI.",
    },
    {
        "id": 331,
        "theme": "coding-mock-currency-best-rate",
        "key": "mock-currency-best-rate",
        "title": "Coding Mock: Currency Best Rate",
        "subtitle": "~18 min problem · two-voice · Dijkstra −log. No AI.",
    },
    {
        "id": 332,
        "theme": "coding-mock-refund-rules",
        "key": "mock-refund-rules",
        "title": "Coding Mock: Refund Rules Engine",
        "subtitle": "~19 min problem · two-voice · rules engine. No AI.",
    },
    {
        "id": 333,
        "theme": "coding-mock-stream-topk",
        "key": "mock-stream-topk",
        "title": "Coding Mock: Stream Top-K + Moving Average",
        "subtitle": "~18 min problem · two-voice · stream window. No AI.",
    },
    {
        "id": 334,
        "theme": "coding-mock-full-hour-dual-mode",
        "key": "mock-full-hour-dual-mode",
        "title": "Coding Mock: Full Dual-Mode Hour (Intro+Problem+AI Dive)",
        "subtitle": "Dress rehearsal · pause mid-ep to code 30m AI-off · then deep dive.",
    },
    {
        "id": 335,
        "theme": "coding-mock-ai-deep-dive-part2",
        "key": "mock-ai-deep-dive-part2",
        "title": "Coding Mock: Part 2 AI Deep Dive Pilot",
        "subtitle": "Two-voice · directed prompts · verify/reject · Claude Code.",
    },
    {
        "id": 336,
        "theme": "coding-mock-stuck-recovery",
        "key": "mock-stuck-recovery",
        "title": "Coding Drill: Stuck Recovery Lines",
        "subtitle": "Short loops · fork script · bug fix · time pressure.",
    },
    {
        "id": 337,
        "theme": "coding-mock-clarify-gym",
        "key": "mock-clarify-gym",
        "title": "Coding Drill: Clarify Gym",
        "subtitle": "Restate + forking questions only · five vague prompts.",
    },
    {
        "id": 338,
        "theme": "coding-mock-intro-drills",
        "key": "mock-intro-drills",
        "title": "Coding Drill: 90s Intro Variants",
        "subtitle": "Three intros · under two minutes · no flattery.",
    },
    {
        "id": 339,
        "theme": "coding-mock-wrong-answers",
        "key": "mock-wrong-answers",
        "title": "Coding Drill: Wrong Answers Clinic",
        "subtitle": "Bad line → fix line · AI policy · FX · money · silence.",
    },
    {
        "id": 340,
        "theme": "coding-mock-lru-cache",
        "key": "mock-lru-cache",
        "title": "Coding Mock: LRU Cache (Model Responses)",
        "subtitle": "~18–20 min · two-voice · map+DLL · eviction · O(1). No AI.",
    },
    {
        "id": 341,
        "theme": "coding-mock-rpn",
        "key": "mock-rpn",
        "title": "Coding Mock: RPN Expression Evaluator",
        "subtitle": "~18–20 min · two-voice · stack · pop order · ÷0. No AI.",
    },
    {
        "id": 342,
        "theme": "coding-mock-idempotency",
        "key": "mock-idempotency",
        "title": "Coding Mock: Idempotency Key Store",
        "subtitle": "~18–20 min · two-voice · body hash · replay · mismatch. No AI.",
    },
    {
        "id": 343,
        "theme": "coding-mock-complexity-edges",
        "key": "mock-complexity-edges",
        "title": "Coding Drill: Complexity & Edges Call-Response",
        "subtitle": "Short daily · Big-O + edge lists by problem type.",
    },
    {
        "id": 344,
        "theme": "coding-mock-mono-stack",
        "key": "mock-mono-stack",
        "title": "Coding Mock: Daily Temperatures (Monotonic Stack)",
        "subtitle": "~20 min · two-voice · next warmer · LC 739 pattern. No AI.",
    },
    {
        "id": 345,
        "theme": "coding-mock-fx-anomaly",
        "key": "mock-fx-anomaly",
        "title": "Coding Mock: FX Anomaly Detector",
        "subtitle": "~20 min · two-voice · 5-min window · 10% vs average. No AI.",
    },
    {
        "id": 346,
        "theme": "coding-mock-bellman-ford",
        "key": "mock-bellman-ford",
        "title": "Coding Mock: FX Arbitrage (Bellman-Ford)",
        "subtitle": "~20 min · two-voice · −log rates · negative cycle. No AI.",
    },
    {
        "id": 347,
        "theme": "coding-mock-two-sum",
        "key": "mock-two-sum",
        "title": "Coding Mock: Two Sum (Hash Map)",
        "subtitle": "~20 min · two-voice · complement map · indices. No AI.",
    },
    {
        "id": 348,
        "theme": "coding-mock-longest-substring",
        "key": "mock-longest-substring",
        "title": "Coding Mock: Longest Substring No Repeat",
        "subtitle": "~20 min · two-voice · sliding window · LC3. No AI.",
    },
    {
        "id": 349,
        "theme": "coding-mock-container-water",
        "key": "mock-container-water",
        "title": "Coding Mock: Container With Most Water",
        "subtitle": "~20 min · two-voice · two pointers · move shorter. No AI.",
    },
    {
        "id": 350,
        "theme": "coding-mock-merge-intervals",
        "key": "mock-merge-intervals",
        "title": "Coding Mock: Merge Intervals",
        "subtitle": "~20 min · two-voice · sort + scan · touch merges. No AI.",
    },
    {
        "id": 351,
        "theme": "coding-mock-num-islands",
        "key": "mock-num-islands",
        "title": "Coding Mock: Number of Islands",
        "subtitle": "~20 min · two-voice · grid DFS flood fill. No AI.",
    },
    {
        "id": 352,
        "theme": "coding-mock-coin-change",
        "key": "mock-coin-change",
        "title": "Coding Mock: Coin Change (Min Coins DP)",
        "subtitle": "~20 min · two-voice · unbounded knapsack · not greedy. No AI.",
    },
]


def dialogue_to_text(dialogue: list[tuple[str, str]]) -> str:
    lines = []
    for speaker, text in dialogue:
        label = speaker.upper()
        lines.append(f"[{label}] {text}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def generate_one(config: dict, force: bool = True) -> dict | None:
    builder = BUILDERS.get(config["theme"])
    if not builder:
        print(f"  ERROR: no builder for {config['theme']}")
        return None

    dialogue = builder()
    words = sum(len(t.split()) for _, t in dialogue)
    print(f"  {config['key']}: {len(dialogue)} turns, {words} words")

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(DRAFT_DIR, exist_ok=True)

    script_body = dialogue_to_text(dialogue)
    draft_path = os.path.join(DRAFT_DIR, f"{config['key']}.txt")
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(script_body)

    txt_path = os.path.join(DATA_DIR, f"coding-prep-{config['key']}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(script_body)

    mp3_path = os.path.join(DATA_DIR, f"coding-prep-{config['key']}.mp3")
    if (not force) and os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 1000:
        print(f"  reuse mp3 {mp3_path}")
    else:
        print("  TTS two-voice…")
        temp_dir = tempfile.mkdtemp(prefix="coding_mock_")
        segs = []
        for i, (speaker, text) in enumerate(dialogue):
            seg = os.path.join(temp_dir, f"seg_{i:04d}.mp3")
            if speaker == "interviewer":
                voice = "interviewer"
            elif speaker == "candidate":
                voice = "candidate"
            else:
                voice = "narrator"
            synthesize(text, seg, voice=voice, preprocess=True, rate="-12%")
            segs.append(seg)
            if (i + 1) % 5 == 0:
                print(f"    {i+1}/{len(dialogue)}")
        if len(segs) == 1:
            shutil.move(segs[0], mp3_path)
        else:
            concatenate_mp3(segs, mp3_path)
        shutil.rmtree(temp_dir, ignore_errors=True)

    duration = get_duration_str(mp3_path)
    size = os.path.getsize(mp3_path)
    print(f"  → {size/1024/1024:.1f} MB, {duration}")

    return {
        **config,
        "mp3_path": mp3_path,
        "txt_path": txt_path,
        "file_size_bytes": size,
        "duration": duration,
        "words": words,
        "theme": f"coding-prep-{config['key']}",
        "description": script_body[:480].replace("\n", " ").strip() + "…",
    }


def generate_rss(manifest: dict) -> bytes:
    rss = Element("rss", version="2.0")
    rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
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
    return minidom.parseString(rough).toprettyxml(indent="  ").encode("utf-8")


def publish(results: list[dict]) -> None:
    print("=== publish coding mocks to R2 + coding-prep playlist ===")
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
        by_id[r["id"]] = {
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

    manifest["episodes"] = sorted(by_id.values(), key=lambda e: e.get("id", 0), reverse=True)

    playlists = manifest.get("playlists") or {}
    if isinstance(playlists, list):
        playlists = {p["id"]: p for p in playlists if "id" in p}

    cp = playlists.get("coding-prep") or {}
    ids = list(cp.get("episode_ids") or [])
    for r in results:
        if r["id"] not in ids:
            ids.append(r["id"])
    ids = sorted(set(ids))
    playlists["coding-prep"] = {
        "title": "Coding Prep — Airwallex Muscle Memory",
        "description": (
            "Mentor monologues + two-voice coding mocks: interviewer sets problem, "
            "candidate clarifies, pseudocode, corners. Dual AI clock ep19–22. "
            "Loop for muscle memory. Pair learn.mingli.world coding-prep."
        ),
        "episode_ids": ids,
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
    for r in results:
        print(f"  → {BASE_URL}/episodes/coding-prep-{r['key']}.mp3")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--theme", type=str)
    ap.add_argument("--from-id", type=int, help="Only episodes with id >= this")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--force-tts", action="store_true", default=True)
    args = ap.parse_args()

    configs = EPISODES
    if args.theme:
        configs = [e for e in EPISODES if e["theme"] == args.theme or e["key"] == args.theme]
        if not configs:
            print("Unknown theme", args.theme)
            sys.exit(1)
    elif args.from_id is not None:
        configs = [e for e in EPISODES if e["id"] >= args.from_id]
        if not configs:
            print("No episodes >=", args.from_id)
            sys.exit(1)
    elif not args.all:
        print("Use --all or --theme … or --from-id N")
        sys.exit(1)

    results = []
    for ep in configs:
        print(f"\n--- {ep['title']} ---")
        r = generate_one(ep, force=args.force_tts)
        if r:
            results.append(r)

    if args.publish and results:
        publish(results)

    print(f"\nDone: {len(results)} coding mocks")


if __name__ == "__main__":
    main()
