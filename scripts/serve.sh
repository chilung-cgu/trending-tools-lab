#!/bin/sh
set -eu
LAB_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$LAB_ROOT"
PORT=${1:-8765}
printf '開啟 http://127.0.0.1:%s/ （Ctrl+C 停止）\n' "$PORT"
exec python3 -m http.server "$PORT" --bind 127.0.0.1
