#!/usr/bin/env python3
"""curate.py — build a ranked queue of candidate learning material.

Reads `scripts/sources.yaml` and scores everything new from both RSS feeds and
YouTube channels, writing `data/candidates.json`.

Two changes from the original: YouTube channels are a first-class source (via
YouTube's own RSS endpoints, which need no API key), and the output is a
*queue* rather than a single winner. The daily pipeline takes the top article;
the ingest step and the youtube-ingest skill take the video candidates.

Nothing is downloaded or published here. Curation only decides what is worth
looking at.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser

ROOT = Path(__file__).resolve().parent.parent
SOURCES_PATH = ROOT / "scripts" / "sources.yaml"
OUT_PATH = ROOT / "data" / "candidates.json"
INGESTED_DIR = ROOT / "content" / "sources" / "youtube"

YOUTUBE_FEED = "https://www.youtube.com/feeds/videos.xml?{key}={value}"


def load_sources() -> dict:
    if not SOURCES_PATH.exists():
        print(f"  no {SOURCES_PATH.name} — nothing to curate")
        return {"rss": [], "youtube": [], "curation": {}}
    import yaml

    return yaml.safe_load(SOURCES_PATH.read_text(encoding="utf-8")) or {}


def already_ingested() -> set[str]:
    """Video ids already pulled down, so a channel isn't re-suggested forever."""
    if not INGESTED_DIR.exists():
        return set()
    return {p.stem for p in INGESTED_DIR.glob("*.json")}


def score(text: str, keywords: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for kw in keywords if kw.lower() in lowered)


def entry_time(entry) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        value = getattr(entry, attr, None)
        if value:
            return datetime(*value[:6], tzinfo=timezone.utc)
    return None


def collect_rss(config: dict, cutoff: datetime, limit: int) -> list[dict]:
    out = []
    for feed_cfg in config.get("rss") or []:
        try:
            feed = feedparser.parse(feed_cfg["url"])
        except Exception as exc:
            print(f"  error {feed_cfg.get('name')}: {exc}")
            continue
        if feed.bozo and not feed.entries:
            print(f"  warning {feed_cfg.get('name')}: unparseable")
            continue

        for entry in feed.entries[:limit]:
            when = entry_time(entry)
            if when and when < cutoff:
                continue
            blob = entry.get("title", "") + " " + entry.get("summary", "")
            out.append(
                {
                    "kind": "rss",
                    "feed": feed_cfg.get("name", ""),
                    "show": feed_cfg.get("show", ""),
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:500],
                    "published": when.isoformat() if when else None,
                    "score": score(blob, feed_cfg.get("keywords", [])),
                }
            )
    return out


def collect_youtube(config: dict, cutoff: datetime, seen: set[str]) -> list[dict]:
    out = []
    for chan in config.get("youtube") or []:
        if chan.get("channel_id"):
            url = YOUTUBE_FEED.format(key="channel_id", value=chan["channel_id"])
        elif chan.get("playlist_id"):
            url = YOUTUBE_FEED.format(key="playlist_id", value=chan["playlist_id"])
        else:
            print(f"  skip {chan.get('name')}: needs channel_id or playlist_id")
            continue

        try:
            feed = feedparser.parse(url)
        except Exception as exc:
            print(f"  error {chan.get('name')}: {exc}")
            continue

        picked = 0
        for entry in feed.entries:
            vid = entry.get("yt_videoid") or entry.get("id", "").split(":")[-1]
            if not vid or vid in seen:
                continue

            when = entry_time(entry)
            if when and when < cutoff:
                continue

            blob = entry.get("title", "") + " " + entry.get("summary", "")
            hits = score(blob, chan.get("keywords", []))
            if hits < config.get("curation", {}).get("min_score", 1):
                continue

            out.append(
                {
                    "kind": "youtube",
                    "feed": chan.get("name", ""),
                    "show": chan.get("show", ""),
                    "video_id": vid,
                    "title": entry.get("title", ""),
                    "url": entry.get("link", f"https://youtu.be/{vid}"),
                    "published": when.isoformat() if when else None,
                    "score": hits,
                }
            )
            picked += 1
            if picked >= chan.get("max_per_run", 2):
                break
    return out


def main() -> int:
    print("=== curate.py ===")
    config = load_sources()
    curation = config.get("curation") or {}

    cutoff = datetime.now(timezone.utc) - timedelta(
        hours=curation.get("prefer_recent_hours", 168)
    )
    seen = already_ingested()

    print(f"  {len(config.get('rss') or [])} RSS feeds, "
          f"{len(config.get('youtube') or [])} YouTube sources, "
          f"{len(seen)} already ingested")

    candidates = collect_rss(config, cutoff, curation.get("max_articles_per_feed", 3))
    candidates += collect_youtube(config, cutoff, seen)
    candidates.sort(key=lambda c: (-c["score"], c.get("published") or ""))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(
            {
                "generated": datetime.now(timezone.utc).isoformat(),
                "candidates": candidates,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    videos = sum(1 for c in candidates if c["kind"] == "youtube")
    print(f"  {len(candidates)} candidates ({videos} video) -> {OUT_PATH.relative_to(ROOT)}")
    for c in candidates[:5]:
        print(f"    [{c['score']}] {c['kind']:<7} {c['title'][:60]}")

    # The daily pipeline still wants a single article; keep today.json for it.
    article = next((c for c in candidates if c["kind"] == "rss"), None)
    today = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "source": article
        or {
            "title": "No article available today",
            "url": "",
            "feed": "fallback",
            "summary": "Today's episode focuses on practice and review.",
            "score": 0,
        },
    }
    (ROOT / "data" / "today.json").write_text(
        json.dumps(today, indent=2) + "\n", encoding="utf-8"
    )
    print("  today.json written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
