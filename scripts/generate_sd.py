#!/usr/bin/env python3
"""generate_sd.py — Build system design episode script from content_bank.json.

Each episode covers 2-5 SD items (concepts, case studies, or architecture patterns).
Includes practice prompts with pause sections. Target: 10-15 minutes per episode.
"""

import json, os, sys, subprocess, shutil
from datetime import datetime, timezone

VOICE = "en-US-ChristopherNeural"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_BANK_PATH = os.path.join(SCRIPT_DIR, "content_bank.json")

SD_EPISODES = [
    {
        "theme": "sd-fundamentals",
        "title": "System Design Fundamentals",
        "subtitle": "CAP, ACID vs BASE, Consensus",
        "item_ids": ["cap-theorem", "acid-vs-base", "consensus"],
        "item_type": "core_concepts"
    },
    {
        "theme": "sd-infrastructure",
        "title": "Infrastructure Essentials",
        "subtitle": "Load Balancing, Caching, CDN, Message Queues",
        "item_ids": ["load-balancing", "caching", "cdn", "message-queues"],
        "item_type": "core_concepts"
    },
    {
        "theme": "sd-data",
        "title": "Data Architecture",
        "subtitle": "Sharding, Replication, Partitioning",
        "item_ids": ["database-sharding", "replication", "data-partitioning"],
        "item_type": "core_concepts"
    },
    {
        "theme": "sd-api-microservices",
        "title": "API & Microservices",
        "subtitle": "API Design, Microservices Architecture",
        "item_ids": ["api-design", "microservices"],
        "item_type": "core_concepts"
    },
    {
        "theme": "sd-reliability",
        "title": "Reliability Engineering",
        "subtitle": "Idempotency, Rate Limiting, Observability",
        "item_ids": ["idempotency", "rate-limiting", "observability"],
        "item_type": "core_concepts"
    },
    {
        "theme": "sd-classic-1",
        "title": "Classic System Design I",
        "subtitle": "URL Shortener + Chat System",
        "item_ids": ["design-url-shortener", "design-chat-system"],
        "item_type": "case_studies"
    },
    {
        "theme": "sd-classic-2",
        "title": "Classic System Design II",
        "subtitle": "News Feed + Search Autocomplete",
        "item_ids": ["design-news-feed", "design-search-autocomplete"],
        "item_type": "case_studies"
    },
    {
        "theme": "sd-classic-3",
        "title": "Classic System Design III",
        "subtitle": "Notification System + Web Crawler",
        "item_ids": ["design-notification-system", "design-web-crawler"],
        "item_type": "case_studies"
    },
    {
        "theme": "sd-advanced-1",
        "title": "Advanced System Design I",
        "subtitle": "Object Storage + Key-Value Store",
        "item_ids": ["design-object-storage", "design-key-value-store"],
        "item_type": "case_studies"
    },
    {
        "theme": "sd-advanced-2",
        "title": "Advanced System Design II",
        "subtitle": "Location Service + Video Streaming",
        "item_ids": ["design-location-service", "design-video-streaming"],
        "item_type": "case_studies"
    },
    {
        "theme": "sd-arch-patterns-1",
        "title": "Architecture Patterns I",
        "subtitle": "Event-Driven, CQRS, Sidecar",
        "item_ids": ["event-driven", "cqrs", "sidecar"],
        "item_type": "architecture_patterns"
    },
    {
        "theme": "sd-arch-patterns-2",
        "title": "Architecture Patterns II",
        "subtitle": "Circuit Breaker, Bulkhead, Saga, Strangler Fig, Backpressure",
        "item_ids": ["circuit-breaker", "bulkhead", "saga", "strangler-fig", "backpressure"],
        "item_type": "architecture_patterns"
    }
]


def load_content_bank():
    with open(CONTENT_BANK_PATH) as f:
        return json.load(f)


def find_items(content_bank, item_type, item_ids):
    if item_type == "core_concepts":
        source = content_bank["system_design"]["core_concepts"]
    elif item_type == "case_studies":
        source = content_bank["system_design"]["case_studies"]
    elif item_type == "architecture_patterns":
        source = content_bank["system_design"]["architecture_patterns"]
    else:
        return []

    items = []
    for item_id in item_ids:
        for item in source:
            if item["id"] == item_id:
                items.append(item)
                break
    return items


def find_prompt_for_item(content_bank, item_id):
    for p in content_bank["prompts"]:
        if p.get("id") == item_id or p.get("id") == item_id.replace("design-", ""):
            return p
    return None


