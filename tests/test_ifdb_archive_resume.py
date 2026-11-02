"""Archive continuation is bound to a snapshot and rechecks the current identity pools."""
import copy
import sys
import unittest
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import ifdb_archive_identity as f


class IFDBArchiveResumeTests(unittest.TestCase):
    def rows(self):
        return [{'tuid':chr(97+i)*16,'title':title,'aliases':[],
                 'firstYear':1993,'published':'1993-01-01 00:00:00','author':'Author',
                 'system':'Inform','language':'en','sourceRefs':['ifdb:'+chr(97+i)*16],
                 'archiveLinks':[]} for i,title in enumerate(['Prior selection','Reserved candidate','New selection'])]

    def test_resume_skips_prior_positions_and_counts_only_new_scan(self):
        rows=self.rows()
        index=defaultdict(set,{'reserved candidate':{('vndb-v999',1993,'reserved-nextmoe')}})
        selected,review=f.choose(rows,1,index,defaultdict(set),str.casefold,'batch',start_position=2)
        self.assertEqual([r['sourceId'] for r in selected],['c'*16])
        self.assertEqual(selected[0]['archivePosition'],3)
        self.assertEqual(review['startPosition'],2)
        self.assertEqual(review['nextPosition'],4)
        self.assertEqual(review['scanned'],2)
        self.assertEqual(review['dispositions'],{'reused-title-alias':1})
        self.assertEqual(review['reusedExisting'][0]['matchedWorkIds'],['vndb-v999'])
        self.assertNotIn('prior selection',index)

    def test_resumed_source_identity_rechecked_case_insensitively(self):
        rows=self.rows()
        rows[1]['sourceRefs'].append('ifid:ABC-123')
        refs=defaultdict(set,{'ifid:abc-123':{'existing-if-work'}})
        selected,review=f.choose(rows,1,defaultdict(set),refs,str.casefold,'batch',start_position=2)
        self.assertEqual(selected[0]['sourceId'],'c'*16)
        self.assertEqual(review['dispositions'],{'reused-external-identity':1})
        self.assertEqual(refs['ifid:abc-123'],{'existing-if-work'})

    def test_zero_slots_does_not_advance_saved_position(self):
        selected,review=f.choose(self.rows(),0,defaultdict(set),defaultdict(set),str.casefold,'batch',start_position=3)
        self.assertEqual(selected,[])
        self.assertEqual((review['scanned'],review['nextPosition']),(0,3))

    def test_resume_rejects_mismatched_snapshot_or_invalid_position(self):
        valid={'url':f.ARCHIVE_URL,'sha256':f.ARCHIVE_SHA256,'nextPosition':219}
        self.assertEqual(f.resume_position(valid),219)
        for key,value in [('url','https://example.com/export.zip'),('sha256','0'*64),
                          ('nextPosition',0),('nextPosition',True),('nextPosition','219')]:
            review=copy.deepcopy(valid); review[key]=value
            with self.assertRaises(ValueError): f.resume_position(review)
        for position in (0,-1,5,True):
            with self.assertRaises(ValueError):
                f.choose(self.rows(),1,defaultdict(set),defaultdict(set),str.casefold,'batch',start_position=position)

    def test_end_of_archive_does_not_invent_missing_identities(self):
        with self.assertRaisesRegex(RuntimeError,'Only 0 safe IFDB identities'):
            f.choose(self.rows(),1,defaultdict(set),defaultdict(set),str.casefold,'batch',start_position=4)

if __name__=='__main__': unittest.main()
