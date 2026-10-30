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
        new=len(json.loads((ROOT/'data/non-rpg-intake-18-studios-result.json').read_text())['added']) + len(json.loads((ROOT/'data/non-rpg-six-studios-expansion-result-20261030.json').read_text())['added']) + len(json.loads((ROOT/'data/non-rpg-recommended-intake-result-20261030.json').read_text())['added'])
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
        nextpatch=json.loads((ROOT/'data/narrative-evidence-round3-20261031.json').read_text())['entries']
        nextcomplete=sum(all(row.get(f) for f in ('position','style','theme','structure')) for row in nextpatch.values())
        nextpartial=len(nextpatch)-nextcomplete
        self.assertEqual(sum(counts.values()),1339+new)
        self.assertEqual(counts,{'complete':1318+fully_filled+round2_complete+round3_complete+six4_complete+nextcomplete,'partial':20+partial_filled+round2_partial+round3_partial+six4_partial+nextpartial,'missing':1+new-len(patches)-len(round2)-len(round3)-len(six4)-len(nextpatch)})
        baseline=json.loads((ROOT/'data/narrative-editorial-baseline-20261029.json').read_text())['works']
        for wid,entry in baseline.items():
            self.assertEqual(self.data['works'][wid],entry)
        for wid,patch in {**patches,**round2,**round3,**six4,**nextpatch}.items():
            record=self.data['works'][wid]
            self.assertEqual(record['status'],'editorialObservation' if all(record.get(k) for k in ('position','style','theme','structure')) else 'partial')
            for field in ('position','style','theme','structure'):
                if patch.get(field):
                    self.assertTrue(record['fieldEvidence'][field]['sourceFields'])
                    self.assertTrue(record['fieldEvidence'][field]['sources'])

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
