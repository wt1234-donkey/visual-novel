"""T4 keeps 2019 Steam development separate from pre-2018 originals."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_entity_model as builder
BASE = '700c5f0c055bd9be328bf7000dc6f004d9162d76'
REVIEW = 'data/entity-creator-t4-review-20261026.json'
IDS = ['entity-tokuma', 'entity-name-2793ee33b030',
       'entity-name-aa2256b9c684', 'entity-toneworks']


def read(path):
    return json.loads(catalogue_bytes(ROOT, path).decode())


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json', 'data/entity-migration-review.json']:
        return json.loads(subprocess.check_output(['git', 'show', f'41aa48d6c62b67c30cf6f516f33dc5aa59e1cdc3:{path}'], cwd=ROOT))
    return read(path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorT4Tests(unittest.TestCase):
    def test_only_two_company_identities_change_without_rewriting_brands_or_dates(self):
        before, after = old('data/entities.json'), applied('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {IDS[1], IDS[2]})
        for eid in [IDS[1], IDS[2]]:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), ('company', 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual((len(ae), sum(e['verification'] == 'unresolved' for e in ae.values())), (326, 50))

    def test_two_exact_steam_credits_preserve_original_brands_and_every_old_role(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(after['credits'][:-2], before['credits'])
        self.assertEqual(len(after['credits']), 5005)
        self.assertEqual([(c['entityId'], c['targetType'], c['targetId'], c['role'])
                          for c in after['credits'][-2:]],
                         [(IDS[2], 'release', 'g900-v9', 'developer'),
                          (IDS[2], 'release', 'g901-v8', 'developer')])
        for c in after['credits'][-2:]:
            self.assertEqual(c['status'], 'sourceReviewed')
            self.assertEqual(c['reviewRecord'], REVIEW.replace('.json', '.md'))
        self.assertEqual([c for c in after['credits'] if c['role'] == 'publisher'],
                         [c for c in before['credits'] if c['role'] == 'publisher'])
        for eid in [IDS[0], IDS[1], IDS[3], 'entity-harukaze', 'entity-name-9832231b6baa']:
            self.assertEqual([c for c in after['credits'] if c['entityId'] == eid],
                             [c for c in before['credits'] if c['entityId'] == eid])
        self.assertEqual(len([c for c in after['credits'] if c['entityId'] == IDS[3]
                              and c['role'] == 'productionBrand']), 6)
        self.assertFalse(any(c['entityId'] == IDS[2] and c['targetType'] != 'release'
                             for c in after['credits']))

    def test_unknown_steam_content_memberships_and_original_catalogue_remain_exact(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(before['dossierMemberships'], after['dossierMemberships'])
        self.assertEqual((len(after['dossierMemberships']), sum(m['status'] == 'pendingRole'
                          for m in after['dossierMemberships'])), (2234, 601))
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/content-migration-baseline.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        games = read('data/games.json')
        for rid, wid in [('g900-v9', 'g900'), ('g901-v8', 'g901')]:
            r = next(r for r in games['platformReleases'] if r['id'] == rid)
            self.assertEqual((r['workId'], r['year'], r['contentRelation']), (wid, 2019, 'unverified'))
            self.assertIsNone(r['contentVersionId'])
        self.assertEqual(applied('data/organizations.json')['works'], old('data/organizations.json')['works'])

    def test_four_consecutive_entities_advance_t_to_tonkin_house(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('T', 16, 19, 295, 298, 'entity-name-679a14238228'))
        self.assertEqual(p['nextName'], 'Tonkin House（トンキンハウス）')
        self.assertEqual(p['processedEntityIds'][:-4], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-4:], IDS)
        review = read(REVIEW)
        self.assertEqual([e['entityId'] for e in review['reviewedEntities']], IDS)
        self.assertEqual([e['entityId'] for e in review['deferredReviews']], IDS)
        queue = review['progress']['queue']
        self.assertEqual([q['status'] for q in queue], ['reviewed'] * 16 + ['pending'] * 3)
        script = """import fs from 'node:fs';
import {sortFamilies} from './relationships-preview.mjs';
const es=JSON.parse(fs.readFileSync('data/entities.json')).entities;
process.stdout.write(JSON.stringify(sortFamilies(es.filter(e=>e.name.toLowerCase().startsWith('t'))
 .map(e=>({id:e.id,title:e.name}))).map(e=>e.id)));"""
        actual = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', script], cwd=ROOT))
        self.assertEqual([q['entityId'] for q in queue], actual)

    def test_scoped_steam_review_rejects_work_content_and_other_release_shortcuts(self):
        original_read = builder.read
        for mutation in [dict(targetType='work'), dict(targetType='content'),
                         dict(targetId='g901-v8'), dict(dossierId='harukaze'),
                         dict(beforeTargetRoles=[])]:
            with self.subTest(mutation=mutation):
                review = copy.deepcopy(read(REVIEW))
                review['creditAdditions'][0].update(mutation)
                with patch.object(builder, 'read', side_effect=lambda path:
                                  review if path == REVIEW else original_read(path)):
                    with self.assertRaises(AssertionError):
                        builder.build()
