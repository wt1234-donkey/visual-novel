"""Saved queue priority, complete accounting and opaque cursor continuation."""
import sys
import unittest
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import import_basic_r24_r25_20261101 as batch


class QueueContinuationTests(unittest.TestCase):
    def row(self,i,year=2000):
        return {'work':{'id':str(i),'firstYear':year},'developers':[]}

    def test_saved_candidates_take_priority_over_rare_live_years(self):
        pending=[self.row(1),self.row(2)]
        fresh=[self.row(3,1980),self.row(4,1990)]
        with patch.object(batch,'CAP',2):
            selected,left=batch.select_pending_first(pending,fresh,{'works':[]})
        self.assertEqual({r['work']['id'] for r in selected},{'1','2'})
        self.assertEqual({r['work']['id'] for r in left},{'3','4'})

    def test_queue_larger_than_cap_does_not_lose_rows_or_admit_live(self):
        pending=[self.row(i) for i in range(3)]
        fresh=[self.row(10,1980)]
        with patch.object(batch,'CAP',2):
            selected,left=batch.select_pending_first(pending,fresh,{'works':[]})
        self.assertEqual(len(selected),2)
        self.assertNotIn('10',{r['work']['id'] for r in selected})
        self.assertEqual({r['work']['id'] for r in selected+left},{'0','1','2','10'})

    def test_resume_uses_returned_opaque_cursor_without_decoding(self):
        audit={'summary':{'paginationTrace':[{'lane':'era-keyset',
            'releasedAfter':'1976-01-01','releasedBefore':'1999-12-31',
            'cursorUsed':'cur_old','nextCursor':'cur_returned_opaque'}]}}
        plan=batch.nextmoe_resume_plan(audit)
        self.assertEqual(plan[0]['cursor'],'cur_returned_opaque')
        self.assertEqual(plan[0]['releasedAfter'],'1976-01-01')
        self.assertIsNone(plan[1]['cursor'])

    def test_exhausted_window_moves_to_next_era(self):
        audit={'summary':{'paginationTrace':[{'lane':'era-keyset',
            'releasedAfter':'1976-01-01','releasedBefore':'1999-12-31',
            'nextCursor':None}]}}
        plan=batch.nextmoe_resume_plan(audit)
        self.assertEqual(plan[0]['releasedAfter'],'2000-01-01')
        self.assertIsNone(plan[0]['cursor'])

    def test_drain_records_existing_identity_without_creating_a_candidate(self):
        old={'work':{'id':'vndb-v9001','title':'Saved title','aliases':[]},
             'vndbId':'v9001','sourceId':'900','sourceReleased':'1999-04-02',
             'sourceDevstatus':0,'developers':[]}
        ctx=batch.context('nextmoe',batch.B25,batch.ROOT/'data/old-audit.json',batch.A25)
        refs=defaultdict(set,{'vndb:v9001':{'nextmoe-existing'}})
        with patch.object(batch,'load',return_value={'deferredEligible':[old]}):
            batch.drain(ctx,defaultdict(set),refs)
        self.assertEqual(ctx['pending'],[])
        self.assertEqual(ctx['pendingInput'],1)
        self.assertEqual(ctx['queueReview'][0]['status'],'reused-identity')
        self.assertEqual(ctx['queueReview'][0]['resolution']['matchedWorkIds'],['nextmoe-existing'])


if __name__=='__main__':
    unittest.main()
