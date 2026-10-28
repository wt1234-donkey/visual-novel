"""The numeric tail completes the current queue without rewriting original releases."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes
from historical_snapshot import cf_applied

ROOT = Path(__file__).resolve().parents[1]
REVIEW = 'data/entity-creator-numeric-review-20261026.json'
SEVEN = 'entity-name-ee1a7668cd89'
IDS = ['entity-5pb', SEVEN, 'entity-name-e1232b52eff7',
       'entity-name-d1903e2fafb1', 'entity-name-de3ed19ac095',
       'entity-name-a978e18d1d4b']


def read(path):
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    if path in {'data/entities.json', 'data/credits.json', 'data/organizations.json',
                'data/entity-migration-review.json'}:
        return cf_applied(ROOT, path)
    # The numeric tail did not alter these catalogue and migration baselines.
    return json.loads(subprocess.check_output(
        ['git', 'show', f'7ea5d46efdfb5a36875fbc48ed3b287ac0dc0e3c:{path}'], cwd=ROOT))


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json',
                'data/entity-migration-review.json']:
        return json.loads(subprocess.check_output(
            ['git', 'show', f'7ea5d46efdfb5a36875fbc48ed3b287ac0dc0e3c:{path}'], cwd=ROOT))
    return read(path)


class CreatorNumericReviewTests(unittest.TestCase):
    def test_only_07th_identity_and_two_original_production_credits_change(self):
        before, after = [dict((e['id'], e) for e in d['entities']) for d in
                         [old('data/entities.json'), applied('data/entities.json')]]
        self.assertEqual(before.keys(), after.keys())
        self.assertEqual({eid for eid in before if before[eid] != after[eid]}, {SEVEN})
        self.assertEqual((before[SEVEN]['type'], before[SEVEN]['verification']), ('unknown', 'unresolved'))
        self.assertEqual((after[SEVEN]['type'], after[SEVEN]['verification']), ('team', 'sourceReviewed'))
        review = read(REVIEW)
        self.assertEqual([r['entityId'] for r in review['identityCorrections']], [SEVEN])
        prior, current = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(current['credits'][:len(prior['credits'])], prior['credits'])
        extra = current['credits'][len(prior['credits']):]
        self.assertEqual([(c['entityId'], c['targetType'], c['targetId'], c['role']) for c in extra],
                         [(SEVEN, 'work', 'g051', 'originalProduction'),
                          (SEVEN, 'work', 'g174', 'originalProduction')])
        self.assertEqual([c['status'] for c in extra], ['sourceReviewed'] * 2)
        self.assertEqual(current['dossierMemberships'], prior['dossierMemberships'])
        self.assertEqual((len(current['credits']), len(current['dossierMemberships']),
                          sum(m['status'] == 'pendingRole' for m in current['dossierMemberships'])),
                         (5013, 2234, 601))
        self.assertEqual(len([c for c in current['credits'] if c['entityId'] == 'entity-5pb']), 71)

    def test_original_catalogue_and_all_other_unverified_identities_remain(self):
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(applied(path), old(path), path)
        before, after = old('data/entity-migration-review.json'), applied('data/entity-migration-review.json')
        self.assertEqual({k: v for k, v in after.items() if k != 'pendingIdentities'},
                         {k: v for k, v in before.items() if k != 'pendingIdentities'})
        self.assertEqual(after['pendingIdentities'],
                         [x for x in before['pendingIdentities'] if x['entityId'] != SEVEN])
        self.assertEqual(len(after['pendingIdentities']), 39)
        self.assertEqual([(e['type'], e['verification']) for e in applied('data/entities.json')['entities']
                          if e['id'] in IDS[2:]], [('unknown', 'unresolved')] * 4)
        games = read('data/games.json')
        mobile = [r for r in games['platformReleases'] if r['id'] in {'g209-v2', 'g209-v3'}]
        self.assertEqual(len(mobile), 2)
        self.assertTrue(all(r['contentRelation'] == 'unverified' and r['contentVersionId'] is None
                            for r in mobile))
        before_org, after_org = old('data/organizations.json'), applied('data/organizations.json')
        for key in ['edges', 'works', 'families']:
            self.assertEqual(after_org[key], before_org[key], key)
        bn, an = [{n['id']: n for n in d['nodes']} for d in [before_org, after_org]]
        self.assertEqual({eid for eid in bn if bn[eid] != an[eid]}, {SEVEN})

    def test_six_complete_the_sorted_missing_queue(self):
        review = read(REVIEW)
        self.assertEqual([r['entityId'] for r in review['reviewedEntities']], IDS)
        self.assertEqual([r['entityId'] for r in review['deferredReviews']], IDS)
        before = old('data/organizations.json')['registrationProgress']
        p = applied('data/organizations.json')['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'], p['total'],
                          p['nextEntityId'], p['nextName']), ('数字及其他', 6, 6, 326, None, None))
        self.assertEqual(p['processedEntityIds'][:320], before['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-6:], IDS)
        self.assertEqual(len(p['processedEntityIds']), len(set(p['processedEntityIds'])))
        script = """import {execFileSync} from 'node:child_process';
import {sortFamilies} from './relationships-preview.mjs';
const es=JSON.parse(execFileSync('git',['show','7ea5d46efdfb5a36875fbc48ed3b287ac0dc0e3c:data/entities.json'],{encoding:'utf8'})).entities;
const ids=sortFamilies(es.map(e=>({id:e.id,title:e.name}))).map(e=>e.id);
process.stdout.write(JSON.stringify(ids));"""
        sorted_ids = json.loads(subprocess.check_output(
            ['node', '--input-type=module', '-e', script], cwd=ROOT))
        self.assertEqual(sorted_ids[-6:], IDS)
        self.assertEqual(set(sorted_ids), set(p['processedEntityIds']))


if __name__ == '__main__':
    unittest.main()
