#!/usr/bin/env python3
"""blueprint_from_source.py — ingested transcript -> study notes -> episode.

    python3 scripts/blueprint_from_source.py <video_id> --notes
    python3 scripts/blueprint_from_source.py <video_id> --episode --show system-design

Stage one distils a source into study notes: outline, claims *with timestamps*,
glossary, the questions an interviewer would ask, misconceptions. Those notes
are worth keeping even if no episode is ever made from them.

Stage two drafts an episode blueprint against the `youtube-derived` template.
The draft is a starting point — the `youtube-ingest` skill requires a human or
agent pass over it before building, because a summary of someone else's video
is not worth publishing. The value added is the interview angle.

Uses `scripts/lib/llm.py`, which resolves a key from the environment or `pass`
at call time. With no key configured both stages fail cleanly and tell you so,
rather than producing something plausible and wrong.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.lib import ids as ids_mod
from scripts.lib import llm
from scripts.lib.blueprint import from_dict, save

SOURCES_DIR = ROOT / "content" / "sources" / "youtube"
NOTES_DIR = ROOT / "content" / "notes"

# Transcripts of hour-long videos exceed a comfortable single prompt; this
# keeps the distil call bounded while still covering the whole video.
MAX_TRANSCRIPT_CHARS = 60_000

NOTES_SYSTEM = """You produce study notes for a software engineer preparing for \
senior backend and system-design interviews in the payments domain.

You are given a transcript of a technical video. Extract what is useful for \
interview preparation. Be concrete and skeptical: if the source asserts \
something without support, say so rather than repeating it.

Return JSON with exactly these keys:
  outline:        [{heading, points: [string], timestamp: number}]
  claims:         [{claim: string, timestamp: number, confidence: "high"|"medium"|"low"}]
  glossary:       [{term, definition}]
  questions:      [{question, answer_shape}]   8-12 interview questions this material prepares you for
  misconceptions: [{belief, correction}]
  payments_angle: string   how this applies to multi-currency payments infrastructure
  verdict:        string   one sentence: is this source worth an episode, and why

Timestamps are seconds into the video, taken from the transcript markers."""

EPISODE_SYSTEM = """You draft podcast episode blueprints for a personal \
interview-prep show. The host is a senior backend engineer preparing for \
interviews at a payments company.

Write in the host's voice: first person, thinking aloud, concrete, no filler, \
no marketing tone. This is audio — every line is spoken, so:
  - no markdown, no bullet characters, no URLs, no ampersands
  - complexity in words ("O of n squared"), never symbols
  - one line per spoken beat, not per paragraph

You are given study notes derived from a source video. Write an ORIGINAL \
episode. Do not reuse the source's phrasing. Credit the source by name in the \
opening. The episode must add the interview angle the source did not cover.

Return JSON: {title, description, keywords: [string], sections: [{id, title, \
factual: bool, lines: [{voice: "narrator", text}]}]}

