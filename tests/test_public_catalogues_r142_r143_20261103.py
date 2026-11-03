import copy
import sys
import unittest
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import import_basic_r142_r143_20261103 as m

class PublicIntakeTest(unittest.TestCase):
    def sample(self):
        return {'id':123456,'name':'Example Story','name_cn':'示例故事','date':'1992-02-01',
                'infobox':[{'key':'游戏类型','value':'RPG'},{'key':'发行日期','value':'1992年2月1日'}],
                'summary':'故事的主人公踏上旅程。','meta_tags':[]}

    def test_rpg_tag_without_narrative_evidence_is_held(self):
        row=self.sample();row['summary']='战斗升级';self.assertEqual(m.bangumi_candidate(row)[1],'narrative-rpg-evidence-held')

    def test_release_year_disagreement_is_held(self):
        row=self.sample();row['infobox'][1]['value']='1993';self.assertEqual(m.bangumi_candidate(row)[1],'source-year-conflict-held')

    def test_remaster_in_description_does_not_create_identity(self):
        row=self.sample();row['summary']+='重制版本。';self.assertEqual(m.bangumi_candidate(row)[1],'possible-edition-or-dependent-content-held')

    def test_alias_and_casefolded_external_id_block_duplicates(self):
        c,_=m.bangumi_candidate(self.sample())
        index=defaultdict(set,{m.e.norm('示例故事'):{('old',1992,'catalogue')}})
        self.assertEqual(m.decide(copy.deepcopy(c),index,defaultdict(set)),'existing-identity')
        c['firstYear']=1993
        self.assertEqual(m.decide(c,index,defaultdict(set)),'name-year-or-multiple-identity-held')
        c,_=m.bangumi_candidate(self.sample())
        self.assertEqual(m.decide(c,defaultdict(set),{'bangumi:123456':{'old'}}),'existing-identity')

    def test_actual_batches_preserve_base_and_caps(self):
        old,new,audits,_=m.build()
        self.assertEqual(new['works'][:len(old['works'])],old['works'])
        self.assertEqual(new['summary']['accepted'],len(new['works']))
        for n in (142,143):
            audit=audits[m.ROOT/f'data/public-catalogues-review-20261103-r{n}.json']
            self.assertLessEqual(audit['summary']['newDistinctWorks'],500)
            self.assertEqual(audit['summary']['scannedRecords'],sum(audit['summary']['dispositions'].values()))
            self.assertTrue(all(r.get('source') for r in audit['records']))

    def test_shortened_subtitle_is_held_instead_of_added(self):
        index=m.NameIndex({m.e.norm('すまいる Cubic! -水平線まで何マイル？アフター＆アナザーストーリーズ-'):{('old',2009,'catalogue')}})
        index.refresh_prefixes()
        c={'title':'すまいるCubic！','aliases':[],'source':'https://bgm.tv/subject/11713','sourceRefs':[],'firstYear':2009}
        self.assertEqual(m.decide(c,index,defaultdict(set)),'possible-title-variant-held')

if __name__=='__main__':unittest.main()
