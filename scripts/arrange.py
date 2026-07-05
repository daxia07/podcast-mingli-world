#!/usr/bin/env python3
"""arrange.py — Collect feedback, compute ratios, write plan.json to R2."""

import json, os, sys
from datetime import datetime, timezone
from collections import defaultdict

from r2_utils import get_json, upload_json, download

BUCKET = "podcast-mingli-world"
PROMOTE_RATIO = 0.8
DROP_RATIO = 0.4
MIN_FEEDBACK = 3


def list_feedback():
    """Collect all feedback from R2 by downloading known keys.

    Since R2 doesn't easily support listing via wrangler,
    we read feedback from the last 30 days by date.
    """
    pattern_stats = defaultdict(lambda: {"good": 0, "bad": 0})
    tip_stats = defaultdict(lambda: {"good": 0, "bad": 0})

    manifest = get_json("manifest.json")
    if not manifest:
        return pattern_stats, tip_stats

    episode_patterns = {}
    episode_tips = {}
    for ep in manifest.get("episodes", []):
        episode_patterns[str(ep["id"])] = ep.get("pattern_id")
        episode_tips[str(ep["id"])] = ep.get("tip_id")

    # Try to read feedback from the last 30 days
    from datetime import timedelta
    today = datetime.now(timezone.utc)

    found_any = False
    for i in range(30):
        d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        # Try known episode IDs
        for ep_id in range(1, 100):
            key = f"feedback/{d}_ep{ep_id}.json"
            data = get_json(key)
            if data:
                found_any = True
                rating = data.get("rating")
                episode_id = str(data.get("episode"))
                pattern_id = episode_patterns.get(episode_id)
                tip_id = episode_tips.get(episode_id)
                if pattern_id and rating in ("good", "bad"):
                    pattern_stats[pattern_id][rating] += 1
                if tip_id and rating in ("good", "bad"):
                    tip_stats[tip_id][rating] += 1

    if found_any:
        print(f"  Found feedback from the last 30 days")

    return pattern_stats, tip_stats


def compute_ratio(stats):
    total = stats["good"] + stats["bad"]
    if total < MIN_FEEDBACK:
        return None
    return stats["good"] / total


def arrange(pattern_stats, tip_stats, content_bank, existing_plan):
    patterns = content_bank["patterns"]
    tips = content_bank["tips"]
    prompts = content_bank["prompts"]

    pattern_by_id = {p["id"]: p for p in patterns}
    tip_by_id = {t["id"]: t for t in tips}

    rated_patterns = []
    for pid, stats in pattern_stats.items():
        ratio = compute_ratio(stats)
        total = stats["good"] + stats["bad"]
        p = pattern_by_id.get(pid, {})
        rated_patterns.append({
            "id": pid, "phrase": p.get("phrase", pid),
            "category": p.get("category", "unknown"),
            "ratio": ratio, "total_votes": total,
            "good": stats["good"], "bad": stats["bad"]
        })

    promote = [p for p in rated_patterns if p["ratio"] is not None and p["ratio"] >= PROMOTE_RATIO]
    drop_ids = {p["id"] for p in rated_patterns if p["ratio"] is not None and p["ratio"] < DROP_RATIO}

    recent_pattern_ids = existing_plan.get("recent_patterns", [])[-3:] if existing_plan else []
    category_usage = defaultdict(int)
    if existing_plan and "recent_categories" in existing_plan:
        for c in existing_plan["recent_categories"]:
            category_usage[c] += 1

    # Pick pattern
    chosen_pattern = None
    chosen_reason = ""

    for p in promote:
        if p["id"] not in recent_pattern_ids and p["id"] not in drop_ids:
            chosen_pattern = p
            chosen_reason = f"promoted: ratio {p['ratio']:.2f} ({p['good']}👍/{p['bad']}👎)"
            break

    if not chosen_pattern:
        for p in patterns:
            if p["id"] not in recent_pattern_ids and p["id"] not in drop_ids:
                if category_usage.get(p["category"], 0) == 0:
                    chosen_pattern = {"id": p["id"], "phrase": p["phrase"], "category": p["category"], "ratio": None, "total_votes": 0}
                    chosen_reason = f"new: unused category '{p['category']}'"
                    break

    if not chosen_pattern:
        for p in patterns:
            if p["id"] not in recent_pattern_ids:
                chosen_pattern = {"id": p["id"], "phrase": p["phrase"], "category": p["category"], "ratio": None, "total_votes": 0}
                chosen_reason = "rotated: not in last 3 episodes"
                break

    if not chosen_pattern:
        p = patterns[0]
        chosen_pattern = {"id": p["id"], "phrase": p["phrase"], "category": p["category"], "ratio": None, "total_votes": 0}
        chosen_reason = "fallback: first available"

    # Pick tip
    chosen_tip = tips[0]
    for t in tips:
        if category_usage.get(f"tip:{t['category']}", 0) == 0:
            chosen_tip = t
            break

    # Pick prompt
    used_prompt_ids = existing_plan.get("used_prompts", []) if existing_plan else []
    chosen_prompt = prompts[0]
    for pr in prompts:
        if pr["id"] not in used_prompt_ids[-10:]:
            chosen_prompt = pr
            break

    today = datetime.now(timezone.utc)
    is_sunday = today.weekday() == 6

    manifest = get_json("manifest.json")
    next_id = 1
    if manifest and manifest.get("episodes"):
        next_id = max(ep["id"] for ep in manifest["episodes"]) + 1

    plan = {
        "episode_id": next_id,
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
        "used_prompts": (used_prompt_ids + [chosen_prompt["id"]])[-20:]
    }

    return plan


def main():
    print("=== arrange.py ===")

    print("Collecting feedback from R2...")
    pattern_stats, tip_stats = list_feedback()
    print(f"  Patterns with feedback: {len(pattern_stats)}")
    for pid, stats in pattern_stats.items():
        ratio = compute_ratio(stats)
        ratio_str = f"{ratio:.2f}" if ratio is not None else "insufficient data"
        print(f"    {pid}: {stats['good']}👍 {stats['bad']}👎 (ratio: {ratio_str})")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, "content_bank.json")) as f:
        content_bank = json.load(f)

    existing_plan = get_json("plan.json") or {}

    print("Arranging next episode...")
    plan = arrange(pattern_stats, tip_stats, content_bank, existing_plan)
    print(f"  Episode #{plan['episode_id']}: '{plan['pattern_phrase']}' — {plan['tip_name']}")
    print(f"  Reason: {plan['reason']}")

    upload_json("plan.json", plan)
    print("plan.json written to R2")


if __name__ == "__main__":
    main()
