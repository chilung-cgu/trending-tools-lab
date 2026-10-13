#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Ensure we are in project root for git config & wt context
cd "${PROJECT_ROOT}"

WT_BIN="${PROJECT_ROOT}/.tools/wt/wt"
EVIDENCE_DIR="${PROJECT_ROOT}/evidence/worktrunk"
mkdir -p "${EVIDENCE_DIR}"

LOG_FILE="${EVIDENCE_DIR}/worktrunk_demo.log"
EVIDENCE_TXT="${EVIDENCE_DIR}/isolation_evidence.txt"
WT_JSON="${EVIDENCE_DIR}/wt_list.json"

# Use unique branch and file name based on timestamp and PID. Never touch existing worktrees.
TIMESTAMP="$(date +%s)"
DEMO_BRANCH="demo-wt-${TIMESTAMP}-$$"
DEMO_FILE="ISOLATED_MODULE_${TIMESTAMP}_$$.py"

exec > >(tee "${LOG_FILE}") 2>&1

echo "=================================================================="
echo "Worktrunk Worktree Isolation Demo"
echo "=================================================================="
echo "Timestamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "Host Architecture: $(uname -m)"
echo "Project Root: ${PROJECT_ROOT}"
echo "Worktrunk Binary: ${WT_BIN}"
echo "Demo Unique Branch: ${DEMO_BRANCH}"
echo "Demo Unique File:   ${DEMO_FILE}"

# Check wt version
"${WT_BIN}" --version

# Verify Git Identity (Must NOT modify global config)
GIT_USER="$(git config user.name || echo 'unset')"
GIT_EMAIL="$(git config user.email || echo 'unset')"
echo ""
echo "[Step 1] Verifying Git Identity:"
echo "  - user.name:  ${GIT_USER}"
echo "  - user.email: ${GIT_EMAIL}"
if [[ "${GIT_USER}" == "unset" || "${GIT_EMAIL}" == "unset" ]]; then
  echo "Error: git user.name or user.email is not set!" >&2
  exit 1
fi

echo ""
echo "[Step 2] Initial Worktree Status via 'wt list':"
"${WT_BIN}" list

echo ""
echo "[Step 3] Creating isolated demo worktree: '${DEMO_BRANCH}'..."
# Native CLI options: --no-hooks --no-cd --format json verified via 'wt switch --help'
CREATE_OUTPUT="$("${WT_BIN}" switch --create "${DEMO_BRANCH}" --base @ --no-hooks --no-cd --format json)"
echo "  - Create result: ${CREATE_OUTPUT}"

DEMO_PATH="$(echo "${CREATE_OUTPUT}" | jq -r '.path')"
echo "  - Worktree directory created at: ${DEMO_PATH}"

if [[ ! -d "${DEMO_PATH}" ]]; then
  echo "Error: Created worktree path does not exist: ${DEMO_PATH}" >&2
  exit 1
fi

echo ""
echo "[Step 4] Querying worktree status in JSON format ('wt list --format json')..."
"${WT_BIN}" list --format json > "${WT_JSON}"
echo "  - Saved full JSON status to: ${WT_JSON}"

echo ""
echo "[Step 5] Creating isolated feature file inside '${DEMO_PATH}'..."
cat << 'EOF_DEMO' > "${DEMO_PATH}/${DEMO_FILE}"
# Isolated feature prototype created in demo worktree
# This file must NOT leak into the parent or other worktrees!

def isolated_telemetry_probe():
    return {"status": "isolated", "active_worktree": "worktrunk-demo"}
EOF_DEMO

echo "  - File created: ${DEMO_PATH}/${DEMO_FILE}"

echo ""
echo "[Step 6] Asserting Worktree Isolation Across All Existing Worktrees:"
# Assertion 1: File exists in demo worktree
if [[ -f "${DEMO_PATH}/${DEMO_FILE}" ]]; then
  echo "  [✓] Assertion 1 Passed: ${DEMO_FILE} exists in demo worktree: ${DEMO_PATH}"
else
  echo "  [✗] Assertion 1 Failed: ${DEMO_FILE} missing in demo worktree!" >&2
  exit 1
fi

# Assertion 2: Exhaustively check every sibling worktree in the repository
CHECKED_COUNT=0
while IFS= read -r line; do
  if [[ "${line}" =~ ^worktree\ (.*)$ ]]; then
    WT_CHECK_DIR="${BASH_REMATCH[1]}"
    if [[ "${WT_CHECK_DIR}" != "${DEMO_PATH}" ]]; then
      if [[ -f "${WT_CHECK_DIR}/${DEMO_FILE}" ]]; then
        echo "  [✗] Assertion Failed: Leak detected in ${WT_CHECK_DIR}!" >&2
        exit 1
      else
        echo "  [✓] Verified absent in: ${WT_CHECK_DIR}"
        CHECKED_COUNT=$((CHECKED_COUNT + 1))
      fi
    fi
  fi
done < <(git worktree list --porcelain)
echo "  - Total sibling worktrees verified clean: ${CHECKED_COUNT}"

# Record human-readable isolation evidence
cat << EOF_EVIDENCE > "${EVIDENCE_TXT}"
Worktree Isolation Verification Evidence
Timestamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')
Demo Branch: ${DEMO_BRANCH}
Demo Worktree Path: ${DEMO_PATH}
Isolated File: ${DEMO_FILE}

Verification Checks:
1. Demo worktree contains isolated file: YES (${DEMO_PATH}/${DEMO_FILE})
2. Verified absent across all ${CHECKED_COUNT} sibling worktrees listed by git worktree list.
3. Zero contamination to other worktrees verified by exhaustive directory check.
EOF_EVIDENCE

echo ""
echo "[Step 7] Clean teardown of our own ephemeral demo worktree without force:"
# First remove the isolated file so working tree is clean
rm "${DEMO_PATH}/${DEMO_FILE}"
echo "  - Removed demo file: ${DEMO_PATH}/${DEMO_FILE}"

# Safely remove only the demo worktree we created, using --foreground and --no-hooks (no force flag!)
"${WT_BIN}" remove "${DEMO_BRANCH}" --foreground --no-hooks --format json
echo "  - Successfully removed demo worktree: ${DEMO_BRANCH}"

echo ""
echo "[Step 8] Final worktree status after demo:"
"${WT_BIN}" list

echo "=================================================================="
echo "Worktree Isolation Demo Completed Successfully!"
echo "Evidence files:"
echo "  - Log:       ${LOG_FILE}"
echo "  - Evidence:  ${EVIDENCE_TXT}"
echo "  - List JSON: ${WT_JSON}"
echo "=================================================================="
