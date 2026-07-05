#!/usr/bin/env python3
"""arrange.py — Collect feedback, compute ratios, write plan.json to R2.

Runs at 4 AM AEST (18:00 UTC) via GitHub Actions.
Reads all /feedback/*.json from R2, computes good/bad ratios per pattern,
updates the content plan, and writes plan.json back to R2.
"""

import json, os, sys
from datetime import datetime, timezone
from collections import defaultdict

import boto3

R2_ENDPOINT = os.environ["R2_ENDPOINT"]
R2_ACCESS_KEY = os.environ["R2_ACCESS_KEY"]
R2_SECRET_KEY = os.environ["R2_SECRET_KEY"]
BUCKET = "podcast-mingli-world"

# Thresholds
PROMOTE_RATIO = 0.8   # ratio above this → promote (schedule more)
DROP_RATIO = 0.4      # ratio below this → drop from rotation
MIN_FEEDBACK = 3      # minimum votes before trusting the ratio


def load_json_from_r2(s3, key):
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=key)
        return json.loads(obj["Body"].read().decode())
    except s3.exceptions.NoSuchKey:
        return None


def save_json_to_r2(s3, key, data):
    s3.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(data, indent=2), ContentType="application/json")


def list_feedback_files(s3):
    """List all /feedback/YYYY-MM-DD.json files in R2."""
    files = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET, Prefix="feedback/"):
        for obj in page.get("Contents", []):
            if obj["Key"].endswith(".json"):
                files.append(obj["Key"])
    return sorted(files)


def collect_feedback(s3):
    """Read all feedback files and aggregate by pattern ID."""
    # pattern_id -> {"good": N, "bad": N}
    pattern_stats = defaultdict(lambda: {"good": 0, "bad": 0})
    tip_stats = defaultdict(lambda: {"good": 0, "bad": 0})
    all_votes = []

    # Load manifest to map episode_id -> pattern_id
    manifest = load_json_from_r2(s3, "manifest.json")
    if not manifest:
        print("No manifest.json found — skipping feedback collection")
        return pattern_stats, tip_stats

    # Build episode -> pattern lookup
    episode_patterns = {}
    episode_tips = {}
    for ep in manifest.get("episodes", []):
        episode_patterns[str(ep["id"])] = ep.get("pattern_id")
        episode_tips[str(ep["id"])] = ep.get("tip_id")

    # Read all feedback files
    for key in list_feedback_files(s3):
        data = load_json_from_r2(s3, key)
        if not data:
            continue
        for episode_id, rating in data.items():
            pattern_id = episode_patterns.get(str(episode_id))
            tip_id = episode_tips.get(str(episode_id))
            if pattern_id and rating in ("good", "bad"):
                pattern_stats[pattern_id][rating] += 1
                all_votes.append({"episode": episode_id, "pattern": pattern_id, "rating": rating})
            if tip_id and rating in ("good", "bad"):
                tip_stats[tip_id][rating] += 1

    return pattern_stats, tip_stats


def compute_ratio(stats):
    """Compute good/(good+bad) ratio for a pattern."""
    total = stats["good"] + stats["bad"]
    if total < MIN_FEEDBACK:
        return None  # not enough data
    return stats["good"] / total


