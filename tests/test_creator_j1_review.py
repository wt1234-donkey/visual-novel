"""J1 keeps three JAST identities separate and adds one documented original."""
import json
import subprocess
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SNAPSHOT='ce97df0ef44facab882b5baf55c5fcae077a2b89'
BASE='310ae9e9f6625fa3b8b17931da73ab7286cb4433'
def read(p):
    if p in {"data/entities.json", "data/credits.json", "data/organizations.json"}:
        return json.loads(subprocess.check_output(["git", "show", f"{SNAPSHOT}:{p}"], cwd=ROOT))
    return json.loads((ROOT/p).read_text())
def old(p):
    return json.loads(subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT))
class CreatorJ1Tests(unittest.TestCase):
    def test_exact_scoped_delta(self):
        b,a=old('data/entities.json'),read('data/entities.json')
        be={e['id']:e for e in b['entities']};ae={e['id']:e for e in a['entities']}
        self.assertEqual(be.keys(),ae.keys())
        self.assertEqual({k for k in be if be[k]!=ae[k]}, {'entity-name-251c0991e4f6','entity-name-8e61b50010ed'})
        self.assertEqual(a['relations'],b['relations'])
        before,after=old('data/credits.json'),read('data/credits.json')
        self.assertEqual(after['credits'][:-1],before['credits'])
        c=after['credits'][-1]
        self.assertEqual((c['entityId'],c['workId'],c['targetType'],c['role'],c['reviewId']),('entity-jast','g015','work','originalProduction','AZJ1-C01'))
        bm={(m['dossierId'],m['workId']):m for m in before['dossierMemberships']}
        am={(m['dossierId'],m['workId']):m for m in after['dossierMemberships']}
        self.assertEqual(bm.keys(),am.keys())
        self.assertEqual({k for k in bm if bm[k]!=am[k]}, {('jast','g015')})
    def test_progress_and_protected_data(self):
        p=read('data/organizations.json')['registrationProgress']
        self.assertEqual((p['letter'],p['letterProcessed'],p['letterTotal'],len(p['processedEntityIds']),p['total'],p['nextName']),('J',5,5,137,137,'KADOKAWA'))
        self.assertEqual(p['processedEntityIds'][-5:],[e['entityId'] for e in read('data/entity-creator-j1-review-20261024.json')['reviewedEntities']])
        for f in ['data/games.json','data/company-coverage.json','data/taxonomy.json','data/entity-migration-baseline.json','data/content-migration-baseline.json']:
            self.assertEqual(read(f),old(f),f)
        self.assertEqual(read('data/organizations.json')['works'],old('data/organizations.json')['works'])
