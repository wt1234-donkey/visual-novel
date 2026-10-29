"""Current admission and identity preservation beyond the historical audits."""
import json, subprocess, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
BASE='6aca87246df60132412331a11e5e1b617e6d6a6f'
def read(p):return json.loads(subprocess.check_output(['git','show','71ef1dfe9c01c87e714c5e34708516a4c24b22f4:'+p],cwd=R))
def old(p):return json.loads(subprocess.check_output(['git','show',BASE+':'+p],cwd=R))
class ManufacturerUpdate(unittest.TestCase):
 def test_old_objects_unchanged_and_first_season_only(self):
  a,b=read('data/games.json'),old('data/games.json')
  for field in ['works','contentVersions','platformReleases']:
   byid={x['id']:x for x in a[field]}
   self.assertEqual([byid[x['id']] for x in b[field]],b[field])
   self.assertEqual(len(a[field]),len(b[field])+1)
  self.assertEqual(a['platformReleases'][-1]['publisherCompanies'],['Sony Computer Entertainment'])
 def test_old_related_and_capcom_identity_reuse(self):
  a={x['id']:x for x in read('data/company-coverage.json')['companies']}
  for c in old('data/company-coverage.json')['companies']:
   for r in c.get('relatedGames',[]):self.assertIn(r,a[c['id']].get('relatedGames',[]))
   for wid in c['workIds']:self.assertIn(wid,a[c['id']]['workIds'])
  self.assertEqual(a['capcom']['workIds'],['g049','g172','g173','g182'])
  e=read('data/entities.json');cap=next(x for x in e['dossiers'] if x['id']=='capcom')
  self.assertEqual(cap['entityIds'],['entity-name-7554e19bb041'])
  self.assertEqual({x['id'] for x in e['entities']},{x['id'] for x in old('data/entities.json')['entities']})
 def test_ultra_story_is_related_and_current_rendering(self):
  a={x['id']:x for x in read('data/company-coverage.json')['companies']}
  r=a['ultra_games']['relatedGames'][0]
  self.assertEqual(r['id'],'ultra-snakes-revenge')
  self.assertNotIn(r['id'],{x['id'] for x in read('data/games.json')['works']})
  for page,n in [('chunsoft',12),('ultra_games',3),('capcom',4)]:
   self.assertEqual(subprocess.check_output(['git','show','71ef1dfe9c01c87e714c5e34708516a4c24b22f4:'+page+'.html'],cwd=R,text=True).count('<article class="card"'),n)
  self.assertIn('data-company="capcom" data-first-year="2001"',(R/'index.html').read_text())
