import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SnapshotsTest(unittest.TestCase):
    def test_history_has_four_successful_dates_and_correct_latest_data(self):
        self.assertTrue((ROOT / 'data/index.json').exists(), 'snapshot export is missing')
        data = json.loads((ROOT / 'data/index.json').read_text())
        self.assertEqual([s['date'] for s in data['snapshots']],
                         ['2026-09-21', '2026-09-28', '2026-10-05', '2026-10-12'])
        names = set()
        for snapshot in data['snapshots']:
            self.assertEqual(len(snapshot['commit']), 40)
            self.assertIn('/blob/' + snapshot['commit'] + '/', snapshot['source_url'])
            raw = json.loads((ROOT / 'data/raw' / (snapshot['date'] + '.json')).read_text())
            self.assertEqual(raw['status'], 'ok')
            for period in ('weekly', 'monthly'):
                self.assertEqual(snapshot[period], raw['periods'][period]['items'])
                self.assertEqual(len(snapshot[period]), 10)
                self.assertEqual([i['rank'] for i in snapshot[period]], list(range(1, 11)))
                names.update(i['full_name'] for i in snapshot[period])
        self.assertEqual(len(names), 47)
        self.assertEqual(data['snapshots'][-1]['weekly'][0]['full_name'], 'boykopovar/AnyPS5')
        self.assertEqual(data['snapshots'][-1]['generated_at_taipei'],
                         '2026-10-12T10:35:06+08:00')


if __name__ == '__main__':
    unittest.main()
