import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class VideoTest(unittest.TestCase):
    def test_composition_preserves_snapshots(self):
        html = (ROOT / 'video/index.html').read_text()
        data = json.loads((ROOT / 'data/index.json').read_text())
        self.assertIn('data-duration="30"', html)
        self.assertIn('data-width="1280"', html)
        self.assertNotIn('fetch(', html)
        for snapshot in data['snapshots']:
            self.assertIn(snapshot['date'], html)
            for item in snapshot['weekly'][:3]:
                self.assertIn(item['full_name'], html)
                self.assertIn(f"{item['period_stars']:,}", html)


if __name__ == '__main__':
    unittest.main()
