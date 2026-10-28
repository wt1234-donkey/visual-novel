"""Ultra stays a publishing brand; same-title NES adventure stays independent."""
import json,subprocess,unittest
from pathlib import Path
from historical_paths import shared_paths
ROOT=Path(__file__).resolve().parents[1];BASE='5ed3e8940cc3f8a159d8c7c17d9dea5009332c57';ULTRA='entity-name-c87c2b9662fc'
def read(p):
 if p in {'data/games.json','data/entities.json','data/credits.json','data/organizations.json','data/company-coverage.json','data/taxonomy.json'}:return json.loads(subprocess.check_output(['git','show',f'efb379a122184182c419382dd5158b35db816bd4:{p}'],cwd=ROOT))
 return json.loads((ROOT/p).read_text())
def old(p):return json.loads(subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT))
class UltraGamesDossierTests(unittest.TestCase):
 def test_one_original_work_content_release_and_all_old_records_preserved(self):
  b,a=old('data/games.json'),read('data/games.json')
  for f,extra in [('works',{'g1285'}),('contentVersions',{'g1285-c-original'}),('platformReleases',{'g1285-v1'})]:
   bs={x['id']:x for x in b[f]};ns={x['id']:x for x in a[f]};self.assertEqual(set(ns)-set(bs),extra);self.assertEqual({i:ns[i] for i in bs},bs)
  w=a['works'][-1];r=a['platformReleases'][-1];self.assertEqual(w['subcategory'],'动作解谜融合');self.assertEqual(w['interactionModes'],['菜单指令','直接移动','即时动作']);self.assertNotIn('文字输入',w['interactionModes']);self.assertEqual(r['platform'],'NES');self.assertEqual(r['releaseRole'],'contentDebut');self.assertEqual(r['voice'],'未核实')
 def test_dossier_reuses_brand_and_nightshade_without_company_duplication(self):
  b,a=old('data/company-coverage.json'),read('data/company-coverage.json');self.assertEqual(a['companies'][:-1],b['companies']);self.assertEqual(a['companies'][-1]['workIds'],['g1029','g1285']);self.assertNotIn('relatedGames',a['companies'][-1])
  b,a=old('data/entities.json'),read('data/entities.json');bs={e['id']:e for e in b['entities']};ns={e['id']:e for e in a['entities']};self.assertEqual(bs.keys(),ns.keys());self.assertEqual({i for i in bs if bs[i]!=ns[i]},{ULTRA});self.assertEqual(ns[ULTRA]['type'],'brand');self.assertEqual(ns[ULTRA]['dates'][0]['kind'],'brandActivityStarted');self.assertEqual(ns[ULTRA]['dates'][0]['value'],'1988');self.assertEqual(a['relations'],b['relations']);self.assertEqual(a['dossiers'][:-1],b['dossiers']);self.assertEqual(a['dossiers'][-1]['dossierType'],'brand');self.assertEqual(a['dossiers'][-1]['entityIds'],[ULTRA])
 def test_exact_publisher_addition_no_developer_inference(self):
  b,a=old('data/credits.json'),read('data/credits.json');bs={x['id']:x for x in b['credits']};ns={x['id']:x for x in a['credits']};self.assertEqual({i:ns[i] for i in bs},bs);new=[ns[i] for i in set(ns)-set(bs)];self.assertEqual(len(new),1);self.assertEqual((new[0]['entityId'],new[0]['targetId'],new[0]['role']),(ULTRA,'g1285-v1','publisher'));self.assertEqual([m for m in a['dossierMemberships'] if m['dossierId']!='ultra_games'],b['dossierMemberships']);self.assertEqual(len([m for m in a['dossierMemberships'] if m['dossierId']=='ultra_games']),2)
 def test_history_and_trademark_remain_separate_from_formal_ownership(self):
  b,a=old('data/organizations.json'),read('data/organizations.json');self.assertEqual(a['verificationLedger'],b['verificationLedger']);self.assertEqual(a['organizationEvents'][:-4],b['organizationEvents']);self.assertEqual([e['year'] for e in a['organizationEvents'][-4:]],[1988,1988,1992,1992]);f=next(f for f in a['families'] if f['id']=='ultra_games');self.assertEqual((f['root'],f['focus']),('entity-konami',ULTRA));self.assertEqual(len(f['entityIds']),3)
  es={e['id']:e for e in a['edges']};self.assertEqual(es['ultra-trademark-owner']['kind'],'trademark');self.assertIn('直接持股',es['ultra-konami-historical']['note']);self.assertTrue(next(n for n in a['nodes'] if n['id']=='preview-ultra-software')['previewOnly']);self.assertEqual(a['unfinished']['counts'],{'identity':32,'duty':595,'creation':804,'evidence':481,'chronology':46,'relation':1})
 def test_rendering_and_frozen_files(self):
  for p in ['data/taxonomy.json','data/entity-migration-baseline.json','data/content-migration-baseline.json']:self.assertEqual(read(p),old(p))
  for p in shared_paths(ROOT, BASE, 'efb379a122184182c419382dd5158b35db816bd4', ['organization-context*.json','organization-verification*.json']):self.assertEqual(read(p),old(p))
  page=subprocess.check_output(['git','show','efb379a122184182c419382dd5158b35db816bd4:ultra_games.html'],cwd=ROOT,text=True);self.assertEqual(page.count('<article class="card"'),2);self.assertIn('g1029',page);self.assertIn('g1285',page);self.assertIn('Game Boy',page);self.assertIn('konami.html#konami-mg',page)
  self.assertIn('data-company="ultra_games" data-first-year="1992" data-kind="brand"',(ROOT/'index.html').read_text())
