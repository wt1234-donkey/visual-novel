"""Regression checks for second review of last 20 isolated identities."""
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import review_basic_r118_r119_last20_20261102 as review
import import_basic_r22_cont_r23_20261101 as src

class Last20ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit=json.loads(review.OUT.read_text(encoding='utf-8'))

    def test_exact_twenty_with_evidence(self):
        self.assertEqual(self.audit['summary'],{
            'reviewed':20,'registeredDistinct':19,
            'reusedExisting':1,'remainingHeld':0})
        self.assertEqual(len(self.audit['decisions']),20)
        self.assertTrue(all(d['sourceUrls'] for d in self.audit['decisions']))

    def test_regression_and_original_rows_preserved(self):
        review.check()

    def test_no_false_1982_new_work(self):
        reg=json.loads(src.REG.read_text(encoding='utf-8'))
        refs=src.identity_map(reg)
        self.assertEqual(refs['ifdb:x7cvej7bm7ixiz0a'],{'ai-earthquake'})
        self.assertNotIn('ifdb-x7cvej7bm7ixiz0a',{w['id'] for w in reg['works']})

    def test_shipwreck_is_distinct_from_1986_work(self):
        self.assertEqual([d['sourceIdentity'] for d in self.audit['decisions']
          if d['status']=='held'],[])
        reg=json.loads(src.REG.read_text(encoding='utf-8'))
        works={w['id']:w for w in reg['works']}
        self.assertEqual(works['ifdb-iq9wxtd9a7vpcy2g']['firstYear'],1987)
        self.assertEqual(works['ifdb-1j9p7lpcoj2sf05i']['firstYear'],1986)

    def test_distinct_spinoffs_and_dates(self):
        new={w['id']:w for w in self.audit['worksToAppend']}
        for ident,year in [('vndb-v62070',2023),('vndb-v62101',2021),
                           ('vndb-v62160',2003),('vndb-v62532',2025),
                           ('vndb-v62845',2026)]:
            self.assertEqual(new[ident]['firstYear'],year)
        self.assertEqual(len(new),19)

if __name__=='__main__':
    unittest.main()
