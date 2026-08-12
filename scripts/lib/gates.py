#!/usr/bin/env python3
"""gates.py — quality gates for blueprints and the manifest.

These exist because the failure modes of this pipeline are expensive and quiet:
a malformed script only reveals itself as a 28-minute MP3 that says "asterisk
asterisk", a colliding episode id silently overwrites a published episode, and a
too-long draft blows the show's format without anyone noticing until playback.

Every gate returns findings rather than raising, so an author sees the whole
list at once. `error` blocks a build; `warn` is advisory.

    python3 -m scripts.lib.gates content/blueprints/coding-prep/ep20.json
    python3 -m scripts.lib.gates --manifest
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from .blueprint import VALID_VOICE_ROLES, Blueprint, BlueprintError, load

ERROR = "error"
WARN = "warn"


@dataclass
class Finding:
    gate: str
    level: str
    message: str
    where: str = ""

    def __str__(self) -> str:
        loc = f" [{self.where}]" if self.where else ""
        return f"{self.level.upper():5} {self.gate}{loc}: {self.message}"


# ---------------------------------------------------------------------------
# Text the TTS engine mishandles
# ---------------------------------------------------------------------------

# edge-tts reads these literally or chokes on them. `tts.py::preprocess_text`
# strips some, but a blueprint should never contain them in the first place —
# spoken text is spoken text.
TTS_HOSTILE = [
    (re.compile(r"\*\*|__"), "markdown emphasis (** or __)"),
    (re.compile(r"^#{1,6}\s", re.M), "markdown heading"),
    (re.compile(r"`"), "backtick"),
    (re.compile(r"={3,}|─{2,}"), "rule/marker characters"),
    (re.compile(r"https?://"), "URL — say the name instead"),
    (re.compile(r"\|"), "pipe (table syntax)"),
    (re.compile(r"[\U0001F300-\U0001FAFF☀-➿]"), "emoji"),
    (re.compile(r"\bO\(([^)]*)\)"), "big-O in symbols — write 'O of n squared'"),
    (re.compile(r"(?<=\w)/(?=\w)"), "slash between words — write 'or'"),
    (re.compile(r"&"), "ampersand — write 'and'"),
    (re.compile(r"^\s*[-*]\s+", re.M), "bullet marker"),
]

# Filler that makes generated prose sound generated.
BANNED_PHRASES = [
    "in today's fast-paced",
    "delve into",
    "it's important to note",
    "in conclusion",
    "as an ai",
    "let's dive in",
    "buckle up",
    "game-changer",
    "in this episode, we will explore",
]


def _findings_for_text(text: str, where: str, level: str = ERROR) -> list[Finding]:
    out = []
    for pattern, label in TTS_HOSTILE:
        if pattern.search(text):
            out.append(Finding("tts_safety", level, label, where))
    lowered = text.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            out.append(Finding("banned_phrases", WARN, f"filler phrase {phrase!r}", where))
    return out


# ---------------------------------------------------------------------------
# Blueprint gates
# ---------------------------------------------------------------------------


def gate_slug(bp: Blueprint) -> list[Finding]:
    from .ids import SLUG_RE

    if not SLUG_RE.match(bp.slug):
        return [
            Finding(
                "slug",
                ERROR,
                f"{bp.slug!r} must be lowercase words joined by single hyphens",
            )
        ]
    return []


def gate_voice_roles(bp: Blueprint) -> list[Finding]:
    out = []
    for section in bp.sections:
        for i, line in enumerate(section.lines):
            resolved = bp.voice_for(line.voice)
            if resolved not in VALID_VOICE_ROLES:
                out.append(
                    Finding(
                        "voice_roles",
                        ERROR,
                        f"unknown voice {line.voice!r} (resolves to {resolved!r}); "
                        f"known roles: {', '.join(sorted(VALID_VOICE_ROLES))}",
                        f"{section.id}.lines[{i}]",
                    )
                )
    return out


def gate_tts_safety(bp: Blueprint) -> list[Finding]:
    # For migrated episodes the audio already exists — this text only feeds the
    # transcript now, where "and/or" reads perfectly well. Blocking on it would
    # make published content unmigratable for a problem that can't be fixed.
    level = WARN if bp.audio == "existing" else ERROR

    out = []
    for section in bp.sections:
        for i, line in enumerate(section.lines):
            out.extend(_findings_for_text(line.text, f"{section.id}.lines[{i}]", level))
    return out


def gate_duration(bp: Blueprint, template: dict | None = None) -> list[Finding]:
    minutes = bp.estimate_minutes()
    if template:
        low = template.get("target_minutes", [None, None])[0]
        high = template.get("target_minutes", [None, None])[1]
        if low and minutes < low:
            return [
                Finding(
                    "duration",
                    WARN,
                    f"~{minutes:.1f} min is under the {template['name']} range "
                    f"({low}-{high} min) — the section plan is probably thin",
                )
            ]
        if high and minutes > high:
            return [
                Finding(
                    "duration",
                    WARN,
                    f"~{minutes:.1f} min exceeds the {template['name']} range "
                    f"({low}-{high} min)",
                )
            ]
    if minutes < 1:
        return [Finding("duration", ERROR, f"~{minutes:.1f} min — too short to publish")]
    return []


def gate_template_coverage(bp: Blueprint, template: dict | None) -> list[Finding]:
    if not template:
        return [
            Finding(
                "template_coverage",
                WARN,
                f"template {bp.template!r} not found in content/templates — coverage unchecked",
            )
        ]

    required = [s["id"] for s in template.get("sections", []) if s.get("required")]
    present = [s.id for s in bp.sections]

    # Already-published audio can't grow a section it never had. Migrated
    # episodes are graded on what they are, not on what the template now wants;
    # the sections still matter because they become chapter boundaries.
    missing_level = WARN if bp.audio == "existing" else ERROR

    out = []
    for sid in required:
        if sid not in present:
            out.append(
                Finding("template_coverage", missing_level, f"missing required section {sid!r}")
            )

    # Order matters for the shows built on a fixed ritual (the coding-prep
    # episodes teach the same eight steps in the same order every time).
    ordered = [sid for sid in present if sid in required]
    if ordered != [sid for sid in required if sid in present]:
        out.append(
            Finding(
                "template_coverage",
                WARN,
                f"required sections out of template order: {ordered}",
            )
        )

    known = {s["id"] for s in template.get("sections", [])}
    for sid in present:
        if sid not in known:
            out.append(
                Finding("template_coverage", WARN, f"section {sid!r} is not in the template")
            )
    return out


def gate_claims(bp: Blueprint) -> list[Finding]:
    """Sections marked factual must cite a source.

    The guard against a derived-from-YouTube episode inventing numbers.
    """
    out = []
    for section in bp.sections:
        if section.factual and not bp.sources:
            out.append(
                Finding(
                    "claims",
                    ERROR,
                    f"section {section.id!r} is marked factual but the blueprint has no sources[]",
                    section.id,
                )
            )
    return out


def gate_board(bp: Blueprint) -> list[Finding]:
    if bp.board is None:
        return []
    if not isinstance(bp.board, dict) or not isinstance(bp.board.get("tabs"), list):
        return [Finding("board", ERROR, "board must be an object with a 'tabs' array")]
    out = []
    for i, tab in enumerate(bp.board["tabs"]):
        if not isinstance(tab, dict) or "title" not in tab or "content" not in tab:
            out.append(
                Finding("board", ERROR, "each tab needs 'title' and 'content'", f"board.tabs[{i}]")
            )
    return out


def run_blueprint(
    bp: Blueprint, template: dict | None = None, manifest: dict | None = None
) -> list[Finding]:
    findings: list[Finding] = []
    findings += gate_slug(bp)
    findings += gate_voice_roles(bp)
    findings += gate_tts_safety(bp)
    findings += gate_template_coverage(bp, template)
    findings += gate_duration(bp, template)
    findings += gate_claims(bp)
    findings += gate_board(bp)
    if manifest is not None:
        findings += gate_id_unique(bp, manifest)
    return findings


def gate_id_unique(bp: Blueprint, manifest: dict) -> list[Finding]:
    out = []
    episodes = manifest.get("episodes", [])
    for ep in episodes:
        if bp.id is not None and ep.get("id") == bp.id and ep.get("slug") != bp.slug:
            out.append(
                Finding(
                    "id_unique",
                    ERROR,
                    f"id {bp.id} already belongs to {ep.get('title', '?')!r}",
                )
            )
        if ep.get("slug") == bp.slug and ep.get("id") != bp.id:
            out.append(
                Finding(
                    "id_unique",
                    ERROR,
                    f"slug {bp.slug!r} already used by episode {ep.get('id')}",
                )
            )
    return out


# ---------------------------------------------------------------------------
# Manifest-wide gates
# ---------------------------------------------------------------------------

# An optional ?v=<hash> cache-buster is expected: episodes are rebuilt in place,
# and without a URL change a client that cached a broken build keeps playing it.
FILE_URL_RE = re.compile(r"^https?://[^/]+/episodes/[A-Za-z0-9._-]+\.mp3(\?v=[a-f0-9]{6,32})?$")
# Historic bug (AGENTS.md gotcha #8): series files once carried a date prefix.
DATE_PREFIXED = re.compile(r"/episodes/\d{4}-\d{2}-\d{2}-[a-z]")


def run_manifest(manifest: dict) -> list[Finding]:
    out: list[Finding] = []
    episodes = manifest.get("episodes", [])

    seen: dict[int, str] = {}
    for ep in episodes:
        eid = ep.get("id")
        title = ep.get("title", "?")
        if eid in seen:
            out.append(
                Finding("manifest_integrity", ERROR, f"duplicate id {eid}: {seen[eid]!r} and {title!r}")
            )
        seen[eid] = title

        url = ep.get("file_url", "")
        if not FILE_URL_RE.match(url):
            out.append(
                Finding("url_convention", ERROR, f"episode {eid}: bad file_url {url!r}")
            )
        elif DATE_PREFIXED.search(url):
            out.append(
                Finding("url_convention", ERROR, f"episode {eid}: date-prefixed series URL {url!r}")
            )

        if not ep.get("source"):
            out.append(Finding("manifest_integrity", WARN, f"episode {eid}: missing 'source'"))

    known_ids = set(seen)
    for pid, playlist in (manifest.get("playlists") or {}).items():
        ids = playlist.get("episode_ids", [])
        if not ids:
            out.append(Finding("manifest_integrity", WARN, f"playlist {pid!r} has no episodes"))
        for eid in ids:
            if eid not in known_ids:
                out.append(
                    Finding(
                        "manifest_integrity",
                        ERROR,
                        f"playlist {pid!r} references missing episode {eid}",
                    )
                )
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def load_template(name: str, root: str | Path = "content/templates") -> dict | None:
    path = Path(root) / f"{name}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def report(findings: list[Finding], label: str) -> int:
    errors = [f for f in findings if f.level == ERROR]
    warns = [f for f in findings if f.level == WARN]

    if not findings:
        print(f"{label}: clean")
        return 0

    for finding in errors + warns:
        print(f"  {finding}")
    print(f"{label}: {len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors else 0


def gate_show_registry(manifest: dict) -> list[Finding]:
    """Playlists must carry everything the frontend needs to render them.

    The AWS AI Practitioner show shipped with episodes but rendered nowhere,
    because app.js took its ordering from a hardcoded list. app.js now reads
    these fields from the manifest, so a show missing them silently falls back
    to a generic tile at the end of the list.
    """
    out = []
    for pid, playlist in (manifest.get("playlists") or {}).items():
        for field in ("title", "mono", "order"):
            if playlist.get(field) in (None, ""):
                out.append(
                    Finding(
                        "show_registry",
                        ERROR,
                        f"playlist {pid!r} is missing {field!r} — add it to "
                        "content/shows.json and re-sync",
                    )
                )
    return out


def gate_new_episodes_have_blueprints(
    manifest: dict,
    *,
    legacy_path: str | Path = "content/legacy-episodes.json",
    blueprint_root: str | Path = "content/blueprints",
) -> list[Finding]:
    """Every episode published from now on must have a blueprint.

    This is what keeps the content system from decaying back into one-off
    scripts. The 157 episodes that predate it are grandfathered by id in
    `content/legacy-episodes.json`; anything new has to come through
    `build_episode.py`, which means it has been gated, has a chapter track and
    has a transcript.
    """
    legacy = Path(legacy_path)
    if not legacy.exists():
        return [
            Finding(
                "blueprint_required",
                WARN,
                f"{legacy_path} missing — cannot tell new episodes from grandfathered ones",
            )
        ]

    try:
        grandfathered = set(json.loads(legacy.read_text(encoding="utf-8")).get("ids", []))
    except (OSError, json.JSONDecodeError) as exc:
        return [Finding("blueprint_required", ERROR, f"{legacy_path}: {exc}")]

    have: set[int] = set()
    for path in Path(blueprint_root).rglob("*.json"):
        try:
            bid = json.loads(path.read_text(encoding="utf-8")).get("id")
        except (OSError, json.JSONDecodeError):
            continue
        if bid is not None:
            have.add(bid)

    out = []
    for ep in manifest.get("episodes", []):
        eid = ep.get("id")
        if eid in grandfathered or eid in have:
            continue
        out.append(
            Finding(
                "blueprint_required",
                ERROR,
                f"episode {eid} ({ep.get('title', '?')!r}) has no blueprint. "
                "New episodes must be built with scripts/build_episode.py "
                "(see .claude/skills/episode-new).",
            )
        )
    return out


def gate_manifest_parity() -> list[Finding]:
    """The two committed manifest copies must be byte-identical.

    They silently diverged once already: `site/manifest.json` sat 102 episodes
    behind and still carried the date-prefixed URLs fixed in af24d96. It is only
    reachable when the R2-backed Function fails — exactly when you least want
    stale data.
    """
    try:
        a = json.loads(Path("scripts/manifest.json").read_text(encoding="utf-8"))
        b = json.loads(Path("site/manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [Finding("manifest_parity", ERROR, f"cannot compare copies: {exc}")]

    if a == b:
        return []

    ids_a = {e.get("id") for e in a.get("episodes", [])}
    ids_b = {e.get("id") for e in b.get("episodes", [])}
    detail = f"{len(ids_a)} vs {len(ids_b)} episodes"
    if ids_a - ids_b:
        detail += f"; missing from site/: {sorted(ids_a - ids_b)[:5]}…"
    return [
        Finding(
            "manifest_parity",
            ERROR,
            f"scripts/manifest.json and site/manifest.json differ ({detail}). "
            "Copy the scripts/ copy over the site/ one.",
        )
    ]


def main(argv: list[str]) -> int:
    if "--manifest" in argv:
        rc = report(gate_manifest_parity(), "manifest parity")
        for path in ("scripts/manifest.json", "site/manifest.json"):
            p = Path(path)
            if not p.exists():
                print(f"{path}: missing")
                rc = 1
                continue
            try:
                manifest = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                print(f"{path}: invalid JSON — {exc}")
                rc = 1
                continue
            rc |= report(run_manifest(manifest) + gate_show_registry(manifest), path)

        manifest = json.loads(Path("scripts/manifest.json").read_text(encoding="utf-8"))
        rc |= report(gate_new_episodes_have_blueprints(manifest), "blueprint coverage")
        return rc

    if not argv:
        print(__doc__)
        return 0

    rc = 0
    for arg in argv:
        try:
            bp = load(arg)
        except BlueprintError as exc:
            print(f"  ERROR blueprint: {exc}")
            rc = 1
            continue
        rc |= report(run_blueprint(bp, load_template(bp.template)), arg)
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
