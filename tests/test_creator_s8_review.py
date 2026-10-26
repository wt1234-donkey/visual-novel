"""Historical Spike, its successor and a Mac publisher retain separate scopes."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '712383317f0cab13cc903a328f986f523ee91bf8'
REVIEW = 'data/entity-creator-s8-review-20261026.json'
IDS = ['entity-name-6d5cd9b9dc38', 'entity-name-8a871cf93bfd',
       'entity-name-6554f3ac70ec', 'entity-sprite']


def read(path):
    return json.loads((ROOT / path).read_text())


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json']:
        return json.loads(subprocess.check_output(['git', 'show', f'a5c6f50f4f6aa62752f328003af9ba13dbd62477:{path}'], cwd=ROOT))
    return read(path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorS8Tests(unittest.TestCase):
    def test_two_company_corrections_preserve_all_names_dates_and_relationships(self):
        before, after = old('data/entities.json'), applied('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {IDS[0], IDS[2]})
        for eid in [IDS[0], IDS[2]]:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), ('company', 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual(len(ae), 326)
        self.assertEqual(sum(e['verification'] == 'unresolved' for e in ae.values()), 63)

    def test_three_original_productions_preserve_all_existing_release_credits(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(after['credits'][:-3], before['credits'])
        self.assertEqual(len(after['credits']), 4989)
        self.assertEqual([(c['entityId'], c['targetType'], c['targetId'], c['role'])
                          for c in after['credits'][-3:]],
                         [(IDS[0], 'work', 'g035', 'originalProduction'),
                          (IDS[1], 'work', 'g160', 'originalProduction'),
                          (IDS[1], 'work', 'g161', 'originalProduction')])
        for c in after['credits'][-3:]:
            self.assertEqual(c['reviewRecord'], REVIEW.replace('.json', '.md'))
            self.assertEqual(c['status'], 'sourceReviewed')
        for eid in IDS[:3]:
            self.assertEqual([c for c in after['credits'] if c['entityId'] == eid and c['targetType'] == 'release'],
                             [c for c in before['credits'] if c['entityId'] == eid and c['targetType'] == 'release'])
        self.assertFalse(any(c['entityId'] == IDS[1] and c['workId'] in ['g035', 'g171']
                             and c['role'] in ['originalProduction', 'developer'] for c in after['credits']))
        self.assertEqual([c for c in after['credits'] if c['entityId'] == IDS[3]],
                         [c for c in before['credits'] if c['entityId'] == IDS[3]])

    def test_memberships_original_catalogue_and_migration_baselines_stay_exact(self):
        bc, ac = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(ac['dossierMemberships'], bc['dossierMemberships'])
        self.assertEqual(len(ac['dossierMemberships']), 2234)
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in ac['dossierMemberships']), 602)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/content-migration-baseline.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        games = read('data/games.json')
        mac = next(r for r in games['platformReleases'] if r['id'] == 'g819-v2')
        self.assertIsNone(mac['contentVersionId'])
        self.assertEqual(mac['contentRelation'], 'unverified')

    def test_four_consecutive_entities_advance_to_square_enix(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('S', 32, 42, 269, 279, 'entity-name-8a3d38d0d11f'))
        self.assertEqual(p['processedEntityIds'][:-4], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-4:], IDS)
        r = read(REVIEW)
        self.assertEqual([e['entityId'] for e in r['reviewedEntities']], IDS)
        self.assertEqual([e['entityId'] for e in r['deferredReviews']], IDS)
        self.assertEqual([q['status'] for q in r['progress']['queue']], ['reviewed'] * 32 + ['pending'] * 10)
        self.assertEqual(after['works'], before['works'])
