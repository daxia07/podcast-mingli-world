#!/usr/bin/env python3
"""Prepare the exact selected three-chapter opening as blueprint data; no TTS."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lib import blueprint, manifest, local_mandarin

SHOW = 'novel-opening-v3'
SOURCE_SHA = '33271a5148c6b78542c949aa71e859fe7eeb922d80f70e89d6d709dcf09d7d4f'


def prepare(source_path):
    raw = source_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError('source is not the confirmed September 27 V3 opening')
    text = raw.decode()
    headings = list(re.finditer(r'^第[一二三]章[　 ]+(.+)$',text,re.M))
    if len(headings) != 3:
        raise ValueError('expected exactly the three opening chapters')
    registry_path=Path('content/shows.json'); registry=json.loads(registry_path.read_text())
    if SHOW in registry['shows'] or SHOW in manifest.load().get('playlists', {}):
        raise ValueError('collection already prepared; refusing to overwrite authoring work')
    if (Path('content/sources')/SHOW).exists() or (Path('content/blueprints')/SHOW).exists() or any(Path('site/novel').glob('opening-v3-*')):
        raise ValueError('opening artifacts already exist; inspect partial work before retrying')
    sources = Path('content/sources')/SHOW; sources.mkdir(parents=True,exist_ok=True)
    sources.joinpath('opening-v3.txt').write_bytes(raw)
    readers = Path('site/novel'); readers.mkdir(parents=True,exist_ok=True)
    drafts, receipts = [], []
    for index, heading in enumerate(headings):
        exact = text[heading.start():headings[index+1].start() if index+1<len(headings) else len(text)].strip()+'\n'
        slug = f'opening-v3-ch{index+1:02d}'
        source = sources/(slug+'.txt'); source.write_text(exact)
        chunks, current, count = [], [], 0
        for paragraph in [p.strip() for p in exact.split('\n\n') if p.strip()]:
            if re.fullmatch(r'[＊*\s]+',paragraph):
                if current: chunks.append(('\n\n'.join(current),True))
                current, count = [],0
                continue
            if current and count+len(paragraph)>200:
                chunks.append(('\n\n'.join(current),False));current,count=[],0
            current.append(paragraph);count+=len(paragraph)
        if current: chunks.append(('\n\n'.join(current),False))
        sections, lines = [], []
        for chunk, ends_scene in chunks:
            lines.append({'voice':'narrator','text':chunk})
            if ends_scene:
                n=len(sections)+1
                sections.append({'id':f'scene-{n:02d}','title':f'片段 {n}','lines':lines});lines=[]
        if lines:
            n=len(sections)+1;lines[-1]['pause_after']=0.5
            sections.append({'id':f'scene-{n:02d}','title':f'片段 {n}','lines':lines})
        config = {'engine':'qwen-mlx','model':local_mandarin.MODEL,'revision':local_mandarin.REVISION,
            'preset':'Serena','temperature':0.7,'seed':142}
        if index==0:
            config['punctuation_overrides']=[{'source':'本轮采集已结束。','spoken':'本轮采集，已结束。',
                'reason':'Retain all source words; punctuation-only audition restores 已 in full and focused ASR. Actual listening remains pending.'}]
        if index==2:
            config['literal_readings']=[{'source':'`aqi/local`','spoken':'A Q I，斜杠，local',
                'reason':'Read the literal source label as letters and a slash. Canonical manuscript and displayed transcript remain byte-preserved; listening still required.'}]
        title = heading.group(0).replace('　',' · ')
        item = {'schema':1,'slug':slug,'show':SHOW,'template':'mandarin-novel',
            'title':title,'description':'2026 年 9 月 27 日开篇 V3 原文。属于三章开篇，完整长篇尚未完成；朗读音频待制作及听校。',
            'language':'zh-CN','tts':config,'source_document':{'path':source.as_posix(),'sha256':local_mandarin.sha(source)},
            'sections':sections,'keywords':['科幻小说','开篇 V3','陈默','周启','罗宁','回声']}
        bp = blueprint.from_dict(item)
        local_mandarin.validate_source(bp)
        blueprint.save(bp,Path('content/blueprints')/SHOW/(slug+'.json'))
        readers.joinpath(slug+'.txt').write_text(exact)
        readers.joinpath(slug+'.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>'+html.escape(title)+' · 开篇 V3</title><script src="/js/theme.js?v=30"></script><link rel="stylesheet" href="/style.css?v=30">'
            '<main class="novel-reader"><a href="/">返回播客目录</a><h1>'+html.escape(title)+'</h1>'
            '<p>开篇三章 · 原文已备，正式音频待制作及听校。此合集不代表已完成的全书。</p>'
            '<a download href="'+slug+'.txt">下载原文</a><pre>'+html.escape(exact)+'</pre></main></html>')
        drafts.append({'slug':slug,'title':title,'reader_url':'/novel/'+slug+'.html',
            'text_url':'/novel/'+slug+'.txt','status':'text-ready-audio-pending'})
        receipts.append({'slug':slug,'source_sha256':local_mandarin.sha(source),
            'chunks':bp.line_count(),'scene_sections':len(sections),'estimated_minutes':round(bp.estimate_minutes(),2),
            'audio_status':'not generated','lexical_source_alignment':'pass'})
    show = {'title':'向后兼容 · 开篇三章','description':'2004 年，陈默、周启、罗宁与回声。2026 年 9 月 27 日开篇 V3，暂用书名。仅含已确认的三章开篇；全书初稿与正式音频尚未完成。',
        'mono':'回声','icon':'📖','default_template':'mandarin-novel','order':0,'featured':True,
        'language':'zh-CN','status':'three-chapter-opening','draft_chapters':drafts}
    m=manifest.load(); manifest.register_show(m,SHOW,show)
    registry['shows'][SHOW]=show
    registry_path.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
    manifest.save_local(m)
    receipt={'status':'three-chapter opening only; no complete novel or published audio claimed',
        'working_title':'向后兼容','source_sha256':SOURCE_SHA,'chapters':receipts,'listening':'pending','published':False}
    Path('content/novel-opening-v3.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(receipt,ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path)
    prepare(parser.parse_args().source)
