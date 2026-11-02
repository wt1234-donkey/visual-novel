"""Only unresolved catalogue rows resume; reviewed aliases block IFDB duplicates."""
from collections import defaultdict
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import import_basic_r134_r135_20261103 as engine


class PC98PendingResumeTests(unittest.TestCase):
    def rows(self):
        return [{'catalogue': 'test-catalogue', 'sourceId': str(i)} for i in range(5)]

    def test_resume_keeps_original_order_and_excludes_admitted_or_reused_rows(self):
        prior = {'records': [
            {'catalogue': 'test-catalogue', 'sourceId': '4', 'status': 'missing-year-held'},
            {'catalogue': 'test-catalogue', 'sourceId': '2', 'status': 'reviewed-candidate'},
            {'catalogue': 'test-catalogue', 'sourceId': '1', 'status': 'needs-primary-year-and-alias-review'},
            {'catalogue': 'test-catalogue', 'sourceId': '0', 'status': 'reused-title-alias-and-year'},
            {'catalogue': 'test-catalogue', 'sourceId': '3', 'status': 'outside-narrative-adv-rpg-scope'}]}
        self.assertEqual([r['sourceId'] for r in engine.unresolved_pc98_rows(self.rows(), prior)], ['1', '4'])

    def test_saved_source_id_not_in_snapshot_is_rejected(self):
        prior = {'records': [{'catalogue': 'test-catalogue', 'sourceId': 'missing', 'status': 'missing-year-held'}]}
        with self.assertRaises(AssertionError):
            engine.unresolved_pc98_rows(self.rows(), prior)

    def test_duplicate_snapshot_source_id_cannot_replay_a_pending_row(self):
        prior = {'records': [{'catalogue': 'test-catalogue', 'sourceId': '0', 'status': 'missing-year-held'}]}
        with self.assertRaises(AssertionError):
            engine.unresolved_pc98_rows([self.rows()[0], self.rows()[0]], prior)

    def row(self, uid, title):
        return {'tuid': uid * 16, 'title': title, 'aliases': [], 'firstYear': 1992,
            'published': '1992-01-01 00:00:00', 'author': 'Author', 'system': 'Inform',
            'language': 'en', 'sourceRefs': ['ifdb:' + uid * 16], 'archiveLinks': []}

    def test_reviewed_reuse_alias_blocks_a_different_ifdb_display_title(self):
        index = defaultdict(set, {engine.norm('既有原题'): {('old-work', 1992, 'historical-dossier')}})
        refs = defaultdict(set)
        evidence = {'title': '既有原题', 'aliases': ['Alternate Latin Title'], 'firstYear': 1992,
            'source': 'https://www.gamepres.org/catalog/?id=test', 'sourceRefs': ['gamepres:test']}
        with patch.object(engine, 'load', return_value={'approved': [evidence]}):
            decisions = engine.reserve_reviewed_pc98_reuse(index, refs)
        self.assertEqual(decisions[0]['matchedWorkId'], 'old-work')
        selected, review = engine.ifdb.choose([self.row('a', 'Alternate Latin Title'), self.row('b', 'New distinct work')],
            1, index, refs, engine.norm, 'test')
        self.assertEqual(selected[0]['sourceId'], 'b' * 16)
        self.assertEqual(review['reusedExisting'][0]['matchedWorkIds'], ['old-work'])

    def test_invalid_ifdb_title_has_a_recorded_hold_and_reconciles_scan_counts(self):
        refs = defaultdict(set)
        selected, review = engine.ifdb.choose([self.row('a', '...'), self.row('b', 'New distinct work')],
            1, defaultdict(set), refs, engine.norm, 'test')
        self.assertEqual(len(selected), 1)
        self.assertEqual(review['dispositions'], {'invalid-name-held': 1})
        self.assertEqual(review['heldForIdentityReview'][0]['sourceId'], 'a' * 16)
        self.assertEqual(review['scanned'], review['selected'] + len(review['heldForIdentityReview']) + len(review['reusedExisting']))
        self.assertNotIn('ifdb:' + 'a' * 16, refs)


if __name__ == '__main__':
    unittest.main()
