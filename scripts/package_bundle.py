"""打包可攜成品及來源；不收錄執行環境、MCP DB 或 agent session。"""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'artifacts/trending-tools-lab.zip'
DIRECTORIES = ['web', 'video', 'cad', 'diagrams', 'context', 'docs', 'scripts',
               'tests', 'data', 'artifacts/archify', 'artifacts/cad', 'artifacts/video', 'artifacts/openrig', 'openrig/rigs',
               'evidence/archify', 'evidence/cad', 'evidence/context',
               'evidence/worktrunk', 'evidence/impeccable']
FILES = ['index.html', 'README.md', 'README.html', 'package.json', 'package-lock.json',
         'pyproject.toml', 'uv.lock', 'playwright.config.js', 'evidence/verification.json',
         'evidence/playwright.json', 'evidence/final-review.md', 'evidence/portable-verification.json', 'NOTICE.md', 'NOTICE.html', 'LICENSE',
         'evidence/re-review-source.json', 'evidence/re-review-python.log',
         'evidence/re-review-browser.log', 'evidence/re-review-cad-cache.log',
         'evidence/re-review-context-red.log', 'evidence/re-review-context-green.log',
         'evidence/re-review-video-gate-red.log', 'evidence/re-review-video-gate-green.log']


def package():
    paths = {ROOT / relative for relative in FILES if (ROOT / relative).is_file()}
    for directory in DIRECTORIES:
        for path in (ROOT / directory).rglob('*'):
            relative_parts = path.relative_to(ROOT).parts
            # OpenRig 席位的 stub 劇本放在 .openrig/，是示範必要檔案；其他隱藏目錄仍然排除。
            hidden_allowed = relative_parts[:2] == ('openrig', 'rigs')
            if path.is_file() and not path.is_symlink() and not any(
                    (part.startswith('.') and not hidden_allowed) or part in {'__pycache__', 'test-results'}
                    for part in relative_parts):
                paths.add(path)
    manifest = {}
    OUTPUT.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(paths):
            relative = path.relative_to(ROOT).as_posix()
            content = path.read_bytes()
            manifest[relative] = hashlib.sha256(content).hexdigest()
            archive.writestr('trending-tools-lab/' + relative, content)
        archive.writestr('trending-tools-lab/BUNDLE-MANIFEST.json', json.dumps(manifest, indent=2))
    with zipfile.ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        for relative, checksum in manifest.items():
            assert hashlib.sha256(archive.read('trending-tools-lab/' + relative)).hexdigest() == checksum
    print(f'{OUTPUT}: {len(manifest)} files, {OUTPUT.stat().st_size:,} bytes, verified SHA-256 manifest')


if __name__ == '__main__':
    package()
