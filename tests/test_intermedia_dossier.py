"""Intermedia reuses its reviewed identity and preserves old catalogue objects."""
import json,subprocess,unittest
from pathlib import Path
from historical_paths import shared_paths
ROOT=Path(__file__).resolve().parents[1]
BASE='329447b4c8ee6c7656301a4a0ab5f1fe9edd51cf'
E='entity-name-9832231b6baa'
def read(p):return json.loads(subprocess.check_output(['git','show',f'508efa3f228b7dc5ca52d1ecc086d813848462a4:{p}'],cwd=ROOT))
def old(p):return json.loads(subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT))
class IntermediaDossierTests(unittest.TestCase):
 def test_exact_two_narratives_and_only_their_original_debuts_are_added(self):
  b,a=old('data/games.json'),read('data/games.json')
  for field,suffix in [('works',''),('contentVersions','-c-original'),('platformReleases','-v1')]:
   before={x['id']:x for x in b[field]};after={x['id']:x for x in a[field]}
   self.assertEqual(set(after)-set(before),{'g1279'+suffix,'g1280'+suffix})
   self.assertEqual({i:after[i] for i in before},before)
  for w in a['works'][-2:]:self.assertEqual(w['interactionModes'],['菜单指令'])
  for r in a['platformReleases'][-2:]:self.assertEqual((r['platform'],r['releaseRole'],r['publisher']),('PC-98','contentDebut','GAMEテクノポリス'))
 def test_old_dossiers_and_all_entities_and_formal_relations_are_preserved(self):
  b,a=old('data/company-coverage.json'),read('data/company-coverage.json')
  self.assertEqual(a['companies'][:-1],b['companies'])
  c=a['companies'][-1];self.assertEqual(c['id'],'tokuma_intermedia')
  self.assertEqual(c['workIds'],['g918','g919','g920','g921','g922','g923','g1279','g1280'])
  self.assertFalse(c.get('relatedGames'));self.assertIn('tokuma.html#tokuma-filena',c['publisherWorkText'])
  b,a=old('data/entities.json'),read('data/entities.json')
  self.assertEqual(a['entities'],b['entities']);self.assertEqual(a['relations'],b['relations'])
  self.assertEqual(a['dossiers'][:-1],b['dossiers']);self.assertEqual(a['dossiers'][-1]['entityIds'],[E])
  self.assertEqual(a['dossiers'][-1]['firstYear'],1991)
 def test_only_two_release_credits_are_added_without_company_development(self):
  b,a=old('data/credits.json'),read('data/credits.json')
  before={x['id']:x for x in b['credits']};after={x['id']:x for x in a['credits']}
  self.assertEqual({i:after[i] for i in before},before)
  added=[after[i] for i in set(after)-set(before)]
  self.assertEqual({(c['entityId'],c['targetId'],c['role']) for c in added},{(E,'g1279-v1','publisher'),(E,'g1280-v1','publisher')})
  self.assertEqual([m for m in a['dossierMemberships'] if m['dossierId']!='tokuma_intermedia'],b['dossierMemberships'])
 def test_limited_history_joins_company_family_without_rewriting_frozen_evidence(self):
  b,a=old('data/organizations.json'),read('data/organizations.json')
  self.assertEqual(a['verificationLedger'],b['verificationLedger'])
  self.assertEqual(a['organizationEvents'][:-3],b['organizationEvents'])
  events=a['organizationEvents'][-3:];self.assertEqual([e['year'] for e in events],[1985,1997,1999])
  self.assertTrue(all(e['sources'] and not e['recordIds'] for e in events))
  self.assertIn('二手',events[1]['note']);self.assertIn('登记',events[0]['note'])
  family=next(f for f in a['families'] if E in f['entityIds']);self.assertIn('entity-tokuma',family['entityIds'])
  self.assertEqual(next(n for n in a['nodes'] if n['id']==E)['productionCount'],0)
  self.assertEqual(a['unfinished']['counts'],{'identity':32,'duty':591,'creation':802,'evidence':481,'chronology':44,'relation':1})
 def test_output_and_immutable_evidence_keep_scope_and_old_links(self):
  for p in shared_paths(ROOT, BASE, '508efa3f228b7dc5ca52d1ecc086d813848462a4', ['organization-verification*.json','organization-context*.json']):self.assertEqual(read(p),old(p))
  for p in ['data/entity-migration-baseline.json','data/content-migration-baseline.json','data/taxonomy.json']:
   self.assertEqual(read(p),old(p))
  page=(ROOT/'tokuma_intermedia.html').read_text();self.assertEqual(page.count('<article class="card"'),8)
  self.assertIn('tokuma.html#tokuma-lovequest',page);self.assertIn('待核：品牌与同名部门',page)
  self.assertIn('data-company="tokuma_intermedia" data-first-year="1991"',(ROOT/'index.html').read_text())
