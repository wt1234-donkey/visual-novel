"""S7 separates historical identity corrections from production and releases."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
BASE = '05b37582360b81dc26c6c5b691e0325fc065d1c3'
REVIEW = 'data/entity-creator-s7-review-20261026.json'
IDS = ['entity-name-539be8af5be9', 'entity-name-8865f66ec578',
       'entity-name-ffa62a4c6281', 'entity-sorahane', 'entity-sphere']


def read(path):
    return json.loads(catalogue_bytes(ROOT, path).decode())


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json']:
        return json.loads(subprocess.check_output(['git', 'show', f'712383317f0cab13cc903a328f986f523ee91bf8:{path}'], cwd=ROOT))
    return read(path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorS7Tests(unittest.TestCase):
    def test_exactly_three_company_identities_change_and_sony_nodes_stay_distinct(self):
        before, after = old('data/entities.json'), applied('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, set(IDS[:3]))
        for eid in IDS[:3]:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), ('company', 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual(len(ae), 326)
        self.assertEqual(sum(e['verification'] == 'unresolved' for e in ae.values()), 65)
        self.assertEqual([x['rawName'] for x in read(REVIEW)['identityCorrections']],
                         ['Sol Press', 'Sony Computer Entertainment', 'ソニー・コンピュータエンタテインメント'])

    def test_all_credits_versions_memberships_and_baselines_are_preserved(self):
        for path in ['data/credits.json', 'data/games.json', 'data/company-coverage.json',
                     'data/taxonomy.json', 'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/content-migration-baseline.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(applied(path), old(path), path)
        c = applied('data/credits.json')
        self.assertEqual((len(c['credits']), len(c['dossierMemberships'])), (4986, 2234))
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in c['dossierMemberships']), 602)
        for eid, count in zip(IDS[:3], [3, 3, 1]):
            rows = [r for r in c['credits'] if r['entityId'] == eid]
            self.assertEqual(len(rows), count)
            self.assertTrue(all(r['role'] == 'publisher' and r['targetType'] == 'release' for r in rows))
        for eid, count in zip(IDS[3:], [3, 4]):
            self.assertEqual(sum(r['entityId'] == eid and r['role'] == 'productionBrand'
                                 for r in c['credits']), count)
        self.assertEqual(read(REVIEW)['creditAdditions'], [])

    def test_five_consecutive_entities_advance_from_sol_press_to_spike(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('S', 28, 42, 265, 279, 'entity-name-6d5cd9b9dc38'))
        self.assertEqual(p['processedEntityIds'][:-5], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-5:], IDS)
        r = read(REVIEW)
        self.assertEqual([e['entityId'] for e in r['reviewedEntities']], IDS)
        self.assertEqual([e['entityId'] for e in r['deferredReviews']], IDS)
        self.assertEqual([q['status'] for q in r['progress']['queue']], ['reviewed'] * 28 + ['pending'] * 14)
        self.assertEqual(after['works'], before['works'])
        self.assertIn('sourceUnavailable'.lower(), r['reviewedEntities'][3]['status'].lower())
