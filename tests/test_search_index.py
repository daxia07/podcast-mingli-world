#!/usr/bin/env python3
"""Tests for scripts/build_search_index.py — the moment index.

The index is what makes Search able to answer "where was that said". These
cover the shaping rules (what becomes a moment and what is dropped) and the
two safety properties: a byte-stable render, so a no-op rebuild produces no
diff, and --no-shrink, so a flaky network cannot quietly delete coverage.
"""

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scripts.build_search_index as bsi  # noqa: E402

VTT = """WEBVTT

1
00:00:00.000 --> 00:00:12.500
A vector database is how retrieval augmented generation finds context.

2
00:00:12.500 --> 00:00:14.000
Right.

3
00:01:05.250 --> 00:01:30.000
<v Host>Embeddings turn text into numbers where meaning becomes distance.
"""

CHAPTERS = json.dumps(
    {
        "version": "1.2.0",
        "chapters": [
            {"startTime": 0, "title": "The concepts"},
            {"startTime": 65.25, "title": "  Vector stores  "},
            {"startTime": 200, "title": ""},
        ],
    }
)


class TestShaping(unittest.TestCase):
    def test_every_cue_becomes_a_moment_with_its_start(self):
        moments = bsi.moments_from_vtt(VTT)
        self.assertEqual(moments[0][0], 0.0)
        self.assertIn("vector database", moments[0][1])

    def test_a_fragment_shorter_than_the_floor_is_dropped(self):
        texts = [m[1] for m in bsi.moments_from_vtt(VTT)]
        self.assertNotIn("Right.", texts, "one-word cues are noise in a result list")
        self.assertEqual(len(texts), 2)

    def test_a_speaker_label_is_stripped_from_the_text(self):
        last = bsi.moments_from_vtt(VTT)[-1]
        self.assertFalse(last[1].startswith("<v"))
        self.assertTrue(last[1].startswith("Embeddings"))
        self.assertEqual(last[0], 65.2, "timestamps are rounded to a tenth")

    def test_chapters_are_trimmed_and_empty_titles_dropped(self):
        chapters = bsi.chapters_from_doc(CHAPTERS)
        self.assertEqual(chapters, [[0.0, "The concepts"], [65.2, "Vector stores"]])

    def test_a_corrupt_chapter_document_yields_nothing_rather_than_raising(self):
        self.assertEqual(bsi.chapters_from_doc("{not json"), [])


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.manifest = {
            "episodes": [
                {"id": 1, "slug": "with-both", "has_transcript": True, "has_chapters": True},
                {"id": 2, "slug": "plain-legacy"},
                {"id": 3, "slug": "claims-but-missing", "has_transcript": True},
            ]
        }
        self._read = bsi.read_artifact
        bsi.read_artifact = lambda slug, kind, offline=False: (
            (VTT if kind == "vtt" else CHAPTERS) if slug == "with-both" else None
        )

    def tearDown(self):
        bsi.read_artifact = self._read

    def test_only_episodes_with_readable_artifacts_are_indexed(self):
        index = bsi.build(self.manifest, verbose=False)
        self.assertEqual(list(index["episodes"]), ["1"])

    def test_an_indexed_episode_carries_its_slug_lines_and_chapters(self):
        entry = bsi.build(self.manifest, verbose=False)["episodes"]["1"]
        self.assertEqual(entry["s"], "with-both")
        self.assertEqual(len(entry["l"]), 2)
        self.assertEqual(len(entry["c"]), 2)

    def test_a_legacy_episode_is_skipped_without_a_fetch(self):
        # An episode with neither flag must not cost a network round trip.
        calls = []
        bsi.read_artifact = lambda slug, kind, offline=False: calls.append(slug)
        bsi.build({"episodes": [{"id": 2, "slug": "plain-legacy"}]}, verbose=False)
        self.assertEqual(calls, [])

    def test_the_render_is_byte_stable(self):
        index = bsi.build(self.manifest, verbose=False)
        self.assertEqual(bsi.render(index), bsi.render(bsi.build(self.manifest, verbose=False)))
        self.assertTrue(bsi.render(index).endswith("\n"))


class TestNoShrink(unittest.TestCase):
    """--no-shrink is the guard against a network wobble deleting coverage."""

    def run_main(self, argv, out):
        old = sys.argv
        sys.argv = ["build_search_index.py", "--out", str(out)] + argv
        try:
            return bsi.main()
        finally:
            sys.argv = old

    def test_a_thinner_build_leaves_the_committed_index_alone(self):
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "search-index.json"
            fat = {"version": 1, "episodes": {"1": {"s": "a"}, "2": {"s": "b"}}}
            out.write_text(bsi.render(fat), encoding="utf-8")

            manifest = {"episodes": [{"id": 1, "slug": "a", "has_transcript": True}]}
            self._patch(manifest, VTT)
            self.assertEqual(self.run_main(["--no-shrink"], out), 0)
            self.assertEqual(len(json.loads(out.read_text())["episodes"]), 2)

    def test_without_the_flag_the_thinner_build_wins(self):
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "search-index.json"
            out.write_text(
                bsi.render({"version": 1, "episodes": {"1": {"s": "a"}, "2": {"s": "b"}}}),
                encoding="utf-8",
            )
            manifest = {"episodes": [{"id": 1, "slug": "a", "has_transcript": True}]}
            self._patch(manifest, VTT)
            self.assertEqual(self.run_main([], out), 0)
            self.assertEqual(len(json.loads(out.read_text())["episodes"]), 1)

    def _patch(self, manifest, vtt):
        self.addCleanup(setattr, bsi, "load_manifest", bsi.load_manifest)
        self.addCleanup(setattr, bsi, "read_artifact", bsi.read_artifact)
        bsi.load_manifest = lambda: manifest
        bsi.read_artifact = lambda slug, kind, offline=False: vtt if kind == "vtt" else None


class TestCommittedIndex(unittest.TestCase):
    """The index that ships is a build artifact — treat a bad one as a failure."""

    def test_the_committed_index_parses_and_has_the_expected_shape(self):
        path = Path(__file__).resolve().parent.parent / "site" / "search-index.json"
        index = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(index["version"], bsi.INDEX_VERSION)
        self.assertTrue(index["episodes"], "the committed index is empty")
        for ep_id, entry in index["episodes"].items():
            self.assertTrue(ep_id.isdigit(), f"episode key {ep_id!r} is not an id")
            self.assertIn("s", entry)
            for moment in entry.get("l", []) + entry.get("c", []):
                self.assertEqual(len(moment), 2)
                self.assertIsInstance(moment[0], (int, float))
                self.assertIsInstance(moment[1], str)


if __name__ == "__main__":
    unittest.main()
