#!/usr/bin/env python3
"""make_artwork.py — generate the podcast cover art.

    python3 scripts/make_artwork.py

Writes site/artwork.png (1400x1400) plus 512 and 192 variants for the web app
manifest. Deterministic, so re-running produces byte-identical files.

Why this exists: `artwork_url` has always pointed at `/artwork.jpg`, but that
file was never created — not in git, not in R2. Podcast clients showed no cover
and Apple requires artwork between 1400 and 3000 pixels square, so the feed was
never submittable. Chrome also refuses to install a PWA whose manifest icons
fail to load, which is why "add to home screen" only ever made a bookmark.

Pure standard library: no Pillow, no ImageMagick, no ffmpeg. PNG is a simple
enough container to emit directly — signature, IHDR, IDAT of zlib-compressed
scanlines, IEND — and each size is drawn at its own resolution rather than
resampled, so there is no interpolation blur.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Straight from the app's CSS tokens so the icon matches the product.
INK = (0x1E, 0x33, 0x5C)      # --accent-ink, deep navy
PAPER = (0xF7, 0xF6, 0xF3)    # --bg, warm off-white
ACCENT = (0x7E, 0xA2, 0xE8)   # --accent in dark mode, for the highlight bar

# A five-bar level meter: unmistakable as audio at 48 pixels, still balanced at
# 1400. Heights as a fraction of the canvas, deliberately asymmetric.
BAR_HEIGHTS = [0.34, 0.62, 0.86, 0.52, 0.26]
HIGHLIGHT = 2  # the tall middle bar picks up the accent colour


def _chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_png(path: Path, size: int) -> Path:
    """Draw the mark at `size` and write a PNG."""
    bg = bytes(INK)

    # Geometry, all proportional so every size is the same design.
    margin = size * 0.17
    span = size - 2 * margin
    gap = span * 0.075
    bar_w = (span - gap * (len(BAR_HEIGHTS) - 1)) / len(BAR_HEIGHTS)
    radius = bar_w / 2
    cy = size / 2

    # Per-bar horizontal extent and vertical half-height.
    bars = []
    for i, frac in enumerate(BAR_HEIGHTS):
        x0 = margin + i * (bar_w + gap)
        half = (span * frac) / 2
        colour = bytes(ACCENT if i == HIGHLIGHT else PAPER)
        bars.append((x0, x0 + bar_w, half, colour))

    rows = bytearray()
    for y in range(size):
        row = bytearray(b"\x00")  # PNG filter byte: none
        py = y + 0.5

        # Which bars this scanline crosses, and their rounded-cap insets.
        spans = []
        for x0, x1, half, colour in bars:
            dy = abs(py - cy)
            if dy > half:
                continue
            # Round the ends: within `radius` of the tip, narrow the bar by the
            # circular offset so the cap is a semicircle rather than a corner.
            inset = 0.0
            depth = half - dy
            if depth < radius:
                inset = radius - (radius * radius - (radius - depth) ** 2) ** 0.5
            spans.append((x0 + inset, x1 - inset, colour))

        if not spans:
            row += bg * size
            rows += row
            continue

        x = 0
        for sx0, sx1, colour in spans:
            start = max(0, int(round(sx0)))
            end = min(size, int(round(sx1)))
            if end <= start:
                continue
            if start > x:
                row += bg * (start - x)
            row += colour * (end - start)
            x = end
        if x < size:
            row += bg * (size - x)
        rows += row

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)  # 8-bit truecolour
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + _chunk(b"IEND", b"")
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)
    return path


def main() -> int:
    targets = [
        (ROOT / "site" / "artwork.png", 1400),   # podcast cover (Apple: 1400-3000)
        (ROOT / "site" / "artwork-512.png", 512),
        (ROOT / "site" / "artwork-192.png", 192),
    ]
    for path, size in targets:
        write_png(path, size)
        kb = path.stat().st_size / 1024
        print(f"  {path.relative_to(ROOT)}  {size}x{size}  {kb:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
