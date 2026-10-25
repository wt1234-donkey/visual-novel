"""S3 confines an official developer listing to one historical release."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BASE = 'af8d34d953350633ef3975aae99384ae01c7a0a6'
REVIEW = 'data/entity-creator-s3-review-20261026.json'
SHIRAVUNE = 'entity-name-5caee77c6090'
SHOGAKUKAN = 'entity-name-663fc46f7715'
IDS = ['entity-sharrock', SHIRAVUNE, 'entity-shopro', SHOGAKUKAN]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_entity_model as builder


def read(path):
    return json.loads((ROOT / path).read_text())


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json']:
        return json.loads(subprocess.check_output(['git', 'show', f'902fcc101e8495cdf72449e904b1972ca1b36e65:{path}'], cwd=ROOT))
    return read(path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorS3Tests(unittest.TestCase):
    def test_one_identity_and_one_release_credit_preserve_all_other_objects(self):
        before, after = old('data/entities.json'), applied('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {SHOGAKUKAN})
        self.assertEqual((ae[SHOGAKUKAN]['type'], ae[SHOGAKUKAN]['verification']),
                         ('company', 'sourceReviewed'))
        for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
            self.assertEqual(be[SHOGAKUKAN].get(field), ae[SHOGAKUKAN].get(field))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual(sum(e['verification'] == 'unresolved' for e in ae.values()), 71)
        bc, ac = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(ac['credits'][:-1], bc['credits'])
        credit = ac['credits'][-1]
        self.assertEqual([credit[k] for k in ['entityId', 'targetType', 'targetId', 'workId', 'role']],
                         [SHIRAVUNE, 'release', 'g046-v3', 'g046', 'developer'])
        self.assertEqual(credit['reviewRecord'], REVIEW.replace('.json', '.md'))
        self.assertEqual(len(ac['credits']), 4980)
        self.assertEqual(ac['dossierMemberships'], bc['dossierMemberships'])
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in ac['dossierMemberships']), 602)
        self.assertFalse(any(c['entityId'] == 'entity-sharrock' for c in ac['credits']))
        self.assertFalse(any(c['entityId'] == SHIRAVUNE and c['targetType'] != 'release'
                             for c in ac['credits']))
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/content-migration-baseline.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)

    def test_four_consecutive_entities_advance_to_sierra(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('S', 11, 42, 248, 279, 'entity-sierra_company'))
        self.assertEqual(p['processedEntityIds'][:-4], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-4:], IDS)
        review = read(REVIEW)
        self.assertEqual([q['status'] for q in review['progress']['queue']],
                         ['reviewed'] * 11 + ['pending'] * 31)
        self.assertEqual([e['entityId'] for e in review['reviewedEntities']], IDS)
        self.assertEqual([e['entityId'] for e in review['deferredReviews']], IDS)
        self.assertEqual(after['works'], before['works'])

    def test_release_review_rejects_wrong_work_missing_target_roles_and_dossier_shortcuts(self):
        original_read = builder.read
        for mutation in [dict(workId='g037'), dict(targetId='missing-release'),
                         dict(beforeTargetRoles=[]), dict(dossierId='elf'),
                         dict(role='originalProduction')]:
            with self.subTest(mutation=mutation):
                review = copy.deepcopy(read(REVIEW))
                review['creditAdditions'][0].update(mutation)
                with patch.object(builder, 'read', side_effect=lambda path:
                                  review if path == REVIEW else original_read(path)):
                    with self.assertRaises(AssertionError):
                        builder.build()
