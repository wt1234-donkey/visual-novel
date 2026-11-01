"""Identity reuse and diversity selection must not create or drop works."""
import sys
import unittest
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import import_basic_r22_cont_r23_20261101 as batch


class BatchSelectionTests(unittest.TestCase):
    def candidate_args(self):
        return ({'id':'v9001','released':'1999-04-02','devstatus':0,'developers':[]},
                'nextmoe','123',['Example'],defaultdict(set),defaultdict(set),
                batch.Counter(),[],[],batch.B23)

    def test_exact_vndb_identity_reuses_old_nextmoe_id(self):
        args=self.candidate_args()
        args[5]['vndb:v9001'].add('nextmoe-old-77')
        self.assertIsNone(batch.candidate(*args))
        self.assertEqual(args[7][0]['matchedWorkIds'],['nextmoe-old-77'])
        self.assertEqual(args[6]['reused-external-identity'],1)

    def test_same_name_with_conflicting_year_is_held(self):
        args=self.candidate_args()
        args[4]['example'].add(('original',1988,'main'))
        self.assertIsNone(batch.candidate(*args))
        self.assertEqual(args[6]['name-year-conflict-held'],1)
        self.assertEqual(args[8][0]['firstYear'],1999)

    def test_new_nextmoe_identity_uses_canonical_vndb_id_and_date(self):
        args=self.candidate_args()
        row=batch.candidate(*args)
        self.assertEqual(row['work']['id'],'vndb-v9001')
        self.assertEqual(row['work']['firstYear'],1999)
        self.assertEqual(row['work']['sourceRefs'],['nextmoe:123','vndb:v9001'])

    def test_balancing_includes_rare_era_and_defers_every_unselected_work(self):
        def row(i,year,producer,kind):
            return {'work':{'id':str(i),'firstYear':year},'developers':[{'id':producer,'type':kind}]}
        pool=[row(i,2020,'p1','co') for i in range(8)]
        pool += [row(8,1980,'p2','co'),row(9,2020,'p3','in')]
        registry={'works':[{'firstYear':2020} for _ in range(100)]}
        with patch.object(batch,'CAP',4):
            chosen,deferred=batch.diverse_select(pool,registry)
        self.assertEqual(len(chosen),4)
        self.assertTrue({'8','9'}.issubset({r['work']['id'] for r in chosen}))
        self.assertEqual({r['work']['id'] for r in chosen+deferred},{str(i) for i in range(10)})
        self.assertFalse({r['work']['id'] for r in chosen}&{r['work']['id'] for r in deferred})


if __name__=='__main__':
    unittest.main()
