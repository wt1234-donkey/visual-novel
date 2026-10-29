"""Append-only catalogue expansion and first-content identity boundaries."""
import json,subprocess,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
BASE='71ef1dfe9c01c87e714c5e34708516a4c24b22f4'
def read(p):return json.loads((R/p).read_text())
def before(p):return json.loads(subprocess.check_output(['git','show',BASE+':'+p],cwd=R))
def chun(data):return next(x for x in data['companies'] if x['id']=='chunsoft')
class ChunsoftCompletion(unittest.TestCase):
 def test_preserve_all_existing_games_contents_releases_and_other_dossiers(self):
  self.assertEqual(read('data/games.json'),before('data/games.json'))
  b,a=before('data/company-coverage.json'),read('data/company-coverage.json')
  self.assertEqual([x for x in a['companies'] if x['id']!='chunsoft'],[x for x in b['companies'] if x['id']!='chunsoft'])
  self.assertTrue(set(chun(b)['workIds'])<=set(chun(a)['workIds']))
  self.assertEqual(set(chun(a)['workIds'])-set(chun(b)['workIds']),{'g979'})
 def test_related_identity_and_first_release_increments(self):
  c=chun(read('data/company-coverage.json'));w={w['id']:w for w in c['relatedGames']}
  self.assertEqual(w['chun-shiren2']['platformReleases'][0]['publisher'],'任天堂');self.assertEqual(len(w),16);self.assertEqual(len(c['workIds']),13)
  self.assertEqual(sum(len(x['contentVersions']) for x in w.values()),21)
  self.assertEqual(sum(len(x['platformReleases']) for x in w.values()),22)
  self.assertTrue(all(r['releaseRole']=='contentDebut' for x in w.values() for r in x['platformReleases']))
  self.assertEqual(len(w['chun-pokemon-rescue']['contentVersions']),1)
  self.assertEqual(len(w['chun-pokemon-rescue']['platformReleases']),2)
  self.assertEqual(len(w['chun-pokemon-adventure']['contentVersions']),3)
  self.assertFalse({'chun-pokemon-fire','chun-pokemon-storm','chun-pokemon-light'}&set(w))
  for wid in ['chun-shiren1','chun-shiren-gb2','chun-pokemon-explorers']:
   self.assertEqual(len(w[wid]['contentVersions']),2)
   self.assertEqual(w[wid]['contentVersions'][1]['comparedTo'],wid+'-c-original')
 def test_scope_credits_and_old_identity_preservation(self):
  b,a=before('data/entities.json'),read('data/entities.json')
  current={e['id']:e for e in a['entities']}
  self.assertEqual([current[e['id']] for e in b['entities']],b['entities'])
  self.assertEqual(a['relations'],b['relations'])
  b,a=before('data/credits.json'),read('data/credits.json');after={x['id']:x for x in a['credits']}
  self.assertEqual([after[x['id']] for x in b['credits']],b['credits'])
  scoped=[x for x in a['credits'] if x['entityId']=='entity-name-21365baf366d' and x['workId']=='chun-asuka']
  self.assertEqual({x['role'] for x in scoped},{'supervisor'})
  self.assertFalse(any(x['role']=='publisher' and x['entityId']=='entity-name-21365baf366d' and x['workId']=='chun-shiren4' for x in a['credits']))
 def test_cross_dossier_reuse_and_current_rendering(self):
  cat=read('data/gameplay-catalogues.json')['companies']['chunsoft']
  rows=[r for g in cat['groups'] for r in g['rows']]
  refs={r['catalogueWorkId'] for r in rows if r.get('catalogueWorkId')}
  self.assertEqual(refs,{'g007','enix-dq1','enix-dq2','enix-dq3','enix-dq4','enix-dq5','enix-torneko2','enix-torneko3'})
  page=(R/'chunsoft.html').read_text()
  self.assertEqual(page.count('<article class="card"'),29)
  for ref in refs:self.assertIn('enix.html#'+ref,page)
  self.assertIn('data-company="chunsoft" data-first-year="1987"',(R/'index.html').read_text())
  review=read('data/chunsoft-source-review-20261029.json')['rows']
  self.assertTrue(all(x['source'] and x['decision'] and x['reason'] for x in review))
