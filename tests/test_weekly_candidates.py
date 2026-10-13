import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import weekly_candidates as wc  # noqa: E402


def snap(date, weekly, monthly=()):
    return {'date': date, 'weekly': list(weekly), 'monthly': list(monthly)}


def item(name, rank, stars=100, language='Python', description='d'):
    return {'full_name': name, 'rank': rank, 'period_stars': stars, 'language': language,
            'description': description, 'url': f'https://github.com/{name}'}


def test_new_this_week_excludes_repos_seen_before_and_already_built():
    snapshots = [snap('2026-10-05', [item('a/old', 1)], [item('b/seen-monthly', 1)]),
                 snap('2026-10-12', [item('a/old', 1), item('c/new', 2), item('d/built', 3), item('b/seen-monthly', 4)])]
    result = wc.pick(snapshots, built={'d/built'})
    assert [c['full_name'] for c in result] == ['c/new']
    assert result[0]['first_observed'] == '2026-10-12'


def test_a_repo_missing_in_earlier_weeks_is_unobserved_not_new_if_it_appeared_earlier():
    snapshots = [snap('2026-09-28', [item('x/y', 5)]), snap('2026-10-05', []),
                 snap('2026-10-12', [item('x/y', 2)])]
    assert wc.pick(snapshots, built=set()) == []


def test_single_snapshot_has_no_baseline_so_nothing_is_called_new():
    assert wc.pick([snap('2026-10-12', [item('a/b', 1)])], built=set()) == []


def test_candidates_keep_unknown_facts_as_unverified_and_never_guess():
    facts = wc.facts_from_api(None)
    assert facts == {'license': '未查證', 'archived': '未查證', 'pushed_at': '未查證'}
    facts = wc.facts_from_api({'license': None, 'archived': False, 'pushed_at': '2026-10-10T00:00:00Z'})
    assert facts['license'] == '無授權資訊'
    assert facts['archived'] is False


def test_report_never_claims_stars_are_additive_and_states_the_observation_window():
    snapshots = [snap('2026-10-05', [item('a/old', 1)]), snap('2026-10-12', [item('c/new', 2, stars=900)])]
    report = wc.render(wc.pick(snapshots, built=set()), snapshots, facts={})
    assert '滾動' in report and '不累加' in report
    assert '2026-10-12' in report and 'c/new' in report


def test_cli_prints_report_for_real_data_without_network(tmp_path):
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/weekly_candidates.py'), '--offline'],
                            capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0, result.stderr
    assert '候選' in result.stdout and '未查證' in result.stdout