def arrange(pattern_stats, tip_stats, content_bank, existing_plan):
    """Determine the next episode's content based on feedback ratios."""
    patterns = content_bank["patterns"]
    tips = content_bank["tips"]
    prompts = content_bank["prompts"]
    categories = content_bank["categories"]

    # Build lookup
    pattern_by_id = {p["id"]: p for p in patterns}
    tip_by_id = {t["id"]: t for t in tips}

    # Compute ratios for all patterns that have been used
    rated_patterns = []
    for pid, stats in pattern_stats.items():
        ratio = compute_ratio(stats)
        total = stats["good"] + stats["bad"]
        p = pattern_by_id.get(pid, {})
        rated_patterns.append({
            "id": pid,
            "phrase": p.get("phrase", pid),
            "category": p.get("category", "unknown"),
            "ratio": ratio,
            "total_votes": total,
            "good": stats["good"],
            "bad": stats["bad"]
        })

    # Identify what to promote, keep, and drop
    promote = [p for p in rated_patterns if p["ratio"] is not None and p["ratio"] >= PROMOTE_RATIO]
    drop_ids = {p["id"] for p in rated_patterns if p["ratio"] is not None and p["ratio"] < DROP_RATIO}
    keep_ids = {p["id"] for p in rated_patterns if p["ratio"] is not None and PROMOTE_RATIO > p["ratio"] >= DROP_RATIO}

    # Used patterns from previous days (spaced repetition: don't repeat within 3 days)
    recent_pattern_ids = []
    if existing_plan and "recent_patterns" in existing_plan:
        recent_pattern_ids = existing_plan["recent_patterns"][-3:]

    # Category rotation: pick from the category used least recently
    category_usage = defaultdict(int)
    if existing_plan and "recent_categories" in existing_plan:
        for c in existing_plan["recent_categories"]:
            category_usage[c] += 1

    # Pick next pattern
    chosen_pattern = None
    chosen_reason = ""

    # 1. Patterns with high ratios in categories needing attention
    for p in promote:
        if p["id"] not in recent_pattern_ids and p["id"] not in drop_ids:
            chosen_pattern = p
            chosen_reason = f"promoted: ratio {p['ratio']:.2f} ({p['good']}👍/{p['bad']}👎)"
            break

    # 2. Any pattern not used recently, not dropped
    if not chosen_pattern:
        for p in patterns:
            if p["id"] not in recent_pattern_ids and p["id"] not in drop_ids:
                # Prefer categories with lower usage
                cat = p["category"]
                if category_usage.get(cat, 0) == 0:
                    chosen_pattern = {"id": p["id"], "phrase": p["phrase"], "category": cat, "ratio": None, "total_votes": 0}
                    chosen_reason = f"new: unused category '{cat}'"
                    break

    # 3. Fallback: any pattern not recently used
    if not chosen_pattern:
        for p in patterns:
            if p["id"] not in recent_pattern_ids:
                chosen_pattern = {"id": p["id"], "phrase": p["phrase"], "category": p["category"], "ratio": None, "total_votes": 0}
                chosen_reason = f"rotated: not in last 3 episodes"
                break

    # 4. Absolute fallback
    if not chosen_pattern:
        chosen_pattern = {"id": patterns[0]["id"], "phrase": patterns[0]["phrase"], "category": patterns[0]["category"], "ratio": None, "total_votes": 0}
        chosen_reason = "fallback: first available pattern"

    # Pick tip — prefer categories with lower usage
    chosen_tip = tips[0]
    for t in tips:
        cat = t["category"]
        if category_usage.get(f"tip:{cat}", 0) == 0:
            chosen_tip = t
            break

    # Pick a random prompt (cycle through)
    used_prompt_ids = existing_plan.get("used_prompts", []) if existing_plan else []
    chosen_prompt = prompts[0]
    for pr in prompts:
        if pr["id"] not in used_prompt_ids[-10:]:
            chosen_prompt = pr
            break

    # Build plan
    # Determine if today is Sunday for review episode
    today = datetime.now(timezone.utc)
    is_sunday = today.weekday() == 6  # Monday=0, Sunday=6

    # Get manifest for next episode number
    manifest = load_json_from_r2(s3, "manifest.json")
    next_episode_id = 1
    if manifest and manifest.get("episodes"):
        next_episode_id = max(ep["id"] for ep in manifest["episodes"]) + 1

    plan = {
        "episode_id": next_episode_id,
        "date": today.strftime("%Y-%m-%d"),
        "episode_type": "review" if is_sunday else "regular",
        "pattern_id": chosen_pattern["id"],
        "pattern_phrase": chosen_pattern["phrase"],
        "tip_id": chosen_tip["id"],
        "tip_name": chosen_tip["name"],
        "prompt_id": chosen_prompt["id"],
        "prompt_text": chosen_prompt["text"],
        "time_allocation": {"pattern": "2min", "tip": "3min"},
        "reason": chosen_reason,
        "promoted_patterns": [p["id"] for p in promote],
        "dropped_patterns": list(drop_ids),
        "recent_patterns": (recent_pattern_ids + [chosen_pattern["id"]])[-7:],
        "recent_categories": (existing_plan.get("recent_categories", []) if existing_plan else []) + [chosen_pattern["category"], f"tip:{chosen_tip['category']}"],
        "used_prompts": (used_prompt_ids + [chosen_prompt["id"]])[-20:],
        "stats": {
            "total_votes_collected": sum(s["good"] + s["bad"] for s in pattern_stats.values()) if pattern_stats else 0,
            "patterns_with_data": len(rated_patterns),
            "promoted_count": len(promote),
            "dropped_count": len(drop_ids)
        }
    }

    return plan


def main():
    s3 = boto3.client("s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY
    )

    print("=== arrange.py ===")

    # Collect feedback
    print("Collecting feedback from R2...")
    pattern_stats, tip_stats = collect_feedback(s3)
    print(f"  Patterns with feedback: {len(pattern_stats)}")
    for pid, stats in pattern_stats.items():
        ratio = compute_ratio(stats)
        ratio_str = f"{ratio:.2f}" if ratio is not None else "insufficient data"
        print(f"    {pid}: {stats['good']}👍 {stats['bad']}👎 (ratio: {ratio_str})")

    # Load content bank
    print("Loading content bank...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, "content_bank.json")) as f:
        content_bank = json.load(f)
    print(f"  {len(content_bank['patterns'])} patterns, {len(content_bank['tips'])} tips, {len(content_bank['prompts'])} prompts")

    # Load existing plan
    existing_plan = load_json_from_r2(s3, "plan.json")

    # Arrange
    print("Arranging next episode...")
    plan = arrange(pattern_stats, tip_stats, content_bank, existing_plan)
    print(f"  Episode #{plan['episode_id']}: pattern='{plan['pattern_phrase']}', tip='{plan['tip_name']}'")
    print(f"  Reason: {plan['reason']}")
    print(f"  Promoted: {plan['promoted_patterns']}, Dropped: {plan['dropped_patterns']}")

    # Save
    save_json_to_r2(s3, "plan.json", plan)
    print("plan.json written to R2 ✓")


if __name__ == "__main__":
    main()
