"""K3 scopes two originals and preserves unrelated publisher memberships."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes
ROOT=Path(__file__).resolve().parents[1]
SNAPSHOT='cf0d917d25c2dd281c91b80df851130e63263e0d'
BASE='ed957dbf835749edd56aba54eec944a143f22a2d'
def read(p):
    if p in {"data/entities.json", "data/credits.json", "data/organizations.json"}:
        return json.loads(subprocess.check_output(["git", "show", f"{SNAPSHOT}:{p}"], cwd=ROOT))
    return json.loads(catalogue_bytes(ROOT, p).decode())
def old(p):return json.loads(subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT))
class CreatorK3Tests(unittest.TestCase):
    def test_one_identity_and_two_originals(self):
        b,a=old('data/entities.json'),read('data/entities.json')
        be={e['id']:e for e in b['entities']};ae={e['id']:e for e in a['entities']}
        self.assertEqual(be.keys(),ae.keys())
        self.assertEqual({k for k in be if be[k]!=ae[k]},{'entity-name-9e2d0b1695d0'})
        self.assertEqual(a['relations'],b['relations'])
        before,after=old('data/credits.json'),read('data/credits.json')
        self.assertEqual(after['credits'][:-2],before['credits'])
        self.assertEqual([(c['entityId'],c['workId'],c['role']) for c in after['credits'][-2:]], [('entity-name-9e2d0b1695d0','ascii-haja','originalProduction'),('entity-konami','g040','originalProduction')])
        bm={(m['dossierId'],m['workId']):m for m in before['dossierMemberships']}
        am={(m['dossierId'],m['workId']):m for m in after['dossierMemberships']}
        self.assertEqual(bm.keys(),am.keys())
        self.assertEqual({k for k in bm if bm[k]!=am[k]}, {('konami','g040')})
        self.assertEqual(am['ascii','ascii-haja']['status'],'pendingRole')
    def test_complete_k_and_preserve_catalogue(self):
        p=read('data/organizations.json')['registrationProgress']
        self.assertEqual((p['letterProcessed'],p['letterTotal'],len(p['processedEntityIds']),p['total'],p['nextEntityId']),(14,14,151,151,'entity-laplacian'))
        self.assertEqual(p['processedEntityIds'][-4:],[e['entityId'] for e in read('data/entity-creator-k3-review-20261025.json')['reviewedEntities']])
        self.assertTrue(all(q['status']=='reviewed' for q in p['queue']))
        for f in ['data/games.json','data/company-coverage.json','data/taxonomy.json','data/entity-migration-baseline.json','data/content-migration-baseline.json']:self.assertEqual(read(f),old(f),f)
        self.assertEqual(read('data/organizations.json')['works'],old('data/organizations.json')['works'])
