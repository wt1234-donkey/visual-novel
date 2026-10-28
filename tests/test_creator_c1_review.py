"""C1 limits Caramel Box creation to two sourced originals."""
from audit_baselines import requires_baseline
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes
from creator_snapshot import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
BASE = 'f1e8d845c5731fe1740763ab194f9bd014a3a435'  # Parent of the C1 audit.

def read(path):
    return load_snapshot(ROOT, path)

def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))

@requires_baseline(ROOT, BASE)
class CreatorC1Tests(unittest.TestCase):
    def test_identity_and_credit_diff(self):
        review = read('data/entity-creator-c1-review-20261023.json')
        b, a = ({e['id']: e for e in x['entities']} for x in [old('data/entities.json'), read('data/entities.json')])
        self.assertEqual({eid for eid in b if b[eid] != a[eid]},
                         {c['entityId'] for batch in [review, read('data/entity-creator-c2-review-20261023.json'), read('data/entity-creator-c3-review-20261023.json'), read('data/entity-creator-c4-review-20261023.json'), read('data/entity-creator-d1-review-20261023.json'), read('data/entity-creator-d2-review-20261023.json'), read('data/entity-creator-d3-review-20261023.json'), read('data/entity-creator-e1-review-20261023.json'), read('data/entity-creator-e2-review-20261024.json'), read('data/entity-creator-e3-review-20261024.json'), read('data/entity-creator-f1-review-20261024.json'), read('data/entity-creator-f2-review-20261024.json'), read('data/entity-creator-g1-review-20261024.json'), read('data/entity-creator-g2-review-20261024.json'), read('data/entity-creator-g3-review-20261024.json'), read('data/entity-creator-h1-review-20261024.json'), read('data/entity-creator-h2-review-20261024.json')]
                          for c in batch['identityCorrections']})
        for correction in review['identityCorrections']:
            eid = correction['entityId']
            self.assertEqual((b[eid]['type'], b[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((a[eid]['type'], a[eid]['verification']), (correction['type'], 'sourceReviewed'))
            self.assertEqual((a[eid]['aliases'], a[eid]['dates']), (b[eid]['aliases'], b[eid]['dates']))
        before, after = old('data/credits.json'), read('data/credits.json')
        b, a = ({c['id']: c for c in x['credits']} for x in [before, after])
        self.assertEqual({cid: a[cid] for cid in b}, b)
        additions = [a[cid] for cid in a.keys() - b.keys() if a[cid].get('reviewRecord') == review['audit']]
        self.assertEqual({(c['entityId'], c['workId'], c['role'], c['targetType']) for c in additions},
                         {('entity-name-53ec4c5b9afc', wid, 'productionBrand', 'work') for wid in ['g639', 'g640']})
        self.assertEqual({c['reviewId'] for c in additions}, {c['reviewId'] for c in review['creditAdditions']})
        self.assertEqual([m for m in after['dossierMemberships'] if (m['dossierId'], m['workId']) not in {('elf', 'g320'), ('enix', 'g984')} and m['dossierId'] != 'hulotte' and m['dossierId'] != 'hummingbird_soft'],
                         [m for m in before['dossierMemberships'] if (m['dossierId'], m['workId']) not in {('elf', 'g320'), ('enix', 'g984')} and m['dossierId'] != 'hulotte' and m['dossierId'] != 'hummingbird_soft'])

    def test_contiguous_progress_and_unchanged_core(self):
        org = read('data/organizations.json')
        p = org['registrationProgress']
        self.assertEqual(p['processedEntityIds'][42:47], read('data/entity-creator-c1-review-20261023.json')['progress']['processedEntityIds'])
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'], len(p['processedEntityIds']), p['total']),
                         ('H', 12, 12, 119, 119))
        self.assertEqual(read('data/entity-creator-c1-review-20261023.json')['progress']['nextEntityId'], 'entity-name-21365baf366d')
        self.assertEqual([r['entityId'] for r in p['reviewedEntities']], p['processedEntityIds'])
        self.assertEqual(org['works'], old('data/organizations.json')['works'])
        nodes = {n['id']: n for n in org['nodes']}
        prior = {n['id']: n for n in old('data/organizations.json')['nodes']}
        self.assertEqual(len(nodes['entity-name-53ec4c5b9afc']['groups']['creation']), 2)
        for eid in ['entity-cabbage', 'entity-name-7554e19bb041', 'entity-carry_lab', 'entity-name-431d2fb7a95c']:
            self.assertEqual(nodes[eid]['groups'], prior[eid]['groups'])
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json',
                     'data/entity-creator-b3-review-20261023.json']:
            self.assertEqual(catalogue_bytes(ROOT, path), subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)

if __name__ == '__main__':
    unittest.main()
