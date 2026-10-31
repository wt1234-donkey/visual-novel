"""Protect per-field narrative provenance and truthful work-level completion."""
import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_narrative_editorial import validate, has_value
from manage_catalogue import restore_historical, load

class NarrativeEditorialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        historical=restore_historical(load(), json.loads((ROOT/'data/management-history.json').read_text()))
        cls.data=historical['editorial']
        cls.catalogue=historical['games']

    def test_frozen_work_review_and_field_sources(self):
        counts=validate(self.data, catalogue=self.catalogue, check_report=False)
        new=len(json.loads((ROOT/'data/non-rpg-intake-18-studios-result.json').read_text())['added']) + len(json.loads((ROOT/'data/non-rpg-six-studios-expansion-result-20261030.json').read_text())['added']) + len(json.loads((ROOT/'data/non-rpg-recommended-intake-result-20261030.json').read_text())['added']) + len(json.loads((ROOT/'data/project-title-year-import-result-20261031.json').read_text())['added'])
        patches=json.loads((ROOT/'data/narrative-evidence-patches-20261030.json').read_text())['entries']
        fully_filled=sum(bool(row.get('position')) and bool(row.get('style')) and bool(row.get('theme')) and bool(row.get('structure')) for row in patches.values())
        partial_filled=len(patches)-fully_filled
        round2=json.loads((ROOT/'data/narrative-evidence-round2-20261030.json').read_text())['entries']
        round2_complete=sum(bool(row.get('position')) and bool(row.get('style')) and bool(row.get('theme')) and bool(row.get('structure')) for row in round2.values())
        round2_partial=len(round2)-round2_complete
        round3=json.loads((ROOT/'data/narrative-evidence-round3-20261030.json').read_text())['entries']
        round3_complete=sum(all(row.get(f) for f in ('position','style','theme','structure')) for row in round3.values())
        round3_partial=len(round3)-round3_complete
        six4=json.loads((ROOT/'data/narrative-evidence-six-studios-r4-20261031.json').read_text())['entries']
        six4_complete=sum(all(row.get(f) for f in ('position','style','theme','structure')) for row in six4.values())
        six4_partial=len(six4)-six4_complete
        round5=json.loads((ROOT/'data/narrative-evidence-giga-light-circus-r5-20261031.json').read_text())['entries']
        round5_complete=sum(all(row.get(f) for f in ('position','style','theme','structure')) for row in round5.values())
        round5_partial=len(round5)-round5_complete
        r6=json.loads((ROOT/'data/narrative-evidence-round3-20261031.json').read_text())['entries']
        r6done=sum(all(row.get(f) for f in ('position','style','theme','structure')) for row in r6.values())
        r6partial=len(r6)-r6done
        latest=json.loads((ROOT/'data/narrative-evidence-rebased-r6-20261031.json').read_text())['entries']
        base53=json.loads((ROOT/'data/narrative-53-pre-merge-r6-audit-20261031.json').read_text())
        self.assertEqual(len(base53['entries']),53)
        self.assertEqual(base53['counts']['missingFields'],121)
        expected={'complete':1534,'partial':35,'missing':18}
        for wid,patch in latest.items():
            self.assertIn(wid,base53['entries'])
            missing=set(base53['entries'][wid]['missing'])
            supplied={field for field in ('position','style','theme','structure') if patch.get(field)}
            self.assertTrue(supplied)
            self.assertTrue(supplied.issubset(missing),f'{wid}: latest batch would overwrite a PR187 field')
            if len(missing)==4:
                expected['missing']-=1
                if missing.issubset(supplied):expected['complete']+=1
                else:expected['partial']+=1
            elif missing.issubset(supplied):
                expected['partial']-=1
                expected['complete']+=1
        seven= json.loads((ROOT/'data/narrative-evidence-seven-r7-20261031.json').read_text())['entries']
        snapshot= json.loads((ROOT/'data/narrative-seven-r7-baseline-20261031.json').read_text())['records']
        self.assertEqual(set(seven),set(snapshot))
        self.assertEqual(len(seven),7)
        for wid,patch in seven.items():
            missing=set(snapshot[wid]['missing'])
            supplied={k for k in ('position','style','theme','structure') if patch.get(k)}
            self.assertEqual(supplied,missing)
            if len(missing)==4:expected['missing']-=1
            else:expected['partial']-=1
            expected['complete']+=1
            for k in supplied:
                self.assertIn(k,self.data['works'][wid]['fieldEvidence'])
                self.assertTrue(self.data['works'][wid]['fieldEvidence'][k]['sourceFields'])
        six8=json.loads((ROOT/'data/narrative-six-final-r8-20261031.json').read_text())['entries']
        self.assertEqual(set(six8),{'g1418','g1419','g1420','g1421','g1448','g1482'})
        for wid,patch in six8.items():
            should={'structure'} if wid=='g1419' else {'position','style','theme','structure'}
            self.assertEqual({k for k in should if patch.get(k)},should)
            for field in should:
                self.assertTrue(self.data['works'][wid][field])
                self.assertIn(field,self.data['works'][wid]['fieldEvidence'])
        expected['missing']-=5
        expected['partial']-=1
        expected['complete']+=6
        final22=json.loads((ROOT/'data/narrative-22-evidence-r9-20261031.json').read_text())['entries']
        frozen22=json.loads((ROOT/'data/narrative-22-baseline-r9-20261031.json').read_text())
        self.assertEqual(len(frozen22['records']),22)
        self.assertEqual(frozen22['counts']['missingFields'],35)
        self.assertEqual(len(final22),8)
        completed_in_r9=0
        for wid,row in final22.items():
            missing=set(frozen22['records'][wid]['missing'])
            supplied={f for f in ('position','style','theme','structure') if row.get(f)}
            self.assertTrue(supplied.issubset(missing),f'{wid}: would override an existing field')
            self.assertTrue(supplied)
            for field in supplied:
                self.assertTrue(self.data['works'][wid]['fieldEvidence'][field]['sources'])
                self.assertTrue(self.data['works'][wid]['fieldEvidence'][field]['sourceFields'])
            if supplied==missing:
                completed_in_r9+=1
                expected['partial']-=1
                expected['complete']+=1
        self.assertEqual(completed_in_r9,7)
        legacy15=json.loads((ROOT/'data/narrative-legacy15-evidence-r10-20261031.json').read_text())['entries']
        self.assertEqual(len(legacy15),6)
        final_five=0
        for wid,patch in legacy15.items():
            supplied={f for f in ('position','style','theme','structure') if patch.get(f)}
            self.assertTrue(supplied)
            for f in supplied:
                self.assertTrue(self.data['works'][wid]['fieldEvidence'][f]['sourceFields'])
                self.assertTrue(self.data['works'][wid]['fieldEvidence'][f]['sources'])
            if all(self.data['works'][wid].get(f) for f in ('position','style','theme','structure')):
                final_five+=1
        self.assertEqual(final_five,5)
        expected['partial']-=5
        expected['complete']+=5
        expected['missing']+=len(json.loads((ROOT/'data/project-title-year-import-result-20261031.json').read_text())['added'])
        self.assertEqual(sum(counts.values()),1339+new)
        self.assertEqual(counts,expected)
        baseline=json.loads((ROOT/'data/narrative-editorial-baseline-20261029.json').read_text())['works']
        for wid,entry in baseline.items():
            self.assertEqual(self.data['works'][wid],entry)
        for wid,patch in {**patches,**round2,**round3,**six4,**round5,**r6,**latest,**seven,**six8,**final22,**legacy15}.items():
            record=self.data['works'][wid]
            self.assertEqual(record['status'],'editorialObservation' if all(record.get(k) for k in ('position','style','theme','structure')) else 'partial')
            for field in ('position','style','theme','structure'):
                if patch.get(field):
                    self.assertTrue(record['fieldEvidence'][field]['sourceFields'])
                    self.assertTrue(record['fieldEvidence'][field]['sources'])

    def test_current_managed_editorial_remains_valid(self):
        validate()

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
