"""A5 audit: ASCII through Atlus, with additive credits and identity-only corrections."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '456057a36fb14202a7b2072c24a6261e031d2e44'

def read(path):
    return json.loads((ROOT / path).read_text())

def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))

class CreatorA5ReviewTests(unittest.TestCase):
    def test_three_ascii_additions_preserve_old_credits(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        b = {c['id']: c for c in before['credits']}
        a = {c['id']: c for c in after['credits']}
        self.assertTrue(b.keys() <= a.keys())
        for cid in b:
            self.assertEqual(a[cid], b[cid], cid)
        added = [a[cid] for cid in a.keys() - b.keys()]
        expected = {('entity-ascii', 'g1003', 'originalProduction'),
                    ('entity-ascii', 'g1004', 'originalProduction'),
                    ('entity-ascii', 'ascii-chaos-angels', 'originalProduction')}
        self.assertEqual(len(added), 3)
        self.assertEqual({(c['entityId'], c['workId'], c['role']) for c in added}, expected)
        review = read('data/entity-creator-a5-review-20261023.json')
        self.assertEqual({(c['entityId'], c['workId'], c['source']) for c in added},
                         {(c['entityId'], c['workId'], c['source']) for c in review['creditAdditions']})
        for c in added:
            self.assertEqual(c['targetType'], 'work')
            self.assertEqual(c['status'], 'sourceReviewed')
            self.assertEqual(c['reviewRecord'], review['audit'])

    def test_identity_corrections_do_not_change_release_roles(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        b = {e['id']: e for e in before['entities']}
        a = {e['id']: e for e in after['entities']}
        changed = {eid for eid in b if b[eid] != a[eid]}
        ids = {'entity-name-9590651f2922', 'entity-name-03ca146bb18c', 'entity-name-6cafab111889'}
        self.assertTrue(ids <= changed)
        for eid in ids:
            self.assertEqual(a[eid]['type'], 'company')
            self.assertEqual(a[eid]['verification'], 'sourceReviewed')
            self.assertEqual(a[eid]['aliases'], b[eid]['aliases'])
            self.assertEqual(a[eid]['dates'], b[eid]['dates'])
        before, after = old('data/entity-migration-review.json'), read('data/entity-migration-review.json')
        self.assertEqual(after['pendingMembershipCount'], 611)
        self.assertEqual(after['pendingIdentities'], [e for e in before['pendingIdentities'] if e['entityId'] not in ids and e['entityId'] not in {'entity-name-a7f6066af4b9', 'entity-name-4b075a5bed09'}])

    def test_progress_and_placements(self):
        org, review = read('data/organizations.json'), read('data/entity-creator-a5-review-20261023.json')
        progress = org['registrationProgress']
        self.assertEqual(progress['processedEntityIds'][:30], review['progress']['processedEntityIds'])
        self.assertEqual(review['progress']['nextEntityId'], 'entity-august')
        self.assertEqual([e['entityId'] for e in progress['reviewedEntities']], progress['processedEntityIds'])
        self.assertIn(review['audit'], progress['audits'])
        nodes = {n['id']: n for n in org['nodes']}
        self.assertEqual({w['workId'] for w in nodes['entity-ascii']['groups']['creation'] if w['workId'] in {'g1003','g1004'}}, {'g1003','g1004'})
        self.assertIn('ascii-chaos-angels', {w['workId'] for w in nodes['entity-ascii']['groups']['creation']})
        self.assertEqual(nodes['entity-ascii']['productionCount'], 2)
        self.assertEqual(nodes['entity-name-9590651f2922']['groups'], old('data/organizations.json')['nodes'][next(i for i,n in enumerate(old('data/organizations.json')['nodes']) if n['id']=='entity-name-9590651f2922')]['groups'])

    def test_core_work_objects_and_previous_reviews_unchanged(self):
        paths = ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                 'data/gameplay-catalogues.json', 'data/work-classification.json',
                 'data/entity-migration-baseline.json', 'data/content-migration-baseline.json',
                 'index.html', 'app.mjs', 'filter.mjs', 'styles.css']
        paths += [f'data/entity-creator-a{suffix}-review-20261023.{ext}' for suffix in ['4'] for ext in ['json','md']]
        for path in paths:
            self.assertEqual((ROOT / path).read_bytes(), subprocess.check_output(['git','show',f'{BASE}:{path}'], cwd=ROOT), path)

if __name__ == '__main__':
    unittest.main()
