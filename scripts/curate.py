#!/usr/bin/env python3
"""curate.py — Fetch RSS feeds, pick a relevant article, write today.json.

Runs at 5 AM AEST (19:00 UTC) via GitHub Actions.
"""

import json, os, sys, hashlib
from datetime import datetime, timezone, timedelta

import feedparser


def load_sources(script_dir):
    sources_path = os.path.join(script_dir, "sources.yaml")
    if os.path.exists(sources_path):
        import yaml
        with open(sources_path) as f:
            return yaml.safe_load(f)
    # Default sources if no yaml file
    return {
        "feeds": [
            {"url": "https://changelog.com/podcast/feed", "name": "Changelog", "keywords": ["engineering", "developer", "software", "leadership"]},
            {"url": "https://feeds.simplecast.com/sdgDQa0T", "name": "Soft Skills Engineering", "keywords": ["communication", "management", "career", "interview"]},
            {"url": "https://hnrss.org/frontpage", "name": "Hacker News", "keywords": ["engineering", "software", "career", "leadership"]},
        ],
        "curation": {"max_articles_per_feed": 3, "prefer_recent_hours": 48, "min_article_length_chars": 300}
    }


def score_article(entry, keywords):
    """Score an article by keyword relevance in title + summary."""
    text = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
    score = sum(1 for kw in keywords if kw.lower() in text)
    return score


def pick_article(feeds_config):
    """Fetch all feeds, return the best article across all of them."""
    best = None
    best_score = -1
    cutoff = datetime.now(timezone.utc) - timedelta(hours=feeds_config.get("curation", {}).get("prefer_recent_hours", 48))

    for feed_cfg in feeds_config["feeds"]:
        try:
            feed = feedparser.parse(feed_cfg["url"])
            if feed.bozo and not feed.entries:
                print(f"  Warning: failed to parse {feed_cfg['name']}: {feed.bozo_exception}")
                continue

            entries = feed.entries[:feeds_config.get("curation", {}).get("max_articles_per_feed", 3)]
            for entry in entries:
                score = score_article(entry, feed_cfg.get("keywords", []))
                if score > best_score:
                    best_score = score
                    best = {
                        "title": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "feed": feed_cfg["name"],
                        "summary": entry.get("summary", "")[:500],
                        "score": score
                    }
                    print(f"  New best: '{best['title']}' (score={score}) from {feed_cfg['name']}")
        except Exception as e:
            print(f"  Error fetching {feed_cfg['name']}: {e}")
            continue

    return best


def main():
    print("=== curate.py ===")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    feeds_config = load_sources(script_dir)

    print(f"Fetching {len(feeds_config['feeds'])} feeds...")
    article = pick_article(feeds_config)

    if not article:
        print("No article found — using fallback")
        article = {"title": "No article available today", "url": "", "feed": "fallback",
                   "summary": "Today's episode focuses on practice and review.", "score": 0}

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output = {
        "date": today,
        "source": article
    }

    out_path = os.path.join(os.path.dirname(script_dir), "data", "today.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"today.json written: {article['title'][:80]}")
    print("✓")


if __name__ == "__main__":
    main()
