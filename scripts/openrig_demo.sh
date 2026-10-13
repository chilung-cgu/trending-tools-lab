#!/usr/bin/env bash
# 在完全隔離的 HOME / OPENRIG_HOME / tmux socket 中執行 OpenRig 三席 stub 團隊示範。
# 產生 <out>/run.json（真實命令輸出的整理結果）；不修改使用者的 ~/.codex、~/.claude、~/.tmux.conf。
set -euo pipefail
trap 'echo "失敗：第 $LINENO 行：$BASH_COMMAND" >&2' ERR

LAB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REAL_HOME="$HOME"
OUT=""
SHOTS=0
while [ $# -gt 0 ]; do
  case "$1" in
    --out) OUT="$2"; shift 2 ;;
    --shots) SHOTS=1; shift ;;
    *) echo "未知參數：$1" >&2; exit 2 ;;
  esac
done
[ -n "$OUT" ] || { echo "用法：$0 --out <不存在或為空的目錄> [--shots]" >&2; exit 2; }
if [ -e "$OUT" ] && [ -n "$(ls -A "$OUT" 2>/dev/null || true)" ]; then
  echo "拒絕使用非空目錄：$OUT" >&2
  exit 3
fi
RIG="$LAB_ROOT/openrig/node_modules/.bin/rig"
[ -x "$RIG" ] || { echo "找不到 OpenRig CLI；請先在 openrig/ 執行 npm ci" >&2; exit 4; }

mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"
SB="$OUT/sandbox"
mkdir -p "$SB/home" "$SB/user/.codex" "$SB/user/.claude"
# 沙箱 HOME 沒有 .zshrc 時，tmux 內的 zsh 會停在首次設定精靈，stub 永遠收不到啟動指令。
: > "$SB/user/.zshrc"
TMUX_DIR="$(mktemp -d /tmp/orx.XXXXXX)"
TMUX_ISOLATED=0
cleanup() {
  set +e
  if [ "$TMUX_ISOLATED" = 1 ] && [ -n "${TMUX_TMPDIR:-}" ] && [ "$TMUX_TMPDIR" = "$TMUX_DIR" ]; then
    "$RIG" down triage --delete --force >/dev/null 2>&1
    "$RIG" daemon stop >/dev/null 2>&1
    # 只在確認 TMUX_TMPDIR 已指向本次隔離目錄時才關閉 tmux，避免誤殺使用者的工作階段。
    tmux kill-server >/dev/null 2>&1
  fi
  python3 -c 'import shutil,sys;shutil.rmtree(sys.argv[1],ignore_errors=True)' "$TMUX_DIR"
}
trap cleanup EXIT
PORT="$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1])')"

snapshot_globals() {
  REAL_HOME="$REAL_HOME" python3 - <<'PY'
import hashlib, os
from pathlib import Path
home = Path(os.environ["REAL_HOME"])
h = hashlib.sha256()
for rel in [".codex/config.toml", ".codex/AGENTS.md", ".tmux.conf", ".claude.json", ".claude/settings.json"]:
    p = home / rel
    h.update(rel.encode())
    h.update(hashlib.sha256(p.read_bytes()).digest() if p.is_file() else b"absent")
for rel in [".claude/skills", ".agents/skills"]:
    d = home / rel
    h.update(rel.encode())
    if d.is_dir():
        for f in sorted(d.rglob("*")):
            h.update(str(f.relative_to(d)).encode())
            h.update(str(f.lstat().st_mtime_ns).encode())
h.update(b"openrig-home:" + (b"present" if (home / ".openrig").exists() else b"absent"))
print(h.hexdigest())
PY
}
BEFORE="$(snapshot_globals)"

export PATH="$LAB_ROOT/.tools/node/bin:$LAB_ROOT/openrig/node_modules/.bin:$PATH"
export OPENRIG_HOME="$SB/home" HOME="$SB/user" CODEX_HOME="$SB/user/.codex" CLAUDE_CONFIG_DIR="$SB/user/.claude"
export TMUX_TMPDIR="$TMUX_DIR" OPENRIG_URL="http://127.0.0.1:$PORT"
export XDG_CONFIG_HOME="$SB/user/.config" XDG_DATA_HOME="$SB/user/.local/share" XDG_STATE_HOME="$SB/user/.local/state" XDG_CACHE_HOME="$SB/user/.cache"
TMUX_ISOLATED=1
unset TMUX OPENRIG_SESSION_NAME


mkdir -p "$SB/rig"
cp -R "$LAB_ROOT/openrig/rigs/trending-desk/." "$SB/rig/"
SPEC="$SB/rig/rig.yaml"
RAW="$OUT/raw"
mkdir -p "$RAW"

"$RIG" --version > "$RAW/version.txt"
"$RIG" spec validate "$SPEC" > "$RAW/validate.txt" 2>&1
"$RIG" config set ui.enabled true > "$RAW/config.txt" 2>&1
"$RIG" daemon start --no-kernel --port "$PORT" --host 127.0.0.1 > "$RAW/daemon-start.txt" 2>&1
"$RIG" up "$SPEC" --json > "$RAW/up.json" 2>&1

