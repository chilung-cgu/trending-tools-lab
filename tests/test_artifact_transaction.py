import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_failed_gate_restores_last_artifact_and_sidecars(tmp_path):
    output = tmp_path / 'artifact'
    output.mkdir()
    (output / 'crawler.html').write_text('last successful artifact')
    (output / 'crawler.browser-check.json').write_text('last successful receipt')
    child = tmp_path / 'fail.py'
    child.write_text('from pathlib import Path\nimport sys\np=Path(sys.argv[1])\n(p/"crawler.html").write_text("broken candidate")\n(p/"new.receipt.json").write_text("failure")\nsys.exit(1)\n')
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/protect_artifact.py'),
                             str(output), sys.executable, str(child), str(output)])
    assert result.returncode == 1
    assert (output / 'crawler.html').read_text() == 'last successful artifact'
    assert (output / 'crawler.browser-check.json').read_text() == 'last successful receipt'
    assert not (output / 'new.receipt.json').exists()
