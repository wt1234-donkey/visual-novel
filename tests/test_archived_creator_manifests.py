"""Keep the recorded A–H review decisions checked after lost stage trees."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ARCHIVED = 'a6 b1 b2 b3 c1 c2 c3 c4 d1 d2 d3 f1 f2 g1 g2 g3 h1 h2 h3'.split()


class ArchivedCreatorManifestTests(unittest.TestCase):
    def test_recorded_identities_credits_and_queue_survive(self):
        entities = {e['id']: e for e in json.loads((ROOT / 'data/entities.json').read_text())['entities']}
        credits = {(c['entityId'], c['workId'], c['role'], c['targetType'])
                   for c in json.loads((ROOT / 'data/credits.json').read_text())['credits']}
        processed = set(json.loads((ROOT / 'data/organizations.json').read_text())
                        ['registrationProgress']['processedEntityIds'])
        for batch in ARCHIVED:
            with self.subTest(batch=batch):
                paths = list((ROOT / 'data').glob(f'entity-creator-{batch}-review-*.json'))
                self.assertEqual(len(paths), 1)
                review = json.loads(paths[0].read_text())
                self.assertTrue(review['audit'])
                self.assertTrue(review['reviewedEntities'])
                self.assertTrue({r['entityId'] for r in review['reviewedEntities']} <= processed)
                for correction in review['identityCorrections']:
                    entity = entities[correction['entityId']]
                    self.assertEqual(entity['type'], correction['type'])
                    self.assertTrue(correction['sources'])
                    self.assertTrue(set(correction['sources']) <= set(entity['sources']))
                for addition in review['creditAdditions']:
                    self.assertTrue(addition['source'])
                    self.assertIn((addition['entityId'], addition['workId'], addition['role'],
                                   addition['targetType']), credits)


if __name__ == '__main__':
    unittest.main()
