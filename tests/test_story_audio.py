#!/usr/bin/env python3
"""Tests for story_audio — the synthesised bed and effects for bedtime shows.

Pure stdlib synthesis, so these run anywhere: no ffmpeg, no network.
The ffmpeg mix itself is exercised in CI builds, not here.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.lib import story_audio


def make_bp(**overrides):
    from scripts.lib import blueprint as bp_mod

    data = {
        "slug": "thumbelina",
        "show": "bedtime-stories",
        "template": "bedtime-story",
        "title": "Thumbelina",
        "description": "A bedtime story.",
        "sections": [
            {
                "id": "welcome",
                "title": "Settle in",
                "lines": [
                    {"voice": "storyteller", "text": "one two three four five six"},
                    {"voice": "storyteller", "text": "seven eight nine", "sfx": "chirp"},
                ],
            }
        ],
    }
    data.update(overrides)
    return bp_mod.from_dict(data)


class TestBed(unittest.TestCase):
    def test_bed_is_requested_length(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bed.wav"
            story_audio.render_bed(3.0, path)
            import wave

            with wave.open(str(path), "rb") as w:
                self.assertEqual(w.getframerate(), 48000)
                self.assertEqual(w.getnchannels(), 1)
                frames = w.getnframes()
        self.assertAlmostEqual(frames / 48000, 3.0, delta=0.05)

    def test_bed_fades_out_at_the_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bed.wav"
            story_audio.render_bed(12.0, path)
            import struct
            import wave

            with wave.open(str(path), "rb") as w:
                head = struct.unpack("<48000h", w.readframes(48000))
                n = w.getnframes()
                w.setpos(n - 24000)  # final half second
                tail = struct.unpack("<24000h", w.readframes(24000))
        head_peak = max(abs(s) for s in head)
        tail_peak = max(abs(s) for s in tail)
        self.assertGreater(head_peak, 1000)
        self.assertLess(tail_peak, head_peak * 0.02)


class TestSfx(unittest.TestCase):
    def test_every_effect_renders_short_mono_wav(self):
        for name, gen in story_audio.SFX.items():
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / f"{name}.wav"
                samples = gen()
                story_audio._write_wav(path, samples)
                import wave

                with wave.open(str(path), "rb") as w:
                    seconds = w.getnframes() / w.getframerate()
                    self.assertEqual(w.getnchannels(), 1)
                    self.assertEqual(w.getframerate(), 48000, name)
                self.assertGreater(seconds, 0.1, name)
                self.assertLess(seconds, 5.0, name)

    def test_effects_are_deterministic(self):
        a = story_audio.SFX["splash"]()
        b = story_audio.SFX["splash"]()
        self.assertEqual(a, b)


class TestGates(unittest.TestCase):
    def test_known_sfx_passes_and_unknown_fails(self):
        gates_mod = __import__("scripts.lib.gates", fromlist=["gates"])
        bp = make_bp()
        self.assertEqual(gates_mod.gate_story_audio(bp), [])

        bad = make_bp(
            sections=[
                {
                    "id": "welcome",
                    "title": "Settle in",
                    "lines": [
                        {"voice": "storyteller", "text": "one two three", "sfx": "explosion"}
                    ],
                }
            ]
        )
        findings = gates_mod.gate_story_audio(bad)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].level, "error")


if __name__ == "__main__":
    unittest.main()
