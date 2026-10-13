#!/usr/bin/env bash
set -euo pipefail

# CAD build script for Task 5
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

export CADGEN_TELEMETRY=0
export CADGEN_UPDATE_CHECK=0
export DO_NOT_TRACK=1

mkdir -p artifacts/cad evidence/cad

if [ -f "${ROOT_DIR}/.venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "${ROOT_DIR}/.venv/bin/activate"
else
    echo "Virtual environment .venv not found. Run uv sync first." >&2
    exit 1
fi

echo "=== Building CAD models (STEP, STL, GLB) ==="
python cad/cable_organizer.py

echo "=== Computing geometry.json ==="
python -c '
import json
from pathlib import Path
import cadgen

step_file = Path("artifacts/cad/cable_organizer.step")
shape = cadgen.read_step(str(step_file))
bbox = shape.bounding_box()

with open("cad/parameters.json", "r", encoding="utf-8") as f:
    params = json.load(f)

geom = {
    "solid_count": len(shape.solids()),
    "volume_mm3": round(shape.volume, 3),
    "bbox": {
        "min": [round(bbox.min.X, 3), round(bbox.min.Y, 3), round(bbox.min.Z, 3)],
        "max": [round(bbox.max.X, 3), round(bbox.max.Y, 3), round(bbox.max.Z, 3)]
    },
    "dimensions_mm": {
        "width": round(bbox.max.X - bbox.min.X, 3),
        "depth": round(bbox.max.Y - bbox.min.Y, 3),
        "height": round(bbox.max.Z - bbox.min.Z, 3)
    },
    "parameters": params
}

with open("artifacts/cad/geometry.json", "w", encoding="utf-8") as f:
    json.dump(geom, f, indent=2, ensure_ascii=False)
print("Saved artifacts/cad/geometry.json")
'

echo "=== Building engineering drawing PDF ==="
python cad/cable_organizer_drawing.py

echo "=== Rendering native snapshot ==="
cadgen step snapshot artifacts/cad/cable_organizer.step evidence/cad/snapshot.png

echo "=== Building portable 3D viewer ==="
"${ROOT_DIR}/.tools/node/bin/node" scripts/build_cad_viewer.mjs

echo "=== CAD Build Complete ==="

