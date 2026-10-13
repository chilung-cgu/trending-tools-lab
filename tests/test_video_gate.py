import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('receipt', [
    '{"ok":false,"browserSkipped":true}',
    '{"ok":false,"browserSkipped":false}',
])
def test_failed_or_skipped_browser_gate_stops_render(tmp_path, receipt):
    scripts = tmp_path / 'scripts'
    scripts.mkdir()
    shutil.copy2(ROOT / 'scripts/build_video.sh', scripts)
    (scripts / 'generate_video.py').write_text('')
    executables = tmp_path / 'bin'
    executables.mkdir()
    hyperframes = executables / 'hyperframes'
    hyperframes.write_text('#!/bin/sh\ncase "$1" in\n'
                          f'check) printf \'%s\\n\' \'{receipt}\';;\n'
                          'render) touch "$PROBE_RENDER_MARKER";;\n'
                          '*) printf \'{}\\n\';;\nesac\n')
    hyperframes.chmod(0o755)
    for name in ['ffprobe', 'ffmpeg']:
        tool = executables / name
        tool.write_text('#!/bin/sh\nprintf \'{}\\n\'\n')
        tool.chmod(0o755)
    marker = tmp_path / 'render-started'
    env = dict(os.environ, PATH=str(executables) + ':' + os.environ['PATH'],
               HYPERFRAMES_BROWSER_PATH='/unused/browser',
               PROBE_RENDER_MARKER=str(marker), PYTHONOPTIMIZE='1')
    result = subprocess.run(['sh', str(scripts / 'build_video.sh')], cwd=tmp_path,
                            env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert not marker.exists(), 'A failed browser check must stop before invoking renderer'
