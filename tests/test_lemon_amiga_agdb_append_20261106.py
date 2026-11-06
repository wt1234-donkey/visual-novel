import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('amiga_agdb_intake', ROOT/'scripts/import_lemon_amiga_agdb_20261106.py')
intake = importlib.util.module_from_spec(spec)
spec.loader.exec_module(intake)


class AmigaAgdbIntakeTests(unittest.TestCase):
    def test_selected_workbook_rows_and_uncertain_metadata_survive(self):
        rows, manifest = intake.source_rows()
        self.assertEqual(len(rows), 489)
        works, summary, audit = intake.build_batch(rows, 222, 107684)
        self.assertEqual(summary['after'], 108173)
        self.assertEqual(summary['unmatched'], 308)
        self.assertEqual(summary['suspectedExisting'], 181)
        self.assertEqual(summary['mixedGameplayCandidates'], 89)
        self.assertEqual(summary['unknownYear'], 3)
        self.assertEqual(len({w['id'] for w in works}), 489)
        unknown = next(w for w in works if w['firstYear'] is None)
        self.assertIn('未核定', unknown['yearBasis'])
        self.assertTrue(all(w['sourceWorkbookRow'] >= 5 for w in works))
        self.assertTrue(all(w['sourceRefs'][0].startswith('lemon-amiga-agdb-snapshot:') for w in works))
        self.assertFalse(any(set(w)&{'contentVersions','platformReleases','synopsis','creators'} for w in works))

    def test_existing_title_and_source_are_appended_without_deduplication(self):
        source, _ = intake.source_rows()
        rows=[]
        for i in range(2):
            row=copy.deepcopy(source[0]);row['sourceSnapshotRow']=i+1
            row['sourceWorkbookRow']=i+5;rows.append(row)
        old={'id':'existing','title':rows[0]['title'],'source':rows[0]['sourceUrls'][0]}
        manifest={'baseWorksCanonicalSha256':intake.canonical_hash([old])}
        registry={'works':[old],'batches':[],'summary':{k:1 for k in ('accepted','candidates','promotedBasic','addedToMainIdentityLayer')}}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data').mkdir();db=root/'data/db.json';db.write_text(json.dumps(registry))
            with patch.multiple(intake,ROOT=root,DB=db,SOURCE=root/'data/source.b64',EXPECTED_BASE=1,EXPECTED_INPUT=2),patch.object(intake,'source_rows',return_value=(rows,manifest)):
                intake.run();result=json.loads(db.read_text())
                self.assertEqual(len(result['works']),3)
                self.assertEqual(result['works'][0],old)
                self.assertEqual([w['title'] for w in result['works']],[old['title']]*3)
                self.assertEqual([w['source'] for w in result['works']],[old['source']]*3)
                before=db.read_bytes();intake.run();self.assertEqual(db.read_bytes(),before)

    def test_original_record_edits_rejected(self):
        with self.assertRaisesRegex(RuntimeError,'Existing records changed'):
            intake.check_registry({'summary':{'accepted':1},'works':[{'id':'changed'}]}, {'baseWorksCanonicalSha256':intake.canonical_hash([{'id':'original'}])})


if __name__ == '__main__':
    unittest.main()
