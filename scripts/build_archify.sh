#!/bin/sh
set -eu

# Robustly determine laboratory root directory regardless of invocation cwd
LAB_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$LAB_ROOT"

NODE_BIN="$LAB_ROOT/.tools/node/bin/node"
if [ ! -x "$NODE_BIN" ]; then
  echo "Error: Node.js executable not found at $NODE_BIN" >&2
  exit 1
fi

export PATH="$LAB_ROOT/.tools/node/bin:$PATH"
export ARCHIFY_UPDATE_CHECK_DISABLED=1
export ARCHIFY_CHROME_NO_SANDBOX=1

# Resolve Chromium via Playwright dependency
if [ -z "${ARCHIFY_CHROME:-}" ]; then
  DETECTED_CHROME=$("$NODE_BIN" -e '
    try {
      const { chromium } = require("playwright");
      const p = chromium.executablePath();
      process.stdout.write(p || "");
    } catch (e) {
      process.stderr.write("Playwright resolution error: " + e.message + "\n");
    }
  ' 2>/dev/null || true)

  if [ -n "$DETECTED_CHROME" ] && [ -x "$DETECTED_CHROME" ]; then
    export ARCHIFY_CHROME="$DETECTED_CHROME"
  else
    echo "Warning: Chromium executable could not be resolved from Playwright." >&2
    echo "Browser-check gate in finalize may fail or skip. Exact blocker: missing Chromium executable." >&2
  fi
fi

mkdir -p "$LAB_ROOT/artifacts/archify" "$LAB_ROOT/evidence/archify"

echo "==> Running Archify native finalize on diagrams/crawler.workflow.json..."
FINALIZE_EXIT=0
python3 "$LAB_ROOT/scripts/protect_artifact.py" "$LAB_ROOT/artifacts/archify" \
  "$NODE_BIN" "$LAB_ROOT/vendor/archify/archify/bin/archify.mjs" finalize workflow \
  "$LAB_ROOT/diagrams/crawler.workflow.json" \
  "$LAB_ROOT/artifacts/archify/crawler.html" \
  --quality showcase \
  --json > "$LAB_ROOT/evidence/archify/finalize.json" || FINALIZE_EXIT=$?

if [ "$FINALIZE_EXIT" -ne 0 ]; then
  echo "Archify finalize failed with exit code $FINALIZE_EXIT" >&2
  exit "$FINALIZE_EXIT"
fi

echo "==> Archify finalize passed successfully."

# Sync sidecar evidence files
for f in crawler.finalize.json crawler.finalize-summary.json crawler.browser-check.json crawler.delivery.json; do
  if [ -f "$LAB_ROOT/artifacts/archify/$f" ]; then
    cp "$LAB_ROOT/artifacts/archify/$f" "$LAB_ROOT/evidence/archify/$f"
  fi
done

# Capture headless browser verification screenshots
if [ -n "${ARCHIFY_CHROME:-}" ] && [ -x "${ARCHIFY_CHROME:-}" ]; then
  echo "==> Capturing high-resolution viewport screenshots..."
  "$NODE_BIN" -e '
    const { chromium } = require("playwright");
    (async () => {
      const browser = await chromium.launch({
        executablePath: process.env.ARCHIFY_CHROME,
        args: ["--no-sandbox", "--disable-setuid-sandbox"]
      });
      const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
      await page.goto("file://" + process.cwd() + "/artifacts/archify/crawler.html", { waitUntil: "networkidle" });
      await page.waitForTimeout(800);
      await page.screenshot({ path: "artifacts/archify/crawler.png", fullPage: true });
      await page.screenshot({ path: "evidence/archify/crawler.png", fullPage: true });
      await browser.close();
      console.log("Screenshots captured successfully.");
    })().catch(err => {
      console.error("Screenshot capture error:", err);
      process.exit(1);
    });
  '
fi

echo "==> Archify build completed successfully."

