import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from manage_catalogue import apply_package,load,read,restore_historical,validate_history

class ManagementTests(unittest.TestCase):
    def setUp(self):
        self.data=load()
        self.games=read('games.json')
        self.baseline=read('narrative-editorial-baseline-20261029.json')
        self.dossiers={d['id'] for d in read('entity-catalogue.json')['model']['dossiers']}
        old=self.data['editorial']['works']['g089']
        after=copy.deepcopy(old)
        after['basis']+=' 本次仅补充资料适用范围的限定说明。'
        self.package={'schemaVersion':1,'createdAt':'2026-10-31','reason':'测试逐项资料订正及冲突保护','operations':[{'resource':'editorial','key':'g089','before':copy.deepcopy(old),'after':after}]}
    def apply(self,p=None):
        return apply_package(p or self.package,self.data,self.games,self.baseline,self.dossiers)
    def test_proposal_is_non_mutating_and_history_reversible(self):
        before=copy.deepcopy(self.data)
        result=self.apply()
        self.assertEqual(before,self.data)
        self.assertNotEqual(result['editorial']['works']['g089'],before['editorial']['works']['g089'])
        self.assertEqual(restore_historical(result,{'batches':[self.package]}),before)
    def test_stale_record_does_not_overwrite_concurrent_edit(self):
        self.package['operations'][0]['before']['basis']='陈旧的原始记录'
        with self.assertRaisesRegex(AssertionError,'数据库已变化'):self.apply()
    def test_no_arbitrary_paths_and_no_deletions(self):
        self.package['operations'][0]['resource']='../../.github/workflows/test'
        with self.assertRaises(AssertionError):self.apply()
        self.package['operations'][0]['resource']='editorial'
        self.package['operations'][0]['after']=None
        with self.assertRaises(AssertionError):self.apply()
    def test_frozen_eight_cannot_be_overwritten(self):
        op=self.package['operations'][0]
        op.update(key='g039',before=self.data['editorial']['works']['g039'])
        with self.assertRaisesRegex(AssertionError,'最初八部'):self.apply()
    def test_field_evidence_and_source_required(self):
        self.package['operations'][0]['after']['fieldEvidence']['style']['sources']=['javascript:alert(1)']
        with self.assertRaises(AssertionError):self.apply()
    def test_duplicate_operations_rejected(self):
        self.package['operations']*=2
        with self.assertRaisesRegex(AssertionError,'重复'):self.apply()
    def test_invalid_person_cannot_be_used_in_credit(self):
        c=copy.deepcopy(self.data['creators']['credits'][0]);c.update(id='g030-writer-nonexistent',personId='nonexistent')
        self.package['operations']=[dict(resource='credits',key=c['id'],before=None,after=c)]
        with self.assertRaises(AssertionError):self.apply()
    def test_current_history(self):
        validate_history()
if __name__=='__main__':unittest.main()
