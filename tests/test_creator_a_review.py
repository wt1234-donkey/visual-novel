"""Exact sourced A-letter delta; raw catalogue and old identities remain preserved."""
import json
import subprocess
import unittest
from pathlib import Path
from creator_snapshot import load_snapshot
ROOT=Path(__file__).resolve().parents[1]
BASE='d8f37e90abf47af94e9285167a26b6865497e332'
def read(p):return load_snapshot(ROOT, p)
APPLIED='c5abca055efbae673c53d8275579e9f42ae815b7'
def applied(p):return json.loads(subprocess.check_output(['git','show',f'{APPLIED}:{p}'],cwd=ROOT,text=True))
def old(p):return json.loads(subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT,text=True))
class CreatorAReviewTests(unittest.TestCase):
 def test_five_credits_append_without_rewriting_old_credits_or_memberships(self):
  before,after=old('data/credits.json'),applied('data/credits.json')
  prior={c['id']:c for c in before['credits']};current={c['id']:c for c in after['credits']}
  self.assertTrue(prior.keys()<=current.keys())
  for cid in prior:self.assertEqual(prior[cid],current[cid],cid)
  added=[current[cid] for cid in current.keys()-prior.keys()]
  review=read('data/entity-creator-a-review-20261022.json')
  self.assertEqual({(c['entityId'],c['workId'],c['role']) for c in added},{(c['entityId'],c['workId'],c['role']) for c in review['creditAdditions']})
  self.assertEqual(len(added),5);self.assertEqual(before['dossierMemberships'],after['dossierMemberships'])
  for c in added:self.assertEqual(c['reviewRecord'],review['audit']);self.assertEqual(c['status'],'sourceReviewed')
 def test_only_akatsuki_identity_changes_and_relations_stay_identical(self):
  before,after=old('data/entities.json'),applied('data/entities.json')
  self.assertEqual(before['relations'],after['relations']);self.assertEqual(before['dossiers'],after['dossiers'])
  b={n['id']:n for n in before['entities']};a={n['id']:n for n in after['entities']}
  self.assertEqual(b.keys(),a.keys());self.assertEqual({eid for eid in b if b[eid]!=a[eid]},{'entity-name-76fdfcac5ffb'})
  self.assertEqual(a['entity-name-76fdfcac5ffb']['type'],'company')
  for eid in b:
   for field in ['id','name','aliases','dates']:self.assertEqual(b[eid][field],a[eid][field])
  self.assertEqual(len(applied('data/entity-migration-review.json')['pendingIdentities']),182)
  self.assertEqual(applied('data/entity-migration-review.json')['pendingMembershipCount'],611)
 def test_core_catalogue_baselines_and_all_prior_evidence_unchanged(self):
  paths=['data/games.json','data/company-coverage.json','data/taxonomy.json','data/gameplay-catalogues.json','data/work-classification.json','data/entity-migration-baseline.json','data/content-migration-baseline.json','index.html','app.mjs','filter.mjs','styles.css']
  paths += [f'data/entity-{batch}-review-20261022.{ext}' for batch in ['priority','followup','third','fourth'] for ext in ['json','md']]
  for p in paths:self.assertEqual((ROOT/p).read_bytes(),subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT),p)
 def test_sequential_progress_and_scope_are_explicit(self):
  review=read('data/entity-creator-a-review-20261022.json');progress=review['progress']
  self.assertEqual(progress['total'],32);self.assertEqual(len(progress['processedEntityIds']),8)
  self.assertEqual([r['name'] for r in review['reviewedEntities']],['Accolade','Activision','Addison-Wesley Productions','Addison-Wesley Publishing Company','Adventure International','Adventure Soft','âge','Akatsuki Games'])
  self.assertEqual(progress['nextName'],'Alchemist')
  org=read('data/organizations.json');nodes={n['id']:n for n in org['nodes']}
  self.assertEqual(nodes['entity-name-c31f977d8bac']['productionCount'],1)
  self.assertEqual(nodes['entity-name-490ea790703a']['productionCount'],1)
  self.assertEqual(nodes['entity-name-f0d25e9c6d82']['productionCount'],2)
  ak=nodes['entity-name-76fdfcac5ffb'];self.assertEqual(ak['productionCount'],0);self.assertEqual(org['works'][ak['groups']['creation'][0]['workId']]['placement'],'related')
  self.assertFalse(nodes['entity-name-5b146b15540c']['groups']['creation'])
