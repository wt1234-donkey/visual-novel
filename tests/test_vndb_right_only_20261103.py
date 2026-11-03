import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import import_vndb_right_only_20261103 as intake

class VndbRightOnlyIntakeTests(unittest.TestCase):
    def test_source_records_dates_counts_and_historical_objects_are_preserved(self):
        intake.check()

    def test_same_title_is_kept_as_an_independent_requested_source_record(self):
        row=intake.source_rows()[0]
        original=intake.work_from(row,145)
        changed={**row,'vID':'v999999999','VNDB链接':'https://vndb.org/v999999999','首发年份':''}
        duplicate=intake.work_from(changed,145)
        self.assertEqual(original['title'],duplicate['title'])
        self.assertNotEqual(original['id'],duplicate['id'])
        self.assertIsNone(duplicate['firstYear'])
        self.assertEqual(duplicate['intakePolicy'],'append-without-deduplication')
