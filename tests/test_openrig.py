import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RIG = ROOT / 'openrig/node_modules/.bin/rig'
NODE_BIN = ROOT / '.tools/node/bin'

pytestmark = pytest.mark.skipif(not RIG.exists(), reason='OpenRig CLI 尚未以 npm ci 安裝')


def _env():
    return dict(os.environ, PATH=f'{NODE_BIN}:{os.environ["PATH"]}')


def test_trending_desk_spec_is_valid_and_has_three_stub_seats():
    spec = ROOT / 'openrig/rigs/trending-desk/rig.yaml'
    result = subprocess.run([str(RIG), 'spec', 'validate', str(spec)], env=_env(),
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    text = spec.read_text()
    for seat in ('lead', 'scout', 'reviewer'):
        assert f'id: {seat}' in text
    assert text.count('runtime: stub') == 3


def test_demo_runs_in_isolation_and_records_real_orchestration(tmp_path):
    out = tmp_path / 'run'
    result = subprocess.run(['bash', str(ROOT / 'scripts/openrig_demo.sh'), '--out', str(out)],
                            env=_env(), capture_output=True, text=True, timeout=240)
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-3000:]
    run = json.loads((out / 'run.json').read_text())
    assert run['openrig_version'].startswith('0.6.10')
    assert run['checks'] == {name: True for name in run['checks']}
    assert run['checks']['global_files_unchanged'] is True
    assert [seat['logical_id'] for seat in run['seats']] == ['desk.lead', 'desk.reviewer', 'desk.scout']
    assert all(seat['startup_status'] == 'ready' for seat in run['seats'])
    chain = run['queue_chain']
    assert [item['owner'] for item in chain] == ['desk-scout@triage', 'desk-reviewer@triage', 'desk-lead@triage']
    assert [item['final_state'] for item in chain] == ['handed-off', 'handed-off', 'done']
    assert run['restore']['without_fresh'] == ['awaiting-decision'] * 3
    assert run['restore']['with_fresh'] == ['fresh-primed'] * 3
    assert run['send']['verified'] is True
    assert run['send']['agent_acknowledged'] is False
    assert '/home/ubuntu' not in json.dumps(run), 'published results must not leak host paths'


def test_demo_refuses_to_run_against_an_existing_sandbox_directory(tmp_path):
    existing = tmp_path / 'occupied'
    existing.mkdir()
    (existing / 'keep.txt').write_text('keep')
    result = subprocess.run(['bash', str(ROOT / 'scripts/openrig_demo.sh'), '--out', str(existing)],
                            env=_env(), capture_output=True, text=True, timeout=60)
    assert result.returncode != 0
    assert (existing / 'keep.txt').read_text() == 'keep'


def test_bundle_keeps_hidden_stub_scripts_that_the_team_needs(tmp_path):
    import importlib.util
    import zipfile
    spec = importlib.util.spec_from_file_location('package_bundle', ROOT / 'scripts/package_bundle.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUTPUT = tmp_path / 'bundle.zip'
    module.package()
    with zipfile.ZipFile(module.OUTPUT) as archive:
        names = set(archive.namelist())
    for seat in ('lead', 'scout', 'reviewer'):
        assert f'trending-tools-lab/openrig/rigs/trending-desk/seats/{seat}/.openrig/stub/script.json' in names
