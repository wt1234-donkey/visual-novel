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
    def new_work_package(self):
        wid='g'+str(max(int(w['id'][1:]) for w in self.games['works'])+1);source='https://example.org/management-test'
        w=dict(id=wid,title='管理台测试原作 '+wid,originalTitle='Management Test Original '+wid,firstYear=2026,category='视觉小说',subcategory='单线视觉小说',genre='测试叙事作品',characters=['测试主人公'],charactersNote='',synopsis='独立作品收录管线的隔离测试，不发布至正式数据库。',notes='',source=source,interactionModes=['阅读推进'],interactionNote='通过阅读推进叙事，仅供测试。',interactionBasis='来源核对',interactionSources=[source])
        c=dict(id=wid+'-c-original',workId=wid,label='原作／首批内容',firstYear=2026,basis='original',evidence='原作首批版本及内容身份的隔离测试资料。',source=source,evidenceReleaseIds=[wid+'-v1'],addedContent=[])
        r=dict(id=wid+'-v1',workId=wid,year=2026,platform='Windows',publisher='Key',publisherCompanies=['Key'],kind='原作',voice='未核实',differences='测试的首次发行批次，仅供隔离测试。',source=source,contentVersionId=c['id'],contentRelation='original',contentNote='测试的首次发行批次，仅供隔离测试。',releaseRole='contentDebut')
        return dict(schemaVersion=1,createdAt='2026-10-31',reason='独立作品隔离测试',operations=[dict(resource='newWork',key=wid,before=None,after=dict(work=w,contentVersions=[c],platformReleases=[r]))])
    def test_add_original_and_first_release_without_mutating_input(self):
        p=self.new_work_package();result=self.apply(p)
        self.assertEqual(len(result['games']['works']),len(self.data['games']['works'])+1)
        self.assertEqual(restore_historical(result,{'batches':[p]}),self.data)
    def test_duplicate_names_ids_and_missing_original_are_rejected(self):
        p=self.new_work_package();p['operations'][0]['after']['work']['title']=self.games['works'][0]['title']
        with self.assertRaisesRegex(AssertionError,'重复'):self.apply(p)
        p=self.new_work_package();p['operations'][0]['after']['contentVersions']=[]
        with self.assertRaises(AssertionError):self.apply(p)
    def test_new_work_cannot_insert_later_port_or_claim_new_content(self):
        p=self.new_work_package();p['operations'][0]['after']['platformReleases'][0]['contentRelation']='same'
        with self.assertRaises(AssertionError):self.apply(p)
    def test_second_first_batch_platform_shares_content_identity(self):
        p=self.new_work_package();bundle=p['operations'][0]['after'];r=copy.deepcopy(bundle['platformReleases'][0]);r.update(id=bundle['work']['id']+'-v2',platform='Linux');bundle['platformReleases'].append(r);bundle['contentVersions'][0]['evidenceReleaseIds'].append(r['id'])
        self.assertEqual(len(self.apply(p)['games']['contentVersions']),len(self.games['contentVersions'])+1)
    def test_current_history(self):
        validate_history()
if __name__=='__main__':unittest.main()
