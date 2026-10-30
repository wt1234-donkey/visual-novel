"""Protect per-field narrative provenance and truthful work-level completion."""
import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_narrative_editorial import validate, has_value

class NarrativeEditorialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'data/discovery-editorial.json').read_text())

    def test_frozen_work_review_and_field_sources(self):
        counts=validate(self.data)
        self.assertEqual(sum(counts.values()),1339)
        self.assertEqual(counts,{'complete':1318,'partial':20,'missing':1})

    def test_existing_record_does_not_imply_four_fields(self):
        record=self.data['works']['g745']
        self.assertTrue(record['basis'])
        self.assertFalse(any(has_value(record,f) for f in ('position','style','theme','structure')))
        self.assertTrue(record['openQuestions'])

    def test_placeholder_cannot_be_counted_as_completed(self):
        changed=copy.deepcopy(self.data)
        changed['works']['g013']['style']=['待核实']
        with self.assertRaisesRegex(AssertionError,'placeholder'):
            validate(changed)

    def test_field_source_cannot_be_replaced_by_work_link_only(self):
        changed=copy.deepcopy(self.data)
        changed['works']['g013']['fieldEvidence']['structure']['sources']=[]
        with self.assertRaisesRegex(AssertionError,'invalid evidence source'):
            validate(changed)

    def test_original_eight_annotations_are_preserved(self):
        changed=copy.deepcopy(self.data)
        changed['works']['g039']['theme']=['替换原编目']
        with self.assertRaisesRegex(AssertionError,'historical editorial'):
            validate(changed)

if __name__=='__main__':
    unittest.main()
