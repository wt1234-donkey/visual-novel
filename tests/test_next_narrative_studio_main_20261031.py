"""Audit all 59 next-batch studio narratives in unified main identity layer."""
import json, unittest
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads((ROOT/p).read_text(encoding='utf8'))
class NextNarrativeStudioTests(unittest.TestCase):
    def test_review_has_all_candidates_once(self):
        seed=read('data/adv-rpg-next-studio-candidates-20261031.json')['records']
        review=read('data/adv-rpg-next-studio-review-20261031.json')
        reg=read('data/main-adv-rpg-works-20261031.json')
        self.assertEqual(len(seed),59)
        self.assertEqual(len({(r['title'],r['year']) for r in seed}),59)
        self.assertEqual(len(review['records']),59)
        self.assertEqual(len({r['title'] for r in review['records']}),59)
        self.assertGreaterEqual(len({r['group'] for r in seed}),10)
        counts=Counter(r['status'] for r in review['records'])
        self.assertEqual(dict(counts),review['summary'])
        self.assertEqual(sum(counts.values()),59)
        self.assertEqual(reg['summary']['nextBatchCandidates'],59)
        self.assertEqual(reg['summary']['nextBatchNewBasic'],counts['promoted-basic'])
        self.assertEqual(reg['summary']['nextBatchLinkedExisting'],counts['linked-existing-registry']+counts['linked-existing-full-or-dossier'])
        self.assertEqual(reg['summary']['nextBatchHeld'],counts['identity-review'])
        self.assertEqual(reg['summary']['candidates'],267)
        self.assertEqual(reg['summary']['accepted'],len(reg['works']))
        self.assertEqual(len({w['id'] for w in reg['works']}),len(reg['works']))
        existing={w['id'] for w in reg['works']}
        for row in review['records']:
            if row['status']=='identity-review':self.assertIsNone(row['registryId'])
            else:self.assertIn(row['registryId'],existing)
            self.assertEqual((row['title'],row['year']),(next(s['title'] for s in seed if s['title']==row['title']),next(s['year'] for s in seed if s['title']==row['title'])))
            self.assertTrue(row['source'].startswith('https://'))
    def test_no_full_dossier_fabricated_and_website_integration(self):
        reg=read('data/main-adv-rpg-works-20261031.json')
        for row in reg['works']:
            self.assertFalse(set(row)&{'characters','synopsis','platformReleases','contentVersions','writer','illustrator','composer'})
        discovery=(ROOT/'discovery.mjs').read_text(encoding='utf8')
        self.assertIn('main-adv-rpg-works-20261031.json',discovery)
        self.assertIn('mainBasicSection()',discovery)
        page=(ROOT/'minimal-adv-rpg.mjs').read_text(encoding='utf8')
        self.assertIn('adv-rpg-next-studio-review-20261031.json',page)
if __name__=='__main__':unittest.main()
