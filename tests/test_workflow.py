import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_failed_crawl_still_commits_snapshot_before_debug_upload():
    diagram = json.loads((ROOT / 'diagrams/crawler.workflow.json').read_text())
    pairs = {(edge['from'], edge['to']) for edge in diagram['edges']}
    assert ('validate_shape', 'git_push') in pairs, 'Valid partial/error snapshot must still reach commit'
    assert ('git_push', 'upload_debug') in pairs, 'Debug upload follows successful commit step'
    assert ('validate_shape', 'upload_debug') not in pairs, 'Do not imply validation failure reaches debug upload'


def test_validation_and_push_errors_abort_job():
    diagram = json.loads((ROOT / 'diagrams/crawler.workflow.json').read_text())
    pairs = {(edge['from'], edge['to']) for edge in diagram['edges']}
    assert ('validate_shape', 'fail_workflow') in pairs
    assert ('git_push', 'fail_workflow') in pairs
