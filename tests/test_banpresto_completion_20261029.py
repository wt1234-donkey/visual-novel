"""ADV/RPG expansion preserves identities and distinguishes the later game label."""
import copy,json,re,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import build_entity_model as builder
BASE='42d02604a6648be5d512b607d902292c4ac587e4'
REVIEW='data/banpresto-source-review-20261029.json'
def read(p):return json.loads((ROOT/p).read_text())
def old(p):return json.loads(subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT))
def company(d):return next(c for c in d['companies'] if c['id']=='banpresto')
class BanprestoCompletionTests(unittest.TestCase):
 def test_main_append_and_other_dossiers_preserved(self):
  a,b=read('data/games.json'),old('data/games.json')
  for field,n in [('works',4),('contentVersions',4),('platformReleases',4)]:
   self.assertEqual(a[field][:len(b[field])],b[field]);self.assertEqual(len(a[field])-len(b[field]),n)
  a,b=read('data/company-coverage.json'),old('data/company-coverage.json')
  self.assertEqual([c for c in a['companies'] if c['id']!='banpresto'],[c for c in b['companies'] if c['id']!='banpresto'])
  for p in ['data/taxonomy.json','data/entity-banpresto-review-20261027.json','data/entity-migration-baseline.json','data/content-migration-baseline.json','data/banpresto-rpg-history.json']:self.assertEqual(read(p),old(p))
 def test_restore_archived_objects_without_new_identity(self):
  co=company(read('data/company-coverage.json'));archive=read('data/banpresto-rpg-history.json')['relatedGames'];active={w['id']:w for w in co['relatedGames']}
  self.assertEqual(len(co['workIds']),25);self.assertEqual(len(active),49)
  for w in archive:self.assertEqual(active[w['id']],w)
  new=read(REVIEW)['newWorkIds'];self.assertEqual(len(new),44);self.assertEqual(len(set(new)),44)
  self.assertFalse(set(new)&{w['id'] for w in archive})
 def test_debuts_and_simultaneous_platform_content(self):
  co=company(read('data/company-coverage.json'));ws={w['id']:w for w in co['relatedGames']}
  for wid in ['banpresto-accel1','banpresto-accel2']:
   w=ws[wid];self.assertEqual(len(w['contentVersions']),1);self.assertEqual(len(w['platformReleases']),2)
   self.assertEqual({r['contentVersionId'] for r in w['platformReleases']},{w['contentVersions'][0]['id']})
   self.assertEqual({r['platform'] for r in w['platformReleases']},{'PlayStation 3','PlayStation Portable'})
   self.assertEqual({r['publisher'] for r in w['platformReleases']},{'バンダイナムコゲームス'})
  for wid in read(REVIEW)['newWorkIds']:
   rs=ws[wid]['platformReleases'] if wid in ws else [r for r in read('data/games.json')['platformReleases'] if r['workId']==wid]
   self.assertTrue(all(r['releaseRole']=='contentDebut' and r['contentRelation']=='original' for r in rs))
 def test_publisher_scope_and_brand_do_not_collapse(self):
  es={e['id']:e for e in read('data/entities.json')['entities']};oldes={e['id']:e for e in old('data/entities.json')['entities']}
  self.assertEqual(set(es)-set(oldes),{'entity-banpresto-game-label'})
  for eid,e in oldes.items():self.assertEqual(es[eid],e)
  cr=read('data/credits.json')['credits'];label=[x for x in cr if x['entityId']=='entity-banpresto-game-label']
  self.assertEqual({x['targetId'] for x in label},{'banpresto-accel1-v-original-1','banpresto-accel1-v-original-2'})
  self.assertTrue(all(x['role']=='publishingBrand' for x in label))
  self.assertFalse(any(x['entityId']=='entity-banpresto' and x['workId'].startswith('banpresto-accel') for x in cr))
  for x in read(REVIEW)['scopedPublisherResolutions']:
   self.assertTrue(any(c['targetId']==x['releaseId'] and c['entityId']==x['entityId'] and c['role']=='publisher' for c in cr))
 def test_unreviewed_or_changed_historical_release_is_rejected(self):
  original=builder.read
  for change in ['drop','change','successor','duplicate']:
   manifest=copy.deepcopy(read(REVIEW));rows=manifest['historicalPublisherAdditions']
   if change=='drop':rows.pop()
   elif change=='change':rows[0]['release']['platform']='wrong'
   elif change=='successor':rows[0]['release']['year']=2012
   else:rows.append(copy.deepcopy(rows[0]))
   with self.subTest(change=change),patch.object(builder,'read',side_effect=lambda p:manifest if p==REVIEW else original(p)):
    with self.assertRaises(AssertionError):builder.build()
 def test_appendix_links_and_single_anchors(self):
  page=(ROOT/'banpresto.html').read_text();ids=re.findall(r'\bid="([^"]+)"',page)
  self.assertEqual(len(ids),len(set(ids)));self.assertEqual(page.count('<article class="card"'),74)
  self.assertIn('elf.html#elf-r14',page);self.assertIn('nitroplus.html#nitroplus-extra-madoka-portable',page)
  self.assertIn('万普）的游戏及游戏类型清单',page)
  for wid in read(REVIEW)['restoredWorkIds']:self.assertEqual(ids.count(wid),1)
  self.assertTrue(all(w['interactionModes']==['待核实'] for w in company(read('data/company-coverage.json'))['relatedGames'] if w['id'] in read(REVIEW)['interactionPendingWorkIds']))
