import copy
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_work_edits import validate

class WorkEditValidationTests(unittest.TestCase):
    def store(self):
        entry=dict(id='isolated-change',revision=1,at='2026-11-01T02:00:00Z',actor='test',reason='核实并补充网站作品备注',sources=['https://example.org/evidence'],before={},after={'notes':'有来源的独立验证备注'})
        return dict(schemaVersion=1,records={'g039':dict(revision=1,overrides=entry['after'].copy(),recent=[entry])})
    def test_saved_overlay_validates_without_changing_source(self):
        store=self.store();before=copy.deepcopy(store);self.assertEqual(validate(store),1);self.assertEqual(store,before)
    def test_history_is_capped_at_three_and_must_match_current_values(self):
        store=self.store();store['records']['g039']['recent']*=4
        with self.assertRaises(AssertionError):validate(store)
        store=self.store();store['records']['g039']['overrides']['notes']='不相符'
        with self.assertRaises(AssertionError):validate(store)
    def test_protected_identity_and_unsafe_urls_are_rejected(self):
        store=self.store();store['records']['g039']['overrides']['firstYear']=2026
        with self.assertRaises(AssertionError):validate(store)
        store=self.store();store['records']['g039']['recent'][0]['sources']=['javascript:alert(1)']
        with self.assertRaises(AssertionError):validate(store)
    def test_creator_names_can_be_added_or_cleared_without_sources(self):
        store=self.store();row=store['records']['g039'];entry=row['recent'][0]
        entry['sources']=[];entry['after']={'writerNames':['剧作甲','剧作乙'],'artistNames':['画师甲'],'musicianNames':['音乐甲']}
        row['overrides']=copy.deepcopy(entry['after']);self.assertEqual(validate(store),1)
        entry['before']=copy.deepcopy(entry['after']);entry['after']={};row['overrides']={}
        self.assertEqual(validate(store),1)
    def test_no_source_exception_cannot_change_other_fields_or_accept_bad_names(self):
        store=self.store();row=store['records']['g039'];entry=row['recent'][0];entry['sources']=[]
        with self.assertRaises(AssertionError):validate(store)
        for names in ('不是列表',['重复','重复'],[''],[1]):
            entry['after']={'writerNames':names};row['overrides']=copy.deepcopy(entry['after'])
            with self.assertRaises(AssertionError):validate(store)
        entry['before']={'notes':'更正过的备注'};entry['after']={'writerNames':['剧作甲']};row['overrides']=entry['after'].copy()
        with self.assertRaises(AssertionError):validate(store)
if __name__=='__main__':unittest.main()
