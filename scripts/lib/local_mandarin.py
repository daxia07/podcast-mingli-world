"""Offline preset-voice Mandarin adapter for the existing blueprint pipeline.

No account, remote TTS, clone voice or fallback engine. Raw source and spoken
punctuation are recorded separately. Cache commits only after PCM validation.
Only final MP3 encoding introduces frame padding; timeline uses exact PCM frames.
"""
from pathlib import Path
from dataclasses import asdict
import hashlib
import importlib.metadata
import json
import math
import os
import re
import subprocess
import unicodedata
import wave
from array import array

from . import audio
from .timeline import build as build_timeline, calibrate, flatten, gaps_for

ROOT = Path(__file__).resolve().parents[2]
MODEL = 'mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-4bit'
REVISION = 'f35faf19b0cc2160865af64ecf0f22f83d335135'
INSTRUCTION = '普通话科幻小说旁白，沉稳、自然、克制，语速适中，句间停顿清楚，对话稍有变化，不夸张，不使用播音腔。'
RATE = 48000
LITERAL_READINGS = {'`aqi/local`': 'A Q I，斜杠，local',
    '二〇〇四年九月二十四日': '二零零四年九月二十四日'}


class MandarinError(ValueError):
    pass


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def source_normalized(text):
    return re.sub(r'[\s＊*]', '', text)


def lexical(text):
    return ''.join(c for c in text if not c.isspace() and not unicodedata.category(c).startswith('P'))


def settings(bp):
    config = bp.tts
    if config.get('engine') != 'qwen-mlx' or not bp.language.startswith('zh'):
        raise MandarinError('Mandarin requires explicit qwen-mlx and zh language; no English fallback')
    if config.get('model') != MODEL or config.get('revision') != REVISION:
        raise MandarinError('unreviewed model/revision')
    if config.get('preset') not in ('Serena', 'Uncle_Fu'):
        raise MandarinError('only reviewed preset voices are supported; no voice cloning')
    temp = config.get('temperature', 0.7)
    seed = config.get('seed', 142)
    if not isinstance(temp, (int, float)) or not math.isfinite(temp) or not 0 < temp <= 1:
        raise MandarinError('invalid temperature')
    if type(seed) is not int or not 0 <= seed < 2**31:
        raise MandarinError('invalid seed')
    if bp.music or bp.rate or any(line.sfx for _, _, line in flatten(bp)):
        raise MandarinError('Mandarin adapter supports plain narration only, without Edge rate or sound effects')
    return {'engine':'qwen-mlx','renderer_version':1,'model':MODEL,'revision':REVISION,
        'preset':config['preset'],'temperature':temp,'seed':seed,'instruction':INSTRUCTION,
        'max_tokens':1800,'streaming_interval':2.0,'sample_rate':RATE,'channels':1,
        'bitrate':'64k','target_lufs':-19,'mlx_audio':'0.5.7','mlx':'0.32.3'}


def spoken_text(bp, text):
    for override in bp.tts.get('punctuation_overrides', []):
        before, after = override.get('source', ''), override.get('spoken', '')
        if not before or lexical(before) != lexical(after) or not override.get('reason'):
            raise MandarinError('a spoken override must change punctuation only and document its reason')
        text = text.replace(before, after)
    for override in bp.tts.get('literal_readings', []):
        before, after = override.get('source'), override.get('spoken')
        if before not in LITERAL_READINGS or after != LITERAL_READINGS[before] or not override.get('reason'):
            raise MandarinError('unreviewed literal-token reading')
        text = text.replace(before, after)
    return text


