from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import tempfile
import unittest
from scripts import build_episode
from scripts.lib import blueprint


class PublishPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.mp3=Path(self.temp.name)/'sample.mp3';self.mp3.write_bytes(b'fixture')
        self.bp=blueprint.from_dict({'id':2,'slug':'new-episode','show':'show','template':'concept-explainer','title':'New','description':'New',
            'sections':[{'id':'first','title':'First','lines':['Fixture']} ]})
        self.manifest={'episodes':[{'id':1,'slug':'old','title':'Old','source':'tts','file_url':'https://example.test/episodes/old.mp3'}],
            'playlists':{'show':{'title':'Show','mono':'SH','order':0,'episode_ids':[1]}}}
    def tearDown(self):self.temp.cleanup()

    def call(self):
        return build_episode.publish(self.bp,self.manifest,self.mp3,'{}','WEBVTT',None,'1:00',500000,False)

    def test_unregistered_show_blocks_before_network_or_upload(self):
        self.bp.show='absent'
        with patch('scripts.lib.r2.get_json') as read, patch('scripts.lib.r2.upload') as upload:
            with self.assertRaises(SystemExit):self.call()
            read.assert_not_called();upload.assert_not_called()

    def test_newer_remote_catalogue_blocks_every_upload_and_preserves_local(self):
        remote=deepcopy(self.manifest);remote['episodes'].append({'id':500,'file_url':'https://example.test/episodes/newer.mp3'})
        before=deepcopy(self.manifest)
        with patch('scripts.lib.r2.get_json',return_value=remote), patch('scripts.lib.r2.upload') as audio, patch('scripts.lib.r2.upload_json') as data, patch('scripts.lib.r2.upload_bytes') as text:
            with self.assertRaises(SystemExit):self.call()
            audio.assert_not_called();data.assert_not_called();text.assert_not_called()
        self.assertEqual(self.manifest,before)

    def test_unreadable_remote_blocks_audio_write(self):
        with patch('scripts.lib.r2.get_json',side_effect=OSError('offline')),patch('scripts.lib.r2.upload') as upload:
            with self.assertRaises(SystemExit):self.call()
            upload.assert_not_called()

    def test_mandarin_missing_listening_review_never_reads_remote(self):
        self.bp=blueprint.load('content/blueprints/novel-opening-v3/opening-v3-ch01.json')
        with patch('scripts.lib.r2.get_json') as read,patch('scripts.lib.r2.upload') as upload:
            with self.assertRaises(SystemExit):self.call()
            read.assert_not_called();upload.assert_not_called()
