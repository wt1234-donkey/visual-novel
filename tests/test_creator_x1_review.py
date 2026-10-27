"""X1 records a complete audit without guessing an ambiguous historical identity."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
BASE = '6d3d3f5be873cf8ba4c9923e6cce6ac7bacbafc6'
XBOX = 'entity-xbox_game_studios'
XING = 'entity-name-40e00ac41438'
REVIEW = 'data/entity-creator-x1-review-20261026.json'


def read(path):
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json',
                'data/entity-migration-review.json']:
        return json.loads(subprocess.check_output(
            ['git', 'show', f'1d1d898595e9979cf7e3f15733777f58ccac029b:{path}'], cwd=ROOT))
    return read(path)


class CreatorX1Tests(unittest.TestCase):
    def test_entire_entity_and_credit_indexes_stay_identical(self):
        self.assertEqual(applied('data/entities.json'), old('data/entities.json'))
        self.assertEqual(applied('data/credits.json'), old('data/credits.json'))
        self.assertEqual(applied('data/entity-migration-review.json'), old('data/entity-migration-review.json'))
        review = read(REVIEW)
        self.assertEqual(review['identityCorrections'], [])
        self.assertEqual(review['creditAdditions'], [])
        entities = {e['id']: e for e in applied('data/entities.json')['entities']}
        self.assertEqual((entities[XBOX]['type'], entities[XBOX]['verification']),
                         ('brand', 'existingDossier'))
        self.assertEqual((entities[XING]['type'], entities[XING]['verification']),
                         ('unknown', 'unresolved'))
        credits = applied('data/credits.json')
        xbox = [c for c in credits['credits'] if c['entityId'] == XBOX]
        xing = [c for c in credits['credits'] if c['entityId'] == XING]
        self.assertEqual((len(xbox), {c['role'] for c in xbox}),
                         (11, {'publishingBrand', 'originalPublishingBrand'}))
        self.assertEqual([(c['targetType'], c['targetId'], c['role']) for c in xing],
                         [('release', 'g830-v2', 'publisher')])
        self.assertEqual((len(credits['credits']), len(credits['dossierMemberships']),
                          sum(m['status'] == 'pendingRole' for m in credits['dossierMemberships'])),
                         (5011, 2234, 601))

    def test_original_records_and_uncertain_x68000_content_are_unchanged(self):
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/content-migration-baseline.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        release = next(r for r in read('data/games.json')['platformReleases'] if r['id'] == 'g830-v2')
        self.assertEqual((release['year'], release['publisher'], release['contentRelation'], release['contentVersionId']),
                         (1993, 'エクシング', 'unverified', None))
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        for field in ['nodes', 'edges', 'works', 'credits', 'families']:
            self.assertEqual(after[field], before[field])

    def test_x_order_progresses_to_yonago_gainax(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('X', 2, 2, 309, 309, 'entity-yonago_gainax'))
        self.assertEqual(p['processedEntityIds'][:-2], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-2:], [XBOX, XING])
        review = read(REVIEW)
        self.assertEqual([e['entityId'] for e in review['reviewedEntities']], [XBOX, XING])
        self.assertEqual([e['entityId'] for e in review['deferredReviews']], [XBOX, XING])
        script = """import fs from 'node:fs';
import {sortFamilies} from './relationships-preview.mjs';
const es=JSON.parse(fs.readFileSync('data/entities.json')).entities;
const sorted=sortFamilies(es.map(e=>({id:e.id,title:e.name})));
process.stdout.write(JSON.stringify({x:sorted.filter(e=>/^x/i.test(e.title)).map(e=>e.id),
 next:sorted[sorted.findIndex(e=>e.id==='entity-name-40e00ac41438')+1].id}));"""
        actual = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', script], cwd=ROOT))
        self.assertEqual(actual['x'], [XBOX, XING])
        self.assertEqual(actual['next'], p['nextEntityId'])


if __name__ == '__main__':
    unittest.main()