def validate_source(bp, root=ROOT):
    settings(bp)
    gain = bp.tts.get('final_gain_db', 0)
    if type(gain) not in (int, float) or not math.isfinite(gain) or not -12 <= gain <= 0:
        raise MandarinError('final encoding gain must be finite attenuation between -12 and 0 dB')
    source = bp.source_document
    relative = source.get('path', '')
    path = (Path(root) / relative).resolve()
    sources_root = (Path(root) / 'content/sources').resolve()
    if not relative or not path.is_relative_to(sources_root) or not path.is_file():
        raise MandarinError('source document must be an existing content/sources file')
    if sha(path) != source.get('sha256'):
        raise MandarinError('source document hash changed')
    lines = [line for _, _, line in flatten(bp)]
    if source_normalized(path.read_text()) != source_normalized(''.join(line.text for line in lines)):
        raise MandarinError('blueprint omits, repeats or changes source text')
    for line in lines:
        if len(line.text) > 260 or line.voice != 'narrator':
            raise MandarinError('use bounded narrator chunks of at most 260 characters')
        if not math.isfinite(line.pause_after) or line.pause_after < 0 or line.pause_after > 10:
            raise MandarinError('invalid chunk pause')
        spoken_text(bp, line.text)
    body = '\n'.join(line.text for line in lines)
    source_hashes = {text_sha(line.text) for line in lines}
    for key, seed in bp.tts.get('chunk_seed_overrides', {}).items():
        if key not in source_hashes or type(seed) is not int or not 0 <= seed < 2**31:
            raise MandarinError('retry seed must identify one exact source chunk and a valid integer seed')
    for override in bp.tts.get('punctuation_overrides', []) + bp.tts.get('literal_readings', []):
        if body.count(override['source']) != 1:
            raise MandarinError('punctuation override must identify exactly one source occurrence')
    return path


def command(argv):
    result = subprocess.run(argv, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if result.returncode:
        raise MandarinError(f'{argv[0]} failed: {result.stderr[-350:]}')
    return result


def verify_pcm(path):
    try:
        with wave.open(str(path), 'rb') as stream:
            if (stream.getframerate(), stream.getnchannels(), stream.getsampwidth()) != (RATE, 1, 2):
                raise MandarinError('chunk is not 48 kHz mono 16-bit PCM')
            frames = stream.getnframes()
            samples = stream.readframes(frames)
    except (wave.Error, EOFError) as exc:
        raise MandarinError(f'undecodable PCM: {exc}') from exc
    if not frames or len(samples) != frames * 2:
        raise MandarinError('empty or truncated PCM')
    values = array('h', samples)
    if not any(values):
        raise MandarinError('silent speech chunk')
    return frames / RATE


def verify_mp3(path):
    runs = audio.scan(path)
    if len(runs) != 1 or (runs[0].fmt.sample_rate, runs[0].fmt.channel_mode, runs[0].fmt.bitrate) != (RATE, 'mono', 64):
        raise MandarinError('MP3 must have actual uniform 48 kHz mono 64 kbps frames')
    command(['ffmpeg','-v','error','-xerror','-err_detect','explode','-i',str(path),'-f','null','-'])
    probe = json.loads(command(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]).stdout)
    streams = probe.get('streams', [])
    if len(streams) != 1 or streams[0].get('codec_name') != 'mp3' or streams[0].get('channels') != 1 or streams[0].get('sample_rate') != str(RATE):
        raise MandarinError('invalid final audio stream')
    seconds = float(probe['format']['duration'])
    if not math.isfinite(seconds) or seconds <= 0:
        raise MandarinError('invalid final duration')
    return seconds


class QwenPreset:
    def __init__(self, config, model_dir):
        path = Path(model_dir or '')
        if not model_dir or not path.is_dir() or path.name != REVISION or not (path/'config.json').is_file():
            raise MandarinError('provide the existing pinned local model snapshot with --model-dir; no automatic downloads')
        for package, expected in [('mlx-audio', config['mlx_audio']), ('mlx', config['mlx'])]:
            if importlib.metadata.version(package) != expected:
                raise MandarinError(f'{package} must match the reviewed version {expected}')
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'
        import mlx.core as mx
        from mlx_audio.tts.utils import load_model
        self.mx = mx
        mx.set_cache_limit(128 * 1024 * 1024)
        self.model = load_model(path)

    def render(self, text, path, config):
        import numpy as np
        from scipy.io import wavfile
        self.mx.random.seed(config['seed'])
        generated = list(self.model.generate_custom_voice(text=text, speaker=config['preset'],
            language='Chinese', instruct=config['instruction'], max_tokens=config['max_tokens'],
            temperature=config['temperature'], stream=True, streaming_interval=config['streaming_interval']))
        tokens = sum(chunk.token_count for chunk in generated)
        if tokens <= 0 or tokens >= config['max_tokens']:
            raise MandarinError('token limit/empty output; refusing a potentially truncated chunk')
        samples = np.concatenate([np.asarray(chunk.audio, dtype=np.float32).reshape(-1) for chunk in generated])
        if not samples.size or not np.isfinite(samples).all() or float(np.max(np.abs(samples))) >= 1:
            raise MandarinError('empty, nonfinite or clipped model output')
        wavfile.write(path, self.model.sample_rate, (samples * 32767).astype(np.int16))
        self.mx.clear_cache()
        return {'generated_tokens':tokens,'raw_sample_rate':self.model.sample_rate}


