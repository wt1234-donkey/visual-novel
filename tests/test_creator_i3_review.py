"""I3 limits Infocom originals and the historical Infogrames identity."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = '25bc47deb8471e58f36f2667fb7d60734c0d8f44'
BASE = 'c9b7398600cd385e8aabcc58fc8991ad23721446'


def read(path):
    if path in {'data/entities.json', 'data/credits.json', 'data/organizations.json'}:
        return json.loads(subprocess.check_output(['git', 'show', f'{SNAPSHOT}:{path}'], cwd=ROOT))
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorI3Tests(unittest.TestCase):
    def test_exact_identity_and_creative_credit_delta(self):
        review = read('data/entity-creator-i3-review-20261024.json')
        b, a = old('data/entities.json'), read('data/entities.json')
        before = {e['id']: e for e in b['entities']}
        after = {e['id']: e for e in a['entities']}
        self.assertEqual(before.keys(), after.keys())
        self.assertEqual({eid for eid in before if before[eid] != after[eid]},
                         {x['entityId'] for x in review['identityCorrections']})
        self.assertEqual(a['relations'], b['relations'])
        prior, current = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(current['credits'][:-3], prior['credits'])
        self.assertEqual([(c['entityId'], c['workId'], c['targetType'], c['role'], c['reviewId'])
                          for c in current['credits'][-3:]],
                         [('entity-infocom', wid, 'work', 'originalProduction', f'AZI3-C0{i}')
                          for i, wid in enumerate(['g002', 'g062', 'g063'], 1)])
        self.assertTrue(all(c['reviewRecord'] == review['audit'] for c in current['credits'][-3:]))
        bmem = {(m['dossierId'], m['workId']): m for m in prior['dossierMemberships']}
        amem = {(m['dossierId'], m['workId']): m for m in current['dossierMemberships']}
        self.assertEqual(bmem.keys(), amem.keys())
        self.assertEqual({key for key in bmem if bmem[key] != amem[key]},
                         {('infocom', wid) for wid in ['g002', 'g062', 'g063']})
        self.assertTrue(all(amem['infocom', wid]['group'] == 'original'
                            for wid in ['g002', 'g062', 'g063']))
        self.assertFalse(any(c['entityId'] == 'entity-name-c8ec85da2361' and
                             c['targetType'] == 'work' for c in current['credits']))

    def test_progress_and_protected_data(self):
        p = read('data/organizations.json')['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('I', 10, 13, 129, 132, 'entity-name-d7900289691e'))
        self.assertEqual(p['processedEntityIds'][-3:],
                         [x['entityId'] for x in read('data/entity-creator-i3-review-20261024.json')['reviewedEntities']])
        self.assertEqual(read('data/organizations.json')['works'], old('data/organizations.json')['works'])
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(catalogue_bytes(ROOT, path),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
