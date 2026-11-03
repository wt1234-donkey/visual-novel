"""Continuation must preserve identity checks when an archive ends early."""
import sys
import unittest
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import ifdb_archive_identity as archive
import import_basic_r134_r135_20261103 as engine


def row(letter, title):
    return {'tuid': letter * 16, 'title': title, 'aliases': [], 'firstYear': 1993,
            'published': '1993-01-01 00:00:00', 'author': '', 'system': '',
            'language': 'en', 'sourceRefs': ['ifdb:' + letter * 16], 'archiveLinks': []}


class ExhaustionTests(unittest.TestCase):
    def test_partial_counts_reuse_and_exhaustion(self):
        rows = [row('a', 'Known'), row('b', 'New')]
        index = defaultdict(set, {'known': {('existing', 1993, 'old')}})
        selected, review = archive.choose(rows, 2, index, defaultdict(set), str.casefold, 'batch', allow_partial=True)
        self.assertEqual(len(selected), 1)
        self.assertEqual((review['scanned'], review['nextPosition']), (2, 3))
        self.assertTrue(review['archiveExhausted'])
        self.assertEqual(review['dispositions'], {'reused-title-alias': 1})

    def test_end_position_and_nonexhausted_limit(self):
        rows = [row('a', 'First'), row('b', 'Second')]
        index, refs = defaultdict(set), defaultdict(set)
        selected, end = archive.choose(rows, 1, index, refs, str.casefold, 'batch', start_position=3, allow_partial=True)
        self.assertEqual((selected, end['scanned'], end['nextPosition']), ([], 0, 3))
        self.assertTrue(end['archiveExhausted'])
        self.assertFalse(index or refs)
        _, first = archive.choose(rows, 1, index, refs, str.casefold, 'batch', allow_partial=True)
        self.assertEqual(first['nextPosition'], 2)
        self.assertFalse(first['archiveExhausted'])

    def test_historical_reviewed_alias_blocks_later_duplicate(self):
        old = {'title': 'Known', 'aliases': ['Alternate'], 'firstYear': 1993,
               'source': 'https://example.org/old', 'sourceRefs': ['catalogue:1']}
        index = defaultdict(set, {engine.norm('Known'): {('existing', 1993, 'old')}})
        refs = defaultdict(set)
        with patch.object(engine, 'load', return_value={'approved': [old]}):
            decisions = engine.reserve_reviewed_pc98_reuse(index, refs, [Path('history')])
        self.assertEqual(decisions[0]['matchedWorkId'], 'existing')
        selected, review = archive.choose([row('a', 'Alternate'), row('b', 'Different')], 1,
                                           index, refs, engine.norm, 'batch')
        self.assertEqual(selected[0]['work']['title'], 'Different')
        self.assertEqual(review['reusedExisting'][0]['matchedWorkIds'], ['existing'])

if __name__ == '__main__':
    unittest.main()
