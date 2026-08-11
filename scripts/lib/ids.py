#!/usr/bin/env python3
"""ids.py — episode ids and slugs.

Two conventions this project already relies on, now enforced in one place:

* The **slug** is the filename stem for every artifact of an episode —
  `episodes/{slug}.mp3`, `transcripts/{slug}.vtt`, `chapters/{slug}.json`,
  `boards/{slug}.json`. Daily episodes use the date as their slug.
* The **id** is the manifest primary key. Series generators used to hardcode
  ids (300+, 46+, …) and collisions silently overwrote published episodes
  (AGENTS.md gotcha #7). Allocation goes through `next_id` now.
"""

from __future__ import annotations

import re
import unicodedata

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_SLUG_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Series ids start well above the daily sequence so the two never race.
SERIES_ID_FLOOR = 300


def slugify(text: str, *, max_length: int = 60) -> str:
    """A filename-safe slug. Deterministic — the same title always maps here."""
    normalised = unicodedata.normalize("NFKD", text)
    ascii_only = normalised.encode("ascii", "ignore").decode("ascii").lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", ascii_only).strip("-")
    cleaned = re.sub(r"-{2,}", "-", cleaned)

    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip("-")
        # Don't end on a half-word if a clean boundary is close by.
        if "-" in cleaned and len(cleaned.rsplit("-", 1)[0]) >= max_length * 0.7:
            cleaned = cleaned.rsplit("-", 1)[0]

    return cleaned or "episode"


def is_valid_slug(slug: str) -> bool:
    return bool(SLUG_RE.match(slug))


def is_daily_slug(slug: str) -> bool:
    return bool(DATE_SLUG_RE.match(slug))


def existing_ids(manifest: dict) -> set[int]:
    return {
        ep["id"]
        for ep in manifest.get("episodes", [])
        if isinstance(ep.get("id"), int)
    }


def next_id(manifest: dict, *, floor: int = SERIES_ID_FLOOR) -> int:
    """Lowest free id at or above `floor`.

    Reuses gaps rather than always appending, so a deleted episode's id comes
    back into circulation instead of the sequence drifting upward forever.
    """
    taken = existing_ids(manifest)
    candidate = floor
    while candidate in taken:
        candidate += 1
    return candidate


def unique_slug(base: str, manifest: dict) -> str:
    """`base`, or `base-2`, `base-3`, … if the manifest already uses it."""
    used = {ep.get("slug") for ep in manifest.get("episodes", [])}
    used |= {
        (ep.get("filename") or "").removesuffix(".mp3")
        for ep in manifest.get("episodes", [])
    }
    used.discard("")
    used.discard(None)

    if base not in used:
        return base
    n = 2
    while f"{base}-{n}" in used:
        n += 1
    return f"{base}-{n}"
