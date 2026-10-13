import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
CAD_DIR = ROOT / "cad"
ARTIFACTS_DIR = ROOT / "artifacts" / "cad"
EVIDENCE_DIR = ROOT / "evidence" / "cad"


def test_cad_parameters_file_exists():
    params_path = CAD_DIR / "parameters.json"
    assert params_path.exists(), f"Missing parameters.json at {params_path}"
    with open(params_path, "r", encoding="utf-8") as f:
        params = json.load(f)
    assert params.get("width") == 100.0
    assert params.get("depth") == 30.0
    assert params.get("height") == 15.0
    assert params.get("slot_diameter") == 6.0
    assert params.get("spacing") == 24.0


def test_artifacts_generated():
    step_file = ARTIFACTS_DIR / "cable_organizer.step"
    stl_file = ARTIFACTS_DIR / "cable_organizer.stl"
    glb_file = ARTIFACTS_DIR / "cable_organizer.glb"
    geom_file = ARTIFACTS_DIR / "geometry.json"
    pdf_file = ARTIFACTS_DIR / "cable_organizer_drawing.pdf"
    snapshot_file = EVIDENCE_DIR / "snapshot.png"

    assert step_file.exists(), f"Missing STEP artifact: {step_file}"
    assert step_file.stat().st_size > 0, "STEP artifact is empty"

    assert stl_file.exists(), f"Missing STL artifact: {stl_file}"
    assert stl_file.stat().st_size > 0, "STL artifact is empty"

    assert glb_file.exists(), f"Missing GLB artifact: {glb_file}"
    assert glb_file.stat().st_size > 0, "GLB artifact is empty"

    assert geom_file.exists(), f"Missing geometry.json: {geom_file}"
    assert geom_file.stat().st_size > 0, "geometry.json is empty"

    assert pdf_file.exists(), f"Missing engineering drawing PDF: {pdf_file}"
    assert pdf_file.stat().st_size > 0, "PDF artifact is empty"
    with open(pdf_file, "rb") as f:
        header = f.read(5)
    assert header == b"%PDF-", "PDF file does not have valid PDF header"

    assert snapshot_file.exists(), f"Missing snapshot evidence: {snapshot_file}"
    assert snapshot_file.stat().st_size > 0, "snapshot.png is empty"


def test_geometry_json_validity():
    geom_file = ARTIFACTS_DIR / "geometry.json"
    assert geom_file.exists(), f"Missing geometry.json at {geom_file}"
    with open(geom_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("solid_count") == 1, "Model must have exactly 1 solid"
    assert data.get("volume_mm3", 0) > 0, "Model volume must be positive"

    bbox = data.get("bbox", {})
    x_len = bbox["max"][0] - bbox["min"][0]
    y_len = bbox["max"][1] - bbox["min"][1]
    z_len = bbox["max"][2] - bbox["min"][2]

    # Defaults: width=100, depth=30, height=15
    assert pytest.approx(100.0, abs=0.5) == x_len
    assert pytest.approx(30.0, abs=0.5) == y_len
    assert pytest.approx(15.0, abs=0.5) == z_len

    params = data.get("parameters", {})
    assert params.get("width") == 100.0
    assert params.get("depth") == 30.0
    assert params.get("height") == 15.0
    assert params.get("slot_diameter") == 6.0
    assert params.get("spacing") == 24.0


def test_native_step_kernel_validation():
    import cadgen

    step_file = ARTIFACTS_DIR / "cable_organizer.step"
    assert step_file.exists(), f"Missing STEP file: {step_file}"

    shape = cadgen.read_step(str(step_file))
    assert shape.is_valid, "Loaded STEP geometry is not valid"
    solids = shape.solids()
    assert len(solids) == 1, f"Expected 1 solid, got {len(solids)}"
    assert shape.volume > 0, f"Expected positive volume, got {shape.volume}"

    geom_file = ARTIFACTS_DIR / "geometry.json"
    with open(geom_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert pytest.approx(shape.volume, rel=1e-3) == data["volume_mm3"]


def test_parameterized_variation_second_size():
    import sys
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from cad.cable_organizer import create_cable_organizer

    # Secondary test parameters: compact variation
    # width=80.0, depth=25.0, height=12.0, slot_diameter=5.0, spacing=20.0
    shape_v2 = create_cable_organizer(
        width=80.0,
        depth=25.0,
        height=12.0,
        slot_diameter=5.0,
        spacing=20.0,
        slot_entry_width=3.0,
    )
    assert shape_v2.is_valid, "Variation geometry is not valid"
    assert len(shape_v2.solids()) == 1, "Variation must have exactly 1 solid"

    bbox_v2 = shape_v2.bounding_box()
    x_len = bbox_v2.max.X - bbox_v2.min.X
    y_len = bbox_v2.max.Y - bbox_v2.min.Y
    z_len = bbox_v2.max.Z - bbox_v2.min.Z

    assert pytest.approx(80.0, abs=0.5) == x_len
    assert pytest.approx(25.0, abs=0.5) == y_len
    assert pytest.approx(12.0, abs=0.5) == z_len

    # Default shape for comparison
    shape_default = create_cable_organizer(
        width=100.0,
        depth=30.0,
        height=15.0,
        slot_diameter=6.0,
        spacing=24.0,
        slot_entry_width=3.5,
    )

    # Volume must change significantly between sizes
    assert shape_v2.volume < shape_default.volume, (
        f"Variation volume {shape_v2.volume} should be smaller than default {shape_default.volume}"
    )


def test_json_change_rebuilds_exported_geometry(tmp_path):
    import os
    import shutil
    import subprocess
    import sys
    import cadgen

    source = tmp_path / 'cad'
    source.mkdir()
    (tmp_path / 'artifacts/cad').mkdir(parents=True)
    shutil.copy2(CAD_DIR / 'cable_organizer.py', source)
    parameters = source / 'parameters.json'
    shutil.copy2(CAD_DIR / 'parameters.json', parameters)
    env = dict(os.environ, CADGEN_TELEMETRY='0', CADGEN_UPDATE_CHECK='0',
               CADGEN_DAEMON='0', CADGEN_CACHE_DIR=str(tmp_path / 'cache'))
    model = source / 'cable_organizer.py'
    exported = tmp_path / 'artifacts/cad/cable_organizer.step'
    subprocess.run([sys.executable, str(model)], cwd=tmp_path, env=env, check=True)
    initial = cadgen.read_step(str(exported)).bounding_box().size.X
    params = json.loads(parameters.read_text())
    params['width'] = 80.0
    params['spacing'] = 20.0
    parameters.write_text(json.dumps(params))
    subprocess.run([sys.executable, str(model)], cwd=tmp_path, env=env, check=True)
    shape = cadgen.read_step(str(exported))
    assert initial == pytest.approx(100.0)
    assert shape.bounding_box().size.X == pytest.approx(80.0), 'JSON edit must invalidate CAD export cache'
    assert shape.is_valid and len(shape.solids()) == 1

