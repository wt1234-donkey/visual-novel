"""Review accounting, historical identity protection, and conservative alias resolution."""
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'd266aae8f7d9ce05993e7bab253d429302067c27'
spec = importlib.util.spec_from_file_location('round3', ROOT/'scripts/promote_narrative_round3_20261031.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RoundThreeTests(unittest.TestCase):
    def test_previous_identities_and_historical_content_preserved(self):
        old = json.loads(subprocess.check_output(['git','show',BASE+':'+module.REGISTRY],cwd=ROOT))
        current = module.read(module.REGISTRY)
        self.assertEqual(current['works'][:len(old['works'])],old['works'])
        self.assertEqual(current['identityReview'][:len(old['identityReview'])],old['identityReview'])
        for path in ['data/games.json','data/company-coverage.json','data/non-rpg-creator-supplement-20261030.json']:
            self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT))

    def test_review_decisions_and_held_works(self):
        review = module.read(module.REVIEW)
        self.assertEqual(review['summary'],{'candidates':26,'newToRegistry':18,'promoted-basic':15,
                         'existing-complete':1,'identity-review':1,'linked-existing-registry':6,
                         'eligibility-review':1,'promoted-dossier':2})
        reg = module.read(module.REGISTRY)
        self.assertGreaterEqual(len(reg['works']),284)
        self.assertGreaterEqual(reg['summary']['candidates'],293)
        self.assertEqual(len({w['id'] for w in reg['works']}),len(reg['works']))
        by_id = {w['id']:w for w in reg['works']}
        for d in review['records']:
            if d['selection']=='defer':
                self.assertIsNone(d['registryId'])
                self.assertNotIn(d['title'],{w['title'] for w in reg['works']})
            else:
                self.assertIn(d['registryId'],by_id)
                self.assertEqual(by_id[d['registryId']]['firstYear'],d['year'])
        for wid in ['g1209','g1378','g1379','g1380','g1382','enix-endonesia','ascii-ufo']:
            self.assertIn(wid,by_id)

    def test_reviewed_historical_batch_stays_unchanged_when_new_batches_are_appended(self):
        # A historical one-batch generator must not be rerun to rebuild the entire
        # cumulative registry after later independent data sources were imported.
        review = module.read(module.REVIEW)
        registry = module.read(module.REGISTRY)
        self.assertEqual(review['summary']['newToRegistry'], 18)
        identities = {row['id'] for row in registry['works']}
        for decision in review['records']:
            if decision.get('registryId'):
                self.assertIn(decision['registryId'], identities)
        self.assertEqual(len([row for row in registry['works'] if row.get('batch') == module.BATCH]), 18)

    def test_alias_resolution_rejects_year_and_identity_conflicts(self):
        key=module.norm('Title')
        with self.assertRaises(ValueError):
            module.resolve({'title':'Title','year':2000},{key:[('a',1999,'complete-main')]})
        with self.assertRaises(ValueError):
            module.resolve({'title':'Title','year':2000},{key:[('a',2000,'complete-main'),('b',2000,'complete-main')]})
        self.assertEqual(module.resolve({'title':'Title','year':2000},
                         {key:[('a',2000,'complete-main'),('supp-a',2000,'supplement-complete')]}),('a','complete-main'))
        self.assertIn(module.norm('Endonesia'),module.keys({'originalTitle':'エンドネシア / Endonesia'}))


if __name__=='__main__':
    unittest.main()
