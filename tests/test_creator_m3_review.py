"""M3 distinguishes original production, joint work, ports and composite names."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'c88ede63da5767fcd562eaa69abc1c83c976d54c'
MICRO = 'entity-microcabin'
MATSUSHITA = 'entity-name-fec7ac8f12b1'
COMPOSITE = 'entity-name-5714be41cf55'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorM3Tests(unittest.TestCase):
    def test_two_company_categories_without_merging_composite_or_relations(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be = {e['id']: e for e in before['entities']}
        ae = {e['id']: e for e in after['entities']}
        expected = {MATSUSHITA, 'entity-name-61d0027ef7ce'}
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, expected)
        for eid in expected:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), ('company', 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates']:
                self.assertEqual(be[eid][field], ae[eid][field])
        self.assertEqual(ae[COMPOSITE], be[COMPOSITE])
        self.assertEqual(ae[COMPOSITE]['type'], 'unknown')
        self.assertEqual(after['relations'], before['relations'])

    def test_exact_scoped_additions_preserve_every_previous_credit(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-30], before['credits'])
        additions = after['credits'][-30:]
        originals = {'g097', 'g098', 'g133', 'g1142', 'g1143', 'g1144', 'g1145',
                     'g1146', 'g1147', 'g1148', 'microcabin-xak', 'microcabin-xak2',
                     'microcabin-gazzel', 'microcabin-illusion', 'microcabin-xak3',
                     'microcabin-dragonhalf', 'microcabin-herowish', 'microcabin-sword',
                     'microcabin-soulgetter', 'microcabin-agent', 'microcabin-worry',
                     'microcabin-harry', 'microcabin-snow'}
        joint = {'g1150', 'microcabin-powers', 'microcabin-riglord', 'microcabin-riglord2'}
        expected = {(MICRO, w, 'originalProduction') for w in originals}
        expected |= {(MICRO, w, 'coDeveloper') for w in joint}
        expected |= {(MATSUSHITA, w, 'coDeveloper') for w in ['g1150', 'microcabin-powers']}
        expected.add((COMPOSITE, 'ascii-rogue', 'coDeveloper'))
        self.assertEqual({(c['entityId'], c['workId'], c['role']) for c in additions}, expected)
        self.assertTrue(all(c['status'] == 'sourceReviewed' and c['targetType'] == 'work'
                            for c in additions))
        deferred = {'g1060', 'g942', 'g820', 'g1149', 'microcabin-nirgends', 'microcabin-ghost'}
        self.assertFalse(deferred & {c['workId'] for c in additions})

    def test_only_own_micro_memberships_change_and_placements_stay(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        bm = {(m['dossierId'], m['workId']): m for m in before['dossierMemberships']}
        am = {(m['dossierId'], m['workId']): m for m in after['dossierMemberships']}
        self.assertEqual(bm.keys(), am.keys())
        changed = [m for k, m in am.items() if m != bm[k]]
        self.assertEqual(len(changed), 27)
        self.assertEqual({m['dossierId'] for m in changed}, {'microcabin'})
        for key in bm:
            self.assertEqual(am[key]['placement'], bm[key]['placement'])
        cleared = {m['workId'] for k, m in am.items()
                   if bm[k]['status'] == 'pendingRole' and m['status'] != 'pendingRole'}
        self.assertEqual(cleared, {'microcabin-riglord', 'microcabin-riglord2', 'microcabin-agent',
                                   'microcabin-worry', 'microcabin-harry', 'microcabin-snow'})
        rogue = next(m for m in am.values() if (m['dossierId'], m['workId']) == ('ascii', 'ascii-rogue'))
        self.assertEqual(rogue['status'], 'pendingRole')

    def test_alphabetic_progress_and_protected_catalogue(self):
        orgs = read('data/organizations.json')
        p = orgs['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('M', 15, 30, 178, 193, 'entity-microsoft'))
        review = read('data/entity-creator-m3-review-20261025.json')
        self.assertEqual(p['processedEntityIds'][-5:], [e['entityId'] for e in review['reviewedEntities']])
        queue = review['progress']['queue']
        self.assertEqual([e['name'].lower() for e in queue], sorted(e['name'].lower() for e in queue))
        self.assertEqual([e['status'] for e in queue], ['reviewed'] * 15 + ['pending'] * 15)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        self.assertEqual(orgs['works'], old('data/organizations.json')['works'])
