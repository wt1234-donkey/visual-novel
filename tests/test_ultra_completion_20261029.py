"""Current Ultra admission, scoped publication and cross-dossier deduplication."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='2fb61d3b03367939dd2e6b1a9ce6c21fe319f779'
ULTRA='entity-name-c87c2b9662fc'
NEW_RELATED={'ultra-star-trek-gb','ultra-tmnt-nes','ultra-tmnt-arcade','ultra-tmnt-fall','ultra-pirates','ultra-defender','ultra-rollergames'}
def read(path):return json.loads((ROOT/path).read_text())
def before(path):return json.loads(subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT))
def company(data,cid):return next(c for c in data['companies'] if c['id']==cid)


class UltraCompletionTests(unittest.TestCase):
 def test_main_append_only_and_other_dossiers_preserved(self):
  old,new=before('data/games.json'),read('data/games.json')
  for field,extra in [('works',{'g1332'}),('contentVersions',{'g1332-c-original'}),('platformReleases',{'g1332-v-original'})]:
   oldmap={x['id']:x for x in old[field]};newmap={x['id']:x for x in new[field]}
   self.assertEqual(set(newmap)-set(oldmap),extra)
   self.assertEqual({i:newmap[i] for i in oldmap},oldmap)
  old,new=before('data/company-coverage.json'),read('data/company-coverage.json')
  self.assertEqual([c for c in old['companies'] if c['id'] not in {'ultra_games','konami'}],[c for c in new['companies'] if c['id'] not in {'ultra_games','konami'}])
  for path in ['data/content-migration-baseline.json','data/entity-migration-baseline.json','data/taxonomy.json']:self.assertEqual(before(path),read(path))

 def test_related_identity_and_content_debuts_are_not_regional_port_copies(self):
  old=company(before('data/company-coverage.json'),'ultra_games');new=company(read('data/company-coverage.json'),'ultra_games')
  works={w['id']:w for w in new['relatedGames']}
  self.assertEqual(set(works)-{w['id'] for w in old['relatedGames']},NEW_RELATED)
  self.assertEqual(works['ultra-snakes-revenge'],old['relatedGames'][0])
  self.assertEqual(new['workIds'],['g1029','g1285','g1332'])
  self.assertEqual(sum(len(works[i]['contentVersions']) for i in NEW_RELATED),7)
  releases=[r for i in NEW_RELATED for r in works[i]['platformReleases']]
  self.assertEqual(len(releases),7)
  self.assertTrue(all(r['releaseRole']=='contentDebut' for r in releases))
  self.assertEqual(works['ultra-tmnt-nes']['platformReleases'][0]['publisher'],'Konami')
  self.assertEqual(works['ultra-tmnt-arcade']['platformReleases'][0]['platform'],'Arcade（北美）')
  self.assertEqual(works['ultra-pirates']['firstYear'],1987)
  self.assertEqual(works['ultra-defender']['firstYear'],1986)
  self.assertNotIn('ultra-star-trek-gb',{w['id'] for w in read('data/games.json')['works']})

 def test_metal_gear_reuses_one_work_and_adds_only_documented_famicom_content(self):
  old,new=[company(loader('data/company-coverage.json'),'konami') for loader in [before,read]]
  b={w['id']:w for w in old['relatedGames']};a={w['id']:w for w in new['relatedGames']}
  self.assertEqual(set(a),set(b))
  self.assertEqual({i:a[i] for i in a if i!='konami-mg'},{i:b[i] for i in b if i!='konami-mg'})
  for key in b['konami-mg']:
   if key in {'contentVersions','platformReleases'}:self.assertEqual(a['konami-mg'][key][:-1],b['konami-mg'][key])
   else:self.assertEqual(a['konami-mg'][key],b['konami-mg'][key])
  added=a['konami-mg']['contentVersions'][-1]
  self.assertEqual((added['id'],added['comparedTo']),('konami-mg-c-famicom','konami-mg-c-original'))
  self.assertEqual(a['konami-mg']['platformReleases'][-1]['publisher'],'Konami')
  self.assertIn('konami.html#konami-mg',(ROOT/'ultra_games.html').read_text())

 def test_limited_ultra_editions_preserve_publication_scope_and_old_credits(self):
  old,new=before('data/credits.json'),read('data/credits.json')
  credits={c['id']:c for c in new['credits']}
  self.assertEqual([credits[c['id']] for c in old['credits']],old['credits'])
  self.assertEqual(new['scopedEditions'][0],old['scopedEditions'][0])
  editions=new['scopedEditions'][1:];self.assertEqual(len(editions),6)
  allreleases={r['id'] for r in read('data/games.json')['platformReleases']}
  for c in read('data/company-coverage.json')['companies']:
   allreleases.update(r['id'] for w in c.get('relatedGames',[]) for r in w['platformReleases'])
  self.assertFalse(allreleases & {e['id'] for e in editions})
  for e in editions:
   self.assertEqual(e['publisher'],'Ultra Games');self.assertIsNone(e['contentVersionId'])
   scoped=[c for c in new['credits'] if c['targetId']==e['id']]
   self.assertEqual([(c['entityId'],c['targetType'],c['role']) for c in scoped],[(ULTRA,'edition','publisher')])
  appended=[c for c in new['credits'] if c['id'] not in {c['id'] for c in old['credits']}]
  self.assertFalse(any(c['entityId']==ULTRA and c['role'] in {'developer','originalProduction','productionBrand'} for c in appended))
  old,new=before('data/entities.json'),read('data/entities.json');entities={e['id']:e for e in new['entities']}
  self.assertEqual([entities[e['id']] for e in old['entities']],old['entities']);self.assertEqual(new['relations'],old['relations'])
  fresh=[e for e in new['entities'] if e['id'] not in {e['id'] for e in old['entities']}]
  self.assertEqual({e['name'] for e in fresh},{'MicroProse','Cinemaware'})
  self.assertTrue(all(e['type']=='unknown' and e['verification']=='unresolved' for e in fresh))

 def test_all_26_source_rows_accounted_for_and_current_page_once(self):
  rows=read('data/ultra-source-review-20261029.json')['rows']
  self.assertEqual((len(rows),sum(r['platform']=='NES' for r in rows),sum(r['platform']=='GB' for r in rows)),(26,17,9))
  self.assertEqual(len({(r['platform'],r['title']) for r in rows}),26)
  self.assertEqual({d:sum(r['decision']==d for r in rows) for d in ['addMain','addRelated','reuse','reuseCrossDossier','referenceOnly']},{'addMain':1,'addRelated':7,'reuse':3,'reuseCrossDossier':1,'referenceOnly':14})
  self.assertTrue(all(r['source'] and r['reason'] and r['type'] for r in rows))
  memberships={m['workId']:m for m in read('data/credits.json')['dossierMemberships'] if m['dossierId']=='ultra_games'}
  for row in rows:
   if row['decision'] in {'addMain','addRelated'}:self.assertEqual(memberships[row['workId']]['source'],row['source'])
  extra=read('data/ultra-source-review-20261029.json')['additionalEditionCandidates']
  self.assertEqual(len(extra),4);self.assertTrue(all('workId' not in row for row in extra))
  page=(ROOT/'ultra_games.html').read_text();self.assertEqual(page.count('<article class="card"'),11)
  for wid in {'g1029','g1285','g1332','ultra-snakes-revenge',*NEW_RELATED}:self.assertEqual(page.count('<article class="card" id="'+wid+'">'),1)
  self.assertIn('data-company="ultra_games" data-first-year="1990"',(ROOT/'index.html').read_text())
