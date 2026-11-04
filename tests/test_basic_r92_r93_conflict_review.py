"""Protect explicit identity decisions, historical objects, and future intake reuse."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import basic_identity_decisions as decisions
import review_basic_r92_r93_conflicts_20261102 as review
import import_basic_r22_cont_r23_20261101 as source


class ReviewedIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = review.review()
        cls.new = {w['id']: w for w in review.additions(cls.audit)}

    def test_exact_delta_and_no_historical_rewrites(self):
        review.check()

    def test_later_append_is_allowed_but_protected_history_is_not(self):
        current = source.load(source.REG)
        appended = copy.deepcopy(next(w for w in reversed(current['works']) if w['mainPlacement'] == 'promoted-basic'))
        appended.update(id='future-test-identity', indexId='future-test-index', batch='future-test')
        current['works'].append(appended)
        current['batches'].append({'id': 'future-test', 'summary': {'candidates': 1}})
        for key in ('candidates', 'accepted', 'promotedBasic', 'addedToMainIdentityLayer'):
            current['summary'][key] += 1
        load = source.load
        with patch.object(source, 'load', side_effect=lambda p: current if p == source.REG else load(p)):
            review.check()
            current['works'][0]['firstYear'] += 1
            with self.assertRaisesRegex(AssertionError, 'Existing work objects'):
                review.check()

    def test_same_name_different_creator_is_kept_separate(self):
        work = self.new['vndb-v42823']
        self.assertEqual(work['firstYear'], 2022)
        self.assertEqual(decisions.reviewed_name_matches(work), {('g003', 1982)})
        changed = copy.deepcopy(work)
        changed['firstYear'] = 1982
        self.assertEqual(decisions.reviewed_name_matches(changed), set())
        self.assertEqual(decisions.reviewed_name_matches({'id': 'unknown', 'title': 'Deadline', 'firstYear': 2022}), set())

    def test_official_full_products_are_not_keyword_demos(self):
        for vid in ('v43131', 'v43222', 'v43246', 'v44020'):
            self.assertIn('vndb-' + vid, self.new)
        self.assertEqual(self.new['vndb-v44020']['firstYear'], 2025)
        self.assertIn('2023', self.new['vndb-v44020']['yearBasis'])

    def test_reused_ifdb_sources_route_to_old_ids(self):
        registry = source.load(source.REG)
        refs = source.identity_map(registry)
        self.assertEqual(decisions.reviewed_identity_targets(registry,refs['ifdb:ug3qu521hze8bsvz']), {'g129'})
        self.assertEqual(decisions.reviewed_identity_targets(registry,refs['ifdb:6dzy6mc93tf0nzfs']), {'g113'})
        self.assertEqual(decisions.reused_source_identities(set()), {})

    def test_unresolved_records_stay_out_and_all_queues_remain(self):
        for wid in ('vndb-v43324', 'vndb-v42946', 'ifdb-5mwsd31guqlqj0kl'):
            self.assertNotIn(wid, self.new)
        paths = self.audit['inputAudits']
        self.assertEqual(sum(len(source.load(ROOT / p)['deferredEligible']) for p in paths), 292)


if __name__ == '__main__':
    unittest.main()