wait_ready() {
  for _ in $(seq 1 40); do
    if "$RIG" ps --nodes --rig triage --json > "$RAW/ps-nodes.tmp" 2>/dev/null \
       && python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));sys.exit(0 if len(d)==3 and all(n["startupStatus"]=="ready" and n["lifecycleState"]=="running" for n in d) else 1)' "$RAW/ps-nodes.tmp"; then
      mv "$RAW/ps-nodes.tmp" "$RAW/ps-nodes.json"
      return 0
    fi
    sleep 1
  done
  return 1
}
wait_ready || { echo "席位未在 40 秒內就緒" >&2; exit 5; }

"$RIG" capture desk-lead@triage --lines 40 > "$RAW/capture-lead.txt" 2>&1 || true

as_seat() { local seat="$1"; shift; OPENRIG_SESSION_NAME="$seat" "$RIG" "$@"; }
# 命令的 JSON 在 stdout；說明與警告在 stderr，分開保存才能解析。
as_seat_json() { local seat="$1" name="$2"; shift 2; OPENRIG_SESSION_NAME="$seat" "$RIG" "$@" > "$RAW/$name.json" 2> "$RAW/$name.stderr"; }
newest_for() { "$RIG" queue list --destination "$1" --json 2>/dev/null | python3 -c 'import json,sys;rows=json.load(sys.stdin);print(sorted(rows,key=lambda r:r["tsCreated"])[-1]["qitemId"])'; }

# 1. lead 派工給 scout；2. scout 查核後交給 reviewer；3. reviewer 覆核後交回 lead；4. lead 驗收結案
as_seat_json desk-lead@triage q1-create queue create --source desk-lead@triage --destination desk-scout@triage \
  --summary "查核候選 repo" --body "查核候選 repo 的授權、安裝需求與帳號需求" --json
Q1="$(newest_for desk-scout@triage)"
as_seat_json desk-scout@triage q1-claim queue claim "$Q1" --json
as_seat_json desk-scout@triage q2-handoff queue handoff "$Q1" --to desk-reviewer@triage --summary "覆核 scout 的查核結果" \
  --body "scout 已查核；請覆核證據" --note "scout done" --json
Q2="$(newest_for desk-reviewer@triage)"
as_seat_json desk-reviewer@triage q2-claim queue claim "$Q2" --json
as_seat_json desk-reviewer@triage q3-handoff queue handoff "$Q2" --to desk-lead@triage --summary "驗收覆核結果" \
  --body "reviewer 已覆核；請驗收" --note "review done" --json
Q3="$(newest_for desk-lead@triage)"
as_seat_json desk-lead@triage q3-claim queue claim "$Q3" --json
as_seat_json desk-lead@triage q3-done queue update "$Q3" --state done --closure-reason no-follow-on --note "dossier accepted" --json

for q in "$Q1" "$Q2" "$Q3"; do "$RIG" queue show "$q" --json > "$RAW/show-$q.json" 2>&1; done
python3 - "$RAW" "$Q1" "$Q2" "$Q3" <<'PY'
import json, sys
raw, *ids = sys.argv[1:]
json.dump(ids, open(f"{raw}/qids.json", "w"))
PY

"$RIG" send desk-scout@triage "hello from the lab" --verify > "$RAW/send.txt" 2>&1 || true
"$RIG" capture desk-scout@triage --lines 60 > "$RAW/capture-scout.txt" 2>&1 || true

if [ "$SHOTS" = 1 ]; then
  (cd "$LAB_ROOT" && PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-$REAL_HOME/.cache/ms-playwright}" node scripts/openrig_shot.mjs "$OPENRIG_URL" "$OUT") || echo "截圖失敗（不影響 run.json）" >&2
fi

"$RIG" down triage --snapshot > "$RAW/down.txt" 2>&1
"$RIG" up triage --existing --json > "$RAW/restore-plain.json" 2>&1 || true
# stub 席位沒有 resume token，結果必為 partially_restored 並以非零結束；是否符合預期由 run.json 的 restore 檢查判斷。
"$RIG" up triage --existing --fresh desk.lead desk.scout desk.reviewer --json > "$RAW/restore-fresh.json" 2>&1 || true
wait_ready || { echo "還原後席位未在 40 秒內就緒" >&2; exit 6; }
cp "$RAW/ps-nodes.json" "$RAW/ps-after.json"

AFTER="$(REAL_HOME="$REAL_HOME" snapshot_globals)"

RAW="$RAW" OUT="$OUT" SB="$SB" LAB_ROOT="$LAB_ROOT" REAL_HOME="$REAL_HOME" BEFORE="$BEFORE" AFTER="$AFTER" \
  python3 "$LAB_ROOT/scripts/openrig_summarize.py"
echo "完成：$OUT/run.json"
