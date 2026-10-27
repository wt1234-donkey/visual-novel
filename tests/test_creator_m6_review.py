"""M6 preserves composite signatures and publisher/developer boundaries."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = 'f7ddbcc5de7eda9850b4433cf84dcdcb79d83f06'
BASE = 'e36c64d55f928d8655262aa8310b3222e565ec77'


def read(path):
    if path in {"data/entities.json", "data/credits.json", "data/organizations.json"}:
        return json.loads(subprocess.check_output(["git", "show", f"{SNAPSHOT}:{path}"], cwd=ROOT))
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorM6Tests(unittest.TestCase):
    def test_exact_two_companies_without_merging_names_or_resolving_composite(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be = {e['id']: e for e in before['entities']}
        ae = {e['id']: e for e in after['entities']}
        expected = {'entity-name-935c3bc35045', 'entity-name-170eeb0b71f8'}
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, expected)
        for eid in expected:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), ('company', 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates']:
                self.assertEqual(be[eid][field], ae[eid][field])
        self.assertEqual(ae['entity-name-588f588386f3'], be['entity-name-588f588386f3'])
        self.assertEqual(ae['entity-name-588f588386f3']['type'], 'unknown')
        self.assertEqual(ae['entity-mosaic'], be['entity-mosaic'])
        self.assertEqual(after['relations'], before['relations'])

    def test_only_child_brand_credit_is_added_without_parent_membership_changes(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-1], before['credits'])
        credit = after['credits'][-1]
        self.assertEqual((credit['entityId'], credit['workId'], credit['role'], credit['targetType'],
                          credit['rawCredit'], credit['status']),
                         ('entity-fairytale_tsuki', 'g792', 'productionBrand', 'work',
                          '月星組/フェアリーテール', 'sourceReviewed'))
        self.assertEqual(after['dossierMemberships'], before['dossierMemberships'])
        parent = next(m for m in after['dossierMemberships']
                      if (m['dossierId'], m['workId']) == ('fairytale', 'g792'))
        self.assertEqual(parent['status'], 'pendingRole')
        moe = [c for c in after['credits'] if c['entityId'] == 'entity-name-588f588386f3']
        self.assertEqual(len(moe), 8)
        self.assertTrue(all(c['role'] == 'publisher' and c['targetType'] == 'release' for c in moe))

    def test_completed_m_progress_and_protected_catalogue(self):
        p = read('data/organizations.json')['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('M', 30, 30, 193, 193, 'entity-nanawind'))
        review = read('data/entity-creator-m6-review-20261025.json')
        self.assertEqual(p['processedEntityIds'][-5:], [e['entityId'] for e in review['reviewedEntities']])
        queue = review['progress']['queue']
        self.assertEqual([e['name'].lower() for e in queue], sorted(e['name'].lower() for e in queue))
        self.assertTrue(all(e['status'] == 'reviewed' for e in queue))
        self.assertEqual(p['nextName'], 'NanaWind')
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        self.assertEqual(read('data/organizations.json')['works'], old('data/organizations.json')['works'])
