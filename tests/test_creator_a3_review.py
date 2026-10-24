"""Protect scope, old evidence and the exact third A-letter review delta."""
import json
import subprocess
import unittest
from pathlib import Path
from creator_snapshot import load_snapshot
ROOT = Path(__file__).resolve().parents[1]
BASE = '570bf41078e39f9d91fb192bef6ef0ad62d66639'
def read(path): return load_snapshot(ROOT, path)
APPLIED = 'f6f53b6faa6bc3ce2091e8cc67c782967fc2a303'
def applied(path): return json.loads(subprocess.check_output(['git', 'show', f'{APPLIED}:{path}'], cwd=ROOT, text=True))
def old(path): return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))
class CreatorA3ReviewTests(unittest.TestCase):
 def test_exact_fourteen_credits_preserve_original_signatures(self):
  b = {c['id']:c for c in old('data/credits.json')['credits']}
  a = {c['id']:c for c in applied('data/credits.json')['credits']}
  self.assertTrue(b.keys() <= a.keys())
  for cid in b: self.assertEqual(b[cid], a[cid], cid)
  added = [a[cid] for cid in a.keys()-b.keys()]
  self.assertEqual(len(added), 14)
  expected = {('entity-name-788994ba8dfb',w,'originalProduction') for w in ['g1198','g1199']}
  expected |= {('entity-applique_imouto',f'g{n}','productionBrand') for n in range(871,875)}
  expected |= {('entity-applique',f'g{n}','productionBrand') for n in [862,863,864,865,866,867,868,870]}
  self.assertEqual({(c['entityId'],c['workId'],c['role']) for c in added}, expected)
  review=read('data/entity-creator-a3-review-20261022.json')
  self.assertEqual({(c['entityId'],c['workId'],c['role'],c['source']) for c in added},{(c['entityId'],c['workId'],c['role'],c['source']) for c in review['creditAdditions']})
  for c in added:
   self.assertEqual(c['targetType'],'work');self.assertEqual(c['status'],'sourceReviewed');self.assertEqual(c['reviewRecord'],review['audit'])
 def test_only_eight_own_memberships_change_and_pending_child_references_remain(self):
  key=lambda m:(m['dossierId'],m['workId'])
  b={key(m):m for m in old('data/credits.json')['dossierMemberships']};a={key(m):m for m in applied('data/credits.json')['dossierMemberships']}
  self.assertEqual(a.keys(),b.keys())
  expected={('applique',f'g{n}') for n in [862,863,864,865,866,867,868,870]}
  self.assertEqual({k for k in b if a[k]!=b[k]},expected)
  for k in b:
   self.assertEqual(a[k]['placement'],b[k]['placement'])
   if b[k]['status']=='pendingRole': self.assertEqual(a[k],b[k])
   if k in expected:
    self.assertEqual(a[k]['group'],'original');self.assertEqual(set(a[k]['roles']),set(b[k]['roles'])|{'productionBrand'})
  self.assertEqual({('applique',f'g{n}') for n in range(871,875)} <= {k for k in a if a[k]['status']=='pendingRole'},True)
 def test_identities_core_main_page_baselines_and_all_older_reviews_unchanged(self):
  paths=['data/entities.json','data/entity-migration-review.json','data/games.json','data/company-coverage.json','data/taxonomy.json','data/gameplay-catalogues.json','data/work-classification.json','data/entity-migration-baseline.json','data/content-migration-baseline.json','index.html','app.mjs','filter.mjs','styles.css']
  paths += [f'data/entity-{batch}-review-20261022.{ext}' for batch in ['priority','followup','third','fourth','creator-a','creator-a2'] for ext in ['json','md']]
  for path in paths:
   actual = subprocess.check_output(['git','show',f'{APPLIED}:{path}'],cwd=ROOT) if path in ['data/entities.json','data/entity-migration-review.json'] else (ROOT/path).read_bytes()
   self.assertEqual(actual,subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT),path)
 def test_alphabetical_progress_and_unconfirmed_scopes_do_not_gain_creation(self):
  org=applied('data/organizations.json');p=org['registrationProgress'];ns={n['id']:n for n in org['nodes']}
  self.assertEqual(p['processedEntityIds'],[q['entityId'] for q in p['queue'][:20]])
  self.assertEqual([q['entityId'] for q in p['reviewedEntities']],p['processedEntityIds'])
  self.assertEqual(p['nextEntityId'],'entity-aquaplus');self.assertEqual(len(p['audits']),3)
  self.assertEqual(ns['entity-applique']['productionCount'],8)
  self.assertEqual(ns['entity-applique_imouto']['productionCount'],4)
  self.assertEqual(ns['entity-name-788994ba8dfb']['productionCount'],2)
  bns={n['id']:n for n in old('data/organizations.json')['nodes']}
  for eid in ['entity-name-bd36baf4b6a9','entity-name-5b146b15540c','entity-angel_hearts','entity-aniplex','entity-aniplex_exe']:
   self.assertEqual(ns[eid]['groups'],bns[eid]['groups'])
  self.assertFalse(any(r['workId']=='g869' for r in ns['entity-applique']['groups']['creation']))
  self.assertEqual({r['workId'] for r in ns['entity-applique']['groups']['pending']},{'g871','g872','g873','g874'})
