"""Test promoted main work identity layer without requiring invented complete dossiers."""
import json
from pathlib import Path
from collections import Counter
import unittest
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
class MainWorkIdentityRegistryTests(unittest.TestCase):
    def setUp(self):
        self.r=read('data/main-adv-rpg-works-20261031.json')
        self.idx=read('data/adv-rpg-minimal-index-20261031.json')
    def test_all_candidates_accounted_for_and_deduplicated(self):
        s=self.r['summary'];w=self.r['works'];q=self.r['identityReview']
        self.assertEqual(s['candidates'],267)
        self.assertEqual(s['accepted'],len(w))
        self.assertEqual(s['nextBatchCandidates'],59)
        self.assertEqual(s['addedToMainIdentityLayer'],s['promotedDossier']+s['promotedBasic'])
        self.assertGreaterEqual(len(w),207)
        self.assertGreaterEqual(len(q),1)
        self.assertEqual(q[0]['title'],'Dragon Knight & Graffiti')
        self.assertEqual({x['indexId'] for x in w[:207]}|{x['indexId'] for x in q[:1]},{x['id'] for x in self.idx['records'][:208]})
        self.assertEqual(len({x['id'] for x in w}),len(w))
        self.assertEqual(Counter(x['mainPlacement'] for x in w[:207]),{'existing-complete':57,'promoted-dossier':103,'promoted-basic':47})
    def test_existing_identifiers_and_minimal_metadata(self):
        main_ids={w['id'] for w in read('data/games.json')['works']}
        dossier_ids={w['id'] for c in read('data/company-coverage.json')['companies'] for key in ('relatedGames','dossierOnlyWorks') for w in c.get(key,[])}
        for w in self.r['works']:
            self.assertTrue(w['title'] and isinstance(w['firstYear'],int) and w['source'].startswith('https://'))
            self.assertIn(w['gameplay'],{'ADV','RPG','ARPG','SRPG','视觉小说','互动电影ADV'})
            self.assertTrue(not set(w)&{'characters','characterDetails','contentVersions','platformReleases','writer','illustrator','composer','synopsis','creators'})
            if w['mainPlacement']=='existing-complete':
                self.assertIn(w['id'],main_ids)
                self.assertEqual(w['id'],w['linkedRecordId'])
            elif w['mainPlacement']=='promoted-dossier':
                self.assertIn(w['id'],dossier_ids)
                self.assertEqual(w['id'],w['linkedRecordId'])
            else:
                self.assertIsNone(w['linkedRecordId'])
    def test_visible_in_main_discovery(self):
        js=(ROOT/'discovery.mjs').read_text(encoding='utf-8')
        self.assertIn('main-adv-rpg-works-20261031.json',js)
        self.assertIn('mainBasicSection()',js)
        self.assertIn('id="sa-basic-works"',js)
        self.assertIn('主库基础作品',js)
        old=(ROOT/'minimal-adv-rpg.mjs').read_text(encoding='utf-8')
        self.assertIn('main-adv-rpg-works-20261031.json',old)
        self.assertIn('identity-review',old)
if __name__=='__main__':unittest.main()
