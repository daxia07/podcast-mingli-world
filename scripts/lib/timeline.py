#!/usr/bin/env python3
"""timeline.py — turn measured per-line audio durations into exact offsets.

This is the piece that makes chapters and a synced transcript free for
TTS-generated episodes (docs/UPGRADE-SPEC.md §3.3). Each blueprint line is
synthesised to its own MP3 and measured; concatenation is `ffmpeg -c copy`,
which is sample-exact, so cumulative offsets are the real playback positions.

Everything here is pure arithmetic — no ffmpeg, no network — so the offset
logic is unit-testable on a machine with no audio tooling installed.

Invariant the tests pin down: the sum of every segment and every gap equals
the total duration. If that drifts, chapter markers drift with it.
"""

from __future__ import annotations

from dataclasses import dataclass

from .blueprint import GAP_BETWEEN_LINES, GAP_BETWEEN_SECTIONS, Blueprint


@dataclass
class TimedLine:
    section_id: str
    section_title: str
    voice: str
    text: str
    start: float
    end: float
    gap_after: float

    @property
    def duration(self) -> float:
        return self.end - self.start


@dataclass
class TimedSection:
    id: str
    title: str
    start: float
    end: float  # runs to the start of the next section, so chapters are contiguous

    @property
    def duration(self) -> float:
        return self.end - self.start


@dataclass
class Timeline:
    lines: list[TimedLine]
    sections: list[TimedSection]
    total: float

    def section_at(self, t: float) -> TimedSection | None:
        for section in self.sections:
            if section.start <= t < section.end:
                return section
        return self.sections[-1] if self.sections and t >= self.total else None


def flatten(bp: Blueprint) -> list[tuple[str, str, object]]:
    """(section_id, section_title, Line) in synthesis order."""
    return [
        (section.id, section.title, line)
        for section in bp.sections
        for line in section.lines
    ]


def gaps_for(bp: Blueprint) -> list[float]:
    """Silence to insert after each line, in synthesis order.

    A line ending a section gets the longer section gap; the final line of the
    episode gets none. Author-specified `pause_after` adds on top.
    """
    flat = flatten(bp)
    last_index_of_section = {}
    for idx, (sid, _, _) in enumerate(flat):
        last_index_of_section[sid] = idx

    gaps = []
    for idx, (sid, _, line) in enumerate(flat):
        if idx == len(flat) - 1:
            base = 0.0
        elif last_index_of_section[sid] == idx:
            base = GAP_BETWEEN_SECTIONS
        else:
            base = GAP_BETWEEN_LINES
        gaps.append(base + float(getattr(line, "pause_after", 0.0) or 0.0))
    return gaps


def build(bp: Blueprint, line_seconds: list[float]) -> Timeline:
    """Compose a Timeline from measured per-line durations.

    `line_seconds` must be in the same order as `flatten(bp)` — one entry per
    line, in seconds, measured *after* any per-segment post-processing, since
    loudnorm and silence trimming change length.
    """
    flat = flatten(bp)
    if len(line_seconds) != len(flat):
        raise ValueError(
            f"expected {len(flat)} durations (one per line), got {len(line_seconds)}"
        )

    gaps = gaps_for(bp)

    lines: list[TimedLine] = []
    cursor = 0.0
    for (sid, stitle, line), seconds, gap in zip(flat, line_seconds, gaps):
        start = cursor
        end = start + float(seconds)
        lines.append(
            TimedLine(
                section_id=sid,
                section_title=stitle,
                voice=line.voice,
                text=line.text,
                start=start,
                end=end,
                gap_after=gap,
            )
        )
        cursor = end + gap

    total = cursor

    # Sections run start-to-next-start so chapters tile the episode with no
    # holes — a gap between two lines belongs to the section that just ended.
    sections: list[TimedSection] = []
    for section in bp.sections:
        member = [ln for ln in lines if ln.section_id == section.id]
        if not member:
            continue
        sections.append(
            TimedSection(
                id=section.id,
                title=section.title,
                start=member[0].start,
                end=member[-1].end,
            )
        )
    for i in range(len(sections) - 1):
        sections[i].end = sections[i + 1].start
    if sections:
        sections[-1].end = total

    return Timeline(lines=lines, sections=sections, total=total)
