"""A second alphabetical pass resolves only well-sourced historic identities."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
BASE = '7ea5d46efdfb5a36875fbc48ed3b287ac0dc0e3c'
REVIEW = 'data/entity-creator-a-recheck1-review-20261026.json'
RECHECK_TREE = '025762765317e2e71b1889fb4f95e164d8588b75'


def read(path):
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


def recheck_snapshot(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{RECHECK_TREE}:{path}'], cwd=ROOT))


class CreatorARecheck1Tests(unittest.TestCase):
    def test_three_identity_corrections_only(self):
        review = read(REVIEW)
        before, after = [dict((e['id'], e) for e in d['entities']) for d in
                         [old('data/entities.json'), recheck_snapshot('data/entities.json')]]
        self.assertEqual(before.keys(), after.keys())
        corrected = {r['entityId'] for r in review['identityCorrections']}
        self.assertEqual({eid for eid in before if before[eid] != after[eid]}, corrected)
        self.assertEqual([r['rawName'] for r in review['identityCorrections']],
                         ['Accolade', 'Activision', 'âge'])
        for r in review['identityCorrections']:
            eid = r['entityId']
            self.assertEqual((before[eid]['type'], before[eid]['verification']),
                             ('unknown', 'unresolved'))
            self.assertEqual((after[eid]['type'], after[eid]['verification']),
                             (r['type'], 'sourceReviewed'))
            self.assertEqual(after[eid]['sources'], list(dict.fromkeys(before[eid]['sources'] + r['sources'])))
            for key in ['id', 'name', 'aliases', 'dates']:
                self.assertEqual(after[eid][key], before[eid][key])
        self.assertTrue(review['identityCorrections'][-1]['preserveReleaseRoles'])
        self.assertEqual(review['creditAdditions'], [])

    def test_original_catalogue_and_historic_roles_stay_unchanged(self):
        for path in ['data/credits.json', 'data/games.json', 'data/company-coverage.json',
                     'data/taxonomy.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(recheck_snapshot(path), old(path), path)
        credits = recheck_snapshot('data/credits.json')['credits']
        age = [c for c in credits if c['entityId'] == 'entity-name-f0d25e9c6d82']
        self.assertEqual(sorted(c['role'] for c in age),
                         ['productionBrand', 'productionBrand', 'publisher', 'publisher'])
        before, after = old('data/entity-migration-review.json'), recheck_snapshot('data/entity-migration-review.json')
        self.assertEqual({k: v for k, v in before.items() if k != 'pendingIdentities'},
                         {k: v for k, v in after.items() if k != 'pendingIdentities'})
        removed = {r['entityId'] for r in read(REVIEW)['identityCorrections']}
        self.assertEqual(after['pendingIdentities'],
                         [x for x in before['pendingIdentities'] if x['entityId'] not in removed])
        self.assertEqual(len(after['pendingIdentities']), 36)
        before_org, after_org = old('data/organizations.json'), recheck_snapshot('data/organizations.json')
        for key in ['edges', 'works', 'credits', 'families', 'registrationProgress']:
            self.assertEqual(after_org[key], before_org[key], key)
        bn, an = [{n['id']: n for n in d['nodes']} for d in [before_org, after_org]]
        self.assertEqual({eid for eid in bn if bn[eid] != an[eid]}, removed)

    def test_second_pass_follows_frozen_alphabetical_queue(self):
        review = read(REVIEW)
        p = recheck_snapshot('data/organizations.json')['recheckProgress']
        self.assertEqual((p['letter'], p['total'], len(p['processedEntityIds']), p['nextName']),
                         ('A', 39, 5, 'Alchemist'))
        self.assertEqual([r['entityId'] for r in review['reviewedEntities']], p['processedEntityIds'])
        self.assertEqual([r['entityId'] for r in review['deferredReviews']], p['processedEntityIds'])
        self.assertEqual([x['entityId'] for x in p['baselineQueue'][:6]],
                         p['processedEntityIds'] + [p['nextEntityId']])
        script = """import fs from 'node:fs';
import {sortFamilies} from './relationships-preview.mjs';
const es=JSON.parse(fs.readFileSync('data/entities.json')).entities;
const candidates=new Set(JSON.parse(fs.readFileSync('data/entity-creator-a-recheck1-review-20261026.json')).recheckProgress.baselineQueue.map(e=>e.entityId));
process.stdout.write(JSON.stringify(sortFamilies(es.filter(e=>candidates.has(e.id)).map(e=>({id:e.id,title:e.name}))).map(e=>e.id)));"""
        sorted_ids = json.loads(subprocess.check_output(
            ['node', '--input-type=module', '-e', script], cwd=ROOT))
        self.assertEqual(sorted_ids, [x['entityId'] for x in p['baselineQueue']])


if __name__ == '__main__':
    unittest.main()
