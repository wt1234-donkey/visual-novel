"""T1 separates creative brands from a software distribution service."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_entity_model as builder
BASE = '7dba8bea89937aca4b47ad5c40a1689f617db456'
REVIEW = 'data/entity-creator-t1-review-20261026.json'
IDS = ['entity-te_soft', 'entity-name-e135870e3299',
       'entity-taito', 'entity-name-08cbddd5e450']


def read(path):
    return json.loads((ROOT / path).read_text())


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json', 'data/entity-migration-review.json']:
        return json.loads(subprocess.check_output(['git', 'show', f'92f37c89e468d73174d3b56b367bcf8b3981e98e:{path}'], cwd=ROOT))
    return read(path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorT1Tests(unittest.TestCase):
    def test_only_two_brand_identities_change_without_merging_names_or_dates(self):
        before, after = old('data/entities.json'), applied('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {IDS[1], IDS[3]})
        for eid in [IDS[1], IDS[3]]:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), ('brand', 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual(len(ae), 326)
        self.assertEqual(sum(e['verification'] == 'unresolved' for e in ae.values()), 56)

    def test_brand_identity_creates_no_roles_and_preserves_every_credit_and_membership(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(after, before)
        self.assertEqual(len(after['credits']), 4999)
        self.assertEqual((len(after['dossierMemberships']), sum(m['status'] == 'pendingRole'
                          for m in after['dossierMemberships'])), (2234, 602))
        self.assertEqual(read(REVIEW)['creditAdditions'], [])
        for eid, count in [(IDS[1], 1), (IDS[3], 3)]:
            cs = [c for c in after['credits'] if c['entityId'] == eid]
            self.assertEqual(len(cs), count)
            self.assertTrue(all(c['role'] == 'publisher' and c['targetType'] == 'release' for c in cs))
            node = next(n for n in applied('data/organizations.json')['nodes'] if n['id'] == eid)
            self.assertEqual(node['groups']['creation'], [])
            self.assertEqual(node['productionCount'], 0)

    def test_all_original_catalogue_objects_and_unknown_content_remain_exact(self):
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/content-migration-baseline.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        release = next(r for r in read('data/games.json')['platformReleases'] if r['id'] == 'g812-v2')
        self.assertIsNone(release['contentVersionId'])
        self.assertEqual(release['contentRelation'], 'unverified')
        self.assertEqual(applied('data/organizations.json')['works'], old('data/organizations.json')['works'])

    def test_t_queue_starts_after_s_in_exact_existing_english_order(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextName']),
                         ('T', 4, 19, 283, 298, 'TamaMako gaming'))
        self.assertEqual(p['processedEntityIds'][:-4], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-4:], IDS)
        review = read(REVIEW)
        self.assertEqual([e['entityId'] for e in review['reviewedEntities']], IDS)
        self.assertEqual([e['entityId'] for e in review['deferredReviews']], IDS)
        queue = review['progress']['queue']
        self.assertEqual([q['status'] for q in queue], ['reviewed'] * 4 + ['pending'] * 15)
        self.assertEqual([q['entityId'] for q in queue[:4]], IDS)
        # Use the same JavaScript sorter as the public catalogue, including punctuation.
        script = """import fs from 'node:fs';
import {sortFamilies} from './relationships-preview.mjs';
const es=JSON.parse(fs.readFileSync('data/entities.json')).entities;
process.stdout.write(JSON.stringify(sortFamilies(es.filter(e=>e.name.toLowerCase().startsWith('t'))
 .map(e=>({id:e.id,title:e.name}))).map(e=>e.id)));"""
        actual = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', script], cwd=ROOT))
        self.assertEqual([q['entityId'] for q in queue], actual)
        self.assertEqual(p['nextEntityId'], actual[4])

    def test_brand_correction_requires_explicit_preservation_of_release_roles(self):
        original_read = builder.read
        for value in [False, None]:
            with self.subTest(preserveReleaseRoles=value):
                review = copy.deepcopy(read(REVIEW))
                review['identityCorrections'][0]['preserveReleaseRoles'] = value
                with patch.object(builder, 'read', side_effect=lambda path:
                                  review if path == REVIEW else original_read(path)):
                    with self.assertRaises(AssertionError):
                        builder.build()
