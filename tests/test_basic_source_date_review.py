import sys
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from basic_source_date_review import reviewed_add_fresh


class CrossSourceOriginalYearTests(unittest.TestCase):
    def setUp(self):
        self.ctx = {'kind': 'nextmoe', 'counts': Counter(), 'held': []}
        self.index, self.refs = {}, {}

    def invoke(self, year, next_date, kind='nextmoe'):
        self.ctx['kind'] = kind
        original = Mock(return_value='accepted')
        item = {'id': 'v56804', 'released': '2016-08-28'}
        result = reviewed_add_fresh(original, lambda _: year, self.ctx, item,
            '53002', ['CROSSOVER'], self.index, self.refs,
            {'nextmoeSourceReleased': next_date})
        return result, original

    def test_later_vndb_original_year_is_held_without_reserving_identity(self):
        result, original = self.invoke(2016, '2005-05-30')
        self.assertIsNone(result)
        original.assert_not_called()
        self.assertEqual(self.ctx['counts']['source-date-conflict-held'], 1)
        self.assertEqual(self.ctx['held'][0]['sourceReleased'], '2016-08-28')
        self.assertEqual(self.ctx['held'][0]['nextmoeSourceReleased'], '2005-05-30')
        self.assertEqual((self.index, self.refs), ({}, {}))

    def test_earlier_canonical_year_is_preserved_for_later_editions(self):
        result, original = self.invoke(2003, '2008-05-30')
        self.assertEqual(result, 'accepted')
        original.assert_called_once()
        self.assertEqual(self.ctx['held'], [])

    def test_same_year_uses_existing_name_and_identity_checks(self):
        result, original = self.invoke(2005, '2005-05-30')
        self.assertEqual(result, 'accepted')
        original.assert_called_once()

    def test_unknown_dates_and_vndb_lane_keep_existing_admission_rules(self):
        for year, date, kind in [(2016, None, 'nextmoe'),
                                 (None, '2005-05-30', 'nextmoe'),
                                 (2016, '2005-05-30', 'vndb')]:
            with self.subTest(year=year, date=date, kind=kind):
                result, original = self.invoke(year, date, kind)
                self.assertEqual(result, 'accepted')
                original.assert_called_once()

    def test_saved_queue_rechecks_both_dates_before_candidate_reservation(self):
        import import_basic_r50_r51_20261101 as importer
        engine = importer.engine
        old = {'vndbId': 'v56804', 'sourceId': '53002',
               'sourceReleased': '2016-08-28', 'sourceDevstatus': 0,
               'developers': [], 'nextmoeSourceReleased': '2005-05-30',
               'work': {'id': 'vndb-v56804', 'title': 'CROSSOVER', 'aliases': []}}
        ctx = engine.context('nextmoe', 'test', engine.ROOT / 'unused-input',
                             engine.ROOT / 'unused-output')
        with patch.object(engine, 'load', return_value={'deferredEligible': [old]}), \
             patch.object(engine.source, 'candidate', importer.reviewed_candidate), \
             patch.object(importer, 'prior_candidate') as original:
            engine.drain(ctx, {}, {})
        original.assert_not_called()
        self.assertEqual(ctx['pendingInput'], 1)
        self.assertEqual(ctx['pending'], [])
        self.assertEqual(ctx['queueReview'][0]['status'], 'held')
        self.assertEqual(ctx['counts']['source-date-conflict-held'], 1)
