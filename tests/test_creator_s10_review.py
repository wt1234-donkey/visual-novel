"""S10 preserves joint publishers, original creators and parent-dossier boundaries."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '498f6f9af8414b8e1d900f306382d1dc27887f8a'
REVIEW = 'data/entity-creator-s10-review-20261026.json'
IDS = ['entity-name-a3d00ecbbdcb', 'entity-name-ccdf9b616bf6',
       'entity-name-456a2209f1ad', 'entity-name-3c3fb799f482']


def read(path):
    return json.loads((ROOT / path).read_text())


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json']:
        return json.loads(subprocess.check_output(['git', 'show', f'8f186829271a10bbd50a23740836523a8152501f:{path}'], cwd=ROOT))
    return read(path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorS10Tests(unittest.TestCase):
    def test_three_company_corrections_preserve_the_unresolved_joint_publisher(self):
        before, after = old('data/entities.json'), applied('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {IDS[0], IDS[1], IDS[3]})
        for eid in [IDS[0], IDS[1], IDS[3]]:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), ('company', 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(ae[IDS[2]], be[IDS[2]])
        self.assertEqual((ae[IDS[2]]['type'], ae[IDS[2]]['verification']), ('unknown', 'unresolved'))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual(len(ae), 326)
        self.assertEqual(sum(e['verification'] == 'unresolved' for e in ae.values()), 58)

    def test_three_original_productions_preserve_every_old_release_and_credit(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(after['credits'][:-3], before['credits'])
        self.assertEqual(len(after['credits']), 4997)
        self.assertEqual([(c['entityId'], c['targetType'], c['targetId'], c['role'])
                          for c in after['credits'][-3:]],
                         [(IDS[1], 'work', 'toho-phanpara', 'originalProduction'),
                          (IDS[3], 'work', 'g1092', 'originalProduction'),
                          (IDS[3], 'work', 'g1093', 'originalProduction')])
        for c in after['credits'][-3:]:
            self.assertEqual(c['status'], 'sourceReviewed')
            self.assertEqual(c['reviewRecord'], REVIEW.replace('.json', '.md'))
        self.assertEqual([c for c in after['credits'] if c['targetType'] == 'release'],
                         [c for c in before['credits'] if c['targetType'] == 'release'])
        for eid in [IDS[0], IDS[2]]:
            self.assertEqual([c for c in after['credits'] if c['entityId'] == eid],
                             [c for c in before['credits'] if c['entityId'] == eid])
        self.assertTrue(all(c['role'] == 'publisher' for c in after['credits'] if c['entityId'] == IDS[0]))

    def test_all_parent_memberships_dates_content_and_baselines_stay_exact(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(after['dossierMemberships'], before['dossierMemberships'])
        members = after['dossierMemberships']
        self.assertEqual((len(members), sum(m['status'] == 'pendingRole' for m in members)), (2234, 602))
        for key in [('toho', 'toho-phanpara'), ('sierra', 'g1092'), ('sierra', 'g1093')]:
            m = next(m for m in members if (m['dossierId'], m['workId']) == key)
            self.assertEqual((m['roles'], m['group'], m['status']),
                             (['catalogueAssociation'], 'unresolved', 'pendingRole'))
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/content-migration-baseline.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)

    def test_four_consecutive_entities_advance_to_syawase(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('S', 40, 42, 277, 279, 'entity-name-b1b599d0fabf'))
        self.assertEqual(p['processedEntityIds'][:-4], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-4:], IDS)
        r = read(REVIEW)
        self.assertEqual([e['entityId'] for e in r['reviewedEntities']], IDS)
        self.assertEqual([e['entityId'] for e in r['deferredReviews']], IDS)
        self.assertEqual([q['status'] for q in r['progress']['queue']], ['reviewed'] * 40 + ['pending'] * 2)
        self.assertEqual(after['works'], before['works'])
