"""Second A-letter batch is an exact additive review, without family inheritance."""
import json
import subprocess
import unittest
from pathlib import Path
from creator_snapshot import load_snapshot
ROOT = Path(__file__).resolve().parents[1]
BASE = 'c5abca055efbae673c53d8275579e9f42ae815b7'
def read(path): return load_snapshot(ROOT, path)
APPLIED = '570bf41078e39f9d91fb192bef6ef0ad62d66639'
def applied(path): return json.loads(subprocess.check_output(['git', 'show', f'{APPLIED}:{path}'], cwd=ROOT, text=True))
def old(path): return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))
class CreatorA2ReviewTests(unittest.TestCase):
 def test_exact_forty_additions_preserve_all_original_credits(self):
  review = read('data/entity-creator-a2-review-20261022.json')
  b = {c['id']: c for c in old('data/credits.json')['credits']}
  a = {c['id']: c for c in applied('data/credits.json')['credits']}
  self.assertTrue(b.keys() <= a.keys())
  for cid in b: self.assertEqual(b[cid], a[cid], cid)
  added = [a[cid] for cid in a.keys() - b.keys()]
  self.assertEqual(len(added), 40)
  self.assertEqual({(c['entityId'], c['workId'], c['role'], c['source']) for c in added}, {(c['entityId'], c['workId'], c['role'], c['source']) for c in review['creditAdditions']})
  for c in added:
   self.assertEqual(c['entityId'], 'entity-alicesoft')
   self.assertEqual(c['role'], 'productionBrand')
   self.assertEqual(c['status'], 'sourceReviewed')
   self.assertEqual(c['reviewRecord'], review['audit'])
 def test_only_the_reviewed_subject_memberships_gain_roles(self):
  key = lambda m: (m['dossierId'], m['workId'])
  b = {key(m): m for m in old('data/credits.json')['dossierMemberships']}
  a = {key(m): m for m in applied('data/credits.json')['dossierMemberships']}
  self.assertEqual(b.keys(), a.keys())
  expected = {('alicesoft', c['workId']) for c in read('data/entity-creator-a2-review-20261022.json')['creditAdditions']}
  self.assertEqual({k for k in b if b[k] != a[k]}, expected)
  for k in b:
   self.assertEqual(b[k]['placement'], a[k]['placement'])
   if b[k]['status'] == 'pendingRole': self.assertEqual(b[k], a[k])
   if k in expected:
    self.assertEqual(a[k]['group'], 'original')
    self.assertEqual(set(a[k]['roles']), set(b[k]['roles']) | {'productionBrand'})
 def test_core_identity_relations_old_reviews_and_main_page_unchanged(self):
  paths = ['data/entities.json','data/entity-migration-review.json','data/games.json','data/company-coverage.json','data/taxonomy.json','data/gameplay-catalogues.json','data/work-classification.json','data/entity-migration-baseline.json','data/content-migration-baseline.json','index.html','app.mjs','filter.mjs','styles.css']
  paths += [f'data/entity-creator-a-review-20261022.{ext}' for ext in ['json','md']]
  for path in paths:
   actual = subprocess.check_output(['git','show',f'{APPLIED}:{path}'],cwd=ROOT) if path in ['data/entities.json','data/entity-migration-review.json'] else (ROOT/path).read_bytes()
   self.assertEqual(actual, subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT),path)
 def test_progress_is_contiguous_and_unverified_brands_do_not_inherit(self):
  review = read('data/entity-creator-a2-review-20261022.json');org = applied('data/organizations.json');p = org['registrationProgress']
  self.assertEqual(p['processedEntityIds'], [r['entityId'] for r in p['queue'][:12]])
  self.assertEqual([r['entityId'] for r in p['reviewedEntities']], p['processedEntityIds'])
  self.assertEqual([r['name'] for r in review['reviewedEntities']], ['Alchemist','Alice Blue','AliceNoir','Alicesoft'])
  self.assertEqual(p['nextEntityId'], p['queue'][12]['entityId'])
  self.assertEqual(len(p['audits']), 2)
  ns = {n['id']: n for n in org['nodes']}
  for eid in ['entity-name-b8b1293f82fa','entity-alice_blue','entity-alice_noir','entity-champion_soft']:
   previous = next(n for n in old('data/organizations.json')['nodes'] if n['id'] == eid)
   self.assertEqual(ns[eid]['groups'], previous['groups'])
  n = ns['entity-alicesoft']
  self.assertEqual(n['productionCount'], 23)
  self.assertEqual(len(n['groups']['creation']), 40)
  self.assertEqual(len(n['groups']['pending']), 75)
  self.assertEqual(sum(c['expectedPlacement']=='related' for c in review['creditAdditions']), 17)
