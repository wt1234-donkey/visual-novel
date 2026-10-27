"""T2 keeps original production, Plus content and regional publishing distinct."""
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
BASE = '92f37c89e468d73174d3b56b367bcf8b3981e98e'
REVIEW = 'data/entity-creator-t2-review-20261026.json'
IDS = ['entity-name-3fc0babaf7f8', 'entity-name-b01843ba1268',
       'entity-tiare', 'entity-name-5f291db8e809']


def read(path):
    return json.loads(catalogue_bytes(ROOT, path).decode())


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json', 'data/entity-migration-review.json']:
        return json.loads(subprocess.check_output(['git', 'show', f'deafc7f5a6e551367b6d06012e6a7afc3337d920:{path}'], cwd=ROOT))
    return read(path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorT2Tests(unittest.TestCase):
    def test_two_identity_corrections_preserve_regional_publisher_and_historical_brand(self):
        before, after = old('data/entities.json'), applied('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {IDS[1], IDS[3]})
        for eid, kind in [(IDS[1], 'team'), (IDS[3], 'company')]:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), (kind, 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual((len(ae), sum(e['verification'] == 'unresolved' for e in ae.values())), (326, 54))

    def test_exact_three_credits_preserve_original_signatures_and_collaborators(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(after['credits'][:-3], before['credits'])
        self.assertEqual(len(after['credits']), 5002)
        self.assertEqual([(c['entityId'], c['targetType'], c['targetId'], c['role'])
                          for c in after['credits'][-3:]],
                         [(IDS[1], 'work', 'g056', 'originalProduction'),
                          (IDS[1], 'content', 'g056-c-3', 'developer'),
                          (IDS[3], 'work', 'g969', 'originalProduction')])
        for c in after['credits'][-3:]:
            self.assertEqual(c['status'], 'sourceReviewed')
            self.assertEqual(c['reviewRecord'], REVIEW.replace('.json', '.md'))
        self.assertEqual([c for c in after['credits'] if c['targetType'] == 'release'],
                         [c for c in before['credits'] if c['targetType'] == 'release'])
        self.assertEqual(after['dossierMemberships'], before['dossierMemberships'])
        for eid in [IDS[0], IDS[2], 'entity-name-22015689e48e']:
            self.assertEqual([c for c in after['credits'] if c['entityId'] == eid],
                             [c for c in before['credits'] if c['entityId'] == eid])

    def test_plus_scope_does_not_fill_mobile_content_or_change_original_catalogue(self):
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/content-migration-baseline.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        games = read('data/games.json')
        plus = next(c for c in games['contentVersions'] if c['id'] == 'g056-c-3')
        self.assertEqual((plus['basis'], plus['comparedTo']), ('added', 'g056-c-original'))
        releases = [r for r in games['platformReleases'] if r['contentVersionId'] == 'g056-c-3']
        self.assertEqual({r['id'] for r in releases}, {'g056-v3', 'g056-v4', 'g056-v5'})
        for rid in ['g056-v6', 'g056-v7']:
            release = next(r for r in games['platformReleases'] if r['id'] == rid)
            self.assertIsNone(release['contentVersionId'])
            self.assertEqual(release['contentRelation'], 'unverified')
        cs = applied('data/credits.json')['credits']
        self.assertEqual([(c['targetType'], c['targetId']) for c in cs
                          if c['entityId'] == IDS[1] and c['role'] == 'developer'], [('content', 'g056-c-3')])
        self.assertEqual(applied('data/organizations.json')['works'], old('data/organizations.json')['works'])

    def test_four_consecutive_entities_advance_t_to_tinmachine(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('T', 8, 19, 287, 298, 'entity-tinmachine'))
        self.assertEqual(p['nextName'], 'TinMachine')
        self.assertEqual(p['processedEntityIds'][:-4], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-4:], IDS)
        review = read(REVIEW)
        self.assertEqual([e['entityId'] for e in review['reviewedEntities']], IDS)
        self.assertEqual([e['entityId'] for e in review['deferredReviews']], IDS)
        queue = review['progress']['queue']
        self.assertEqual([q['status'] for q in queue], ['reviewed'] * 8 + ['pending'] * 11)
        script = """import fs from 'node:fs';
import {sortFamilies} from './relationships-preview.mjs';
const es=JSON.parse(fs.readFileSync('data/entities.json')).entities;
process.stdout.write(JSON.stringify(sortFamilies(es.filter(e=>e.name.toLowerCase().startsWith('t'))
 .map(e=>({id:e.id,title:e.name}))).map(e=>e.id)));"""
        actual = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', script], cwd=ROOT))
        self.assertEqual([q['entityId'] for q in queue], actual)

    def test_plus_development_rejects_original_content_wrong_work_and_dossier_shortcuts(self):
        original_read = builder.read
        for mutation in [dict(targetId='g056-c-original'), dict(workId='g969'),
                         dict(targetId='missing-content'), dict(dossierId='jast'),
                         dict(beforeTargetRoles=['publisher'])]:
            with self.subTest(mutation=mutation):
                review = copy.deepcopy(read(REVIEW))
                review['creditAdditions'][1].update(mutation)
                with patch.object(builder, 'read', side_effect=lambda path:
                                  review if path == REVIEW else original_read(path)):
                    with self.assertRaises(AssertionError):
                        builder.build()