Use exactly these section ids, in this order: framing, core, gaps, questions, wrap.
Mark `factual: true` on any section stating verifiable claims about real systems."""


def load_source(video_id: str) -> dict:
    path = SOURCES_DIR / f"{video_id}.json"
    if not path.exists():
        raise SystemExit(
            f"ERROR: {path} not found — run `python3 scripts/ingest_youtube.py <url>` first"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def transcript_for_prompt(source: dict) -> str:
    """Timestamped transcript, truncated to a sane prompt size."""
    lines = [f"[{int(c['start'])}s] {c['text']}" for c in source.get("transcript", [])]
    text = "\n".join(lines)
    if len(text) <= MAX_TRANSCRIPT_CHARS:
        return text
    # Keep the opening and the closing: intros state the thesis, conclusions
    # state the takeaways, and the middle is the most compressible part.
    head = text[: int(MAX_TRANSCRIPT_CHARS * 0.6)]
    tail = text[-int(MAX_TRANSCRIPT_CHARS * 0.4) :]
    return f"{head}\n\n[... middle of transcript omitted for length ...]\n\n{tail}"


def distil(source: dict) -> dict:
    prompt = (
        f"Video: {source['title']}\n"
        f"Channel: {source['channel']}\n"
        f"Duration: {source['duration_seconds'] // 60} minutes\n\n"
        f"Transcript:\n{transcript_for_prompt(source)}"
    )
    return llm.complete_json("distiller", prompt, NOTES_SYSTEM, max_tokens=6000)


def notes_markdown(source: dict, notes: dict) -> str:
    out = [
        f"# {source['title']}",
        "",
        f"Source: [{source['channel']}]({source['url']}) · "
        f"{source['duration_seconds'] // 60} min · {source['word_count']} words",
        "",
        f"**Verdict:** {notes.get('verdict', '—')}",
        "",
        "## Outline",
        "",
    ]
    for item in notes.get("outline", []):
        out.append(f"### {item.get('heading', '')} ({int(item.get('timestamp', 0))}s)")
        out += [f"- {p}" for p in item.get("points", [])] + [""]

    out += ["## Claims", ""]
    for claim in notes.get("claims", []):
        out.append(
            f"- [{int(claim.get('timestamp', 0))}s] ({claim.get('confidence', '?')}) "
            f"{claim.get('claim', '')}"
        )

    out += ["", "## Interview questions", ""]
    for q in notes.get("questions", []):
        out += [f"**{q.get('question','')}**", "", f"{q.get('answer_shape','')}", ""]

    out += ["## Glossary", ""]
    for term in notes.get("glossary", []):
        out.append(f"- **{term.get('term','')}** — {term.get('definition','')}")

    out += ["", "## Misconceptions", ""]
    for m in notes.get("misconceptions", []):
        out.append(f"- ~~{m.get('belief','')}~~ → {m.get('correction','')}")

    out += ["", "## Payments angle", "", notes.get("payments_angle", "—"), ""]
    return "\n".join(out)


def compose_episode(source: dict, notes: dict, show: str) -> dict:
    prompt = (
        f"Source video: {source['title']} by {source['channel']} ({source['url']})\n\n"
        f"Study notes:\n{json.dumps(notes, indent=2)[:20000]}"
    )
    draft = llm.complete_json("writer", prompt, EPISODE_SYSTEM, max_tokens=12000)

    slug = ids_mod.slugify(f"yt-{draft.get('title', source['title'])}")
    return {
        "schema": 1,
        "slug": slug,
        "show": show,
        "template": "youtube-derived",
        "title": draft.get("title", source["title"]),
        "description": draft.get("description", ""),
        "keywords": draft.get("keywords", []),
        "voices": {"narrator": "narrator"},
        "sections": draft.get("sections", []),
        "notes_md": f"content/notes/{slug}.md",
        "sources": [
            {
                "type": "youtube",
                "id": source["id"],
                "url": source["url"],
                "title": source["title"],
                "channel": source["channel"],
                "used_for": ["outline", "claims"],
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("video_id")
    parser.add_argument("--notes", action="store_true", help="write study notes")
    parser.add_argument("--episode", action="store_true", help="draft an episode blueprint")
    parser.add_argument("--show", default="sd-youtube")
    args = parser.parse_args()

    if not (args.notes or args.episode):
        parser.error("pick --notes and/or --episode")

    source = load_source(args.video_id)
    print(f"=== {source['title']} ({source['word_count']} words) ===")

    if not llm.available():
        print(
            "ERROR: no LLM key configured. Set LLM_PASS_SSH_HOST=agent, or export "
            "DEEPSEEK_API_KEY. Run `python3 -m scripts.lib.llm --check` to diagnose.",
            file=sys.stderr,
        )
        return 1

    print("  distilling...")
    try:
        notes = distil(source)
    except llm.LlmError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    slug = ids_mod.slugify(f"yt-{source['title']}")
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    notes_path = NOTES_DIR / f"{slug}.md"
    notes_path.write_text(notes_markdown(source, notes), encoding="utf-8")
    print(f"  notes -> {notes_path}")
    print(f"  verdict: {notes.get('verdict', '—')}")

    if not args.episode:
        return 0

    print("  composing episode draft...")
    try:
        data = compose_episode(source, notes, args.show)
        bp = from_dict(data)
    except llm.LlmError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: draft was not a valid blueprint — {exc}", file=sys.stderr)
        return 1

    path = save(bp, ROOT / "content" / "blueprints" / bp.show / f"{bp.slug}.json")
    print(f"  draft -> {path}")
    print(f"  ~{bp.estimate_minutes():.1f} min across {len(bp.sections)} sections")
    print("\n  NEXT: read and rewrite the draft, then run the gates. A summary of")
    print("  someone else's video is not worth publishing — add the interview angle.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
