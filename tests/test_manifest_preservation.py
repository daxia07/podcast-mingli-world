import copy
import unittest
from unittest.mock import patch

from scripts import sync_manifest


def catalogue():
    return {
        "episodes": [{"id": 1, "file_url": "https://podcast.example/episodes/one.mp3?v=old"}],
        "playlists": {"interviews": {"episode_ids": [1]}},
    }


class PreservationTests(unittest.TestCase):
    def test_rebuilding_feed_preserves_original_publication_dates_without_changing_records(self):
        from scripts.lib import manifest
        from xml.etree import ElementTree
        data = catalogue()
        before = copy.deepcopy(data['episodes'])
        date = 'Thu, 24 Sep 2026 11:21:48 +1000'
        data['rss_pub_dates'] = {'1': date}
        data['episodes'].append({'id': 2, 'file_url': 'https://podcast.example/episodes/new.mp3'})
        feed = ElementTree.fromstring(manifest.generate_rss(data)).findall('channel/item')
        original = next(item for item in feed if item.findtext('guid').endswith('/one.mp3'))
        self.assertEqual(original.findtext('pubDate'), date)
        self.assertEqual(data['episodes'][:1], before)
        self.assertEqual(len(feed), 2)

    def test_stale_checkout_cannot_remove_a_published_episode(self):
        remote = catalogue()
        local = copy.deepcopy(remote)
        local["episodes"] = [{"id": 2, "file_url": "https://podcast.example/episodes/two.mp3"}]
        self.assertTrue(sync_manifest.preservation_errors(local, remote))

    def test_archiving_and_cache_busting_preserve_history(self):
        remote = catalogue()
        local = copy.deepcopy(remote)
        local["episodes"][0].update(archived=True, file_url="https://podcast.example/episodes/one.mp3?v=new")
        local["playlists"]["interviews"]["archived"] = True
        self.assertEqual(sync_manifest.preservation_errors(local, remote), [])

    def test_new_episodes_can_be_added(self):
        remote = catalogue()
        local = copy.deepcopy(remote)
        local["episodes"].append({"id": 2, "file_url": "https://podcast.example/episodes/two.mp3"})
        self.assertEqual(sync_manifest.preservation_errors(local, remote), [])

    def test_removing_a_show_or_changing_a_published_path_is_rejected(self):
        remote = catalogue()
        local = copy.deepcopy(remote)
        local["playlists"] = {}
        local["episodes"][0]["file_url"] = "https://podcast.example/episodes/replacement.mp3"
        self.assertEqual(len(sync_manifest.preservation_errors(local, remote)), 2)

    def test_missing_or_malformed_remote_catalogue_is_rejected(self):
        for remote in (None, {}, {"episodes": [], "playlists": []}):
            with self.subTest(remote=remote):
                self.assertTrue(sync_manifest.preservation_errors(catalogue(), remote))

    def run_sync(self, local, remote=None, error=None, args=()):
        with patch.object(sync_manifest.manifest_mod, "load", return_value=local), \
             patch.object(sync_manifest.gates_mod, "run_manifest", return_value=[]), \
             patch.object(sync_manifest.gates_mod, "gate_show_registry", return_value=[]), \
             patch("scripts.lib.r2.get_json", return_value=remote, side_effect=error), \
             patch("scripts.lib.r2.upload_json") as upload_json, \
             patch("scripts.lib.r2.upload_bytes") as upload_bytes:
            code = sync_manifest.main(list(args))
            return code, upload_json.call_count, upload_bytes.call_count

    def test_unreadable_remote_never_uploads(self):
        self.assertEqual(self.run_sync(catalogue(), error=RuntimeError("unavailable")), (1, 0, 0))

    def test_missing_live_entry_never_uploads_even_with_equal_counts(self):
        remote = catalogue()
        remote["episodes"][0]["id"] = 500
        self.assertEqual(self.run_sync(catalogue(), remote), (1, 0, 0))

    def test_matching_catalogue_and_dry_run_never_upload(self):
        remote = catalogue()
        self.assertEqual(self.run_sync(remote, remote), (0, 0, 0))
        local = copy.deepcopy(remote)
        local["episodes"][0]["archived"] = True
        self.assertEqual(self.run_sync(local, remote, args=("--dry-run",)), (0, 0, 0))

    def test_safe_visibility_update_still_syncs_manifest_and_feed(self):
        remote = catalogue()
        local = copy.deepcopy(remote)
        local["episodes"][0]["archived"] = True
        self.assertEqual(self.run_sync(local, remote), (0, 1, 1))


if __name__ == "__main__":
    unittest.main()
