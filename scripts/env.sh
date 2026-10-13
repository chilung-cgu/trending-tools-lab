#!/bin/sh
LAB_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
export PATH="$LAB_ROOT/.tools/node/bin:$LAB_ROOT/.tools/bin:$LAB_ROOT/node_modules/.bin:$PATH"
export ARCHIFY_UPDATE_CHECK_DISABLED=1
export CADGEN_TELEMETRY=0
export CADGEN_UPDATE_CHECK=0
export DO_NOT_TRACK=1
