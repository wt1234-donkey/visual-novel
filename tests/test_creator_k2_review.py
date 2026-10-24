"""K2 resolves two historical companies without extrapolating development."""
import json
import subprocess
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='ee2cb4aff414842d17946462571dc2f33586e72a'
def read(p):return json.loads((ROOT/p).read_text())
def old(p):return json.loads(subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT))
class CreatorK2Tests(unittest.TestCase):
    def test_exact_identity_delta_and_no_new_roles(self):
        b,a=old('data/entities.json'),read('data/entities.json')
        be={e['id']:e for e in b['entities']};ae={e['id']:e for e in a['entities']}
        self.assertEqual(be.keys(),ae.keys())
        self.assertEqual({k for k in be if be[k]!=ae[k]},{'entity-name-d045c5d84903','entity-name-3a59ff4a4f09'})
        self.assertEqual(a['relations'],b['relations'])
        self.assertEqual(read('data/credits.json'),old('data/credits.json'))
        for k in ['entity-key','entity-koei_tecmo']:self.assertEqual(be[k],ae[k])
    def test_progress_and_catalogue_preservation(self):
        p=read('data/organizations.json')['registrationProgress']
        self.assertEqual((p['letterProcessed'],p['letterTotal'],len(p['processedEntityIds']),p['total'],p['nextEntityId']),(10,14,147,151,'entity-koei'))
        self.assertEqual(p['processedEntityIds'][-4:],[e['entityId'] for e in read('data/entity-creator-k2-review-20261024.json')['reviewedEntities']])
        for f in ['data/games.json','data/company-coverage.json','data/taxonomy.json','data/entity-migration-baseline.json','data/content-migration-baseline.json']:self.assertEqual(read(f),old(f),f)
        self.assertEqual(read('data/organizations.json')['works'],old('data/organizations.json')['works'])
