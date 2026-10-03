from argparse import Namespace
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch
import json
import tempfile
import unittest
from scripts import build_episode as B
from scripts.lib import blueprint, chapters, transcript
from scripts.lib.timeline import build


class BuiltPublishTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.bp=blueprint.from_dict({'id':439,'slug':'fixture','show':'novel','template':'mandarin-novel',
            'title':'Fixture','description':'Fixture','language':'zh-CN',
            'sections':[{'id':'scene-01','title':'Scene','lines':['原文。','完整保留。']}]})
        self.timeline=build(self.bp,[40,40]);self.path=self.root/'fixture.mp3';self.path.write_bytes(b'x'*500001)
        self.path.with_suffix('.build.json').write_text(json.dumps({'timeline':asdict(self.timeline)}))
        (self.root/'fixture.chapters.json').write_text(chapters.dumps(self.timeline,title=self.bp.title))
        (self.root/'fixture.vtt').write_text(transcript.build(self.timeline))
        self.args=Namespace(output_dir=str(self.root),listening_review='fixture-review')
    def tearDown(self):self.temp.cleanup()
    def invoke(self):
        with patch.object(B,'run_gates'),patch('scripts.lib.local_mandarin.validate_source'),\
                patch('scripts.lib.local_mandarin.require_listening_review') as review,\
                patch.object(B,'publish',return_value=0) as publish:
            try:result=B.publish_built(self.bp,{},self.args)
            except SystemExit:result='rejected'
            return result,review.call_count,publish.call_count
    def test_reviewed_sidecars_publish_without_synthesis(self):
        self.assertEqual(self.invoke(),(0,1,1))
    def test_changed_transcript_or_timeline_never_reaches_publisher(self):
        (self.root/'fixture.vtt').write_text('changed')
        self.assertEqual(self.invoke(),('rejected',1,0))
        (self.root/'fixture.vtt').write_text(transcript.build(self.timeline))
        self.timeline.lines[0].text='不是原文'
        self.path.with_suffix('.build.json').write_text(json.dumps({'timeline':asdict(self.timeline)}))
        self.assertEqual(self.invoke(),('rejected',1,0))
