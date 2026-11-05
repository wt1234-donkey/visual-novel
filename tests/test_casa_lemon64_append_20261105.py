import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('casa_lemon_intake', ROOT/'scripts/import_casa_lemon64_20261105.py')
intake = importlib.util.module_from_spec(spec)
spec.loader.exec_module(intake)


class CasaLemonIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.manifest = intake.source_rows()

    def test_full_selection_and_batch_boundaries(self):
        self.assertEqual(len(self.rows), 5480)
        works = []
        for n in range(211, 222):
            block, summary, audit = intake.build_batch(self.rows,n,102204+(n-211)*500)
            self.assertEqual(len(block),480 if n==221 else 500)
            self.assertEqual(summary['deduplication'],'not-performed')
            works.extend(block)
        self.assertEqual(len({w['id'] for w in works}),5480)
        self.assertEqual(sum(w['sourceSubset']=='unmatched' for w in works),2381)
        self.assertEqual(sum(w['sourcePlatform']=='CASA' for w in works),5028)
        self.assertEqual(sum(w['sourcePlatform']=='Lemon64' for w in works),452)
        self.assertEqual(sum(w['firstYear'] is None for w in works),24)

    def test_source_year_and_limited_evidence_stay_explicit(self):
        row = next(r for r in self.rows if r['来源平台']=='Lemon64' and r['目录年份'] is None)
        w = intake.work_from(row,211)
        self.assertIsNone(w['firstYear'])
        self.assertIn('非跨平台原作首发核定',w['yearBasis'])
        self.assertIn('/games/list.php?',w['source'])
        self.assertNotIn('lemon64:',str(w['sourceRefs']))
        self.assertTrue(w['sourceRefs'][0].startswith('lemon64-snapshot:'))
        self.assertTrue(w['originalWorkbookRow'] and w['sourceWorkbookRow'])
        self.assertFalse(set(w)&{'contentVersions','platformReleases','synopsis','creators','interactionModes'})
        row = copy.deepcopy(self.rows[0]);row['目录年份']=True
        with self.assertRaisesRegex(RuntimeError,'Invalid directory year'):
            intake.work_from(row,211)

    def test_no_name_or_source_dedup_but_complete_rerun_is_idempotent(self):
        template=self.rows[0];rows=[]
        for i in range(501):
            row=copy.deepcopy(template);row['CASA ID']=str(90000+i)
            row['作品/列表链接']=f'https://solutionarchive.com/game/id%2C{90000+i}/Same.html'
            row['sourceSnapshotRow']=i+1;row['sourceWorkbookRow']=i+11
            row['sourceSubset']='suspected-existing' if i==500 else 'unmatched';rows.append(row)
        old={'id':'existing','title':template['作品原名'],'source':rows[0]['作品/列表链接'],'sourceRefs':['casa:90000']}
        manifest={'baseWorksCanonicalSha256':intake.canonical_hash([old])}
        registry={'works':[old],'batches':[],'summary':{k:1 for k in ('accepted','candidates','promotedBasic','addedToMainIdentityLayer')}}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data').mkdir();db=root/'data/db.json';db.write_text(json.dumps(registry))
            with patch.multiple(intake,ROOT=root,DB=db,SOURCE=root/'data/source.b64',EXPECTED_BASE=1,EXPECTED_INPUT=501,LAST_BATCH=212),patch.object(intake,'source_rows',return_value=(rows,manifest)):
                before=db.read_bytes();intake.run(dry_run=True);self.assertEqual(db.read_bytes(),before)
                intake.run();result=json.loads(db.read_text());self.assertEqual(len(result['works']),502)
                self.assertEqual(result['works'][0],old)
                self.assertEqual(result['works'][1]['source'],old['source'])
                self.assertEqual(result['works'][-1]['sourceSubset'],'suspected-existing')
                self.assertEqual([b['summary']['appendedRecords'] for b in result['batches']],[500,1])
                before=db.read_bytes();intake.run();self.assertEqual(db.read_bytes(),before)

    def test_baseline_changes_are_rejected(self):
        with self.assertRaisesRegex(RuntimeError,'Existing records changed'):
            intake.check_registry({'summary':{'accepted':1},'works':[{'id':'changed'}]}, {'baseWorksCanonicalSha256':intake.canonical_hash([{'id':'original'}])})


if __name__ == '__main__':
    unittest.main()
