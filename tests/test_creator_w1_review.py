"""W1 audits two company identities, two brand identities and scoped HBR roles."""
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
BASE = '7fd9b99d705fcbd62e47bdc5fb02b8fc4e419208'
REVIEW = 'data/entity-creator-w1-review-20261026.json'
IDS = ['entity-name-a7663faeee46', 'entity-whale', 'entity-name-0d7ac5f6433b',
       'entity-name-10c3ce8b67e2', 'entity-name-9e9cc680be5a']


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json', 'data/entity-migration-review.json']:
        return json.loads(subprocess.check_output(['git', 'show', f'6d3d3f5be873cf8ba4c9923e6cce6ac7bacbafc6:{path}'], cwd=ROOT))
    return read(path)


class CreatorW1Tests(unittest.TestCase):
    def test_four_scoped_identities_preserve_names_dates_and_relationships(self):
        before, after = old('data/entities.json'), applied('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({eid for eid in be if be[eid] != ae[eid]}, set(IDS) - {IDS[1]})
        self.assertEqual([(ae[eid]['type'], ae[eid]['verification']) for eid in IDS],
                         [('company', 'sourceReviewed'), ('brand', 'existingDossier'),
                          ('brand', 'sourceReviewed'), ('company', 'sourceReviewed'),
                          ('brand', 'sourceReviewed')])
        for eid in IDS:
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual((len(ae), sum(e['verification'] == 'unresolved' for e in ae.values())), (326, 40))

    def test_only_two_explicit_branded_roles_added_without_catalogue_changes(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(after['credits'][:-2], before['credits'])
        self.assertEqual(after['dossierMemberships'], before['dossierMemberships'])
        self.assertEqual((len(after['credits']), len(after['dossierMemberships']),
                          sum(m['status'] == 'pendingRole' for m in after['dossierMemberships'])),
                         (5011, 2234, 601))
        self.assertEqual([(c['entityId'], c['targetType'], c['targetId'], c['role'])
                          for c in after['credits'][-2:]],
                         [(IDS[-1], 'work', 'key-rpg-hbr', 'productionBrand'),
                          (IDS[-1], 'release', 'key-rpg-hbr-v3', 'developer')])
        self.assertEqual([c for c in before['credits'] if c['targetType'] == 'release' and c['role'] == 'publisher'],
                         [c for c in after['credits'] if c['targetType'] == 'release' and c['role'] == 'publisher'])
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/content-migration-baseline.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        self.assertEqual(applied('data/organizations.json')['works'], old('data/organizations.json')['works'])
        hbr = next(w for c in read('data/company-coverage.json')['companies'] if c['id'] == 'key'
                   for w in c['relatedGames'] if w['id'] == 'key-rpg-hbr')
        pc = next(r for r in hbr['platformReleases'] if r['id'] == 'key-rpg-hbr-v3')
        self.assertIsNone(pc['contentVersionId'])
        self.assertEqual(pc['contentRelation'], 'unverified')
        self.assertEqual([(r['id'], r['year'], r['publisher']) for r in read('data/games.json')['platformReleases']
                          if r['workId'] == 'g085'],
                         [('g085-v1', 1985, 'Data East'), ('g085-v2', 1992, 'Wolf Team')])

    def test_complete_w_order_and_next_xbox(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('W', 5, 5, 307, 307, 'entity-xbox_game_studios'))
        self.assertEqual(p['processedEntityIds'][:-5], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-5:], IDS)
        self.assertEqual([e['entityId'] for e in read(REVIEW)['reviewedEntities']], IDS)
        script = """import fs from 'node:fs';
import {sortFamilies} from './relationships-preview.mjs';
const es=JSON.parse(fs.readFileSync('data/entities.json')).entities;
const sorted=sortFamilies(es.map(e=>({id:e.id,title:e.name})));
process.stdout.write(JSON.stringify({w:sorted.filter(e=>/^w/i.test(e.title)).map(e=>e.id),
 next:sorted[sorted.findIndex(e=>e.id==='entity-name-9e9cc680be5a')+1].id}));"""
        actual = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', script], cwd=ROOT))
        self.assertEqual([q['entityId'] for q in read(REVIEW)['progress']['queue']], actual['w'])
        self.assertEqual(actual['next'], p['nextEntityId'])

    def test_brand_corrections_require_explicit_publisher_preservation(self):
        original_read = builder.read
        for index in [1, 3]:
            for value in [False, None]:
                with self.subTest(index=index, preserve=value):
                    review = copy.deepcopy(read(REVIEW))
                    review['identityCorrections'][index]['preserveReleaseRoles'] = value
                    with patch.object(builder, 'read', side_effect=lambda path:
                                      review if path == REVIEW else original_read(path)):
                        with self.assertRaises(AssertionError):
                            builder.build()


if __name__ == '__main__':
    unittest.main()
