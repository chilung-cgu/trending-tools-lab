from __future__ import annotations
import json
from pathlib import Path
from cadgen import build123d as bd
from cadgen import glb, step, stl

_HERE = Path(__file__).resolve().parent
_PARAMS_FILE = _HERE / "parameters.json"

if _PARAMS_FILE.exists():
    with open(_PARAMS_FILE, "r", encoding="utf-8") as f:
        _PARAMS = json.load(f)
else:
    _PARAMS = {
        "width": 100.0,
        "depth": 30.0,
        "height": 15.0,
        "slot_diameter": 6.0,
        "spacing": 24.0,
        "slot_entry_width": 3.5,
        "fillet_radius": 3.0,
    }

WIDTH = float(_PARAMS.get("width", 100.0))
DEPTH = float(_PARAMS.get("depth", 30.0))
HEIGHT = float(_PARAMS.get("height", 15.0))
SLOT_DIAMETER = float(_PARAMS.get("slot_diameter", 6.0))
SPACING = float(_PARAMS.get("spacing", 24.0))
SLOT_ENTRY_WIDTH = float(_PARAMS.get("slot_entry_width", 3.5))
FILLET_RADIUS = float(_PARAMS.get("fillet_radius", 3.0))


def create_cable_organizer(
    width: float = WIDTH,
    depth: float = DEPTH,
    height: float = HEIGHT,
    slot_diameter: float = SLOT_DIAMETER,
    spacing: float = SPACING,
    slot_entry_width: float = SLOT_ENTRY_WIDTH,
    fillet_radius: float = FILLET_RADIUS,
) -> bd.Shape:
    """Constructs a genuine 3-slot parameterized desktop cable organizer in millimeters."""
    slot_z = height * 0.5
    base = bd.Box(width, depth, height, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))

    if fillet_radius > 0:
        vertical_edges = base.edges().filter_by(bd.Axis.Z)
        base = bd.fillet(vertical_edges, radius=fillet_radius)

    cut_tools = []
    # 3 slots symmetrically centered at -spacing, 0, +spacing
    slot_positions = [-spacing, 0.0, spacing]
    for x in slot_positions:
        # Cylindrical cable holding chamber along Y
        tunnel = bd.Pos(x, 0.0, slot_z) * (
            bd.Rot(90, 0, 0) * bd.Cylinder(radius=slot_diameter / 2.0, height=depth + 4.0)
        )
        cut_tools.append(tunnel)

        # Top entry slit for snapping cables in from the top surface
        slit_h = (height - slot_z) + 2.0
        slit = bd.Pos(x, 0.0, slot_z) * bd.Box(
            slot_entry_width, depth + 4.0, slit_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        )
        cut_tools.append(slit)

    combined_cut = bd.Compound(children=cut_tools)
    body = base - combined_cut
    body.label = "desktop_cable_organizer"
    return body


@step(out="../artifacts/cad/cable_organizer.step")
@stl(out="../artifacts/cad/cable_organizer.stl")
@glb(out="../artifacts/cad/cable_organizer.glb")
def cable_organizer():
    return create_cable_organizer()


if __name__ == "__main__":
    cable_organizer()

