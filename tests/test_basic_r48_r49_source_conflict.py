import sys
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import import_basic_r48_r49_20261101 as importer


class ReviewedSourceConflictTests(unittest.TestCase):
    def test_known_nextmoe_conflict_is_held_before_identity_registration(self):
        counts, reused, held, index, refs = Counter(), [], [], {}, {}
        item = {'id': 'v46627', 'released': '2023-07-31'}
        with patch.object(importer, 'original_candidate') as original:
            result = importer.reviewed_candidate(item, 'nextmoe', '43993',
                ['Delusion'], index, refs, counts, reused, held, 'r49')
        self.assertIsNone(result)
        original.assert_not_called()
        self.assertEqual(dict(counts), {'source-date-conflict-held': 1})
        self.assertEqual(held[0]['sourceReleased'], '2023-07-31')
        self.assertEqual(held[0]['nextmoeSourceReleased'], '2006-03-23')
        self.assertEqual((index, refs, reused), ({}, {}, []))

    def test_vndb_identity_itself_remains_eligible_for_normal_review(self):
        marker = object()
        with patch.object(importer, 'original_candidate', return_value=marker) as original:
            result = importer.reviewed_candidate({'id': 'v46627'}, 'vndb',
                'v46627', ['Delusion'], {}, {}, Counter(), [], [], 'r48')
        self.assertIs(result, marker)
        original.assert_called_once()

    def test_unrelated_nextmoe_candidates_use_existing_rules(self):
        marker = object()
        with patch.object(importer, 'original_candidate', return_value=marker) as original:
            result = importer.reviewed_candidate({'id': 'v1'}, 'nextmoe',
                '43994', ['Other'], {}, {}, Counter(), [], [], 'r49')
        self.assertIs(result, marker)
        original.assert_called_once()
