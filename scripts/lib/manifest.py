#!/usr/bin/env python3
"""manifest.py — manifest reads/writes and RSS generation.

The manifest is the database (AGENTS.md), so every mutation goes through
`add_or_update` rather than ad-hoc dict edits in a dozen generator scripts.

Two RSS bugs in the previous generator are fixed here:

* `pubDate` was emitted as `2026-07-06T06:00:00+10:00`. RSS 2.0 requires
  RFC 822 dates (`Mon, 06 Jul 2026 06:00:00 +1000`); the ISO form is not
  guaranteed to parse, and a client that rejects it drops the episode.
* Duration used a bare `<duration>` element, which no podcast client reads.
  The recognised tag is `<itunes:duration>`.

New: `<podcast:transcript>` and `<podcast:chapters>` per item, plus
`<itunes:episode>` and per-item artwork.
"""

from __future__ import annotations

import json
import os
from email.utils import format_datetime
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

BASE_URL = os.environ.get("BASE_URL", "https://podcast.mingli.world")

# Episodes have always been dated as 6am Melbourne time.
PUBLISH_TZ = timezone(timedelta(hours=10))
PUBLISH_HOUR = 6

ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"
PODCAST_NS = "https://podcastindex.org/namespace/1.0"

LOCAL_COPIES = ("scripts/manifest.json", "site/manifest.json")


# ---------------------------------------------------------------------------
# Load / save
# ---------------------------------------------------------------------------


def load(path: str | Path = "scripts/manifest.json") -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_local(manifest: dict, copies: tuple[str, ...] = LOCAL_COPIES) -> list[Path]:
    """Write the committed copies. R2 remains authoritative at runtime."""
    written = []
    payload = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    for rel in copies:
        path = Path(rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
        written.append(path)
    return written


# ---------------------------------------------------------------------------
# Mutation
# ---------------------------------------------------------------------------


def add_or_update(manifest: dict, entry: dict) -> dict:
    """Insert or replace an episode by id, keeping `episodes` sorted by id.

    Returns the manifest (mutated in place). Idempotent: publishing the same
    episode twice leaves the manifest byte-identical, which is what makes the
    daily bot commit a no-op when nothing changed.
    """
    if "id" not in entry:
        raise ValueError("episode entry needs an 'id'")

    episodes = manifest.setdefault("episodes", [])
    for i, existing in enumerate(episodes):
        if existing.get("id") == entry["id"]:
            episodes[i] = {**existing, **entry}
            break
    else:
        episodes.append(entry)

    episodes.sort(key=lambda e: e.get("id", 0))
    return manifest


def attach_to_playlist(manifest: dict, playlist_id: str, episode_id: int) -> dict:
    """Add an episode to a show, creating nothing — the show must be registered."""
    playlists = manifest.setdefault("playlists", {})
    if playlist_id not in playlists:
        raise KeyError(
            f"unknown playlist {playlist_id!r} — register it in content/shows.json first"
        )
    ids = playlists[playlist_id].setdefault("episode_ids", [])
    if episode_id not in ids:
        ids.append(episode_id)
        ids.sort()
    return manifest


def apply_shows(manifest: dict, shows: dict) -> dict:
    """Sync the `playlists` block from content/shows.json, keeping episode_ids.

    Carries the presentation fields (mono badge, order, featured) into the
    manifest so the frontend can read them from data. They used to live in a
    hardcoded `SHOW_META` in app.js that had drifted — it was missing four
    shows entirely, which is why they rendered without titles.
    """
    playlists = manifest.setdefault("playlists", {})
    for show_id, show in shows.get("shows", {}).items():
        existing = playlists.get(show_id, {})
        playlists[show_id] = {
            "title": show["title"],
            "description": show.get("description", ""),
            "icon": show.get("icon", ""),
            "mono": show.get("mono", ""),
            "order": show.get("order", 999),
            "featured": bool(show.get("featured")),
            "default_template": show.get("default_template", ""),
            "episode_ids": existing.get("episode_ids", []),
        }
    return manifest


# ---------------------------------------------------------------------------
# RSS
# ---------------------------------------------------------------------------


def _pub_date(date_str: str) -> str:
    """`YYYY-MM-DD` -> RFC 822, which is what RSS 2.0 actually requires."""
    try:
        day = datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        day = datetime.now(PUBLISH_TZ)
        return format_datetime(day)
    stamped = day.replace(hour=PUBLISH_HOUR, tzinfo=PUBLISH_TZ)
    return format_datetime(stamped)


def _artifact_url(kind: str, episode: dict) -> str | None:
    """URL for a per-episode side artifact, if the episode declares one."""
    slug = episode.get("slug") or (episode.get("filename") or "").removesuffix(".mp3")
    if not slug or not episode.get(f"has_{kind}"):
        return None
    ext = {"transcript": "vtt", "chapters": "json"}[kind]
    folder = {"transcript": "transcripts", "chapters": "chapters"}[kind]
    return f"{BASE_URL}/{folder}/{slug}.{ext}"


def generate_rss(manifest: dict) -> str:
    rss = Element("rss", version="2.0")
    rss.set("xmlns:itunes", ITUNES_NS)
    rss.set("xmlns:content", CONTENT_NS)
    rss.set("xmlns:podcast", PODCAST_NS)

    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = manifest.get("title", "Daily Interview English")
    SubElement(channel, "link").text = BASE_URL
    SubElement(channel, "description").text = manifest.get("description", "")
    SubElement(channel, "language").text = "en"

    author = manifest.get("author", "Daily Interview English")
    SubElement(channel, "itunes:author").text = author
    SubElement(channel, "itunes:explicit").text = "false"
    artwork = manifest.get("artwork_url") or f"{BASE_URL}/artwork.png"
    SubElement(channel, "itunes:image").set("href", artwork)
    SubElement(channel, "itunes:category").set("text", "Education")

    owner = SubElement(channel, "itunes:owner")
    SubElement(owner, "itunes:name").text = author

    for ep in sorted(manifest.get("episodes", []), key=lambda e: e.get("id", 0), reverse=True):
        item = SubElement(channel, "item")
        SubElement(item, "title").text = ep.get("title", "")
        SubElement(item, "description").text = ep.get("description", "")
        SubElement(item, "itunes:summary").text = ep.get("description", "")

        enclosure = SubElement(item, "enclosure")
        enclosure.set("url", ep.get("file_url", ""))
        enclosure.set("length", str(ep.get("file_size_bytes", 0)))
        enclosure.set("type", "audio/mpeg")

        guid = SubElement(item, "guid")
        guid.text = ep.get("file_url", "")
        guid.set("isPermaLink", "true")

        SubElement(item, "pubDate").text = _pub_date(ep.get("date", ""))
        SubElement(item, "itunes:duration").text = ep.get("duration", "")

        if isinstance(ep.get("id"), int):
            SubElement(item, "itunes:episode").text = str(ep["id"])

        transcript_url = _artifact_url("transcript", ep)
        if transcript_url:
            node = SubElement(item, "podcast:transcript")
            node.set("url", transcript_url)
            node.set("type", "text/vtt")
            node.set("language", "en")

        chapters_url = _artifact_url("chapters", ep)
        if chapters_url:
            node = SubElement(item, "podcast:chapters")
            node.set("url", chapters_url)
            node.set("type", "application/json+chapters")

    raw = tostring(rss, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ")
