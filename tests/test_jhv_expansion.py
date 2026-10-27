"""JHV supplementation preserves identities and separates cooperation from ownership."""
import json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='54abb80b9ee2303f294d2bc0e0d3189482e045cf'
def read(p):return json.loads((ROOT/p).read_text())
def old(p):return json.loads(subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT))
class JHVExpansionTests(unittest.TestCase):
 def test_catalogue_identity_and_historical_credits_unchanged(self):
  for p in ['data/games.json','data/taxonomy.json','data/entity-migration-baseline.json','data/content-migration-baseline.json','data/work-classification.json']:self.assertEqual(read(p),old(p))
  b,a=old('data/company-coverage.json'),read('data/company-coverage.json')
  self.assertEqual([c for c in a['companies'] if c['id']!='jhv'],[c for c in b['companies'] if c['id']!='jhv'])
  for key in ['workIds','publisherWorkIds','relatedGames']:
   self.assertEqual(next(c for c in a['companies'] if c['id']=='jhv')[key],next(c for c in b['companies'] if c['id']=='jhv')[key])
 def test_exact_new_entities_and_three_scoped_credits(self):
  b,a=old('data/entities.json'),read('data/entities.json');bs={e['id']:e for e in b['entities']};ns={e['id']:e for e in a['entities']}
  self.assertEqual(set(ns)-set(bs),{'entity-headroom','entity-tenky'})
  self.assertEqual({i for i in bs if bs[i]!=ns[i]},{'entity-jhv'})
  self.assertEqual(ns['entity-headroom']['type'],'team');self.assertEqual(ns['entity-tenky']['type'],'company')
  self.assertEqual(ns['entity-jhv']['dates'][0]['value'],'1984-05-26')
  self.assertEqual(a['relations'],b['relations'])
  b,a=old('data/credits.json'),read('data/credits.json');bs={c['id']:c for c in b['credits']};ns={c['id']:c for c in a['credits']}
  self.assertEqual({i:ns[i] for i in bs},bs);new=[ns[i] for i in set(ns)-set(bs)]
  self.assertEqual({(c['entityId'],c['targetId'],c['role']) for c in new},{('entity-headroom','g830','originalProduction'),('entity-headroom','g831','coDeveloper'),('entity-tenky','g831','coDeveloper')})
  self.assertEqual(a['dossierMemberships'],b['dossierMemberships'])
 def test_notes_for_all_five_main_works(self):
  a,b=read('data/work-notes.json'),old('data/work-notes.json');self.assertEqual({i:a['works'][i] for i in b['works']},b['works'])
  self.assertEqual(set(a['works'])-set(b['works']),{'g830','g831','g832','g833','g834'})
  self.assertEqual(sum(len(a['works'][i]) for i in set(a['works'])-set(b['works'])),7)
  page=(ROOT/'jhv.html').read_text();self.assertEqual(page.count('<article class="card"'),9)
  for text in ['HEADROOM','TENKY','成立日期','Sensual Angels','g830-c-4']:self.assertIn(text,page)
 def test_organization_cooperation_is_not_ownership_and_unknown_dates_listed(self):
  d=read('data/organizations.json');family=next(f for f in d['families'] if f['id']=='jhv');self.assertEqual(family['root'],'entity-jhv');self.assertEqual(len(family['entityIds']),4)
  es=[e for e in d['edges'] if e['id'].startswith('jhv-')];self.assertEqual({e['kind'] for e in es},{'cooperation','affiliation'})
  self.assertTrue(all('子公司' in e['note'] or '控制' in e['note'] for e in es))
  self.assertIn('edge:jhv-estation-affiliation',{i['id'] for i in d['unfinished']['items']})
  self.assertEqual(d['unfinished']['counts'],{'identity':32,'duty':595,'creation':803,'evidence':481,'chronology':45,'relation':1})
  self.assertNotIn('creation:g830',{i['id'] for i in d['unfinished']['items']});self.assertNotIn('creation:g831',{i['id'] for i in d['unfinished']['items']})
 def test_frozen_ledger_and_previous_events_preserved(self):
  b,a=old('data/organizations.json'),read('data/organizations.json');self.assertEqual(a['verificationLedger'],b['verificationLedger']);self.assertEqual(a['organizationEvents'][:-5],b['organizationEvents']);self.assertEqual([e['year'] for e in a['organizationEvents'][-5:]],[1984,1992,1993,1994,2004])
  for pattern in ['organization-context*.json','organization-verification*.json']:
   for p in (ROOT/'data').glob(pattern):self.assertEqual(read(str(p.relative_to(ROOT))),old(str(p.relative_to(ROOT))))
