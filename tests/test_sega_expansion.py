"""SEGA keeps its dossier identity while two narratives and scoped history are added."""
import json,subprocess,unittest
from pathlib import Path
from historical_paths import shared_paths
ROOT=Path(__file__).resolve().parents[1]
BASE='508efa3f228b7dc5ca52d1ecc086d813848462a4'
def read(p):return json.loads(subprocess.check_output(['git','show',f'd80510b343d53f61c0df6ad799466aaca55ea2f3:{p}'],cwd=ROOT))
def old(p):return json.loads(subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT))
class SegaExpansionTests(unittest.TestCase):
 def test_exact_two_original_narratives_preserve_all_old_objects(self):
  b,a=old('data/games.json'),read('data/games.json')
  for field,suffix in [('works',''),('contentVersions','-c-original'),('platformReleases','-v1')]:
   before={x['id']:x for x in b[field]};after={x['id']:x for x in a[field]}
   self.assertEqual(set(after)-set(before),{'g1281'+suffix,'g1282'+suffix});self.assertEqual({i:after[i] for i in before},before)
  ws={w['id']:w for w in a['works']}
  self.assertEqual(ws['g1281']['interactionModes'],['选项分支','限时反应']);self.assertEqual(ws['g1282']['interactionModes'],['选项分支'])
  self.assertTrue(all(r['platform']=='Dreamcast' and r['releaseRole']=='contentDebut' for r in a['platformReleases'][-2:]))
 def test_dossier_and_old_anchors_survive_without_another_sega_identity(self):
  b,a=old('data/company-coverage.json'),read('data/company-coverage.json')
  before={c['id']:c for c in b['companies']};after={c['id']:c for c in a['companies']};self.assertEqual(before.keys(),after.keys())
  self.assertEqual({i for i in before if before[i]!=after[i]},{'sega'})
  self.assertEqual(after['sega']['workIds'],before['sega']['workIds']+['g1281','g1282'])
  self.assertEqual(after['sega']['relatedGames'],before['sega']['relatedGames'])
  self.assertEqual(after['sega']['entries'][:len(before['sega']['entries'])],before['sega']['entries'])
  page=subprocess.check_output(['git','show','d80510b343d53f61c0df6ad799466aaca55ea2f3:sega.html'],cwd=ROOT,text=True);self.assertEqual(page.count('<article class="card"'),22)
  for wid in before['sega']['workIds']:self.assertIn('id="'+wid+'"',page)
 def test_formal_entities_and_credits_do_not_inherit_group_game_development(self):
  b,a=old('data/entities.json'),read('data/entities.json')
  before={e['id']:e for e in b['entities']};after={e['id']:e for e in a['entities']};self.assertEqual(before.keys(),after.keys())
  self.assertEqual({i for i in before if before[i]!=after[i]},{'entity-sega'})
  self.assertEqual({k for k in before['entity-sega'] if before['entity-sega'][k]!=after['entity-sega'][k]},{'historyNote'})
  self.assertEqual(a['relations'],b['relations'])
  bd={d['id']:d for d in b['dossiers']};ad={d['id']:d for d in a['dossiers']}
  self.assertEqual(bd.keys(),ad.keys());self.assertEqual({i for i in bd if bd[i]!=ad[i]},{'sega'})
  self.assertEqual({k for k in bd['sega'] if bd['sega'][k]!=ad['sega'][k]},{'scope'})
  b,a=old('data/credits.json'),read('data/credits.json');before={c['id']:c for c in b['credits']};after={c['id']:c for c in a['credits']}
  self.assertEqual({i:after[i] for i in before},before)
  self.assertEqual({(after[i]['entityId'],after[i]['targetId'],after[i]['role']) for i in set(after)-set(before)},{('entity-sega','g1281-v1','publisher'),('entity-sega','g1282-v1','publisher')})
 def test_preview_group_nodes_and_dates_are_scoped_to_original_sources(self):
  b,a=old('data/relationships-preview-config.json'),read('data/relationships-preview-config.json')
  self.assertEqual(a['previewNodes'][:-3],b['previewNodes']);self.assertEqual(a['previewEdges'][:-4],b['previewEdges'])
  self.assertTrue(all(n['previewOnly'] and not n['works'] for n in a['previewNodes'][-3:]))
  self.assertEqual([h['dateLabel'][:4] for h in a['nameHistory'][-4:]],['1965','2000','2015','2020'])
  self.assertTrue(all(h['fromId']==h['toId']=='entity-sega' for h in a['nameHistory'][-4:]))
  b,a=old('data/organizations.json'),read('data/organizations.json')
  self.assertEqual(a['verificationLedger'],b['verificationLedger']);self.assertEqual(a['organizationEvents'][:-7],b['organizationEvents'])
  family=next(f for f in a['families'] if f['id']=='sega')
  self.assertEqual((family['root'],family['focus']),('preview-sega-sammy','entity-sega'))
  self.assertEqual(set(family['entityIds']),{'preview-sega-sammy','preview-sega-group','preview-sega-interactive','entity-sega'})
  self.assertEqual([e['year'] for e in a['organizationEvents'][-7:]],[1960,1965,2000,2004,2015,2020,2021])
  self.assertIn('计划',a['organizationEvents'][-1]['note']);self.assertIn('确认',a['organizationEvents'][-1]['note'])
  self.assertEqual(a['unfinished']['counts'],{'identity':32,'duty':591,'creation':804,'evidence':481,'chronology':44,'relation':1})
 def test_frozen_evidence_and_migration_rules_stay_unchanged(self):
  for p in shared_paths(ROOT, BASE, 'd80510b343d53f61c0df6ad799466aaca55ea2f3', ['organization-context*.json','organization-verification*.json']):self.assertEqual(read(p),old(p))
  for p in ['data/taxonomy.json','data/entity-migration-baseline.json','data/content-migration-baseline.json']:
   self.assertEqual(read(p),old(p))
