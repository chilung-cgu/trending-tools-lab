import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://github.com/chilung-cgu/trending-tools-lab/blob/main/'
# 在 Pages 上瀏覽器會把這些副檔名當原始檔案下載或顯示成文字，不是可閱讀的頁面。
# 程式、設定與原始文件在 Pages 上會被下載或顯示成純文字，必須改連 GitHub 原始碼檢視頁或渲染後的網頁。
# 純資料檔（json、txt、log）刻意允許：瀏覽器直接顯示內容，這正是想給讀者看的原始紀錄。
RAW_SUFFIXES = ('.md', '.py', '.sh', '.yaml', '.yml', '.js')
MEDIA = ('.png', '.pdf', '.mp4', '.glb', '.stl', '.step')


def tracked_html():
    out = subprocess.check_output(['git', 'ls-files', '*.html'], cwd=ROOT, text=True).split()
    return [p for p in out if not p.startswith('artifacts/cad/assets/')]


def hrefs(path):
    text = (ROOT / path).read_text(errors='ignore')
    return re.findall(r'(?:href|src)="([^"#]+)(?:#[^"]*)?"', text)


def anchors(path):
    """只取 a 標籤的 href：讀者點擊後才會下載或看到原始碼；script 與 link 載入的頁面資源不算。"""
    text = (ROOT / path).read_text(errors='ignore')
    return re.findall(r'<a\s[^>]*href="([^"#]+)(?:#[^"]*)?"', text)


def is_local(target):
    return not target.startswith(('http://', 'https://', 'mailto:', 'data:', '//'))


def test_site_has_nojekyll_marker_or_pages_workflow_that_bypasses_jekyll():
    workflow = ROOT / '.github/workflows/pages.yml'
    assert workflow.exists()
    text = workflow.read_text()
    assert 'actions/deploy-pages' in text and 'actions/upload-pages-artifact' in text
    assert (ROOT / '.nojekyll').exists(), 'Jekyll would drop the hidden .openrig stub scripts'


def test_no_root_absolute_urls_that_break_under_the_repo_subpath():
    for page in tracked_html():
        for target in hrefs(page):
            assert not re.match(r'^/[^/]', target), f'{page}: {target} breaks under /trending-tools-lab/'


def test_pages_never_link_to_raw_source_files_that_would_download_instead_of_render():
    offenders = []
    for page in tracked_html():
        for target in anchors(page):
            if is_local(target) and target.lower().endswith(RAW_SUFFIXES):
                offenders.append((page, target))
    assert offenders == [], offenders


def test_every_local_link_resolves_to_a_published_file():
    missing = []
    for page in tracked_html():
        for target in hrefs(page):
            if not is_local(target):
                continue
            path = (ROOT / page).parent / target
            resolved = (path / 'index.html') if target.endswith('/') else path
            if not resolved.exists():
                missing.append((page, target))
    assert missing == [], missing


def test_site_is_assembled_from_tracked_files_only():
    """網站內容只來自 git 追蹤的檔案，所以被忽略的 .sandbox、.venv、node_modules、vendor 不可能被發布。"""
    workflow = (ROOT / '.github/workflows/pages.yml').read_text()
    assert 'git ls-files' in workflow
    assert 'path: _site' in workflow
    assert 'uses: actions/checkout@' in workflow
    for ignored in ('.sandbox', '.venv', '.tools', 'node_modules', 'vendor'):
        assert ignored in (ROOT / '.gitignore').read_text()


def test_workflow_uses_least_privilege_and_pinned_actions():
    workflow = (ROOT / '.github/workflows/pages.yml').read_text()
    assert 'pages: write' in workflow and 'id-token: write' in workflow and 'contents: read' in workflow
    assert 'permissions: write-all' not in workflow
    for action in re.findall(r'uses:\s*(\S+)', workflow):
        assert re.search(r'@[0-9a-f]{40}$', action), f'action not pinned to a commit: {action}'


def test_readme_gives_the_live_site_address():
    assert 'https://chilung-cgu.github.io/trending-tools-lab/' in (ROOT / 'README.md').read_text()


def test_no_clickable_localhost_links_that_would_point_at_the_readers_own_machine():
    offenders = []
    for page in tracked_html():
        for target in anchors(page):
            if target.startswith(('http://127.0.0.1', 'http://localhost')):
                offenders.append((page, target))
    assert offenders == [], offenders
