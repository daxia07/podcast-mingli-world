#!/usr/bin/env python3
"""generate_mock_interviews_v2.py — Generate expanded mock interview episodes.

Generates 9 new mock interview episodes using the mock_dialogues package.
Each episode uses two voices: interviewer (AvaNeural) + candidate (BrianNeural).

Usage:
  python3 generate_mock_interviews_v2.py [theme]
  python3 generate_mock_interviews_v2.py mock-fx-ledger
"""

import json, os, sys, shutil, tempfile

from tts import synthesize, get_duration_str, concatenate_mp3
from mock_dialogues import BUILDERS

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

EPISODES = [
    {"id": 49, "theme": "mock-cross-border-payments", "title": "Mock Interview: Cross-Border Payments", "subtitle": "Designing a multi-currency payment pipeline with FX conversion"},
    {"id": 50, "theme": "mock-distributed-cache", "title": "Mock Interview: Distributed Cache", "subtitle": "Designing a Redis-like distributed caching system"},
    {"id": 51, "theme": "mock-notification-system", "title": "Mock Interview: Notification System", "subtitle": "Designing multi-channel notifications (push, email, SMS)"},
    {"id": 52, "theme": "mock-typeahead-search", "title": "Mock Interview: Typeahead / Search Autocomplete", "subtitle": "Designing a low-latency autocomplete system"},
    {"id": 53, "theme": "mock-object-storage", "title": "Mock Interview: Object Storage (S3)", "subtitle": "Designing a durable, scalable object storage system"},
    {"id": 54, "theme": "mock-fx-ledger", "title": "Mock Interview: FX & Multi-Currency Ledger", "subtitle": "Designing an FX rate engine and double-entry ledger"},
    {"id": 55, "theme": "mock-top-k-heavy-hitters", "title": "Mock Interview: Top-K / Heavy Hitters", "subtitle": "Finding the most frequent items in a data stream at scale"},
    {"id": 56, "theme": "mock-chat-system", "title": "Mock Interview: Real-Time Chat", "subtitle": "Designing a WhatsApp-like messaging system"},
    {"id": 57, "theme": "mock-location-service", "title": "Mock Interview: Location-Based Service", "subtitle": "Designing nearby-driver search and real-time tracking"},
]


def generate_episode(config):
    builder = BUILDERS.get(config["theme"])
    if not builder:
        print(f"  ERROR: No builder for theme '{config['theme']}'")
        return None

    dialogue = builder()
    words = sum(len(t.split()) for _, t in dialogue)
    print(f"  Dialogue: {len(dialogue)} turns, ~{words} words, ~{words/159:.0f} min")

    temp_dir = tempfile.mkdtemp(prefix="mock_v2_")
    segment_paths = []

    for i, (speaker, text) in enumerate(dialogue):
        seg_path = os.path.join(temp_dir, f"seg_{i:04d}.mp3")
        voice = "interviewer" if speaker == "interviewer" else "narrator"
        synthesize(text, seg_path, voice=voice, preprocess=True)
        segment_paths.append(seg_path)
        if (i + 1) % 10 == 0:
            print(f"    Synthesized {i+1}/{len(dialogue)} segments...")

    mp3_path = os.path.join(DATA_DIR, f"mock-v2-{config['theme']}.mp3")
    if len(segment_paths) == 1:
        shutil.move(segment_paths[0], mp3_path)
    else:
        concatenate_mp3(segment_paths, mp3_path)

    shutil.rmtree(temp_dir, ignore_errors=True)

    script_path = os.path.join(DATA_DIR, f"mock-v2-{config['theme']}.txt")
    with open(script_path, "w") as f:
        for speaker, text in dialogue:
            label = "INTERVIEWER" if speaker == "interviewer" else "CANDIDATE"
            f.write(f"[{label}] {text}\n\n")

    duration = get_duration_str(mp3_path)
    size = os.path.getsize(mp3_path)

    print(f"  MP3: {size/(1024*1024):.1f} MB, {duration}")

    return {
        "id": config["id"],
        "theme": config["theme"],
        "title": config["title"],
        "subtitle": config["subtitle"],
        "mp3_path": mp3_path,
        "script_path": script_path,
        "file_size_bytes": size,
        "duration": duration,
        "words": words,
    }


def main():
    print("=== generate_mock_interviews_v2.py ===")
    os.makedirs(DATA_DIR, exist_ok=True)

    theme = sys.argv[1] if len(sys.argv) > 1 else None
    configs = EPISODES
    if theme:
        configs = [c for c in configs if c["theme"] == theme]
        if not configs:
            print(f"ERROR: Unknown theme '{theme}'")
            print(f"Available: {[c['theme'] for c in EPISODES]}")
            sys.exit(1)

    results = []
    for config in configs:
        print(f"\n--- #{config['id']}: {config['title']} ---")
        result = generate_episode(config)
        if result:
            results.append(result)

    print(f"\n{'='*60}")
    print(f"Done — {len(results)} episodes generated")
    print(f"{'='*60}")
    for r in results:
        print(f"  #{r['id']}: {r['duration']} ({r['words']} words, {r['file_size_bytes']/(1024*1024):.1f} MB)")
        print(f"    MP3: {r['mp3_path']}")
        print(f"    Script: {r['script_path']}")


if __name__ == "__main__":
    main()
