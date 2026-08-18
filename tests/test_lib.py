#!/usr/bin/env python3
"""Unit tests for scripts/lib — stdlib unittest, no third-party deps.

Run from the repo root:  python3 -m unittest discover -s tests -v

Deliberately runnable on a machine with no ffmpeg, no network and no API key:
the timing logic is pure arithmetic and everything else takes injected data.
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.lib import blueprint as bp_mod
from scripts.lib import chapters as chapters_mod
from scripts.lib import gates as gates_mod
from scripts.lib import ids as ids_mod
from scripts.lib import manifest as manifest_mod
from scripts.lib import timeline as timeline_mod
from scripts.lib import transcript as transcript_mod


def make_blueprint(**overrides):
    data = {
        "slug": "ep20-topological-sort",
        "show": "coding-prep",
        "template": "think-aloud-coding",
        "title": "Topological Sort",
        "description": "A think-aloud walkthrough.",
        "sections": [
            {
                "id": "cold-open",
                "title": "Cold open",
                "lines": [{"voice": "narrator", "text": "one two three four five"}],
            },
            {
                "id": "clarify",
                "title": "Clarify first",
                "lines": [
                    {"voice": "narrator", "text": "six seven eight"},
                    {"voice": "narrator", "text": "nine ten"},
                ],
            },
        ],
    }
    data.update(overrides)
    return bp_mod.from_dict(data)


class TestBlueprint(unittest.TestCase):
    def test_loads_a_valid_blueprint(self):
        bp = make_blueprint()
        self.assertEqual(bp.slug, "ep20-topological-sort")
        self.assertEqual(len(bp.sections), 2)
        self.assertEqual(bp.line_count(), 3)
        self.assertEqual(bp.word_count(), 10)

    def test_bare_string_line_uses_the_section_voice(self):
        bp = bp_mod.from_dict(
            {
                "slug": "x",
                "show": "s",
                "template": "t",
                "title": "T",
                "description": "d",
                "sections": [
                    {"id": "a", "title": "A", "voice": "interviewer", "lines": ["hello there"]}
                ],
            }
        )
        self.assertEqual(bp.sections[0].lines[0].voice, "interviewer")

    def test_missing_key_is_reported_by_name(self):
        with self.assertRaises(bp_mod.BlueprintError) as ctx:
            bp_mod.from_dict({"slug": "x"})
        self.assertIn("show", str(ctx.exception))
        self.assertIn("sections", str(ctx.exception))

    def test_duplicate_section_id_rejected(self):
        with self.assertRaises(bp_mod.BlueprintError) as ctx:
            bp_mod.from_dict(
                {
                    "slug": "x",
                    "show": "s",
                    "template": "t",
                    "title": "T",
                    "description": "d",
                    "sections": [
                        {"id": "a", "title": "A", "lines": ["one"]},
                        {"id": "a", "title": "B", "lines": ["two"]},
                    ],
                }
            )
        self.assertIn("duplicate section id", str(ctx.exception))

    def test_empty_line_text_rejected(self):
        with self.assertRaises(bp_mod.BlueprintError):
            bp_mod.from_dict(
                {
                    "slug": "x",
                    "show": "s",
                    "template": "t",
                    "title": "T",
                    "description": "d",
                    "sections": [{"id": "a", "title": "A", "lines": ["   "]}],
                }
            )

    def test_roundtrips_through_to_dict(self):
        bp = make_blueprint(keywords=["graph"], sources=[{"type": "youtube", "id": "x"}])
        again = bp_mod.from_dict(bp.to_dict())
        self.assertEqual(again.to_dict(), bp.to_dict())


class TestTimeline(unittest.TestCase):
    def test_offsets_accumulate_with_gaps(self):
        bp = make_blueprint()
        tl = timeline_mod.build(bp, [10.0, 20.0, 30.0])

        self.assertEqual(tl.lines[0].start, 0.0)
        self.assertEqual(tl.lines[0].end, 10.0)
        # End of section 1 -> the longer section gap.
        self.assertAlmostEqual(tl.lines[1].start, 10.0 + bp_mod.GAP_BETWEEN_SECTIONS)
        # Within a section -> the short line gap.
        self.assertAlmostEqual(
            tl.lines[2].start,
            10.0 + bp_mod.GAP_BETWEEN_SECTIONS + 20.0 + bp_mod.GAP_BETWEEN_LINES,
        )

    def test_total_equals_segments_plus_gaps(self):
        """The invariant chapter accuracy rests on."""
        bp = make_blueprint()
        durations = [10.0, 20.0, 30.0]
        tl = timeline_mod.build(bp, durations)
        expected = sum(durations) + sum(timeline_mod.gaps_for(bp))
        self.assertAlmostEqual(tl.total, expected, places=6)

    def test_sections_tile_without_holes(self):
        bp = make_blueprint()
        tl = timeline_mod.build(bp, [10.0, 20.0, 30.0])
        self.assertEqual(tl.sections[0].start, 0.0)
        for a, b in zip(tl.sections, tl.sections[1:]):
            self.assertEqual(a.end, b.start)
        self.assertAlmostEqual(tl.sections[-1].end, tl.total)

    def test_explicit_pause_extends_the_gap(self):
        bp = make_blueprint()
        bp.sections[1].lines[0].pause_after = 5.0
        tl = timeline_mod.build(bp, [1.0, 1.0, 1.0])
        self.assertAlmostEqual(tl.lines[2].start - tl.lines[1].end, bp_mod.GAP_BETWEEN_LINES + 5.0)

    def test_duration_count_mismatch_is_an_error(self):
        with self.assertRaises(ValueError):
            timeline_mod.build(make_blueprint(), [1.0, 2.0])

    def test_section_at_resolves_playback_position(self):
        bp = make_blueprint()
        tl = timeline_mod.build(bp, [10.0, 20.0, 30.0])
        self.assertEqual(tl.section_at(5.0).id, "cold-open")
        self.assertEqual(tl.section_at(40.0).id, "clarify")


class TestChapters(unittest.TestCase):
    def _timeline(self, per_line):
        data = {
            "slug": "x",
            "show": "s",
            "template": "t",
            "title": "T",
            "description": "d",
            "sections": [
                {"id": f"s{i}", "title": f"Section {i}", "lines": [f"line {i}"]}
                for i in range(len(per_line))
            ],
        }
        return timeline_mod.build(bp_mod.from_dict(data), per_line)

    def test_long_sections_become_chapters(self):
        chapters = chapters_mod.build(self._timeline([120.0, 120.0, 120.0]))
        self.assertEqual(len(chapters), 3)
        self.assertEqual(chapters[0]["startTime"], 0.0)
        self.assertEqual(chapters[0]["title"], "Section 0")

    def test_short_section_merges_into_the_previous_chapter(self):
        chapters = chapters_mod.build(self._timeline([120.0, 5.0, 120.0, 120.0]))
        self.assertEqual(len(chapters), 3)
        # The 5s section is absorbed, so chapter 0 now runs past its own end.
        self.assertGreater(chapters[0]["endTime"], 120.0)

    def test_short_first_section_folds_forward(self):
        chapters = chapters_mod.build(self._timeline([5.0, 120.0, 120.0, 120.0]))
        self.assertEqual(chapters[0]["startTime"], 0.0)
        self.assertEqual(len(chapters), 3)

    def test_chapters_remain_contiguous_after_merging(self):
        chapters = chapters_mod.build(self._timeline([120.0, 5.0, 120.0, 4.0, 120.0]))
        for a, b in zip(chapters, chapters[1:]):
            self.assertEqual(a["endTime"], b["startTime"])

    def test_too_few_chapters_returns_none_at_all(self):
        # Two chapters add nothing over a plain seek bar.
        self.assertEqual(chapters_mod.build(self._timeline([120.0, 120.0])), [])

    def test_long_titles_are_shortened(self):
        title = chapters_mod._shorten("A very long chapter title that runs past the Apple limit")
        self.assertLessEqual(len(title), chapters_mod.MAX_TITLE_CHARS)
        self.assertTrue(title.endswith("…"))


class TestTranscript(unittest.TestCase):
    def test_timestamp_format(self):
        self.assertEqual(transcript_mod.format_timestamp(0), "00:00:00.000")
        self.assertEqual(transcript_mod.format_timestamp(61.5), "00:01:01.500")
        self.assertEqual(transcript_mod.format_timestamp(3661.25), "01:01:01.250")

    def test_single_voice_has_no_speaker_tags(self):
        tl = timeline_mod.build(make_blueprint(), [10.0, 20.0, 30.0])
        vtt = transcript_mod.build(tl)
        self.assertTrue(vtt.startswith("WEBVTT"))
        self.assertNotIn("<v ", vtt)

    def test_two_voice_episode_labels_speakers(self):
        bp = bp_mod.from_dict(
            {
                "slug": "x",
                "show": "s",
                "template": "t",
                "title": "T",
                "description": "d",
                "sections": [
                    {
                        "id": "a",
                        "title": "A",
                        "lines": [
                            {"voice": "interviewer", "text": "Tell me about a wallet."},
                            {"voice": "candidate", "text": "It is a ledger."},
                        ],
                    }
                ],
            }
        )
        vtt = transcript_mod.build(timeline_mod.build(bp, [5.0, 5.0]))
        self.assertIn("<v Interviewer>", vtt)
        self.assertIn("<v Candidate>", vtt)

    def test_roundtrips_through_the_parser(self):
        tl = timeline_mod.build(make_blueprint(), [10.0, 20.0, 30.0])
        cues = transcript_mod.parse(transcript_mod.build(tl))
        self.assertEqual(len(cues), 3)
        self.assertEqual(cues[0]["start"], 0.0)
        self.assertEqual(cues[0]["text"], "one two three four five")

    def test_cue_holds_until_the_next_one_starts(self):
        tl = timeline_mod.build(make_blueprint(), [10.0, 20.0, 30.0])
        cues = transcript_mod.parse(transcript_mod.build(tl))
        for a, b in zip(cues, cues[1:]):
            self.assertAlmostEqual(a["end"], b["start"], places=2)


class TestIds(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(ids_mod.slugify("Two Sum — Think Aloud!"), "two-sum-think-aloud")
        self.assertEqual(ids_mod.slugify("  Café  Crème  "), "cafe-creme")
        self.assertEqual(ids_mod.slugify("!!!"), "episode")

    def test_slugify_truncates_on_a_word_boundary(self):
        slug = ids_mod.slugify("alpha beta gamma delta epsilon zeta eta theta", max_length=20)
        self.assertLessEqual(len(slug), 20)
        self.assertFalse(slug.endswith("-"))

    def test_next_id_fills_gaps(self):
        manifest = {"episodes": [{"id": 300}, {"id": 301}, {"id": 303}]}
        self.assertEqual(ids_mod.next_id(manifest), 302)

    def test_next_id_respects_the_floor(self):
        self.assertEqual(ids_mod.next_id({"episodes": [{"id": 5}]}), 300)

    def test_unique_slug_suffixes_on_collision(self):
        manifest = {"episodes": [{"slug": "two-sum"}, {"slug": "two-sum-2"}]}
        self.assertEqual(ids_mod.unique_slug("two-sum", manifest), "two-sum-3")
        self.assertEqual(ids_mod.unique_slug("three-sum", manifest), "three-sum")


class TestManifest(unittest.TestCase):
    def test_add_is_idempotent(self):
        manifest = {"episodes": []}
        entry = {"id": 5, "title": "Five"}
        manifest_mod.add_or_update(manifest, entry)
        manifest_mod.add_or_update(manifest, entry)
        self.assertEqual(len(manifest["episodes"]), 1)

    def test_update_merges_and_keeps_sort_order(self):
        manifest = {"episodes": [{"id": 9, "title": "Nine", "duration": "1:00"}]}
        manifest_mod.add_or_update(manifest, {"id": 3, "title": "Three"})
        manifest_mod.add_or_update(manifest, {"id": 9, "duration": "2:00"})
        self.assertEqual([e["id"] for e in manifest["episodes"]], [3, 9])
        nine = manifest["episodes"][1]
        self.assertEqual(nine["title"], "Nine")  # preserved
        self.assertEqual(nine["duration"], "2:00")  # updated

    def test_attach_to_unknown_playlist_raises(self):
        with self.assertRaises(KeyError):
            manifest_mod.attach_to_playlist({"playlists": {}}, "nope", 1)

    def test_rss_pubdate_is_rfc822(self):
        rss = manifest_mod.generate_rss(
            {"episodes": [{"id": 1, "date": "2026-07-06", "title": "T", "file_url": "u"}]}
        )
        self.assertIn("<pubDate>Mon, 06 Jul 2026 06:00:00 +1000</pubDate>", rss)
        self.assertNotIn("2026-07-06T06:00:00", rss)

    def test_rss_uses_itunes_duration(self):
        rss = manifest_mod.generate_rss(
            {"episodes": [{"id": 1, "date": "2026-07-06", "duration": "28:14", "file_url": "u"}]}
        )
        self.assertIn("<itunes:duration>28:14</itunes:duration>", rss)

    def test_rss_links_transcript_and_chapters_when_present(self):
        rss = manifest_mod.generate_rss(
            {
                "episodes": [
                    {
                        "id": 1,
                        "date": "2026-07-06",
                        "slug": "ep01",
                        "file_url": "u",
                        "has_transcript": True,
                        "has_chapters": True,
                    }
                ]
            }
        )
        self.assertIn("podcast:transcript", rss)
        self.assertIn("/transcripts/ep01.vtt", rss)
        self.assertIn("/chapters/ep01.json", rss)

    def test_rss_omits_artifacts_when_absent(self):
        rss = manifest_mod.generate_rss(
            {"episodes": [{"id": 1, "date": "2026-07-06", "slug": "ep01", "file_url": "u"}]}
        )
        self.assertNotIn("podcast:transcript", rss)


class TestGates(unittest.TestCase):
    def _levels(self, findings, gate):
        return [f for f in findings if f.gate == gate]

    def test_clean_blueprint_passes(self):
        # Long enough to clear the duration floor — the tiny shared fixture is
        # ~6 seconds of audio, which the gate rightly refuses to publish.
        bp = make_blueprint()
        bp.sections[0].lines[0].text = " ".join(["word"] * 400)
        findings = gates_mod.run_blueprint(bp)
        errors = [f for f in findings if f.level == gates_mod.ERROR]
        self.assertEqual(errors, [], msg=str([str(f) for f in errors]))

    def test_markdown_is_caught(self):
        bp = make_blueprint()
        bp.sections[0].lines[0].text = "This is **important** stuff"
        findings = self._levels(gates_mod.gate_tts_safety(bp), "tts_safety")
        self.assertTrue(findings)

    def test_big_o_in_symbols_is_caught(self):
        bp = make_blueprint()
        bp.sections[0].lines[0].text = "That is O(n^2) time"
        self.assertTrue(gates_mod.gate_tts_safety(bp))

    def test_url_is_caught(self):
        bp = make_blueprint()
        bp.sections[0].lines[0].text = "Go to https://example.com now"
        self.assertTrue(gates_mod.gate_tts_safety(bp))

    def test_unknown_voice_is_an_error(self):
        bp = make_blueprint()
        bp.sections[0].lines[0].voice = "robot"
        findings = gates_mod.gate_voice_roles(bp)
        self.assertEqual(findings[0].level, gates_mod.ERROR)

    def test_voice_override_resolves(self):
        bp = make_blueprint(voices={"host": "narrator"})
        bp.sections[0].lines[0].voice = "host"
        self.assertEqual(gates_mod.gate_voice_roles(bp), [])

    def test_missing_required_section_is_an_error(self):
        template = {
            "name": "think-aloud-coding",
            "sections": [
                {"id": "cold-open", "required": True},
                {"id": "clarify", "required": True},
                {"id": "complexity", "required": True},
            ],
        }
        findings = gates_mod.gate_template_coverage(make_blueprint(), template)
        messages = " ".join(f.message for f in findings)
        self.assertIn("complexity", messages)

    def test_factual_section_without_sources_is_an_error(self):
        bp = make_blueprint()
        bp.sections[0].factual = True
        findings = gates_mod.gate_claims(bp)
        self.assertEqual(findings[0].level, gates_mod.ERROR)

    def test_factual_section_with_sources_passes(self):
        bp = make_blueprint(sources=[{"type": "youtube", "id": "abc"}])
        bp.sections[0].factual = True
        self.assertEqual(gates_mod.gate_claims(bp), [])

    def test_banned_phrase_warns_but_does_not_block(self):
        bp = make_blueprint()
        bp.sections[0].lines[0].text = "Let us delve into the topic"
        findings = gates_mod.gate_tts_safety(bp)
        self.assertTrue(all(f.level == gates_mod.WARN for f in findings))

    def test_manifest_duplicate_id_is_an_error(self):
        manifest = {
            "episodes": [
                {"id": 1, "title": "A", "file_url": "https://x/episodes/a.mp3", "source": "tts"},
                {"id": 1, "title": "B", "file_url": "https://x/episodes/b.mp3", "source": "tts"},
            ]
        }
        findings = [f for f in gates_mod.run_manifest(manifest) if f.level == gates_mod.ERROR]
        self.assertTrue(any("duplicate id" in f.message for f in findings))

    def test_manifest_date_prefixed_series_url_is_an_error(self):
        manifest = {
            "episodes": [
                {
                    "id": 1,
                    "title": "A",
                    "file_url": "https://x/episodes/2026-07-06-two-sum.mp3",
                    "source": "tts",
                }
            ]
        }
        findings = [f for f in gates_mod.run_manifest(manifest) if f.level == gates_mod.ERROR]
        self.assertTrue(any("date-prefixed" in f.message for f in findings))

    def test_manifest_playlist_referencing_missing_episode(self):
        manifest = {
            "episodes": [
                {"id": 1, "title": "A", "file_url": "https://x/episodes/a.mp3", "source": "tts"}
            ],
            "playlists": {"show": {"episode_ids": [1, 99]}},
        }
        findings = [f for f in gates_mod.run_manifest(manifest) if f.level == gates_mod.ERROR]
        self.assertTrue(any("missing episode 99" in f.message for f in findings))


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestYouTubeIngest(unittest.TestCase):
    """dedupe_cues is the part of ingestion that runs without yt-dlp."""

    def setUp(self):
        import importlib
        self.mod = importlib.import_module("scripts.ingest_youtube")

    def test_video_id_from_several_url_shapes(self):
        vid = self.mod.video_id
        self.assertEqual(vid("https://www.youtube.com/watch?v=ruxGKk51aHo"), "ruxGKk51aHo")
        self.assertEqual(vid("https://youtu.be/ruxGKk51aHo"), "ruxGKk51aHo")
        self.assertEqual(vid("https://youtube.com/shorts/ruxGKk51aHo"), "ruxGKk51aHo")
        self.assertEqual(vid("ruxGKk51aHo"), "ruxGKk51aHo")

    def test_bad_url_raises(self):
        with self.assertRaises(self.mod.IngestError):
            self.mod.video_id("https://example.com/not-a-video")

    def test_dedupe_collapses_identical_consecutive_cues(self):
        cues = [
            {"start": 0.0, "end": 1.0, "text": "hello there"},
            {"start": 1.0, "end": 2.0, "text": "hello there"},
            {"start": 2.0, "end": 3.0, "text": "next line"},
        ]
        out = self.mod.dedupe_cues(cues)
        self.assertEqual([c["text"] for c in out], ["hello there", "next line"])
        self.assertEqual(out[0]["end"], 2.0)  # extended, not dropped

    def test_dedupe_collapses_the_rolling_caption_window(self):
        # YouTube auto-captions grow a line then repeat it with the next one.
        cues = [
            {"start": 0.0, "end": 1.0, "text": "the wallet is"},
            {"start": 1.0, "end": 2.0, "text": "the wallet is a ledger"},
            {"start": 2.0, "end": 3.0, "text": "and correctness matters"},
        ]
        out = self.mod.dedupe_cues(cues)
        self.assertEqual(
            [c["text"] for c in out], ["the wallet is a ledger", "and correctness matters"]
        )

    def test_dedupe_drops_blank_cues(self):
        out = self.mod.dedupe_cues([{"start": 0, "end": 1, "text": "   "}])
        self.assertEqual(out, [])


class TestBlueprintRequiredGate(unittest.TestCase):
    """The gate that keeps future episodes on the blueprint path."""

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "bp").mkdir()
        (self.root / "legacy.json").write_text(json.dumps({"ids": [1, 2]}))

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, manifest):
        return gates_mod.gate_new_episodes_have_blueprints(
            manifest,
            legacy_path=self.root / "legacy.json",
            blueprint_root=self.root / "bp",
        )

    def test_grandfathered_episodes_need_no_blueprint(self):
        self.assertEqual(self._run({"episodes": [{"id": 1}, {"id": 2}]}), [])

    def test_new_episode_without_a_blueprint_is_an_error(self):
        findings = self._run({"episodes": [{"id": 9, "title": "New"}]})
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].level, gates_mod.ERROR)
        self.assertIn("build_episode.py", findings[0].message)

    def test_new_episode_with_a_blueprint_passes(self):
        (self.root / "bp" / "x.json").write_text(json.dumps({"id": 9, "slug": "x"}))
        self.assertEqual(self._run({"episodes": [{"id": 9}]}), [])

    def test_missing_legacy_file_warns_rather_than_blocking(self):
        findings = gates_mod.gate_new_episodes_have_blueprints(
            {"episodes": [{"id": 9}]},
            legacy_path=self.root / "nope.json",
            blueprint_root=self.root / "bp",
        )
        self.assertEqual(findings[0].level, gates_mod.WARN)


class TestCalibration(unittest.TestCase):
    """MP3 frame padding makes the real file longer than the computed sum."""

    def test_calibrated_total_matches_the_measured_file(self):
        bp = make_blueprint()
        tl = timeline_mod.build(bp, [10.0, 20.0, 30.0])
        actual = tl.total + 1.69          # observed drift on a real 40-segment build
        cal = timeline_mod.calibrate(tl, actual)
        self.assertAlmostEqual(cal.total, actual, places=6)

    def test_calibration_preserves_spoken_durations(self):
        # The ffprobe measurements are correct; only the joins are wrong.
        bp = make_blueprint()
        tl = timeline_mod.build(bp, [10.0, 20.0, 30.0])
        cal = timeline_mod.calibrate(tl, tl.total + 2.0)
        for original, adjusted in zip(tl.lines, cal.lines):
            self.assertAlmostEqual(original.end - original.start,
                                   adjusted.end - adjusted.start, places=6)

    def test_drift_is_spread_evenly_across_joins(self):
        bp = make_blueprint()
        tl = timeline_mod.build(bp, [10.0, 20.0, 30.0])
        cal = timeline_mod.calibrate(tl, tl.total + 2.0)
        per_join = 2.0 / (len(tl.lines) - 1)
        for original, adjusted in zip(tl.lines[:-1], cal.lines[:-1]):
            self.assertAlmostEqual(adjusted.gap_after, original.gap_after + per_join, places=6)

    def test_sections_still_tile_after_calibration(self):
        bp = make_blueprint()
        cal = timeline_mod.calibrate(timeline_mod.build(bp, [10.0, 20.0, 30.0]), 65.0)
        for a, b in zip(cal.sections, cal.sections[1:]):
            self.assertAlmostEqual(a.end, b.start, places=6)
        self.assertAlmostEqual(cal.sections[-1].end, cal.total, places=6)

    def test_negative_drift_never_produces_a_negative_gap(self):
        bp = make_blueprint()
        tl = timeline_mod.build(bp, [10.0, 20.0, 30.0])
        cal = timeline_mod.calibrate(tl, tl.total - 100.0)
        for line in cal.lines:
            self.assertGreaterEqual(line.gap_after, 0.0)
            self.assertGreaterEqual(line.end, line.start)


class TestShowRegistryGate(unittest.TestCase):
    """A show must arrive complete or the frontend cannot place it."""

    def test_complete_playlist_passes(self):
        manifest = {"playlists": {"x": {"title": "X", "mono": "XX", "order": 1}}}
        self.assertEqual(gates_mod.gate_show_registry(manifest), [])

    def test_missing_mono_or_order_is_an_error(self):
        manifest = {"playlists": {"x": {"title": "X"}}}
        findings = gates_mod.gate_show_registry(manifest)
        fields = " ".join(f.message for f in findings)
        self.assertIn("mono", fields)
        self.assertIn("order", fields)
        self.assertTrue(all(f.level == gates_mod.ERROR for f in findings))

    def test_order_zero_is_valid(self):
        # Falsy but meaningful — the first show in the list.
        manifest = {"playlists": {"x": {"title": "X", "mono": "XX", "order": 0}}}
        self.assertEqual(gates_mod.gate_show_registry(manifest), [])


class TestShowsSyncedGate(unittest.TestCase):
    """The guard for the langgraph build that died mid-publish on 2026-08-18."""

    def _registry(self, tmp, show_ids):
        path = Path(tmp) / "shows.json"
        payload = {"schema": 1, "shows": {sid: {"title": sid} for sid in show_ids}}
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_synced_show_passes(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            manifest = {"playlists": {"x": {"episode_ids": []}}}
            registry = self._registry(tmp, ["x"])
            self.assertEqual(gates_mod.gate_shows_synced(manifest, shows_path=registry), [])

    def test_registered_but_unsynced_show_is_an_error(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            manifest = {"playlists": {"x": {"episode_ids": []}}}
            registry = self._registry(tmp, ["x", "langgraph"])
            findings = gates_mod.gate_shows_synced(manifest, shows_path=registry)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].level, gates_mod.ERROR)
            self.assertIn("langgraph", findings[0].message)

    def test_playlist_without_a_registry_entry_is_not_flagged(self):
        # apply_shows never removes a playlist, so one left behind by a deleted
        # show is expected rather than a failure.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            manifest = {"playlists": {"x": {}, "retired": {}}}
            registry = self._registry(tmp, ["x"])
            self.assertEqual(gates_mod.gate_shows_synced(manifest, shows_path=registry), [])

    def test_unreadable_registry_warns_rather_than_blocks(self):
        findings = gates_mod.gate_shows_synced({"playlists": {}}, shows_path="/nope/shows.json")
        self.assertEqual([f.level for f in findings], [gates_mod.WARN])

    def test_the_committed_manifest_is_in_sync(self):
        # The regression itself: the real registry against the real manifest.
        manifest = json.loads(Path("scripts/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(gates_mod.gate_shows_synced(manifest), [])


class TestAudioUniformity(unittest.TestCase):
    """The guard for the bug where episodes stopped playing at 11 seconds."""

    def setUp(self):
        from scripts.lib import audio
        self.audio = audio

    def _frame(self, version_bits, rate_idx, bitrate_idx, channel=3):
        # 4-byte MPEG audio frame header, Layer III, no CRC.
        b1 = 0xFF
        b2 = 0xE0 | (version_bits << 3) | (1 << 1)          # layer III
        b3 = (bitrate_idx << 4) | (rate_idx << 2)
        b4 = (channel << 6)
        return bytes([b1, b2, b3, b4])

    def _write(self, tmp, frames):
        import pathlib
        # Each header is followed by enough padding to reach its frame length.
        out = bytearray()
        for version_bits, rate_idx, bitrate_idx, size in frames:
            out += self._frame(version_bits, rate_idx, bitrate_idx)
            out += b"\x00" * (size - 4)
        p = pathlib.Path(tmp) / "t.mp3"
        p.write_bytes(bytes(out))
        return p

    def test_uniform_file_is_one_run(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            # MPEG1 (3) @ 48000 (idx 1), 64 kbps (idx 5) -> 192-byte frames
            p = self._write(tmp, [(3, 1, 5, 192)] * 8)
            runs = self.audio.scan(p)
            self.assertEqual(len(runs), 1)
            self.assertEqual(runs[0].fmt.sample_rate, 48000)
            self.assertEqual(runs[0].fmt.bitrate, 64)
            self.assertTrue(self.audio.is_uniform(p))

    def test_sample_rate_change_is_detected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            # The exact shape of the shipped bug: 48k speech, 24k silence, back.
            p = self._write(tmp, [(3, 1, 5, 192)] * 4 + [(2, 1, 6, 144)] * 2 + [(3, 1, 5, 192)] * 4)
            runs = self.audio.scan(p)
            self.assertEqual(len(runs), 3)
            self.assertEqual(runs[0].fmt.sample_rate, 48000)
            self.assertEqual(runs[1].fmt.sample_rate, 24000)
            self.assertFalse(self.audio.is_uniform(p))

    def test_describe_names_the_first_change_time(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            p = self._write(tmp, [(3, 1, 5, 192)] * 4 + [(2, 1, 6, 144)] * 2)
            text = self.audio.describe(p)
            self.assertIn("format changes", text)
            self.assertIn("24000", text)

    def test_id3_header_is_skipped(self):
        import tempfile, pathlib
        with tempfile.TemporaryDirectory() as tmp:
            p = self._write(tmp, [(3, 1, 5, 192)] * 4)
            body = p.read_bytes()
            # ID3v2 with a 20-byte syncsafe payload.
            p.write_bytes(b"ID3\x04\x00\x00\x00\x00\x00\x14" + b"\x00" * 20 + body)
            self.assertTrue(self.audio.is_uniform(p))
            self.assertEqual(self.audio.scan(p)[0].fmt.sample_rate, 48000)


class TestEpisodeUrlVersioning(unittest.TestCase):
    """Rebuilt episodes must bust caches without changing their identity."""

    def test_guid_drops_the_cache_buster(self):
        rss = manifest_mod.generate_rss({
            "episodes": [{
                "id": 1, "date": "2026-07-06",
                "file_url": "https://x/episodes/a.mp3?v=deadbeef",
            }]
        })
        self.assertIn("<guid isPermaLink=\"true\">https://x/episodes/a.mp3</guid>", rss)

    def test_enclosure_keeps_the_cache_buster(self):
        rss = manifest_mod.generate_rss({
            "episodes": [{
                "id": 1, "date": "2026-07-06",
                "file_url": "https://x/episodes/a.mp3?v=deadbeef",
            }]
        })
        self.assertIn('url="https://x/episodes/a.mp3?v=deadbeef"', rss)

    def test_url_convention_gate_accepts_a_version_query(self):
        manifest = {"episodes": [{
            "id": 1, "title": "A", "source": "tts",
            "file_url": "https://x/episodes/a.mp3?v=deadbeef",
        }]}
        errors = [f for f in gates_mod.run_manifest(manifest) if f.level == gates_mod.ERROR]
        self.assertEqual(errors, [], msg=str([str(e) for e in errors]))
