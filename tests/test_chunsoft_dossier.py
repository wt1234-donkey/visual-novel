"""Chunsoft identity, content increments and merger direction stay explicit."""
import json,subprocess,unittest
from pathlib import Path
from historical_paths import shared_paths
ROOT=Path(__file__).resolve().parents[1]
BASE='d80510b343d53f61c0df6ad799466aaca55ea2f3'
CH='entity-name-21365baf366d';SP='entity-name-6d5cd9b9dc38';SC='entity-name-8a871cf93bfd'
def read(p):
 if p in {'data/games.json','data/entities.json','data/credits.json','data/organizations.json','data/company-coverage.json','data/taxonomy.json'}:return json.loads(subprocess.check_output(['git','show',f'54abb80b9ee2303f294d2bc0e0d3189482e045cf:{p}'],cwd=ROOT))
 return json.loads((ROOT/p).read_text())
def old(p):return json.loads(subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT))
class ChunsoftDossierTests(unittest.TestCase):
 def test_exact_two_works_four_contents_four_releases_preserve_every_old_object(self):
  b,a=old('data/games.json'),read('data/games.json')
  extras={'works':{'g1283','g1284'},'contentVersions':{'g1283-c-original','g1283-c-special','g1284-c-original','g1284-c-complete'},'platformReleases':{'g1283-v1','g1283-v2','g1284-v1','g1284-v2'}}
  for field,expected in extras.items():
   before={x['id']:x for x in b[field]};after={x['id']:x for x in a[field]}
   self.assertEqual(set(after)-set(before),expected);self.assertEqual({i:after[i] for i in before},before)
  cs={c['id']:c for c in a['contentVersions']};rs={r['id']:r for r in a['platformReleases']}
  self.assertEqual(cs['g1283-c-special']['comparedTo'],'g1283-c-original');self.assertEqual(cs['g1284-c-complete']['comparedTo'],'g1284-c-original')
  self.assertEqual(rs['g1283-v2']['publisher'],'世嘉');self.assertIn('2005-07-28',rs['g1284-v2']['differences']);self.assertIn('09-29',rs['g1284-v2']['differences'])
  self.assertTrue(all(rs[i]['releaseRole']=='contentDebut' for i in extras['platformReleases']))
 def test_new_dossier_reuses_existing_identity_and_old_dossiers(self):
  b,a=old('data/company-coverage.json'),read('data/company-coverage.json');self.assertEqual(a['companies'][:-1],b['companies'])
  c=a['companies'][-1];self.assertEqual(c['id'],'chunsoft');self.assertEqual(len(c['workIds']),11);self.assertNotIn('relatedGames',c)
  self.assertIn('enix.html#enix-dq1',c['publisherWorkText'])
  b,a=old('data/entities.json'),read('data/entities.json');before={e['id']:e for e in b['entities']};after={e['id']:e for e in a['entities']}
  self.assertEqual(before.keys(),after.keys());self.assertEqual({i for i in before if before[i]!=after[i]},{CH})
  self.assertEqual(after[CH]['name'],'Chunsoft（チュンソフト）');self.assertEqual(after[CH]['type'],'company')
  self.assertEqual(a['relations'],b['relations']);self.assertEqual(a['dossiers'][:-1],b['dossiers']);self.assertEqual(a['dossiers'][-1]['entityIds'],[CH])
 def test_only_scoped_release_and_one_production_credit_are_added(self):
  b,a=old('data/credits.json'),read('data/credits.json');before={c['id']:c for c in b['credits']};after={c['id']:c for c in a['credits']}
  self.assertEqual({i:after[i] for i in before},before)
  added=[after[i] for i in set(after)-set(before)];self.assertEqual(len(added),5)
  self.assertEqual([(c['entityId'],c['workId'],c['role']) for c in added if c['targetType']=='work'],[(CH,'g1284','originalProduction')])
  self.assertEqual(sum(c['role']=='publisher' for c in added),4)
  self.assertEqual([m for m in a['dossierMemberships'] if m['dossierId']!='chunsoft'],b['dossierMemberships'])
  pending={m['workId'] for m in a['dossierMemberships'] if m['dossierId']=='chunsoft' and m['status']=='pendingRole'}
  self.assertEqual(pending,{'g034','g055','g179','g181'})
 def test_explicit_family_merger_direction_and_frozen_audit_preserved(self):
  b,a=old('data/organizations.json'),read('data/organizations.json');self.assertEqual(a['verificationLedger'],b['verificationLedger'])
  self.assertEqual(a['organizationEvents'][:-5],b['organizationEvents']);self.assertEqual([e['year'] for e in a['organizationEvents'][-5:]],[1984,1992,1993,2006,2012])
  family=next(f for f in a['families'] if f['id']=='chunsoft');self.assertEqual((family['root'],family['focus']),(CH,CH));self.assertEqual(set(family['entityIds']),{CH,SP,SC})
  edges={e['id']:e for e in a['edges']};self.assertEqual((edges['chunsoft-successor-2012']['parent'],edges['chunsoft-successor-2012']['child']),(CH,SC));self.assertIn('存续',edges['chunsoft-successor-2012']['note']);self.assertIn('消灭',edges['spike-absorbed-2012']['note'])
  self.assertEqual(a['unfinished']['counts'],{'identity':32,'duty':595,'creation':805,'evidence':481,'chronology':44,'relation':1})
 def test_rendered_scope_and_old_evidence_remain(self):
  for p in shared_paths(ROOT, BASE, '54abb80b9ee2303f294d2bc0e0d3189482e045cf', ['organization-context*.json','organization-verification*.json']):self.assertEqual(read(p),old(p))
  for p in ['data/taxonomy.json','data/entity-migration-baseline.json','data/content-migration-baseline.json']:self.assertEqual(read(p),old(p))
  page=(ROOT/'chunsoft.html').read_text();self.assertEqual(page.count('<article class="card"'),11);self.assertIn('09-29',page);self.assertIn('g1284-c-complete',page)
  self.assertIn('data-company="chunsoft" data-first-year="1992"',(ROOT/'index.html').read_text())
