#!/usr/bin/env python3
"""blueprint.py — the episode blueprint: load, validate, normalise.

A blueprint is the authored artifact for one episode (docs/UPGRADE-SPEC.md §4.1).
It lives in git as JSON, is written either by a coding agent or by
`scripts/lib/llm.py`, and is the only supported input to `build_episode.py`.

Validation is hand-rolled rather than JSON Schema on purpose: the error
messages are the product here. An author needs "sections[2].lines[7]: text
contains markdown '**'", not "does not match schema". No third-party
dependency either, which keeps the pipeline importable on a bare runner.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

# Words per minute for a duration estimate. edge-tts at the project's default
# rate (-5%) lands near 145 for narration; two-voice dialogue runs slower
# because of the turn gaps, which `estimate_seconds` accounts for separately.
WORDS_PER_MINUTE = 145.0

# Silence inserted between lines, and extra silence at a section boundary.
GAP_BETWEEN_LINES = 0.35
GAP_BETWEEN_SECTIONS = 0.9

VALID_VOICE_ROLES = {"narrator", "interviewer", "candidate", "estimation", "legacy"}


class BlueprintError(ValueError):
    """The blueprint is malformed in a way that blocks any further work."""


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


@dataclass
class Line:
    voice: str
    text: str
    pause_after: float = 0.0

    def word_count(self) -> int:
        return len(self.text.split())


@dataclass
class Section:
    id: str
    title: str
    lines: list[Line]
    target_minutes: float | None = None
    factual: bool = False

    def word_count(self) -> int:
        return sum(line.word_count() for line in self.lines)


@dataclass
class Blueprint:
    slug: str
    show: str
    template: str
    title: str
    description: str
    sections: list[Section]
    id: int | None = None
    schema: int = 1
    keywords: list[str] = field(default_factory=list)
    voices: dict[str, str] = field(default_factory=dict)
    board: dict | None = None
    notes_md: str | None = None
    sources: list[dict] = field(default_factory=list)
    audio: str = "synth"  # "synth" | "existing" (migrated episodes)
    path: Path | None = None

    # -- derived ------------------------------------------------------------

    def word_count(self) -> int:
        return sum(section.word_count() for section in self.sections)

    def line_count(self) -> int:
        return sum(len(section.lines) for section in self.sections)

    def estimate_seconds(self) -> float:
        """Rough spoken duration, including the gaps the builder inserts."""
        speech = self.word_count() / WORDS_PER_MINUTE * 60.0
        gaps = (
            max(self.line_count() - 1, 0) * GAP_BETWEEN_LINES
            + max(len(self.sections) - 1, 0) * GAP_BETWEEN_SECTIONS
        )
        explicit = sum(
            line.pause_after for section in self.sections for line in section.lines
        )
        return speech + gaps + explicit

    def estimate_minutes(self) -> float:
        return self.estimate_seconds() / 60.0

    def voice_for(self, role: str) -> str:
        """Map a line's role through the blueprint's overrides to a TTS voice key."""
        return self.voices.get(role, role)

    def to_dict(self) -> dict:
        out = {
            "schema": self.schema,
            "id": self.id,
            "slug": self.slug,
            "show": self.show,
            "template": self.template,
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "voices": self.voices,
            "sections": [
                {
                    "id": s.id,
                    "title": s.title,
                    **({"target_minutes": s.target_minutes} if s.target_minutes else {}),
                    **({"factual": True} if s.factual else {}),
                    "lines": [
                        {
                            "voice": ln.voice,
                            "text": ln.text,
                            **({"pause_after": ln.pause_after} if ln.pause_after else {}),
                        }
                        for ln in s.lines
                    ],
                }
                for s in self.sections
            ],
        }
        if self.board:
            out["board"] = self.board
        if self.notes_md:
            out["notes_md"] = self.notes_md
        if self.sources:
            out["sources"] = self.sources
        if self.audio != "synth":
            out["audio"] = self.audio
        return out


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

_REQUIRED_TOP = ("slug", "show", "template", "title", "description", "sections")


def from_dict(data: dict, path: Path | None = None) -> Blueprint:
    """Build a Blueprint, raising BlueprintError on anything structural.

    Structural problems (missing keys, wrong types) raise here. Quality
    problems (too long, banned phrases, TTS-hostile text) are gates — see
    `gates.py` — so an author can see all of them at once instead of one per run.
    """
    if not isinstance(data, dict):
        raise BlueprintError("blueprint must be a JSON object")

    missing = [k for k in _REQUIRED_TOP if k not in data]
    if missing:
        raise BlueprintError(f"missing required keys: {', '.join(missing)}")

    raw_sections = data["sections"]
    if not isinstance(raw_sections, list) or not raw_sections:
        raise BlueprintError("sections must be a non-empty array")

    sections = []
    seen_ids: set[str] = set()
    for i, raw in enumerate(raw_sections):
        if not isinstance(raw, dict):
            raise BlueprintError(f"sections[{i}] must be an object")
        for key in ("id", "title", "lines"):
            if key not in raw:
                raise BlueprintError(f"sections[{i}]: missing '{key}'")

        sid = str(raw["id"])
        if sid in seen_ids:
            raise BlueprintError(f"sections[{i}]: duplicate section id '{sid}'")
        seen_ids.add(sid)

        raw_lines = raw["lines"]
        if not isinstance(raw_lines, list) or not raw_lines:
            raise BlueprintError(f"sections[{i}] ({sid}): lines must be a non-empty array")

        lines = []
        for j, rl in enumerate(raw_lines):
            if isinstance(rl, str):
                # Shorthand: a bare string uses the section's default voice.
                rl = {"voice": raw.get("voice", "narrator"), "text": rl}
            if not isinstance(rl, dict) or "text" not in rl:
                raise BlueprintError(
                    f"sections[{i}] ({sid}).lines[{j}]: must be a string or an object with 'text'"
                )
            text = str(rl["text"]).strip()
            if not text:
                raise BlueprintError(f"sections[{i}] ({sid}).lines[{j}]: text is empty")
            lines.append(
                Line(
                    voice=str(rl.get("voice", raw.get("voice", "narrator"))),
                    text=text,
                    pause_after=float(rl.get("pause_after", 0.0) or 0.0),
                )
            )

        sections.append(
            Section(
                id=sid,
                title=str(raw["title"]),
                lines=lines,
                target_minutes=(
                    float(raw["target_minutes"]) if raw.get("target_minutes") else None
                ),
                factual=bool(raw.get("factual", False)),
            )
        )

    episode_id = data.get("id")
    if episode_id is not None:
        try:
            episode_id = int(episode_id)
        except (TypeError, ValueError):
            raise BlueprintError(f"id must be an integer, got {data['id']!r}") from None

    return Blueprint(
        slug=str(data["slug"]),
        show=str(data["show"]),
        template=str(data["template"]),
        title=str(data["title"]),
        description=str(data["description"]),
        sections=sections,
        id=episode_id,
        schema=int(data.get("schema", 1)),
        keywords=list(data.get("keywords") or []),
        voices=dict(data.get("voices") or {}),
        board=data.get("board"),
        notes_md=data.get("notes_md"),
        sources=list(data.get("sources") or []),
        audio=str(data.get("audio", "synth")),
        path=path,
    )


def load(path: str | Path) -> Blueprint:
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BlueprintError(f"{path}: invalid JSON — {exc}") from None
    except OSError as exc:
        raise BlueprintError(f"{path}: cannot read — {exc}") from None
    return from_dict(data, path=path)


def save(bp: Blueprint, path: str | Path | None = None) -> Path:
    target = Path(path or bp.path or f"content/blueprints/{bp.show}/{bp.slug}.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(bp.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    bp.path = target
    return target


def iter_blueprints(root: str | Path = "content/blueprints"):
    """Yield every blueprint under `root`, sorted for stable CI output."""
    for path in sorted(Path(root).rglob("*.json")):
        yield load(path)
