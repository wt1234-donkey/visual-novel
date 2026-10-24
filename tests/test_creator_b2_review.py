"""B2 changes two identities while preserving scoped release credits and work objects."""
import json
import subprocess
import unittest
from pathlib import Path
from creator_snapshot import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
BASE = '25dbfb53406b05a00e3bd6fe4df6ad6bdd2e1c69'

def read(path):
    return load_snapshot(ROOT, path)

def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))

class CreatorB2Tests(unittest.TestCase):
    def test_only_two_sourced_identity_corrections(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        b, a = {e['id']: e for e in before['entities']}, {e['id']: e for e in after['entities']}
        expected = {'entity-name-c45d1636d3b0': 'brand', 'entity-name-91ab620ad791': 'company'}
        self.assertTrue(set(expected) <= {eid for eid in b if b[eid] != a[eid]})
        for eid, kind in expected.items():
            self.assertEqual((a[eid]['type'], a[eid]['verification']), (kind, 'sourceReviewed'))
            self.assertEqual(a[eid]['aliases'], b[eid]['aliases'])
            self.assertEqual(a[eid]['dates'], b[eid]['dates'])
        self.assertEqual(a['entity-blissbrain'], b['entity-blissbrain'])
        previous, current = old('data/credits.json'), read('data/credits.json')
        prior = {c['id']: c for c in previous['credits']}
        self.assertEqual(prior, {c['id']: c for c in current['credits'] if c['id'] in prior})

    def test_queue_and_scopes(self):
        org = read('data/organizations.json')
        p = org['registrationProgress']
        snapshot = read('data/entity-creator-b2-review-20261023.json')['progress']
        self.assertEqual((len(snapshot['processedEntityIds']), snapshot['total']), (6, 10))
        self.assertEqual(snapshot['nextEntityId'], 'entity-name-cb3c445f13f2')
        self.assertEqual(p['processedEntityIds'][32:38], snapshot['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'], [r['entityId'] for r in p['reviewedEntities']])
        self.assertEqual(org['works'], old('data/organizations.json')['works'])
        old_nodes = {n['id']: n for n in old('data/organizations.json')['nodes']}
        nodes = {n['id']: n for n in org['nodes']}
        for eid in ['entity-name-c45d1636d3b0', 'entity-blissbrain', 'entity-name-91ab620ad791']:
            self.assertEqual(nodes[eid]['groups'], old_nodes[eid]['groups'])
            self.assertEqual(nodes[eid]['productionCount'], old_nodes[eid]['productionCount'])

    def test_core_baselines_unchanged(self):
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/work-classification.json', 'data/entity-migration-baseline.json',
                     'data/content-migration-baseline.json', 'index.html', 'app.mjs',
                     'filter.mjs', 'styles.css', 'data/entity-creator-b1-review-20261023.json']:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)

if __name__ == '__main__':
    unittest.main()
