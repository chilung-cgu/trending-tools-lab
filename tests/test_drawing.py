import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def test_drawing_annotations_do_not_escape_page_margin(tmp_path):
    preview = tmp_path / 'drawing'
    subprocess.run(['pdftoppm', '-scale-to', '1400', '-singlefile', '-png',
                    str(ROOT / 'artifacts/cad/cable_organizer_drawing.pdf'), str(preview)], check=True)
    image = Image.open(str(preview) + '.png').convert('L')
    margin = image.crop((0, 0, image.width, 20))
    assert margin.getextrema()[0] >= 250, 'Dimensions clipped above the drawing frame'
