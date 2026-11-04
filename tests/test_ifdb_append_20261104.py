import hashlib
import importlib.util
import json
import tempfile
import unittest
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import basic_identity_decisions
spec = importlib.util.spec_from_file_location('ifdb_append', ROOT/'scripts/import_ifdb_append_20261104.py')
intake = importlib.util.module_from_spec(spec)
spec.loader.exec_module(intake)


def row(uid, subset, position, year=2000):
    return {'IFDB_TUID': uid*16, '作品名称': 'An existing title', '发行年份': year,
            '作者或创作主体': 'Source author', 'IFDB页面': 'https://ifdb.org/viewgame?id='+uid*16,
            'sourceSubset': subset, 'sourceSnapshotRow': position,
            'sourceSheet': '未匹配作品' if subset=='unmatched' else '同名及版本待核',
            'sourceWorksheetRow': position+5, '基础库候选ID': 'original' if subset=='suspected-existing' else ''}


class IfdbAppendTests(unittest.TestCase):
    def test_existing_external_id_and_title_are_still_appended_and_reruns_do_not_repeat_batch(self):
        old = {'id':'original','title':'An existing title','firstYear':2000,
               'sourceRefs':['ifdb:'+'a'*16], 'source':'https://ifdb.org/viewgame?id='+'a'*16}
        original = json.dumps([old],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        manifest = {'baseWorksCanonicalSha256':hashlib.sha256(original).hexdigest()}
        records = [row('a','unmatched',1),row('b','suspected-existing',2,year=None)]
        registry = {'works':[old], 'batches':[], 'summary':{
            'accepted':1,'candidates':1,'promotedBasic':1,'addedToMainIdentityLayer':1}}
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); db=root/'data/registry.json';db.parent.mkdir();db.write_text(json.dumps(registry))
            with patch.multiple(intake,ROOT=root,DB=db,SOURCE=root/'data/source.b64',
                                EXPECTED_BASE=1,EXPECTED_INPUT=2,LAST_BATCH=199), \
                 patch.object(intake,'source_rows',return_value=(records,manifest)):
                intake.run(pair=1)
                result=json.loads(db.read_text())
                self.assertEqual(len(result['works']),3)
                self.assertEqual(result['works'][0],old)
                self.assertEqual([w['sourceRefs'][0] for w in result['works'][1:]],['ifdb:'+'a'*16,'ifdb:'+'b'*16])
                self.assertIsNone(result['works'][2]['firstYear'])
                self.assertEqual(result['works'][2]['sourcePossibleExistingId'],'original')
                self.assertEqual(result['summary']['accepted'],3)
                before=db.read_bytes()
                intake.run(pair=1)
                self.assertEqual(db.read_bytes(),before)

    def test_missing_previous_pair_does_not_write(self):
        old={'id':'old'}
        canonical=json.dumps([old],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        manifest={'baseWorksCanonicalSha256':hashlib.sha256(canonical).hexdigest()}
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);db=root/'registry.json'
            registry={'works':[old],'batches':[],'summary':{'accepted':1}}
            db.write_text(json.dumps(registry))
            with patch.multiple(intake,ROOT=root,DB=db,EXPECTED_BASE=1), \
                 patch.object(intake,'source_rows',return_value=([],manifest)):
                before=db.read_bytes()
                with self.assertRaisesRegex(RuntimeError,'Previous pair'):
                    intake.run(pair=2)
                self.assertEqual(db.read_bytes(),before)

    def test_source_snapshot_contains_both_complete_subsets(self):
        records, manifest=intake.source_rows()
        self.assertEqual(len(records),3370)
        self.assertEqual(sum(r['sourceSubset']=='unmatched' for r in records),2022)
        self.assertEqual(sum(r['sourceSubset']=='suspected-existing' for r in records),1348)
        self.assertEqual(len({r['IFDB_TUID'] for r in records}),3370)
        self.assertEqual(manifest['expectedBaseRecords'],96484)

    def test_short_source_ids_are_preserved_without_padding(self):
        r=row('a','unmatched',1)
        r['IFDB_TUID']='drzxv17mobammbv'
        r['IFDB页面']='https://ifdb.org/viewgame?id='+r['IFDB_TUID']
        imported=intake.work_from(r,199)
        self.assertEqual(imported['id'],'ifdb-table-20261104-drzxv17mobammbv')
        self.assertEqual(imported['sourceRefs'][0],'ifdb:drzxv17mobammbv')
        self.assertEqual(imported['source'],r['IFDB页面'])

    def test_historical_reuse_assertions_keep_reviewed_targets_and_full_lookup_keeps_appends(self):
        registry={'works':[{'id':'original'},
                 {'id':'raw','intakePolicy':'append-without-deduplication'},
                 {'id':'other-reviewed'}]}
        full_targets={'original','raw','other-reviewed'}
        self.assertEqual(basic_identity_decisions.reviewed_identity_targets(registry,full_targets),{'original','other-reviewed'})
        self.assertEqual(full_targets,{'original','raw','other-reviewed'})


if __name__ == '__main__':
    unittest.main()
