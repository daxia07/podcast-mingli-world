#!/usr/bin/env python3
"""Reconcile a saved public snapshot locally; this command never uses the network."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lib import catalogue, manifest, gates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('--apply-local', action='store_true')
    args = parser.parse_args()
    local = manifest.load()
    remote = json.loads(args.snapshot.read_text())
    candidate = catalogue.reconcile(local, remote)
    errors = [f for f in gates.run_manifest(candidate) + gates.gate_show_registry(candidate) if f.level == gates.ERROR]
    if errors:
        raise ValueError('\n'.join(str(f) for f in errors))
    old_ids = {ep['id'] for ep in local['episodes']}
    added = [ep for ep in candidate['episodes'] if ep['id'] not in old_ids]
    print(json.dumps({'episodes':len(candidate['episodes']),'shows':len(candidate['playlists']),
        'added_ids':[ep['id'] for ep in added],'shared_records_preserved':True,'applied_locally':args.apply_local}))
    if not args.apply_local:
        return
    shows_path = Path('content/shows.json'); shows = json.loads(shows_path.read_text())
    for sid, show in candidate['playlists'].items():
        if sid not in shows['shows']:
            shows['shows'][sid] = {k:v for k,v in show.items() if k != 'episode_ids'}
    frozen_path = Path('content/reconciled-live-episodes.json'); frozen = json.loads(frozen_path.read_text())
    existing = {ep['id'] for ep in frozen['episodes']}
    frozen['episodes'].extend({'id':ep['id'],'slug':ep['slug']} for ep in added if ep['id'] not in existing)
    frozen['reconciled_at'] = '2026-10-02'
    frozen['note'] = 'Exact ID/slug pairs already published while Git lagged behind R2. Source scripts are owned elsewhere. This list preserves existing content; genuinely new episodes still require blueprints.'
    shows_path.write_text(json.dumps(shows, ensure_ascii=False, indent=2)+'\n')
    frozen_path.write_text(json.dumps(frozen, ensure_ascii=False, indent=2)+'\n')
    manifest.save_local(candidate)


if __name__ == '__main__':
    main()
