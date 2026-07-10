#!/usr/bin/env python3
"""generate_mock_interview.py — Two-voice mock interview dialogue episodes.

Interviewer: en-US-AvaNeural (expressive, friendly)
Candidate: en-US-BrianNeural (casual, approachable)
Duration: 25-30 min per episode
Structure: 5 min requirements → 10 min high-level → 10 min deep dive → 3 min debrief
"""

import json, os, sys, subprocess, shutil, tempfile
from datetime import datetime, timezone

from tts import synthesize, get_duration_str, concatenate_mp3, crossfade_mp3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_BANK_PATH = os.path.join(SCRIPT_DIR, "content_bank.json")
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

MOCK_INTERVIEWS = [
    {
        "id": 46, "theme": "mock-payment-system",
        "title": "Mock Interview: Payment System",
        "subtitle": "Full 30-min mock system design interview",
        "playlist_id": "sd-mock-interviews",
        "item_id": "design-payment-system",
        "interviewer_style": "structured",
    },
    {
        "id": 47, "theme": "mock-url-shortener",
        "title": "Mock Interview: URL Shortener",
        "subtitle": "Full 25-min mock system design interview",
        "playlist_id": "sd-mock-interviews",
        "item_id": "design-url-shortener",
        "interviewer_style": "exploratory",
    },
    {
        "id": 48, "theme": "mock-news-feed",
        "title": "Mock Interview: News Feed",
        "subtitle": "Full 30-min mock system design interview",
        "playlist_id": "sd-mock-interviews",
        "item_id": "design-news-feed",
        "interviewer_style": "structured",
    },
]


def load_content_bank():
    with open(CONTENT_BANK_PATH) as f:
        return json.load(f)


def find_item(content_bank, item_id):
    for section in ["core_concepts", "case_studies", "architecture_patterns"]:
        for item in content_bank["system_design"].get(section, []):
            if item["id"] == item_id:
                return item
    return None


def build_interview_dialogue(item, config):
    """Generate two-voice interview dialogue from item data."""
    name = item["name"]
    desc = item.get("description", "")
    components = item.get("key_components", [])
    estimates = item.get("estimates", "")
    bottlenecks = item.get("bottlenecks", "")
    trade_offs = item.get("trade_offs", "")
    key_points = item.get("key_points", [])

    lines = []

    # Intro
    lines.append(("interviewer", "Hi, thanks for coming in today. I'd like to do a system design interview with you. The problem is: design a system for " + name + ". Before we dive in, how would you approach this?"))

    # Requirements clarification
    lines.append(("candidate", "Great, thanks. So before I start drawing boxes, let me clarify the requirements. What's the primary use case here?"))

    lines.append(("interviewer", desc + " What questions do you have?"))

    lines.append(("candidate", "OK, so a few things. What's the scale we're talking about? How many users, how many requests per second?"))

    if estimates:
        lines.append(("interviewer", "Good question. " + estimates + "."))

    lines.append(("candidate", "Alright, that's helpful. And what about latency requirements? Are we talking milliseconds, seconds?"))

    lines.append(("interviewer", "For this problem, let's say we need reasonable latency. Nothing sub-millisecond, but it should feel responsive. What else?"))

    lines.append(("candidate", "I'd also want to know about availability requirements. Is this a system where downtime is acceptable, or do we need five nines? And what about consistency? If data is replicated, can we tolerate eventual consistency?"))

    lines.append(("interviewer", "Great questions. For availability, let's say we need 99.9%. And consistency depends on the operation — some need strong consistency, others can be eventual. How would you handle that?"))

    # Estimation
    lines.append(("candidate", "Hmm, interesting. So let me do some quick estimation first. "))

    if estimates:
        lines.append(("candidate", "Based on those numbers... let me work through this. " + estimates + ". So we're definitely looking at horizontal scaling here."))

    lines.append(("interviewer", "Walk me through your math."))

    lines.append(("candidate", "Sure. So if we take the peak load and add a safety margin of, say, 2x, we need to handle roughly double the stated throughput. And for storage, we need to plan for growth over, let's say, 5 years. That means our storage estimate needs to account for that growth curve."))

    # High-level design
    lines.append(("interviewer", "OK, good. Now let's talk about the high-level architecture. What are the main components you'd need?"))

    lines.append(("candidate", "At a high level, I'm thinking we need a few core pieces. Let me think through this step by step."))

    if components:
        for i, comp in enumerate(components[:4]):
            if i == 0:
                lines.append(("candidate", "First, " + comp + "."))
            elif i == len(components[:4]) - 1:
                lines.append(("candidate", "And then, " + comp + "."))
            else:
                lines.append(("candidate", "Next, " + comp + "."))

    if len(components) > 4:
        lines.append(("candidate", "There are a few more components, but those are the main ones I'd start with."))

    lines.append(("interviewer", "That's a good start. Now, which of these do you think is the hardest part?"))

    # Deep dive
    lines.append(("candidate", "Hmm, let me think... "))

    if bottlenecks:
        lines.append(("candidate", "I think the main bottleneck is " + bottlenecks.split(".")[0].lower() + ". Let me dive deeper into that."))
    else:
        lines.append(("candidate", "I think the hardest part is making sure the system stays consistent under load. Let me dive into that."))

    lines.append(("interviewer", "Go ahead. How would you handle that?"))

    if key_points:
        for kp in key_points[:3]:
            lines.append(("candidate", "So, " + kp + "."))

    if trade_offs:
        lines.append(("candidate", "And the trade-off here is " + trade_offs + ". In an interview, I'd want to name this explicitly and explain why I chose one side."))
    elif bottlenecks:
        lines.append(("candidate", "To address the bottleneck, I'd add caching at the read layer and use async processing for writes. The trade-off is added complexity, but it's necessary at this scale."))

    lines.append(("interviewer", "What happens if things go wrong? What are the failure modes?"))

    lines.append(("candidate", "Good question. The failure mode I'm most concerned about is cascading failures. If one component goes down, the others shouldn't follow. I'd use circuit breakers to stop cascading failures, and bulkhead patterns to isolate resources."))

    lines.append(("interviewer", "How would you handle retries without causing duplicate side effects?"))

    lines.append(("candidate", "Ah, that's where idempotency comes in. Every request would carry an idempotency key. The server checks if it's already processed that key, and if so, returns the cached result instead of processing again. Stripe does this really well — every API call requires an Idempotency-Key header."))

    # Trade-offs discussion
    lines.append(("interviewer", "Let's talk about trade-offs more broadly. What would you do differently if the scale was 10x?"))

    lines.append(("candidate", "At 10x scale, I'd probably need to shard the database. A single database instance wouldn't handle that throughput. I'd also add a caching layer — something like Redis — to absorb reads. And I'd move more processing to async queues to decouple the write path from the read path."))

    lines.append(("interviewer", "What if the scale was 0.1x, much smaller?"))

    lines.append(("candidate", "At much smaller scale, I'd keep it simple. A single database, maybe even a single server. No caching, no sharding, no microservices. The simpler approach is easier to operate, easier to debug, and good enough for the traffic. I'd only add complexity when the data tells me I need it."))

    # Debrief
    lines.append(("interviewer", "Alright, that covers the main areas. Let me give you some feedback. You did a good job clarifying requirements upfront — that's really important. Your estimation was solid, and you named trade-offs explicitly, which is exactly what we look for. One thing to improve: when you were discussing the deep dive, you could have been more specific about the data model. Walking through the schema or the API contract in detail shows the interviewer you can think at that level. Overall though, strong performance."))

    lines.append(("candidate", "Thanks for the feedback. Yeah, I agree — I should have been more specific on the data model. That's something I'll practice more."))

    lines.append(("interviewer", "Great. Thanks for your time."))

    return lines


