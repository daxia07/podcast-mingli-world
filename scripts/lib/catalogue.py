"""Offline, lossless catalogue reconciliation and reversible display proposals."""
from copy import deepcopy
from collections import defaultdict
import hashlib
import json
from urllib.parse import urlsplit


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def indexed(document):
    if not isinstance(document, dict) or not isinstance(document.get('episodes'), list):
        raise ValueError('unverified episode catalogue')
    if not isinstance(document.get('playlists'), dict):
        raise ValueError('unverified show catalogue')
    result = {}
    for episode in document['episodes']:
        if not isinstance(episode, dict) or type(episode.get('id')) is not int:
            raise ValueError('each episode needs an integer identity')
        if episode['id'] in result:
            raise ValueError('duplicate episode identity')
        result[episode['id']] = episode
    return result


def reconcile(local, captured_live):
    """Merge additions only; any conflicting shared value needs separate review."""
    left, right = indexed(local), indexed(captured_live)
    for eid in left.keys() & right.keys():
        if left[eid] != right[eid]:
            raise ValueError(f'episode {eid} has conflicting records; refusing an overwrite')
    for sid in local['playlists'].keys() & captured_live['playlists'].keys():
        if local['playlists'][sid] != captured_live['playlists'][sid]:
            raise ValueError(f'show {sid} has conflicting records')
    for key in local.keys() & captured_live.keys() - {'episodes', 'playlists'}:
        if local[key] != captured_live[key]:
            raise ValueError(f'catalogue field {key} conflicts')
    result = deepcopy(captured_live)
    for key in local.keys() - result.keys():
        result[key] = deepcopy(local[key])
    result['episodes'].extend(deepcopy(left[eid]) for eid in left.keys() - right.keys())
    result['episodes'].sort(key=lambda episode: episode['id'])
    for sid in local['playlists'].keys() - result['playlists'].keys():
        result['playlists'][sid] = deepcopy(local['playlists'][sid])
    # Check every original, not merely counts or URLs.
    merged = indexed(result)
    assert all(merged[eid] == ep for catalogue in (left, right) for eid, ep in catalogue.items())
    return result


def display_proposal(manifest):
    """Choose representative labels for exact URL aliases; never infer content."""
    groups = defaultdict(list)
    for ep in indexed(manifest).values():
        parsed = urlsplit(ep.get('file_url', ''))
        if parsed.scheme in ('http', 'https') and parsed.netloc and parsed.path.endswith('.mp3'):
            groups[ep['file_url']].append(ep)

    def score(ep):
        return (int(bool(ep.get('has_transcript'))) + int(bool(ep.get('has_chapters'))),
                sum(bool(ep.get(k)) for k in ('title','description','slug','date','duration','source')),
                min(len(ep.get('description', '').strip()), 500), -ep['id'])

    result = {'schema':1,'status':'local review proposal; not published',
        'rule':'Group exact full audio URLs only. Rank transcript/chapter availability, populated title/description/slug/date/duration/source fields, description length capped at 500, then smallest ID. This selects a display label, not a verified transcript or audio title.',
        'preservation':'Every original record, ID, URL, playlist membership, RSS item, saved progress and queue identity remains intact. Restore aliases per device; undo removes only that visibility override.',
        'manifest_sha256':digest(manifest),'groups':[],'aliases':{}}
    for url, episodes in sorted(groups.items()):
        if len(episodes) < 2:
            continue
        canonical = max(episodes, key=score)
        aliases = [ep['id'] for ep in episodes if ep['id'] != canonical['id']]
        result['groups'].append({'file_url':url,'canonical_id':canonical['id'],'alias_ids':aliases,
            'records':[{'id':ep['id'],'title':ep.get('title'),'score':list(score(ep)),
                        'record_sha256':digest(ep)} for ep in episodes]})
        result['aliases'].update({str(eid):canonical['id'] for eid in aliases})
    return result


def validate_aliases(manifest):
    episodes = indexed(manifest)
    aliases = manifest.get('display_aliases', {})
    if not isinstance(aliases, dict):
        raise ValueError('display_aliases must be an object')
    for key, canonical in aliases.items():
        if not str(key).isdigit() or int(key) not in episodes or canonical not in episodes:
            raise ValueError('alias refers to a missing identity')
        if int(key) == canonical or str(canonical) in aliases:
            raise ValueError('alias cycles/chains are not allowed')
        if episodes[int(key)]['file_url'] != episodes[canonical]['file_url']:
            raise ValueError('display aliases must share the exact audio URL')
    return True