def synthesize(bp, out_path, *, workdir, model_dir=None, progress=print, backend_factory=QwenPreset, source_root=ROOT):
    validate_source(bp, root=source_root)
    config = settings(bp)
    config['ffmpeg'] = command(['ffmpeg','-version']).stdout.splitlines()[0]
    out_path, workdir = Path(out_path), Path(workdir)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    workdir.mkdir(parents=True, exist_ok=True)
    records, paths, durations, backend = [], [], [], None
    for index, (_, _, line) in enumerate(flatten(bp)):
        spoken = spoken_text(bp, line.text)
        seed = bp.tts.get('chunk_seed_overrides', {}).get(text_sha(line.text), config['seed'] + index)
        params = {**config, 'seed':seed}
        identity = {'source_text_sha256':text_sha(line.text),'spoken_text_sha256':text_sha(spoken),'settings':params}
        key = text_sha(json.dumps(identity, sort_keys=True))
        pcm, receipt = workdir/f'{index:04d}-{key}.wav', workdir/f'{index:04d}-{key}.json'
        if receipt.exists():
            record = json.loads(receipt.read_text())
            if record.get('identity') != identity or not pcm.is_file() or record.get('pcm_sha256') != sha(pcm):
                raise MandarinError(f'chunk {index} cache is damaged; preserve it and rebuild in another workdir')
            duration = verify_pcm(pcm)
            if abs(duration - record['duration_seconds']) > 1/RATE:
                raise MandarinError('cached duration mismatch')
            progress(f'  chunk {index+1}: verified cache')
        else:
            if backend is None:
                backend = backend_factory(config, model_dir)
            raw, temporary = workdir/f'{index:04d}-{key}.raw.wav', workdir/f'{index:04d}-{key}.partial.wav'
            result = backend.render(spoken, raw, params)
            if not 0 < result.get('generated_tokens', 0) < params['max_tokens']:
                raise MandarinError('unverified token count')
            command(['ffmpeg','-y','-v','error','-xerror','-i',str(raw),'-af',
                'loudnorm=I=-19:TP=-2:LRA=7','-ar',str(RATE),'-ac','1','-c:a','pcm_s16le',str(temporary)])
            duration = verify_pcm(temporary)
            if duration > 145:
                raise MandarinError('chunk exceeds reviewed decoder bound')
            record = {'identity':identity,'duration_seconds':duration,'pcm_sha256':sha(temporary),
                'raw_sha256':sha(raw),'generation':result,'source_text':line.text,'spoken_text':spoken,
                'listening':'pending'}
            temporary.replace(pcm)
            pending = receipt.with_suffix('.partial.json')
            pending.write_text(json.dumps(record, ensure_ascii=False, indent=2))
            pending.replace(receipt)
            progress(f'  chunk {index+1}: rendered and validated {duration:.2f}s')
        records.append(record); paths.append(pcm); durations.append(duration)
    assembled = workdir/'assembled.wav'
    with wave.open(str(assembled), 'wb') as target:
        target.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        for pcm, gap in zip(paths, gaps_for(bp)):
            with wave.open(str(pcm), 'rb') as chunk:
                target.writeframes(chunk.readframes(chunk.getnframes()))
            target.writeframes(bytes(round(gap * RATE) * 2))
    timeline = build_timeline(bp, durations)
    if abs(verify_pcm(assembled) - timeline.total) > len(paths)/RATE:
        raise MandarinError('assembled PCM does not match every source chunk and pause')
    temporary_mp3 = out_path.with_suffix('.partial.mp3')
    gain = bp.tts.get('final_gain_db', 0)
    command(['ffmpeg','-y','-v','error','-xerror','-i',str(assembled),'-ar',str(RATE),'-ac','1',
        '-af',f'volume={gain}dB','-c:a','libmp3lame','-b:a','64k','-id3v2_version','3',str(temporary_mp3)])
    actual = verify_mp3(temporary_mp3)
    if abs(actual - timeline.total) > 0.15:
        raise MandarinError('final encoder duration drift exceeds 150 ms')
    timeline = calibrate(timeline, actual)
    if len(timeline.lines) == 1:
        timeline.lines[0].gap_after += actual - timeline.total
        timeline.total = actual
        timeline.sections[-1].end = actual
    if abs(timeline.total - actual) > 0.05:
        raise MandarinError('timeline calibration failed')
    temporary_mp3.replace(out_path)
    report = {'schema':1,'mp3_sha256':sha(out_path),'source_document':bp.source_document,
        'final_encoding':{'gain_db':gain,'assembled_pcm_sha256':sha(assembled)},
        'blueprint_sha256':text_sha(json.dumps(bp.to_dict(),ensure_ascii=False,sort_keys=True)),
        'chunks':records,'timeline':asdict(timeline),'audio_validation':'pass','listening':'pending',
        'published':False,'note':'Source alignment and decoding do not prove pronunciation or comfort.'}
    out_path.with_suffix('.build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    return timeline


def require_listening_review(bp, path, review_path):
    if not review_path:
        raise MandarinError('publication requires an explicit audio review for this exact MP3 and source')
    review = json.loads(Path(review_path).read_text())
    if (review.get('approved') is not True or not review.get('reviewer') or not review.get('reviewed_at')
            or review.get('open_issues') != [] or review.get('mp3_sha256') != sha(path)
            or review.get('source_sha256') != bp.source_document.get('sha256')):
        raise MandarinError('audio review missing, unresolved, or for a different artifact')
    build = json.loads(Path(path).with_suffix('.build.json').read_text())
    expected_blueprint = text_sha(json.dumps(bp.to_dict(), ensure_ascii=False, sort_keys=True))
    if (build.get('audio_validation') != 'pass' or build.get('mp3_sha256') != sha(path)
            or build.get('source_document') != bp.source_document
            or build.get('blueprint_sha256') != expected_blueprint
            or len(build.get('chunks', [])) != bp.line_count()):
        raise MandarinError('audio build receipt does not match this exact source and blueprint')
    mode = review.get('review_mode', 'listening')
    if mode == 'objective':
        # The user may delegate release without an available listening tool.
        # Record this honestly and bind every automated screen to exact PCM;
        # never label ASR, source hashes or codec checks as human listening.
        if review.get('listening_performed') is not False or not review.get('method') or not review.get('limitations'):
            raise MandarinError('objective review must explicitly disclose its method and lack of listening')
        checks = review.get('chunk_reviews', [])
        expected = [(c['pcm_sha256'], c['identity']['source_text_sha256']) for c in build['chunks']]
        actual = [(c.get('pcm_sha256'), c.get('source_text_sha256')) for c in checks]
        if actual != expected:
            raise MandarinError('objective review does not cover every exact rendered chunk in order')
        review_root = Path(review_path).resolve().parent
        for check in checks:
            evidence = (review_root / check.get('evidence_path', '')).resolve()
            if (check.get('assessment') != 'pass' or not evidence.is_relative_to(review_root)
                    or not evidence.is_file() or sha(evidence) != check.get('evidence_sha256')):
                raise MandarinError('objective review evidence is missing, changed or unresolved')
            payload = json.loads(evidence.read_text())
            if (payload.get('pcm_sha256') != check['pcm_sha256']
                    or payload.get('source_text_sha256') != check['source_text_sha256']
                    or not payload.get('model') or not isinstance(payload.get('text'), str)):
                raise MandarinError('objective evidence is not bound to the reviewed audio and source')
    elif mode != 'listening' or review.get('listening_performed', True) is not True:
        raise MandarinError('unsupported or contradictory audio review mode')
    verify_mp3(path)
