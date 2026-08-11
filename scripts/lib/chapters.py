#!/usr/bin/env python3
"""chapters.py — Podcasting 2.0 chapter files from a Timeline.

Apple's guidance, which most other players also respect: at least 3 chapters,
titles short enough not to truncate (~45 chars), and nothing so brief that the
chapter list becomes noise. Blueprint sections map to chapters almost directly;
this module applies the length rules and emits the JSON.

Format: https://github.com/Podcastindex-org/podcast-namespace — the
`application/json+chapters` document referenced by <podcast:chapters>.
"""

from __future__ import annotations

import json

from .timeline import Timeline

MIN_CHAPTER_SECONDS = 45.0
MAX_TITLE_CHARS = 45
MIN_CHAPTERS = 3


def _shorten(title: str, limit: int = MAX_TITLE_CHARS) -> str:
    title = " ".join(title.split())
    if len(title) <= limit:
        return title
    cut = title[: limit - 1]
    # Prefer a word boundary, but not if it throws away most of the title.
    if " " in cut and len(cut.rsplit(" ", 1)[0]) >= limit * 0.6:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:—-") + "…"


def build(timeline: Timeline, *, min_seconds: float = MIN_CHAPTER_SECONDS) -> list[dict]:
    """Timeline sections -> chapter dicts, merging anything too short.

    A short section is absorbed by the chapter before it (or, if it is first,
    it absorbs the one after) so the result still tiles the whole episode.
    """
    if not timeline.sections:
        return []

    merged: list[dict] = []
    for section in timeline.sections:
        entry = {
            "startTime": round(section.start, 3),
            "endTime": round(section.end, 3),
            "title": _shorten(section.title),
        }
        if merged and (section.end - section.start) < min_seconds:
            # Too short to stand alone — extend the previous chapter over it.
            merged[-1]["endTime"] = entry["endTime"]
            continue
        merged.append(entry)

    # A short *first* section can't merge backwards; fold it forwards instead.
    if len(merged) > 1 and (merged[0]["endTime"] - merged[0]["startTime"]) < min_seconds:
        merged[1]["startTime"] = merged[0]["startTime"]
        merged.pop(0)

    # Below the useful minimum, a chapter list adds nothing over a plain seek bar.
    if len(merged) < MIN_CHAPTERS:
        return []

    return merged


def to_document(chapters: list[dict], *, title: str | None = None) -> dict:
    doc = {"version": "1.2.0", "chapters": chapters}
    if title:
        doc["title"] = title
    return doc


def dumps(timeline: Timeline, *, title: str | None = None, **kw) -> str:
    return json.dumps(to_document(build(timeline, **kw), title=title), indent=2) + "\n"