def generate_episode(config, content_bank):
    """Generate a complete mock interview episode."""
    item = find_item(content_bank, config["item_id"])
    if not item:
        print(f"  WARNING: Item {config['item_id']} not found")
        return None

    dialogue = build_interview_dialogue(item, config)

    # Split into interviewer and candidate segments
    interviewer_segments = []
    candidate_segments = []

    current_speaker = None
    current_text = []

    for speaker, text in dialogue:
        if speaker != current_speaker:
            if current_speaker and current_text:
                segment_text = " ".join(current_text)
                if current_speaker == "interviewer":
                    interviewer_segments.append(segment_text)
                else:
                    candidate_segments.append(segment_text)
            current_speaker = speaker
            current_text = [text]
        else:
            current_text.append(text)

    if current_speaker and current_text:
        segment_text = " ".join(current_text)
        if current_speaker == "interviewer":
            interviewer_segments.append(segment_text)
        else:
            candidate_segments.append(segment_text)

    # Generate audio for each speaker alternately, then interleave
    temp_dir = tempfile.mkdtemp(prefix="mock_interview_")
    segment_paths = []

    interviewer_idx = 0
    candidate_idx = 0
    turn = "interviewer"

    for speaker, text in dialogue:
        seg_idx = interviewer_idx if speaker == "interviewer" else candidate_idx
        seg_path = os.path.join(temp_dir, f"seg_{len(segment_paths):04d}.mp3")
        voice = "interviewer" if speaker == "interviewer" else "narrator"
        synthesize(text, seg_path, voice=voice, preprocess=True)
        segment_paths.append(seg_path)

        if speaker == "interviewer":
            interviewer_idx += 1
        else:
            candidate_idx += 1

    # Concatenate all segments
    mp3_path = os.path.join(DATA_DIR, f"mock-{config['theme']}.mp3")
    if len(segment_paths) == 1:
        shutil.move(segment_paths[0], mp3_path)
    else:
        concatenate_mp3(segment_paths, mp3_path)

    shutil.rmtree(temp_dir, ignore_errors=True)

    # Also save the script
    script_path = os.path.join(DATA_DIR, f"mock-{config['theme']}.txt")
    script_lines = []
    for speaker, text in dialogue:
        label = "INTERVIEWER" if speaker == "interviewer" else "CANDIDATE"
        script_lines.append(f"[{label}] {text}")
        script_lines.append("")

    with open(script_path, "w") as f:
        f.write("\n".join(script_lines))

    return {
        "id": config["id"],
        "theme": config["theme"],
        "title": config["title"],
        "subtitle": config["subtitle"],
        "playlist_id": config["playlist_id"],
        "mp3_path": mp3_path,
        "script_path": script_path,
        "file_size_bytes": os.path.getsize(mp3_path),
        "duration": get_duration_str(mp3_path),
    }


def main():
    print("=== generate_mock_interview.py ===")

    content_bank = load_content_bank()
    os.makedirs(DATA_DIR, exist_ok=True)

    theme = sys.argv[1] if len(sys.argv) > 1 else None
    configs = MOCK_INTERVIEWS
    if theme:
        configs = [c for c in configs if c["theme"] == theme]
        if not configs:
            print(f"ERROR: Unknown theme '{theme}'")
            sys.exit(1)

    results = []
    for config in configs:
        print(f"\n--- #{config['id']}: {config['title']} ---")
        result = generate_episode(config, content_bank)
        if result:
            print(f"  MP3: {result['file_size_bytes']/(1024*1024):.1f} MB, {result['duration']}")
            results.append(result)

    print(f"\nDone — {len(results)} mock interview episodes generated")


if __name__ == "__main__":
    main()
