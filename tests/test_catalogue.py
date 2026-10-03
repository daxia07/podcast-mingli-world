import copy
import json
from pathlib import Path
import unittest
from scripts.lib import catalogue, manifest


class CatalogueTests(unittest.TestCase):
    def sample(self):
        return {'title':'Audio','episodes':[{'id':1,'slug':'one','title':'First','file_url':'https://example.test/episodes/a.mp3'}],
                'playlists':{'one':{'title':'Original','episode_ids':[1]}}}

    def test_reconcile_is_lossless_and_does_not_mutate_inputs(self):
        local=self.sample(); remote=copy.deepcopy(local)
        remote['episodes'].append({'id':500,'slug':'new','file_url':'https://example.test/episodes/new.mp3'})
        remote['playlists']['new']={'title':'New','episode_ids':[500]}
        old=copy.deepcopy(local); result=catalogue.reconcile(local,remote)
        self.assertEqual(result,remote);self.assertEqual(local,old)
        self.assertEqual(catalogue.reconcile(result,remote),result)

    def test_conflicting_shared_record_or_show_fails(self):
        local=self.sample()
        for key in ('episode','show','title'):
            remote=copy.deepcopy(local)
            if key=='episode':remote['episodes'][0]['title']='Changed'
            elif key=='show':remote['playlists']['one']['title']='Changed'
            else:remote['title']='Changed'
            with self.assertRaises(ValueError):catalogue.reconcile(local,remote)

    def test_bad_identity_or_missing_catalogue_fails(self):
        for invalid in ({}, {'episodes':[]}, {'episodes':[{'id':'1'}],'playlists':{}},
                        {'episodes':[{'id':1},{'id':1}],'playlists':{}}):
            with self.assertRaises(ValueError):catalogue.reconcile(self.sample(),invalid)

    def test_canonical_selection_is_deterministic_and_preserves_source(self):
        m=self.sample();m['episodes'] += [{**m['episodes'][0],'id':2,'description':'Rich metadata'},
                                       {**m['episodes'][0],'id':3,'description':'Rich metadata'}]
        before=copy.deepcopy(m);proposal=catalogue.display_proposal(m)
        self.assertEqual(proposal['aliases'],{'1':2,'3':2});self.assertEqual(m,before)
        m['display_aliases']=proposal['aliases'];self.assertTrue(catalogue.validate_aliases(m))
        m['display_aliases']['2']=1
        with self.assertRaises(ValueError):catalogue.validate_aliases(m)

    def test_different_query_versions_are_not_grouped(self):
        m=self.sample();m['episodes'].append({**m['episodes'][0],'id':2,'file_url':m['episodes'][0]['file_url']+'?v=abcdef'})
        self.assertEqual(catalogue.display_proposal(m)['aliases'],{})

    def test_candidate_preserves_all_captured_live_records(self):
        snapshot=json.loads(Path('content/sources/catalogue-live-20261002.json').read_text())
        candidate=manifest.load();old=catalogue.indexed(snapshot);new=catalogue.indexed(candidate)
        self.assertEqual(len(old),249)
        self.assertTrue(all(new[eid]==ep for eid,ep in old.items()))
        self.assertTrue(all(candidate['playlists'][sid]==show for sid,show in snapshot['playlists'].items()))
        self.assertTrue(all(eid in new for eid in range(500,510)))
        self.assertTrue(catalogue.validate_aliases(candidate))
        self.assertEqual(len(candidate['display_aliases']),13)
        from xml.etree import ElementTree
        self.assertEqual(len(ElementTree.fromstring(manifest.generate_rss(candidate)).findall('channel/item')),249,
                         'display aliases must not remove RSS records')

    def test_register_show_never_rewrites_published_records(self):
        m=self.sample();before=copy.deepcopy(m)
        manifest.register_show(m,'novel',{'title':'Opening','mono':'N','order':0,'draft_chapters':[{'title':'One'}]})
        self.assertEqual(m['episodes'],before['episodes'])
        self.assertEqual(m['playlists']['one'],before['playlists']['one'])
        with self.assertRaises(ValueError):manifest.register_show(m,'one',{})
