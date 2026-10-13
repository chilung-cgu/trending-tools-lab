#!/bin/sh
set -eu
LAB_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
export PATH="$LAB_ROOT/.tools/node/bin:$LAB_ROOT/node_modules/.bin:$PATH"
export DO_NOT_TRACK=1
if [ -z "${HYPERFRAMES_BROWSER_PATH:-}" ]; then
  HYPERFRAMES_BROWSER_PATH=$(node --input-type=module -e 'import {chromium} from "@playwright/test"; process.stdout.write(chromium.executablePath())')
  export HYPERFRAMES_BROWSER_PATH
fi
cd "$LAB_ROOT"
mkdir -p artifacts/video evidence/video
python3 scripts/generate_video.py
hyperframes lint video --json > evidence/video/lint.json
hyperframes check video --json > evidence/video/check.json 2> evidence/video/check.stderr
python3 -c 'import json,sys; result=json.load(open("evidence/video/check.json")); sys.exit(0 if result.get("ok") and not result.get("browserSkipped") else "HyperFrames browser gate failed or was skipped")'
hyperframes render video --fps 24 --workers 1 --no-browser-gpu --quality looks --output "$LAB_ROOT/artifacts/video/trending.mp4"
ffprobe -v error -show_format -show_streams -of json artifacts/video/trending.mp4 > evidence/video/ffprobe.json
for second in 1 6 13 20 28; do
  ffmpeg -v error -y -ss "$second" -i artifacts/video/trending.mp4 -frames:v 1 "artifacts/video/frame-$second.png"
done