def build_concept_section(item, index, total):
    lines = []
    lines.append(f"── {item['name']} ({index} of {total}) ──")
    lines.append("")
    lines.append(item["description"])
    lines.append("")

    if item.get("key_points"):
        lines.append("Key points:")
        for kp in item["key_points"]:
            lines.append(f"  - {kp}")
        lines.append("")

    if item.get("trade_offs"):
        lines.append(f"Trade-offs: {item['trade_offs']}")
        lines.append("")

    if item.get("real_examples"):
        lines.append(f"Real-world examples: {item['real_examples']}")
        lines.append("")

    return lines


def build_case_section(item, index, total):
    lines = []
    lines.append(f"── {item['name']} ({index} of {total}) ──")
    lines.append("")
    lines.append(item["description"])
    lines.append("")

    if item.get("key_components"):
        lines.append("Key components:")
        for kc in item["key_components"]:
            lines.append(f"  - {kc}")
        lines.append("")

    if item.get("estimates"):
        lines.append(f"Scale estimates: {item['estimates']}")
        lines.append("")

    if item.get("bottlenecks"):
        lines.append(f"Primary bottlenecks: {item['bottlenecks']}")
        lines.append("")

    return lines


def build_pattern_section(item, index, total):
    lines = []
    lines.append(f"── {item['name']} ({index} of {total}) ──")
    lines.append("")
    lines.append(item["description"])
    lines.append("")

    if item.get("when_to_use"):
        lines.append(f"When to use: {item['when_to_use']}")
        lines.append("")

    if item.get("key_benefits"):
        lines.append("Key benefits:")
        for b in item["key_benefits"]:
            lines.append(f"  - {b}")
        lines.append("")

    if item.get("common_pitfalls"):
        lines.append("Common pitfalls:")
        for pi in item["common_pitfalls"]:
            lines.append(f"  - {pi}")
        lines.append("")

    if item.get("technologies"):
        lines.append(f"Technologies: {item['technologies']}")
        lines.append("")

    return lines


def build_practice_section(prompt, item_name):
    lines = []
    lines.append("── Practice ──")
    lines.append("")
    if prompt:
        lines.append(f"Here's a practice question: {prompt['text']}")
        lines.append("")
        if prompt.get("structure"):
            lines.append("Structure your answer using these steps:")
            for i, s in enumerate(prompt["structure"], 1):
                lines.append(f"  {i}. {s}")
            lines.append("")
        lines.append("Pause this episode now and answer out loud. Use the RESHADED framework to organize your response.")
    else:
        lines.append(f"Imagine you're in an interview and asked to discuss {item_name}. Structure your answer by first clarifying requirements, then estimating scale, then designing the high-level architecture, and finally diving deep into one component. Name the trade-offs explicitly.")
        lines.append("")
        lines.append("Pause now and practice your answer out loud.")
    lines.append("")
    return lines


def build_script(episode_config, content_bank):
    today = datetime.now(timezone.utc)
    items = find_items(content_bank, episode_config["item_type"], episode_config["item_ids"])

    if not items:
        print(f"  WARNING: No items found for {episode_config['theme']}")
        return ""

    lines = []

    lines.append(f"Welcome to System Design Deep Dive. {today.strftime('%B %d, %Y')}.")
    lines.append("")
    lines.append(f"Today's topic: {episode_config['title']}. {episode_config['subtitle']}.")
    lines.append("")

    hook_map = {
        "core_concepts": "These are the building blocks that every system design interview assumes you know. If you can explain these clearly, you'll have the foundation to tackle any design question.",
        "case_studies": "These are the classic interview problems that appear again and again. The specific system matters less than the thinking framework — how you decompose the problem, estimate scale, and navigate trade-offs.",
        "architecture_patterns": "These patterns are the reusable solutions that experienced architects reach for. Knowing when to apply each one — and when not to — is what separates junior from senior design answers."
    }
    lines.append(hook_map.get(episode_config["item_type"], "Let's dive in."))
    lines.append("")

    for i, item in enumerate(items, 1):
        if episode_config["item_type"] == "core_concepts":
            lines.extend(build_concept_section(item, i, len(items)))
        elif episode_config["item_type"] == "case_studies":
            lines.extend(build_case_section(item, i, len(items)))
        elif episode_config["item_type"] == "architecture_patterns":
            lines.extend(build_pattern_section(item, i, len(items)))

        prompt = find_prompt_for_item(content_bank, item["id"])
        lines.extend(build_practice_section(prompt, item["name"]))

    lines.append("── Quick Review ──")
    lines.append("")
    lines.append("Let's review the key takeaways from today's episode.")
    lines.append("")
    for item in items:
        if item.get("trade_offs"):
            lines.append(f"{item['name']}: the core trade-off is {item['trade_offs'].split('.')[0]}.")
        elif item.get("bottlenecks"):
            lines.append(f"{item['name']}: the primary bottleneck is {item['bottlenecks'].split('.')[0]}.")
        elif item.get("when_to_use"):
            lines.append(f"{item['name']}: use when {item['when_to_use'].split('.')[0]}.")
        else:
            lines.append(f"{item['name']}: {item['description'][:100]}.")
    lines.append("")

    lines.append("── Outro ──")
    lines.append("")
    lines.append("Remember: the key to system design interviews is naming trade-offs explicitly. Don't just describe a design — explain why you chose it and what you gave up.")
    lines.append("")
    lines.append("Great work today. Consistent practice builds system design intuition. See you next time.")
    lines.append("")

    return "\n".join(lines)


