from __future__ import annotations
from pathlib import Path
import cadgen
from cadgen.eng_drawing import Sheet, eng_drawing
from cable_organizer import (
    DEPTH,
    FILLET_RADIUS,
    HEIGHT,
    SLOT_DIAMETER,
    SLOT_ENTRY_WIDTH,
    SPACING,
    WIDTH,
)

_HERE = Path(__file__).resolve().parent
_STEP_PATH = _HERE / "../artifacts/cad/cable_organizer.step"


@eng_drawing(out="../artifacts/cad/cable_organizer_drawing.pdf")
def cable_organizer_drawing():
    part = cadgen.read_step(_STEP_PATH)
    sheet = Sheet(
        size="A4",
        scale=0.8,
        title="3-SLOT DESKTOP CABLE ORGANIZER",
        part_number="CO-100",
        material="DEMO ONLY",
        revision="A",
        author="Trending Tools Lab",
        units="mm",
        projection="THIRD ANGLE",
        general_tolerance="",
        notes=[
            "DESKTOP DEMONSTRATION MODEL (NON-PRODUCTION).",
            "DIMENSIONS DEMONSTRATION ONLY; NO TOLERANCE OR MATERIAL CERTIFICATION.",
            "UNITS IN MILLIMETERS (MM); TOLERANCES UNSPECIFIED.",
        ],
    )
    top, front, right, iso = sheet.three_views(part, gap=36.0, iso=True)
    top.overall()
    top.dim((-SPACING, 0, 0), (SPACING, 0, 0))
    front.overall()
    right.overall()
    return sheet


if __name__ == "__main__":
    cable_organizer_drawing()

