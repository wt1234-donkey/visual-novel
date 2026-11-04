import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('archive_append',ROOT/'scripts/import_ifarchive_append_20261104.py')
intake=importlib.util.module_from_spec(spec);spec.loader.exec_module(intake)

def row(uid,subset,position,year=1980):
    return {'IFDB_TUID':uid*15,'作品名称':'Already registered title','发行年份':year,
        '作者或创作主体':'Source author','IFDB页面':'https://ifdb.org/viewgame?id='+uid*15,
        'Archive关联文件数':2,'Archive文件路径清单':'if-archive/games/test.z5\nif-archive/solutions/test.txt',
        '核查说明':'包含游戏及资料，版本关系待核','关联依据':'Archive文件元数据TUID','Archive原表行号':position+1,
        'sourceSubset':subset,'sourceSnapshotRow':position,'sourceSheet':'未匹配作品' if subset=='unmatched' else '同名及版本待核',
        'sourceWorksheetRow':position+5,'基础库候选ID':'original' if subset=='suspected-existing' else ''}

class ArchiveAppendTests(unittest.TestCase):
    def test_existing_ifdb_identity_is_appended_and_rerunning_group_is_safe(self):
        old={'id':'original','title':'Already registered title','sourceRefs':['ifdb:'+'a'*15]}
        manifest={'baseWorksCanonicalSha256':hashlib.sha256(json.dumps([old],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
        records=[row('a','unmatched',1),row('b','suspected-existing',2,year=None)]
        registry={'works':[old],'batches':[],'summary':{k:1 for k in ('accepted','candidates','promotedBasic','addedToMainIdentityLayer')}}
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);db=root/'data/registry.json';db.parent.mkdir();db.write_text(json.dumps(registry))
            with patch.multiple(intake,ROOT=root,DB=db,SOURCE=root/'data/source.b64',EXPECTED_BASE=1,EXPECTED_INPUT=2,LAST_BATCH=206), \
                 patch.object(intake,'source_rows',return_value=(records,manifest)):
                intake.run(pair=1)
                result=json.loads(db.read_text())
                self.assertEqual(result['works'][0],old)
                self.assertEqual(len(result['works']),3)
                self.assertEqual(result['works'][1]['sourceRefs'][0],'ifdb:'+'a'*15)
                self.assertEqual(result['works'][2]['sourcePossibleExistingId'],'original')
                self.assertIsNone(result['works'][2]['firstYear'])
                self.assertEqual(result['works'][1]['sourceArchivePaths'],['if-archive/games/test.z5','if-archive/solutions/test.txt'])
                before=db.read_bytes();intake.run(pair=1);self.assertEqual(db.read_bytes(),before)

    def test_complete_source_subsets_and_archive_provenance(self):
        records,manifest=intake.source_rows()
        self.assertEqual(len(records),1089)
        self.assertEqual(sum(r['sourceSubset']=='unmatched' for r in records),601)
        self.assertEqual(sum(r['sourceSubset']=='suspected-existing' for r in records),488)
        self.assertEqual(manifest['expectedBaseRecords'],99854)
        imported=intake.work_from(records[0],206)
        self.assertTrue(imported['source'].startswith('https://ifarchive.org/if-archive/'))
        self.assertIn(records[0]['IFDB页面'],imported['additionalSources'])
        self.assertEqual(imported['sourceArchiveFileCount'],records[0]['Archive关联文件数'])
        self.assertEqual(imported['sourceArchiveVerification'],records[0]['核查说明'])

    def test_archive_paths_accept_literal_newline_markers_and_preserve_short_id(self):
        r=row('a','unmatched',1)
        r['Archive文件路径清单']='if-archive/games/a.z5\\nif-archive/games/source/a.inf'
        result=intake.work_from(r,206)
        self.assertEqual(result['id'],'ifarchive-table-20261104-'+'a'*15)
        self.assertEqual(result['sourceArchivePaths'],['if-archive/games/a.z5','if-archive/games/source/a.inf'])

if __name__=='__main__':unittest.main()
