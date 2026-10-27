"""I4 preserves historical credits while resolving only two legal identities."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes
ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = '310ae9e9f6625fa3b8b17931da73ab7286cb4433'
BASE = '25bc47deb8471e58f36f2667fb7d60734c0d8f44'
def read(p):
    if p in {"data/entities.json", "data/credits.json", "data/organizations.json"}:
        return json.loads(subprocess.check_output(["git", "show", f"{SNAPSHOT}:{p}"], cwd=ROOT))
    return json.loads(catalogue_bytes(ROOT, p).decode())
def old(p):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{p}'], cwd=ROOT))
class CreatorI4Tests(unittest.TestCase):
    def test_exact_identity_scope_and_preserved_roles(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        b = {e['id']:e for e in before['entities']}
        a = {e['id']:e for e in after['entities']}
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual({k for k in a if a[k] != b[k]},
                         {'entity-name-8447c5d78187','entity-name-8daa9d3fef6f'})
        self.assertEqual(after['relations'], before['relations'])
        self.assertEqual(read('data/credits.json'), old('data/credits.json'))
        self.assertEqual(a['entity-name-d7900289691e'], b['entity-name-d7900289691e'])
        for p in ['data/games.json','data/company-coverage.json','data/taxonomy.json',
                  'data/entity-migration-baseline.json','data/content-migration-baseline.json']:
            self.assertEqual(read(p), old(p), p)
    def test_completed_i_and_next_queue(self):
        p = read('data/organizations.json')['registrationProgress']
        self.assertEqual((p['letterProcessed'],p['letterTotal'],len(p['processedEntityIds']),
                          p['total'],p['nextName']), (13,13,132,132,'J. K. Greye Software'))
        self.assertTrue(all(q['status']=='reviewed' for q in p['queue']))
        self.assertEqual(read('data/organizations.json')['works'], old('data/organizations.json')['works'])
