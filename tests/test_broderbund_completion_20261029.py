"""Brøderbund shared identities, first batches, parser boundary and later Red Orb label."""
import copy,json,re,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import validate_entity_model as validator
BASE='2c1e3874d369da741c42ef909bfcc5e24a6570c2'
def read(p):return json.loads((ROOT/p).read_text())
def old(p):return json.loads(subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT))
def company(d):return next(c for c in d['companies'] if c['id']=='broderbund')
class BroderbundCompletionTests(unittest.TestCase):
 def test_append_only_shared_database_and_other_dossiers(self):
  a,b=read('data/games.json'),old('data/games.json')
  for field,n in [('works',6),('contentVersions',6),('platformReleases',7)]:
   bm={x['id']:x for x in b[field]};am={x['id']:x for x in a[field]}
   self.assertEqual({i:am[i] for i in bm},bm);self.assertEqual(len(am)-len(bm),n+len(read('data/non-rpg-intake-18-studios-result.json')['added']))
  a,b=read('data/company-coverage.json'),old('data/company-coverage.json')
  self.assertEqual([c for c in a['companies'] if c['id']!='broderbund'],[c for c in b['companies'] if c['id']!='broderbund'])
  for p in ['data/content-migration-baseline.json','data/entity-migration-baseline.json','data/taxonomy.json']:self.assertEqual(read(p),old(p))
 def test_riven_reuses_work_and_content_and_preserves_enix_and_pending_remake(self):
  g=read('data/games.json');co=company(read('data/company-coverage.json'))
  self.assertIn('g1001',co['workIds']);self.assertEqual(len([w for w in g['works'] if 'riven' in w['originalTitle'].casefold()]),1)
  rs=[r for r in g['platformReleases'] if r['workId']=='g1001'];self.assertEqual(len(rs),3)
  self.assertEqual(rs[-1]['contentVersionId'],'g1001-c-original');self.assertEqual(rs[-1]['publisher'],'Brøderbund');self.assertEqual(rs[0]['publisher'],'エニックス')
  self.assertEqual(rs[1]['contentVersionId'],None);self.assertEqual(rs[1]['contentRelation'],'unverified')
  self.assertEqual([c for c in g['contentVersions'] if c['workId']=='g1001'],[c for c in old('data/games.json')['contentVersions'] if c['workId']=='g1001'])
 def test_first_batches_and_input_bibliography(self):
  co=company(read('data/company-coverage.json'));self.assertEqual((len(co['workIds']),len(co['relatedGames']),len(co['dossierOnlyWorks'])),(10,1,8))
  oldco=company(old('data/company-coverage.json'));self.assertEqual(co['dossierOnlyWorks'][:2],oldco['dossierOnlyWorks'])
  ids=read('data/broderbund-source-review-20261029.json')['newBibliographyWorkIds']
  self.assertEqual(len(ids),6)
  for w in co['dossierOnlyWorks']:
   self.assertIn('文字输入',w['interactionModes']);self.assertNotIn('platformReleases',w);self.assertNotIn('contentVersions',w)
  cy=next(w for w in co['dossierOnlyWorks'] if w['id']=='broderbund-cyborg');self.assertEqual(cy['firstYear'],1981);self.assertIn('复句',cy['interactionNote'])
  uk=next(w for w in co['dossierOnlyWorks'] if w['id']=='broderbund-uukrul');self.assertIn('传送地点',uk['interactionNote'])
  cent=co['relatedGames'][0];self.assertEqual(cent['firstYear'],1990);self.assertNotIn('文字输入',cent['interactionModes']);self.assertIn('五字母',cent['interactionNote'])
  self.assertTrue(all(r['releaseRole']=='contentDebut' for r in cent['platformReleases']))
 def test_red_orb_publisher_and_later_region_do_not_become_old_company_development(self):
  e=read('data/entities.json');es={x['id']:x for x in e['entities']};self.assertEqual(es['entity-red-orb']['type'],'brand')
  oldes={x['id']:x for x in old('data/entities.json')['entities']}
  self.assertTrue(all(r in e['relations'] for r in old('data/entities.json')['relations']))
  for i,old_entity in oldes.items():
   current=es[i].copy();self.assertTrue(set(old_entity.get('sources',[]))<=set(current.get('sources',[])))
   current['sources']=old_entity.get('sources',[]);self.assertEqual(current,old_entity)
  co=next(c for c in e['dossiers'] if c['id']=='broderbund');self.assertEqual(co['dossierType'],'history');self.assertIn('entity-red-orb',co['entityIds'])
  g=read('data/games.json');self.assertEqual(next(r for r in g['platformReleases'] if r['workId']=='g1340')['publisher'],'Red Orb Entertainment');self.assertEqual(next(r for r in g['platformReleases'] if r['workId']=='g1342')['publisher'],'Cryo Interactive Entertainment')
  cr=read('data/credits.json');ed=next(e for e in cr['scopedEditions'] if e['id']=='broderbund-ring-redorb-us-1999');self.assertEqual(ed['actualPublisher'],'Mindscape, Inc.');self.assertIsNone(ed['contentVersionId']);self.assertNotIn(ed['id'],{r['id'] for r in g['platformReleases']})
  label=next(c for c in cr['credits'] if c['targetId']==ed['id']);self.assertEqual((label['entityId'],label['role']),('entity-red-orb','publishingBrand'))
  self.assertFalse(any(c['entityId']=='entity-name-e0c32a99a906' and c['workId'] in {'g1340','g1342'} for c in cr['credits']))
 def test_scoped_brand_requires_matching_identity_and_review(self):
  original=validator.read
  for change in ['identity','raw','review']:
   c=copy.deepcopy(read('data/credits.json'));x=next(x for x in c['credits'] if x['targetId']=='broderbund-ring-redorb-us-1999')
   if change=='identity':x['entityId']='entity-name-e0c32a99a906'
   elif change=='raw':x['rawCredit']='wrong'
   else:x.pop('reviewRecord')
   with self.subTest(change=change),patch.object(validator,'read',side_effect=lambda p:c if p=='data/credits.json' else original(p)):
    with self.assertRaises(AssertionError):validator.validate()
 def test_reference_table_completeness_cross_links_and_anchors(self):
  p=(ROOT/'broderbund.html').read_text();ids=re.findall(r'\bid="([^"]+)"',p);self.assertEqual(len(ids),len(set(ids)));self.assertEqual(p.count('<article class="card"'),19)
  a=read('data/gameplay-catalogues.json')['companies']['broderbund'];self.assertEqual(len(a['groups'][0]['rows']),18);self.assertEqual(sum(len(g['rows']) for g in a['groups']),33)
  refs=[r['workId'] for g in a['groups'] for r in g['rows'] if 'workId' in r];self.assertEqual(len(refs),len(set(refs)));self.assertEqual(len(refs),19)
  for link in ['legend_entertainment.html#legend-entertainment-blackstone','riverhill_soft.html#riverhill-prince','falcom.html#falcom-ys1','riverhill_soft.html#g942']:self.assertIn(link,p)
  self.assertNotIn('万普）的游戏及游戏类型清单',p);self.assertIn('Brøderbund的游戏及游戏类型清单',p)
