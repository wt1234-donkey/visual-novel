"""P2 keeps personal authorship, brand publishing and port work in separate scopes."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
BASE = '2e12fdb62250aed0fe483391ff09850fe20493e4'
PONY = 'entity-name-e8f2daf6c0f9'
PRINCESS = 'entity-name-e853d08ed1b6'
PSI = 'entity-name-cd9fca98a5c2'


def read(path):
    if path in {'data/entities.json', 'data/credits.json', 'data/organizations.json'}:
        return json.loads(subprocess.check_output(['git', 'show', f'172ad9c4edd2e7e5459f02fa9055381ecd8cb9f9:{path}'], cwd=ROOT))
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorP2Tests(unittest.TestCase):
    def test_three_scoped_identities_keep_names_aliases_dates_and_relationships(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {PONY, PRINCESS, PSI})
        for eid, kind in [(PONY, 'company'), (PRINCESS, 'brand'), (PSI, 'individual')]:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), (kind, 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(ae['entity-name-fb8b690c85a0'], be['entity-name-fb8b690c85a0'])
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        review = read('data/entity-creator-p2-review-20261025.json')
        self.assertIs(review['identityCorrections'][1]['preserveReleaseRoles'], True)

    def test_one_personal_original_credit_preserves_all_old_platform_and_brand_roles(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-1], before['credits'])
        c = after['credits'][-1]
        self.assertEqual((c['entityId'], c['targetType'], c['targetId'], c['workId'], c['role'],
                          c['rawCredit'], c['status']),
                         (PSI, 'work', 'g970', 'g970', 'originalProduction', 'Psionic', 'sourceReviewed'))
        self.assertEqual(c['source'], 'https://retrovandal.itch.io/')
        self.assertEqual(len(after['credits']), 4958)
        for eid, count in [(PONY, 3), (PRINCESS, 2), ('entity-prototype', 37)]:
            scoped = [c for c in after['credits'] if c['entityId'] == eid]
            self.assertEqual(len(scoped), count)
            self.assertTrue(all(c['targetType'] == 'release' and c['role'] == 'publisher' for c in scoped))
        pride = [c for c in after['credits'] if c['entityId'] == 'entity-pride']
        self.assertEqual({c['role'] for c in pride}, {'publishingBrand', 'originalPublishingBrand'})

    def test_all_memberships_and_catalogue_objects_are_unchanged(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(before['dossierMemberships'], after['dossierMemberships'])
        self.assertEqual(len(after['dossierMemberships']), 2234)
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in after['dossierMemberships']), 604)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)

    def test_p_order_retains_evidence_gaps_and_next_psk(self):
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'], len(p['processedEntityIds']),
                          p['total'], p['nextEntityId']), ('P', 10, 13, 228, 231, 'entity-psk'))
        self.assertEqual(p['processedEntityIds'][:-5], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-5:], [PONY, 'entity-pride', PRINCESS, 'entity-prototype', PSI])
        review = read('data/entity-creator-p2-review-20261025.json')
        self.assertEqual([q['status'] for q in review['progress']['queue']], ['reviewed'] * 10 + ['pending'] * 3)
        self.assertEqual([d['entityId'] for d in review['deferredReviews']],
                         [PONY, 'entity-pride', PRINCESS, 'entity-prototype'])
        nodes = {n['id']: n for n in after['nodes']}
        self.assertEqual((nodes[PSI]['type'], nodes[PSI]['productionCount']), ('individual', 1))
        self.assertEqual(nodes['entity-prototype']['productionCount'], 0)
        self.assertEqual(after['works'], before['works'])