def run_edge_tts(script_text, output_path):
    script_path = "/tmp/sd_episode_script.txt"
    with open(script_path, "w") as f:
        f.write(script_text)

    cmd = ["edge-tts", "--voice", VOICE, "--rate=-15%", "--text", script_text, "--write-media", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        cmd2 = ["edge-tts", "--voice", VOICE, "--rate=-15%", "-f", script_path, "--write-media", output_path]
        result2 = subprocess.run(cmd2, capture_output=True, text=True)
        if result2.returncode != 0:
            raise RuntimeError(f"edge-tts failed: {result2.stderr[:500]}")

    if shutil.which("ffmpeg"):
        temp_path = output_path + ".temp.mp3"
        os.rename(output_path, temp_path)
        subprocess.run([
            "ffmpeg", "-y", "-i", temp_path,
            "-af", "loudnorm, silenceremove=stop_periods=-1:stop_duration=0.3:stop_threshold=-40dB",
            output_path
        ], capture_output=True)
        os.remove(temp_path)


def get_duration_minutes(mp3_path):
    if not shutil.which("ffprobe"):
        return 0
    result = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", mp3_path
    ], capture_output=True, text=True)
    try:
        seconds = float(result.stdout.strip())
        return int(seconds / 60)
    except (ValueError, TypeError):
        return 0


def main():
    print("=== generate_sd.py ===")

    content_bank = load_content_bank()
    data_dir = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
    os.makedirs(data_dir, exist_ok=True)

    theme = sys.argv[1] if len(sys.argv) > 1 else None

    if theme:
        configs = [ec for ec in SD_EPISODES if ec["theme"] == theme]
        if not configs:
            print(f"ERROR: Unknown theme '{theme}'. Available: {[e['theme'] for e in SD_EPISODES]}")
            sys.exit(1)
    else:
        configs = SD_EPISODES

    results = []

    for config in configs:
        print(f"\n--- {config['title']}: {config['subtitle']} ---")

        script = build_script(config, content_bank)
        if not script:
            continue

        word_count = len(script.split())
        est_min = word_count / 140
        print(f"  Script: {word_count} words, ~{est_min:.0f} min estimated")

        script_path = os.path.join(data_dir, f"sd-{config['theme']}.txt")
        with open(script_path, "w") as f:
            f.write(script)

        mp3_path = os.path.join(data_dir, f"sd-{config['theme']}.mp3")
        print(f"  Generating audio...")
        run_edge_tts(script, mp3_path)

        size_mb = os.path.getsize(mp3_path) / (1024 * 1024)
        dur_min = get_duration_minutes(mp3_path)
        print(f"  MP3: {size_mb:.1f} MB, ~{dur_min} min")

        results.append({
            "theme": config["theme"],
            "title": config["title"],
            "subtitle": config["subtitle"],
            "item_type": config["item_type"],
            "item_ids": config["item_ids"],
            "script_path": script_path,
            "mp3_path": mp3_path,
            "file_size_bytes": os.path.getsize(mp3_path),
            "duration_min": dur_min
        })

    results_path = os.path.join(data_dir, "sd_episodes.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDone — {len(results)} SD episodes generated")
    print(f"Results saved to {results_path}")


if __name__ == "__main__":
    main()
