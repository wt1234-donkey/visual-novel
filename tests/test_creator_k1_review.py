"""K1 changes four categories without merging historical or composite nodes."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes
ROOT=Path(__file__).resolve().parents[1]
SNAPSHOT='ee2cb4aff414842d17946462571dc2f33586e72a'
BASE='ce97df0ef44facab882b5baf55c5fcae077a2b89'
def read(p):
    if p in {"data/entities.json", "data/credits.json", "data/organizations.json"}:
        return json.loads(subprocess.check_output(["git", "show", f"{SNAPSHOT}:{p}"], cwd=ROOT))
    return json.loads(catalogue_bytes(ROOT, p).decode())
def old(p):return json.loads(subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT))
class CreatorK1Tests(unittest.TestCase):
    def test_only_four_identity_categories(self):
        b,a=old('data/entities.json'),read('data/entities.json')
        be={e['id']:e for e in b['entities']};ae={e['id']:e for e in a['entities']}
        self.assertEqual(be.keys(),ae.keys())
        ids={c['entityId'] for c in read('data/entity-creator-k1-review-20261024.json')['identityCorrections']}
        self.assertEqual(len(ids),4)
        self.assertEqual({k for k in be if be[k]!=ae[k]},ids)
        self.assertTrue(all(ae[k]['type']=='company' for k in ids))
        self.assertEqual(a['relations'],b['relations'])
        self.assertEqual(read('data/credits.json'),old('data/credits.json'))
        for k in ['entity-name-82fc3d1bfdaa','entity-name-0f93dc471cd5']:
            self.assertEqual(ae[k],be[k])
    def test_queue_and_protected_catalogue(self):
        p=read('data/organizations.json')['registrationProgress']
        self.assertEqual((p['letter'],p['letterProcessed'],p['letterTotal'],len(p['processedEntityIds']),p['total'],p['nextEntityId']),('K',6,14,143,151,'entity-name-d045c5d84903'))
        self.assertEqual(p['processedEntityIds'][-6:],[e['entityId'] for e in read('data/entity-creator-k1-review-20261024.json')['reviewedEntities']])
        for f in ['data/games.json','data/company-coverage.json','data/taxonomy.json','data/entity-migration-baseline.json','data/content-migration-baseline.json']:
            self.assertEqual(read(f),old(f),f)
        self.assertEqual(read('data/organizations.json')['works'],old('data/organizations.json')['works'])
