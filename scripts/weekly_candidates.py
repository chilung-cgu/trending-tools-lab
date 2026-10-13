"""每週從 data/index.json 挑出「本週新上榜」的候選 repo，輸出繁中報告，供人工決定要實踐哪些。

只產生報告，不下載、不安裝、不發布。查不到的事實一律標示「未查證」，不推測。
--offline 不連網；否則只對候選 repo 讀取 GitHub 公開 API 的授權、封存狀態與最近推送時間。
"""
import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNVERIFIED = '未查證'
# 已經實踐過的 repo（owner/name 小寫）。
BUILT = {'mvschwarz/openrig', 'earthtojake/text-to-cad', 'heygen-com/hyperframes',
         'mksglu/context-mode', 'pbakaus/impeccable', 'tt-a1i/archify', 'max-sixty/worktrunk'}


def seen_before(snapshots):
    names = set()
    for snap in snapshots:
        for period in ('weekly', 'monthly'):
            names.update(i['full_name'].lower() for i in snap[period])
    return names


def pick(snapshots, built):
    """最新快照中，先前任何快照（週榜或月榜）都沒出現過的 repo。只有一份快照時沒有比較基準，回傳空。"""
    if len(snapshots) < 2:
        return []
    latest, earlier = snapshots[-1], snapshots[:-1]
    known = seen_before(earlier) | {b.lower() for b in built}
    result = []
    for period in ('weekly', 'monthly'):
        for it in latest[period]:
            name = it['full_name']
            if name.lower() in known or any(r['full_name'] == name for r in result):
                continue
            result.append({**it, 'period': period, 'first_observed': latest['date']})
    return result


def facts_from_api(payload):
    if payload is None:
        return {'license': UNVERIFIED, 'archived': UNVERIFIED, 'pushed_at': UNVERIFIED}
    lic = payload.get('license')
    return {'license': (lic or {}).get('spdx_id') if lic else '無授權資訊',
            'archived': payload.get('archived'), 'pushed_at': payload.get('pushed_at') or UNVERIFIED}


def fetch_facts(full_name, timeout=15):
    request = urllib.request.Request(f'https://api.github.com/repos/{full_name}',
                                     headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'trending-tools-lab'})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return facts_from_api(json.load(response))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return facts_from_api(None)


def render(candidates, snapshots, facts):
    latest = snapshots[-1]['date']
    lines = [f'# 本週候選（觀測日 {latest}）', '',
             '資料是 Trending 快照的歷史觀測。週榜與月榜為滾動區間，period_stars 不累加；沒進 Top 10 代表未觀測，不是 0。', '']
    if not candidates:
        lines.append('本週沒有先前快照都沒出現過、且尚未實踐的新 repo。')
        return '\n'.join(lines) + '\n'
    lines.append(f'共 {len(candidates)} 個候選（{UNVERIFIED}代表沒有連網查核，不是沒有）：')
    lines.append('')
    for c in candidates:
        f = facts.get(c['full_name'], facts_from_api(None))
        lines += [f"## {c['full_name']}",
                  f"- 榜單：{'週榜' if c['period'] == 'weekly' else '月榜'}第 {c['rank']} 名，{c.get('period_label', '')} {c.get('period_stars', UNVERIFIED)}",
                  f"- 語言：{c.get('language') or UNVERIFIED}",
                  f"- 描述：{c.get('description') or UNVERIFIED}",
                  f"- 授權：{f['license']}；封存：{f['archived']}；最近推送：{f['pushed_at']}",
                  f"- 連結：{c['url']}", '']
    lines.append('下一步由人決定：讀官方 README、確認安裝需求與授權，再實踐成小成果。')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--offline', action='store_true', help='不連網，授權等事實標示為未查證')
    parser.add_argument('--index', default=str(ROOT / 'data/index.json'))
    args = parser.parse_args(argv)
    snapshots = json.loads(Path(args.index).read_text())['snapshots']
    candidates = pick(snapshots, BUILT)
    facts = {} if args.offline else {c['full_name']: fetch_facts(c['full_name']) for c in candidates}
    sys.stdout.write(render(candidates, snapshots, facts))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
