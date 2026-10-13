"""閘門失敗時還原指定成品目錄中的檔案；不適用並行 writer。"""
import subprocess
import sys
from pathlib import Path


def run(directory, command):
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    before = {path: path.read_bytes() for path in directory.iterdir()
              if path.is_file() and not path.is_symlink()}

    def restore():
        for path in directory.iterdir():
            if (path.is_file() or path.is_symlink()) and path not in before:
                path.unlink()
        for path, content in before.items():
            if path.is_symlink():
                path.unlink()
            path.write_bytes(content)

    try:
        for path in before:
            if path.name.endswith(('.browser-check.json', '.finalize.json', '.finalize-summary.json')):
                path.unlink()
        result = subprocess.run(command)
    except BaseException:
        restore()
        raise
    if result.returncode:
        restore()
    return result.returncode


if __name__ == '__main__':
    sys.exit(run(sys.argv[1], sys.argv[2:]))
