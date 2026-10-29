"""Old game company, new prize corporation and category brand stay distinct."""
import json,subprocess,unittest,sys,copy
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];BASE='efb379a122184182c419382dd5158b35db816bd4';sys.path.insert(0,str(ROOT/'scripts'))
import build_entity_model as builder
REVIEW='data/entity-banpresto-review-20261027.json'
def read(p):
 if p != REVIEW and p in {'data/games.json','data/credits.json','data/work-classification.json','data/taxonomy.json','data/entity-migration-baseline.json','data/content-migration-baseline.json','data/company-coverage.json','data/entities.json','data/work-notes.json','data/organizations.json'}:
  return json.loads(subprocess.check_output(['git','show',f'4cd26b3:{p}'],cwd=ROOT))
 return json.loads((ROOT/p).read_text())
def old(p):return json.loads(subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT))
class BanprestoExpansionTests(unittest.TestCase):
 def test_all_work_content_release_and_scoped_credits_preserved(self):
  for p in ['data/games.json','data/credits.json','data/work-classification.json','data/taxonomy.json','data/entity-migration-baseline.json','data/content-migration-baseline.json']:self.assertEqual(read(p),old(p))
  b,a=old('data/company-coverage.json'),read('data/company-coverage.json');self.assertEqual([c for c in a['companies'] if c['id']!='banpresto'],[c for c in b['companies'] if c['id']!='banpresto']);bc=next(c for c in b['companies'] if c['id']=='banpresto');ac=next(c for c in a['companies'] if c['id']=='banpresto')
  for k in ['workIds','workGroups','publisherWorkIds','relatedGames','historicalArchive']:self.assertEqual(ac[k],bc[k])
  self.assertEqual(len(ac['workIds']),21)
 def test_only_old_company_identity_is_corrected(self):
  b,a=old('data/entities.json'),read('data/entities.json');bs={e['id']:e for e in b['entities']};ns={e['id']:e for e in a['entities']};self.assertEqual(bs.keys(),ns.keys());self.assertEqual({i for i in bs if ns[i]!=bs[i]},{'entity-banpresto'});e=ns['entity-banpresto'];self.assertEqual((e['type'],e['verification']),('company','sourceReviewed'));self.assertEqual(e['dates'][0]['value'],'1977-04-30');self.assertEqual(e['name'],'Banpresto（バンプレスト）');self.assertEqual(a['relations'],b['relations']);self.assertEqual(next(d for d in a['dossiers'] if d['id']=='banpresto')['dossierType'],'history')
  scope=read(REVIEW)['identityCorrections'][0]['historicalPublisherScope'];self.assertEqual(len(scope['releaseIds']),18);rs={r['id']:r for r in read('data/games.json')['platformReleases']};self.assertTrue(all(rs[i]['year']<2008 for i in scope['releaseIds']))
 def test_main_notes_cover_nine_existing_works_without_duplicate_counts(self):
  b,a=old('data/work-notes.json'),read('data/work-notes.json');new={'g304','g1061','g1062','g1063','g1075','g1076','g1077','g1078','g1079'};self.assertEqual(set(a['works'])-set(b['works']),new);self.assertEqual({i:a['works'][i] for i in b['works']},b['works']);self.assertTrue(all(len(a['works'][i])==1 for i in new))
  page=subprocess.check_output(['git','show','4cd26b3:banpresto.html'],cwd=ROOT).decode();self.assertEqual(page.count('<article class="card"'),21);self.assertIn('2019',page);self.assertIn('1977',page)
 def test_two_absorptions_split_and_brand_are_distinct(self):
  b,a=old('data/organizations.json'),read('data/organizations.json');self.assertEqual(a['verificationLedger'],b['verificationLedger']);self.assertEqual(a['organizationEvents'][:-7],b['organizationEvents']);self.assertEqual([e['year'] for e in a['organizationEvents'][-7:]],[1977,1995,2006,2008,2015,2018,2019]);self.assertEqual(a['unfinished']['counts'],b['unfinished']['counts'])
  f=next(f for f in a['families'] if f['id']=='banpresto');self.assertEqual(f['root'],'entity-banpresto');self.assertEqual(len(f['entityIds']),5);es={e['id']:e for e in a['edges']};self.assertEqual(es['banpresto-game-absorption-2008']['child'],'entity-name-40ed6431d1a6');self.assertEqual(es['banpresto-prize-absorption-2019']['parent'],'preview-banpresto-prize-2008');self.assertEqual(es['banpresto-prize-absorption-2019']['child'],'preview-bandai-spirits');self.assertEqual(es['banpresto-prize-brand-2019']['child'],'preview-banpresto-prize-brand')
  for eid in ['preview-banpresto-prize-2008','preview-bandai-spirits','preview-banpresto-prize-brand']:
   n=next(n for n in a['nodes'] if n['id']==eid);self.assertTrue(n['previewOnly']);self.assertEqual(n['productionCount'],0)
 def test_correction_checks_old_state_and_historical_scope(self):
  original=builder.read
  for mutate in ['before','scope']:
   review=copy.deepcopy(read(REVIEW))
   if mutate=='before':review['identityCorrections'][0]['before']['type']='company'
   else:review['identityCorrections'][0]['historicalPublisherScope']['beforeYear']=1995
   with self.subTest(mutate=mutate),patch.object(builder,'read',side_effect=lambda p: review if p==REVIEW else original(p)):
    with self.assertRaises(AssertionError):builder.build()
