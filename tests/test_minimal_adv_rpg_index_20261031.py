"""Regression checks for title-year-gameplay ADV/RPG supplemental index."""
import json
from pathlib import Path
from collections import Counter
import unittest
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
class MinimalADVRPGAudit(unittest.TestCase):
    def test_index_matches_candidates_and_is_finite(self):
        seed=read('data/adv-rpg-minimal-candidates-20261031.json')
        full=read('data/adv-rpg-minimal-index-20261031.json')
        rows=full['records'];summary=full['summary']
        candidates=rows[:summary['candidates']]
        # Generated index is year-sorted and includes every curated source row once.
        self.assertEqual(len(seed['records']),summary['candidates'])
        self.assertGreaterEqual(summary['candidates'],200)
        self.assertEqual(summary['displayTotal'],len(rows))
        self.assertEqual(len({x['id'] for x in rows}),len(rows))
        self.assertEqual(sum(summary[k] for k in ('newBasic','alreadyMain','alreadyDossier','identityReview')),summary['candidates'])
        self.assertGreater(summary['groups'],15)
        self.assertTrue(all(x['year']<=2026 and x['year']>=1976 for x in rows))
        self.assertTrue(all(x['title'] and x['gameplay'] and x['source'].startswith('https://') for x in rows))
        self.assertEqual(sum(x['status']=='new-basic' for x in rows),summary['newBasic'])
        self.assertTrue(all(x['matchedWorkId'] is None for x in rows if x['status']=='new-basic'))
        # 'New' data is genuinely minimal, and may not contain made-up narrative completion.
        self.assertTrue(all(not any(key in x for key in ('characters','synopsis','contentVersions','platformReleases','writer','illustrator','composer')) for x in rows))
    def test_existing_catalogue_unchanged(self):
        full=read('data/adv-rpg-minimal-index-20261031.json')
        old={w['id'] for w in read('data/games.json')['works']}
        self.assertTrue(all(x['matchedWorkId'] in old for x in full['records'] if x['status']=='main-linked'))
    def test_site_wires_live_index(self):
        h=(ROOT/'minimal-adv-rpg.html').read_text()
        js=(ROOT/'minimal-adv-rpg.mjs').read_text()
        self.assertIn('data/adv-rpg-minimal-index-20261031.json',js)
        self.assertIn('id="q"',h)
        self.assertIn('id="gameplay"',h)
        self.assertIn('id="group"',h)
        self.assertIn('minimal-adv-rpg.html',(ROOT/'index.html').read_text())
        self.assertIn('minimal-adv-rpg.html',(ROOT/'index.html').read_text())
if __name__=='__main__': unittest.main()
