#!/usr/bin/env python3
"""ingest_youtube.py — a video's *text*, not its audio.

    python3 scripts/ingest_youtube.py https://youtube.com/watch?v=...
    python3 scripts/ingest_youtube.py --from-candidates
    python3 scripts/ingest_youtube.py --backfill        # existing re-hosted eps

Writes `content/sources/youtube/<video_id>.json`: title, channel, duration, the
video's own chapter markers, and a timestamped transcript. That file is the
input to `blueprint_from_source.py`, which distils study notes and drafts an
original episode.

Subtitles come from yt-dlp when the video has them (uploaded or auto-generated)
and from faster-whisper when it doesn't. We store text, and — for new material —
no audio: the derived episode is written in our own voice, so there is nothing
to re-host.

This replaces the download-only `download_youtube.py`, which pulled MP3s from a
hardcoded list of 14 URLs and extracted no text at all.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.lib import transcript as transcript_mod

SOURCES_DIR = ROOT / "content" / "sources" / "youtube"
DATA_DIR = ROOT / "data"

VIDEO_ID_RE = re.compile(r"(?:v=|youtu\.be/|/shorts/|/embed/)([A-Za-z0-9_-]{11})")


class IngestError(RuntimeError):
    pass


def video_id(url: str) -> str:
    match = VIDEO_ID_RE.search(url)
    if match:
        return match.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url  # already an id
    raise IngestError(f"could not find a video id in {url!r}")


def require(tool: str, hint: str) -> None:
    if not shutil.which(tool):
        raise IngestError(f"{tool} not installed — {hint}")


def _run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)


def fetch_metadata_and_subs(url: str, workdir: Path) -> tuple[dict, str | None]:
    """yt-dlp: info JSON plus an English VTT if one exists."""
    require("yt-dlp", "pip install yt-dlp")

    result = _run(
        [
            "yt-dlp",
            "--skip-download",
            "--write-info-json",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs", "en.*",
            "--sub-format", "vtt",
            "--output", "%(id)s",
            url,
        ],
        cwd=workdir,
    )
    if result.returncode != 0:
        raise IngestError(f"yt-dlp failed: {result.stderr.strip()[:300]}")

    info_files = list(workdir.glob("*.info.json"))
    if not info_files:
        raise IngestError("yt-dlp produced no info JSON")
    info = json.loads(info_files[0].read_text(encoding="utf-8"))

    vtt_files = sorted(workdir.glob("*.vtt"))
    vtt = vtt_files[0].read_text(encoding="utf-8") if vtt_files else None
    return info, vtt


def whisper_transcribe(url: str, workdir: Path) -> str:
    """Fallback for videos with no subtitles at all."""
    require("yt-dlp", "pip install yt-dlp")
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise IngestError(
            "video has no subtitles and faster-whisper is not installed "
            "(pip install faster-whisper)"
        ) from None

    audio = workdir / "audio.m4a"
    result = _run(
        ["yt-dlp", "-f", "bestaudio", "--output", str(audio), url]
    )
    if result.returncode != 0 or not audio.exists():
        raise IngestError(f"audio download failed: {result.stderr.strip()[:200]}")

    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(audio), vad_filter=True)

    lines = ["WEBVTT", ""]
    for i, seg in enumerate(segments, start=1):
        lines += [
            str(i),
            f"{transcript_mod.format_timestamp(seg.start)} --> "
            f"{transcript_mod.format_timestamp(seg.end)}",
            seg.text.strip(),
            "",
        ]
    return "\n".join(lines)


def dedupe_cues(cues: list[dict]) -> list[dict]:
    """YouTube auto-captions repeat each line as a rolling two-line window.

    Left alone this doubles the transcript and wrecks any word count taken
    from it, so identical consecutive text is collapsed.
    """
    out: list[dict] = []
    for cue in cues:
        text = " ".join(cue["text"].split())
        if not text:
            continue
        if out and out[-1]["text"] == text:
            out[-1]["end"] = cue["end"]
            continue
        if out and text.startswith(out[-1]["text"]):
            # Rolling window: the new cue contains the previous one.
            out[-1]["text"] = text
            out[-1]["end"] = cue["end"]
            continue
        out.append({"start": cue["start"], "end": cue["end"], "text": text})
    return out


def build_source(info: dict, vtt: str) -> dict:
    cues = dedupe_cues(transcript_mod.parse(vtt))
    chapters = [
        {"start": float(c.get("start_time", 0)), "title": c.get("title", "")}
        for c in (info.get("chapters") or [])
    ]
    return {
        "schema": 1,
        "id": info.get("id"),
        "url": info.get("webpage_url") or f"https://youtu.be/{info.get('id')}",
        "title": info.get("title", ""),
        "channel": info.get("uploader") or info.get("channel", ""),
        "published": str(info.get("upload_date") or ""),
        "duration_seconds": int(info.get("duration") or 0),
        "chapters": chapters,
        "transcript": cues,
        "text": " ".join(c["text"] for c in cues),
        "word_count": sum(len(c["text"].split()) for c in cues),
        "license_note": (
            "Transcript stored for personal study. Source audio is not re-hosted; "
            "derived episodes are written in our own words with attribution."
        ),
    }


def ingest(url: str, *, force: bool = False) -> Path | None:
    vid = video_id(url)
    out_path = SOURCES_DIR / f"{vid}.json"

    if out_path.exists() and not force:
        print(f"  SKIP {vid} — already ingested (use --force to refresh)")
        return out_path

    SOURCES_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f"yt_{vid}_") as tmp:
        workdir = Path(tmp)
        info, vtt = fetch_metadata_and_subs(url, workdir)
        if not vtt:
            print("  no subtitles published — falling back to whisper")
            vtt = whisper_transcribe(url, workdir)

        source = build_source(info, vtt)

    if source["word_count"] < 200:
        print(f"  WARNING {vid}: only {source['word_count']} words — transcript looks empty")

    out_path.write_text(json.dumps(source, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"  ok {vid}  {source['duration_seconds'] // 60}min  "
        f"{source['word_count']} words  {len(source['chapters'])} chapters  "
        f"{source['title'][:48]}"
    )
    return out_path


def from_candidates() -> list[str]:
    path = DATA_DIR / "candidates.json"
    if not path.exists():
        raise IngestError("no data/candidates.json — run scripts/curate.py first")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [c["url"] for c in payload.get("candidates", []) if c.get("kind") == "youtube"]


def backfill_urls() -> list[str]:
    """URLs of the already-published, re-hosted YouTube episodes."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from download_youtube import YOUTUBE_VIDEOS

    return [v["url"] for v in YOUTUBE_VIDEOS]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("urls", nargs="*", help="video URLs or ids")
    parser.add_argument("--from-candidates", action="store_true")
    parser.add_argument("--backfill", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    urls = list(args.urls)
    try:
        if args.from_candidates:
            urls += from_candidates()
        if args.backfill:
            urls += backfill_urls()
    except IngestError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not urls:
        parser.error("give a URL, or --from-candidates / --backfill")

    print(f"=== ingest_youtube: {len(urls)} video(s) ===")
    failures = 0
    for url in urls:
        try:
            ingest(url, force=args.force)
        except IngestError as exc:
            print(f"  FAIL {url}: {exc}")
            failures += 1

    print(f"\n  {len(urls) - failures} ingested, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
