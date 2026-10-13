import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'vendor/crawler'
DATES = {'2026-09-21', '2026-09-28', '2026-10-05', '2026-10-12'}
PATH = 'data/github-trending/latest-success.json'


def export():
    log = subprocess.check_output(
        ['git', '-C', str(SOURCE), 'log', '--format=%H', '--', PATH], text=True)
    snapshots = {}
    for commit in log.splitlines():
        content = subprocess.check_output(
            ['git', '-C', str(SOURCE), 'show', f'{commit}:{PATH}'])
        raw = json.loads(content)
        date = raw['generated_at_taipei'][:10]
        if date not in DATES or date in snapshots or raw['status'] != 'ok':
            continue
        if any(raw['periods'][p]['status'] != 'ok' for p in ('weekly', 'monthly')):
            continue
        (ROOT / 'data/raw').mkdir(parents=True, exist_ok=True)
        (ROOT / 'data/raw' / f'{date}.json').write_bytes(content)
        snapshots[date] = {
            'date': date, 'commit': commit,
            'generated_at_taipei': raw['generated_at_taipei'],
            'source_url': f'https://github.com/chilung-cgu/github-trending-crawler/blob/{commit}/{PATH}',
            **{p: raw['periods'][p]['items'] for p in ('weekly', 'monthly')},
        }
    if set(snapshots) != DATES:
        raise RuntimeError(f'Missing snapshots: {DATES - set(snapshots)}')
    index = {'schema_version': 1, 'snapshots': [snapshots[d] for d in sorted(snapshots)]}
    (ROOT / 'data/index.json').write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    (ROOT / 'data/provenance.json').write_text(json.dumps({
        'repository': 'https://github.com/chilung-cgu/github-trending-crawler',
        'selection': 'last successful snapshot per Taipei date, by git history',
        'commits': {d: s['commit'] for d, s in sorted(snapshots.items())},
        'limitations': ['top 10 only', 'weekly and monthly rolling windows overlap',
                        'absence is unobserved, not zero stars'],
    }, ensure_ascii=False, indent=2) + '\n')
    print(f'Exported {len(snapshots)} snapshots')


if __name__ == '__main__':
    export()
