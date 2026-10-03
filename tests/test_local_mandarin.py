from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import json
import math
import shutil
import struct
import tempfile
import unittest
import wave
from scripts.lib import blueprint, local_mandarin as M, transcript


class MandarinFixture(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        source=self.root/'content/sources/sample.txt';source.parent.mkdir(parents=True);source.write_text('陈默看着显示器。\n\n周启拔掉了线。\n')
        self.bp=blueprint.from_dict({'slug':'sample','show':'novel','template':'mandarin-novel','title':'Test','description':'Test',
            'language':'zh-CN','tts':{'engine':'qwen-mlx','model':M.MODEL,'revision':M.REVISION,'preset':'Serena'},
            'source_document':{'path':'content/sources/sample.txt','sha256':M.sha(source)},
            'sections':[{'id':'scene-01','title':'Opening','lines':['陈默看着显示器。','周启拔掉了线。']}]})
    def tearDown(self):self.temp.cleanup()


class MandarinTests(MandarinFixture):
    def test_blueprint_roundtrip_and_han_estimate(self):
        copy=blueprint.from_dict(self.bp.to_dict());self.assertEqual(copy.to_dict(),self.bp.to_dict())
        self.assertGreater(copy.estimate_seconds(),4)

    def test_source_alignment_rejects_missing_repeated_or_changed_words(self):
        M.validate_source(self.bp,self.root)
        for text in ['陈默看着。','陈默看着显示器。陈默看着显示器。','陈墨看着显示器。']:
            changed=deepcopy(self.bp);changed.sections[0].lines[0].text=text
            with self.assertRaises(M.MandarinError):M.validate_source(changed,self.root)

    def test_changed_source_hash_or_path_escape_fails(self):
        for change in ({'sha256':'wrong'},{'path':'../../elsewhere'}):
            bp=deepcopy(self.bp);bp.source_document.update(change)
            with self.assertRaises(M.MandarinError):M.validate_source(bp,self.root)

    def test_engine_and_voice_cannot_silently_fallback(self):
        for change in ({'engine':'edge'},{'revision':'latest'},{'preset':'clone'},{'temperature':float('nan')}):
            bp=deepcopy(self.bp);bp.tts.update(change)
            with self.assertRaises(M.MandarinError):M.settings(bp)
        with self.assertRaises(M.MandarinError):M.QwenPreset(M.settings(self.bp),None)

    def test_only_documented_punctuation_and_literal_readings_allowed(self):
        self.bp.tts['punctuation_overrides']=[{'source':'陈默看着','spoken':'陈默，看着','reason':'pause'}]
        self.assertEqual(M.spoken_text(self.bp,'陈默看着显示器。'),'陈默，看着显示器。')
        self.bp.tts['punctuation_overrides'][0]['spoken']='陈墨看着'
        with self.assertRaises(M.MandarinError):M.spoken_text(self.bp,'陈默看着')
        self.bp.tts.pop('punctuation_overrides')
        self.bp.tts['literal_readings']=[{'source':'`aqi/local`','spoken':'A Q I，斜杠，local','reason':'literal path'}]
        self.assertEqual(M.spoken_text(self.bp,'`aqi/local`。'),'A Q I，斜杠，local。')
        self.bp.tts['literal_readings'][0]['spoken']='A different label'
        with self.assertRaises(M.MandarinError):M.spoken_text(self.bp,'`aqi/local`。')

    def test_all_three_canonical_blueprints_align_and_reserve_distinct_ids(self):
        paths=sorted(Path('content/blueprints/novel-opening-v3').glob('*.json'))
        self.assertEqual(len(paths),3)
        for path in paths:
            bp=blueprint.load(path);M.validate_source(bp)
            self.assertGreater(bp.estimate_minutes(),10)
            self.assertLess(bp.estimate_minutes(),25)
        self.assertEqual(sum(blueprint.load(p).line_count() for p in paths),59)
        ids=[blueprint.load(p).id for p in paths if blueprint.load(p).id is not None]
        self.assertEqual(len(ids),len(set(ids)))

    def test_retry_seed_must_identify_one_known_source_chunk(self):
        key=M.text_sha(self.bp.sections[0].lines[0].text)
        self.bp.tts['chunk_seed_overrides']={key:987};M.validate_source(self.bp,self.root)
        for overrides in ({'unknown':987},{key:True},{key:-1}):
            self.bp.tts['chunk_seed_overrides']=overrides
            with self.assertRaises(M.MandarinError):M.validate_source(self.bp,self.root)

    def test_listening_gate_rejects_absent_or_wrong_artifact_before_decoding(self):
        path=self.root/'sample.mp3';path.write_bytes(b'not audio')
        with self.assertRaises(M.MandarinError):M.require_listening_review(self.bp,path,None)
        review=self.root/'review.json';review.write_text(json.dumps({'approved':True,'reviewer':'Fixture','reviewed_at':'test','open_issues':[],
            'mp3_sha256':'wrong','source_sha256':self.bp.source_document['sha256']}))
        with patch.object(M,'verify_mp3') as decoder:
            with self.assertRaises(M.MandarinError):M.require_listening_review(self.bp,path,review)
            decoder.assert_not_called()


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'optional real codec tools')
class MandarinCodecTests(MandarinFixture):
    def render(self, factory):
        return M.synthesize(self.bp,self.root/'result.mp3',workdir=self.root/'chunks',backend_factory=factory,
            source_root=self.root,progress=lambda _:None)

    def factory(self, calls, fail_at=None):
        class Fixture:
            def __init__(self, *_):pass
            def render(inner, text, path, params):
                calls.append(text)
                if len(calls)==fail_at:raise RuntimeError('simulated interruption')
                samples=b''.join(struct.pack('<h',int(2500*math.sin(2*math.pi*220*i/24000))) for i in range(12000))
                with wave.open(str(path),'wb') as stream:
                    stream.setparams((1,2,24000,0,'NONE','not compressed'));stream.writeframes(samples)
                return {'generated_tokens':7,'fixture':'synthetic codec tone, not speech'}
        return Fixture

    def test_interruption_resumes_only_complete_verified_chunks(self):
        first=[]
        with self.assertRaises(RuntimeError):self.render(self.factory(first,fail_at=2))
        self.assertFalse((self.root/'result.mp3').exists())
        second=[];timeline=self.render(self.factory(second))
        self.assertEqual(second,['周启拔掉了线。'])
        self.assertEqual(len(timeline.lines),2)
        self.assertAlmostEqual(timeline.total,M.verify_mp3(self.root/'result.mp3'),places=3)
        self.assertIn('周启拔掉了线。',transcript.build(timeline))
        third=[];self.render(self.factory(third));self.assertEqual(third,[])

    def test_cache_corruption_fails_closed_and_parameter_change_does_not_reuse(self):
        self.render(self.factory([]))
        self.bp.tts['seed']=145;calls=[];self.render(self.factory(calls));self.assertEqual(len(calls),2)
        receipt=next(p for p in (self.root/'chunks').glob('*.json') if json.loads(p.read_text())['identity']['settings']['seed']==145)
        receipt.with_suffix('.wav').write_bytes(b'broken')
        with self.assertRaises(M.MandarinError):self.render(self.factory([]))

    def test_targeted_retry_preserves_other_verified_chunks(self):
        self.render(self.factory([]))
        self.bp.tts['chunk_seed_overrides']={M.text_sha(self.bp.sections[0].lines[1].text):888}
        calls=[];self.render(self.factory(calls))
        self.assertEqual(calls,['周启拔掉了线。'])

    def test_objective_review_is_explicit_complete_and_bound_to_evidence(self):
        self.render(self.factory([]));path=self.root/'result.mp3'
        build=json.loads(path.with_suffix('.build.json').read_text());checks=[]
        for i,chunk in enumerate(build['chunks']):
            evidence=self.root/f'asr-{i}.json'
            payload={'pcm_sha256':chunk['pcm_sha256'],'source_text_sha256':chunk['identity']['source_text_sha256'],
                'model':'test-only fake ASR','text':chunk['source_text']}
            evidence.write_text(json.dumps(payload))
            checks.append({**{k:payload[k] for k in ['pcm_sha256','source_text_sha256']},'assessment':'pass',
                'evidence_path':evidence.name,'evidence_sha256':M.sha(evidence)})
        review={'approved':True,'reviewer':'test fixture','reviewed_at':'test','open_issues':[],
            'mp3_sha256':M.sha(path),'source_sha256':self.bp.source_document['sha256'],
            'review_mode':'objective','listening_performed':False,'method':'test fixture',
            'limitations':'No speech or listening in this synthetic codec test.','chunk_reviews':checks}
        review_path=self.root/'review.json'
        def save():review_path.write_text(json.dumps(review))
        save();M.require_listening_review(self.bp,path,review_path)
        review['listening_performed']=True;save()
        with self.assertRaises(M.MandarinError):M.require_listening_review(self.bp,path,review_path)
        review['listening_performed']=False;review['chunk_reviews']=checks[:-1];save()
        with self.assertRaises(M.MandarinError):M.require_listening_review(self.bp,path,review_path)
        review['chunk_reviews']=checks;save();(self.root/'asr-0.json').write_text('{}')
        with self.assertRaises(M.MandarinError):M.require_listening_review(self.bp,path,review_path)

    def test_non_audio_and_wrong_rate_are_rejected(self):
        path=self.root/'bad.mp3';path.write_bytes(b'not mp3')
        with self.assertRaises(M.MandarinError):M.verify_mp3(path)
        raw=self.root/'raw.wav';self.factory([])().render('fixture',raw,{})
        M.command(['ffmpeg','-y','-v','error','-i',str(raw),'-ar','44100','-ac','1','-b:a','64k',str(path)])
        with self.assertRaises(M.MandarinError):M.verify_mp3(path)

    def test_empty_or_token_limited_backend_never_commits_a_chunk(self):
        class Empty:
            def __init__(self,*_):pass
            def render(self,*_):return {'generated_tokens':1800}
        with self.assertRaises(M.MandarinError):self.render(Empty)
        self.assertFalse(list((self.root/'chunks').glob('*.json')))
