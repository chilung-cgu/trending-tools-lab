#!/bin/sh
# 用途：下載與驗證重建本專案所需的 vendor/ 原始碼（只含兩個建置必要來源）。
# - crawler：scripts/export_snapshots.py 從它的 Git 歷史匯出四週快照。
# - archify：scripts/build_archify.sh 用它重新生成流程圖。
# Impeccable、HyperFrames、text-to-cad、context-mode 由 npm ci 與 uv sync 的固定版本提供，不需要 vendor。
set -eu

# ==============================================================================
# Vendor 來源設定表格 (依據 data/tool-sources.json 與盤點結果)
# ------------------------------------------------------------------------------
# Name             | Commit                                   | URL
# -----------------+------------------------------------------+-----------------
# archify          | 58ab0b98d2d0def8e49dced705c7b566936723ec | https://github.com/tt-a1i/archify
# crawler          | c169d08b730d4c995a0c83141565621f47e8ba12 | https://github.com/chilung-cgu/github-trending-crawler
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENDOR_DIR="${LAB_VENDOR_DIR:-"$REPO_ROOT/vendor"}"

ALL_REPOS="archify crawler"

get_repo_info() {
  case "$1" in
    archify)
      REPO_COMMIT="58ab0b98d2d0def8e49dced705c7b566936723ec"
      REPO_URL="https://github.com/tt-a1i/archify"
      ;;
    crawler)
      REPO_COMMIT="c169d08b730d4c995a0c83141565621f47e8ba12"
      REPO_URL="https://github.com/chilung-cgu/github-trending-crawler"
      ;;
    *)
      echo "Error: 未知 vendor 套件 '$1'" >&2
      exit 1
      ;;
  esac
}

usage() {
  cat << USAGE_EOF
Usage: $0 [OPTIONS]

Options:
  --check        驗證各 vendor 套件是否存在且 HEAD 符合固定 commit，不執行下載
  --dry-run      預覽將執行的動作，不進行實際下載或變更
  --only <name>  僅處理指定的 vendor 套件 (例如 crawler)
  -h, --help     顯示本說明訊息

Environment:
  LAB_VENDOR_DIR 指定 vendor 目錄路徑 (預設: <repo>/vendor)
USAGE_EOF
}

CHECK_MODE=0
DRY_RUN=0
ONLY_REPO=""

while [ $# -gt 0 ]; do
  case "$1" in
    --check)
      CHECK_MODE=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --only)
      if [ $# -lt 2 ]; then
        echo "Error: --only 需要指定 repo 名稱" >&2
        exit 1
      fi
      ONLY_REPO="$2"
      shift 2
      ;;
    --only=*)
      ONLY_REPO="${1#--only=}"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: 未知參數: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

TARGET_LIST="${ONLY_REPO:-"$ALL_REPOS"}"
FAILURES=0

for repo in $TARGET_LIST; do
  get_repo_info "$repo"
  target_dir="$VENDOR_DIR/$repo"

  if [ "$CHECK_MODE" -eq 1 ]; then
    if true; then
      if [ ! -d "$target_dir" ]; then
        echo "[FAIL] $repo: 目錄不存在 ($target_dir)" >&2
        FAILURES=$((FAILURES + 1))
      elif [ ! -d "$target_dir/.git" ]; then
        echo "[FAIL] $repo: $target_dir 存在但不是 git 儲存庫" >&2
        FAILURES=$((FAILURES + 1))
      else
        act_commit="$(git -C "$target_dir" rev-parse HEAD 2>/dev/null || true)"
        if [ "$act_commit" != "$REPO_COMMIT" ]; then
          echo "[FAIL] $repo: commit 不符！預期 $REPO_COMMIT，實際為 $act_commit" >&2
          FAILURES=$((FAILURES + 1))
        else
          echo "[OK] $repo: commit 相符 ($REPO_COMMIT)"
        fi
      fi
    fi
  else
    # Fetch / Clone 模式
    if true; then
      if [ -d "$target_dir" ]; then
        if [ ! -d "$target_dir/.git" ]; then
          echo "Error: $repo: 目錄已存在但非 git 儲存庫 ($target_dir)" >&2
          FAILURES=$((FAILURES + 1))
        else
          act_commit="$(git -C "$target_dir" rev-parse HEAD 2>/dev/null || true)"
          if [ "$act_commit" != "$REPO_COMMIT" ]; then
            echo "Error: $repo: 目錄已存在但 commit 不符！預期 $REPO_COMMIT，實際為 $act_commit (不覆蓋/不reset)" >&2
            FAILURES=$((FAILURES + 1))
          else
            echo "[OK] $repo: 目錄已存在且 commit 相符 ($REPO_COMMIT)"
          fi
        fi
      else
        if [ "$DRY_RUN" -eq 1 ]; then
          echo "[DRY-RUN] git clone $REPO_URL $target_dir"
          echo "[DRY-RUN] git -C $target_dir checkout --detach $REPO_COMMIT"
        else
          echo "正在下載 $repo ($REPO_URL)..."
          mkdir -p "$VENDOR_DIR"
          git clone "$REPO_URL" "$target_dir"
          git -C "$target_dir" checkout --detach "$REPO_COMMIT"
          echo "[OK] $repo: 已下載並切換至固定 commit ($REPO_COMMIT)"
        fi
      fi
    fi
  fi
done

if [ "$FAILURES" -ne 0 ]; then
  exit 1
fi
