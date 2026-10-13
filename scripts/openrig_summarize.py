"""把 OpenRig 示範的原始命令輸出整理成 run.json；只採用實際輸出，並移除主機路徑。"""
import json
import os
import re
from pathlib import Path

RAW = Path(os.environ["RAW"])
OUT = Path(os.environ["OUT"])
LAB_ROOT = os.environ["LAB_ROOT"]
REAL_HOME = os.environ["REAL_HOME"]


def load(name):
    return json.loads((RAW / name).read_text())


def scrub(value):
    text = json.dumps(value, ensure_ascii=False)
    for needle, repl in ((str(OUT), '<out>'), (LAB_ROOT, '<lab>'), (REAL_HOME, '<home>'),
                         ('/tmp/orx.', '<tmux>')):
        text = text.replace(needle, repl)
    text = re.sub(r'127\.0\.0\.1:\d+', '127.0.0.1:<port>', text)
    return json.loads(text)


def last_json_object(path):
    text = (RAW / path).read_text()
    start = text.find('{')
    return json.loads(text[start:]) if start >= 0 else {}


version = (RAW / 'version.txt').read_text().strip()
nodes = load('ps-nodes.json')
seats = [{'logical_id': n['logicalId'], 'session': n['canonicalSessionName'], 'runtime': n['runtime'],
          'startup_status': n['startupStatus'], 'lifecycle': n['lifecycleState']}
         for n in sorted(nodes, key=lambda n: n['logicalId'])]

qids = load('qids.json')
chain = []
for qid in qids:
    item = load(f'show-{qid}.json')
    chain.append({'owner': item['destinationSession'], 'source': item['sourceSession'],
                  'summary': item.get('summary'), 'final_state': item['state'],
                  'closure_reason': item.get('closureReason'), 'handed_off_to': item.get('handedOffTo')})

plain = last_json_object('restore-plain.json')
fresh = last_json_object('restore-fresh.json')
without_fresh = [n['status'] for n in sorted(plain.get('nodes', []), key=lambda n: n['logicalId'])]
with_fresh = [n['status'] for n in sorted(fresh.get('nodes', []), key=lambda n: n['logicalId'])]
after = load('ps-after.json')

send_text = (RAW / 'send.txt').read_text()
capture = (RAW / 'capture-scout.txt').read_text()

checks = {
    'validate_passed': 'valid' in (RAW / 'validate.txt').read_text().lower(),
    'three_seats_ready': len(seats) == 3 and all(s['startup_status'] == 'ready' for s in seats),
    'all_runtime_stub': all(s['runtime'] == 'stub' for s in seats),
    'queue_chain_complete': [c['final_state'] for c in chain] == ['handed-off', 'handed-off', 'done'],
    'send_verified': 'Verified: yes' in send_text,
    'message_in_pane': 'hello from the lab' in capture,
    'restore_needs_fresh': without_fresh == ['awaiting-decision'] * 3,
    'restore_fresh_primed': with_fresh == ['fresh-primed'] * 3,
    'restored_running': len(after) == 3 and all(n['lifecycleState'] == 'running' for n in after),
    'global_files_unchanged': os.environ['BEFORE'] == os.environ['AFTER'],
}
run = {
    'openrig_version': version,
    'seats': seats,
    'queue_chain': chain,
    'restore': {'without_fresh': without_fresh, 'with_fresh': with_fresh},
    'send': {'verified': checks['send_verified'], 'agent_acknowledged': False,
             'meaning': '訊息已出現在目標 pane；stub 不會讀取輸入或回覆'},
    'checks': checks,
    'limits': ['stub 席位不呼叫模型', '只驗證本機 tmux、daemon、SQLite 與 CLI 的團隊機制',
               '未測 Claude Code 或 Codex 真實席位、herdr、cmux 與跨主機'],
}
(OUT / 'run.json').write_text(json.dumps(scrub(run), ensure_ascii=False, indent=2) + '\n')
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('檢查失敗：' + ', '.join(failed))
