import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('moby_pc_append', ROOT / 'scripts/import_mobygames_pc88_pc98_20261105.py')
intake = importlib.util.module_from_spec(spec)
spec.loader.exec_module(intake)


def source_row(number, subset='unmatched'):
    return {'Moby ID': number, '作品名称': 'Already registered title', '目录平台': 'PC-88 / PC-98',
        'PC-88 发行年': 1986, 'PC-98 发行年': 1987, 'Moby 最早年（补充）': None,
        '目录类型（原文）': 'Action', '开发商关联（补充）': None, '发行商关联（补充）': None,
        'MobyGames 来源 URL': f'https://www.mobygames.com/game/{number}/already-registered-title/',
        '比对结论': '未匹配' if subset == 'unmatched' else '疑似已有', '判断依据': 'source comparison',
        '候选基础库 ID': 'original' if subset == 'suspected-existing' else None,
        '候选作品名称': 'Already registered title' if subset == 'suspected-existing' else None,
        'sourceSubset': subset, 'sourceWorkbookSheet': '未匹配作品' if subset == 'unmatched' else '疑似已有',
        'sourceWorkbookRow': number + 5, 'sourceSnapshotRow': number}


class MobyPcAppendTests(unittest.TestCase):
    def test_source_selection_and_650_611_boundary(self):
        rows, manifest = intake.source_rows()
        self.assertEqual(len(rows), 1261)
        self.assertEqual(sum(r['sourceSubset'] == 'unmatched' for r in rows), 1118)
        self.assertEqual(sum(r['sourceSubset'] == 'suspected-existing' for r in rows), 143)
        self.assertEqual(manifest['batchSize'], 650)
        first, a, _ = intake.build_batch(rows, 209, 100943)
        second, b, _ = intake.build_batch(rows, 210, 101593)
        self.assertEqual((len(first), len(second)), (650, 611))
        self.assertEqual((a['unmatched'], a['suspectedExisting']), (650, 0))
        self.assertEqual((b['unmatched'], b['suspectedExisting']), (468, 143))
        self.assertEqual(b['after'], 102204)
        self.assertEqual(len({w['id'] for w in first + second}), 1261)
        self.assertTrue(all(w['sourceRefs'] == ['mobygames:' + str(w['sourceMobyId'])] for w in first + second))

    def test_platform_dates_do_not_masquerade_as_original_debut(self):
        row = source_row(1)
        w = intake.work_from(row, 209)
        self.assertEqual(w['firstYear'], 1986)
        self.assertEqual(w['sourceYearKind'], 'platform-earliest-only')
        self.assertIsNone(w['sourceEarliestYear'])
        self.assertIn('不声明为原作首发年', w['yearBasis'])
        row['Moby 最早年（补充）'] = 1982
        w = intake.work_from(row, 209)
        self.assertEqual(w['firstYear'], 1982)
        self.assertEqual(w['sourceYearKind'], 'source-work-earliest')
        row.update({'Moby 最早年（补充）': None, 'PC-88 发行年': None, 'PC-98 发行年': None})
        w = intake.work_from(row, 209)
        self.assertIsNone(w['firstYear'])
        self.assertEqual(w['sourceYearKind'], 'unknown')
        self.assertEqual(w['group'], '厂商待核')

    def test_matching_names_and_sources_are_appended_but_retries_do_not_duplicate(self):
        old = {'id': 'original', 'title': 'Already registered title', 'sourceRefs': ['mobygames:1']}
        rows = [source_row(i) for i in range(1, 651)] + [source_row(651, 'suspected-existing')]
        manifest = {'baseWorksCanonicalSha256': intake.canonical_hash([old])}
        registry = {'works': [old], 'batches': [], 'summary': {k: 1 for k in ('accepted', 'candidates', 'promotedBasic', 'addedToMainIdentityLayer')}}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / 'data/registry.json'
            db.parent.mkdir()
            db.write_text(json.dumps(registry))
            with patch.multiple(intake, ROOT=root, DB=db, SOURCE=root/'data/source.b64', EXPECTED_BASE=1, EXPECTED_INPUT=651), patch.object(intake, 'source_rows', return_value=(rows, manifest)):
                before = db.read_bytes()
                intake.run(dry_run=True)
                self.assertEqual(before, db.read_bytes())
                intake.run()
                result = json.loads(db.read_text())
                self.assertEqual(result['works'][0], old)
                self.assertEqual(len(result['works']), 652)
                self.assertEqual(result['works'][-1]['sourcePossibleExistingId'], 'original')
                self.assertEqual(result['works'][1]['sourceRefs'], old['sourceRefs'])
                self.assertEqual([b['summary']['appendedRecords'] for b in result['batches']], [650, 1])
                self.assertTrue(all(not set(w) & {'contentVersions', 'platformReleases', 'synopsis', 'creators'} for w in result['works']))
                before = db.read_bytes()
                intake.run()
                self.assertEqual(db.read_bytes(), before)

    def test_refuses_url_identity_conflict_and_invalid_year(self):
        row = source_row(1)
        row['MobyGames 来源 URL'] = 'https://www.mobygames.com/game/2/other-title/'
        with self.assertRaisesRegex(RuntimeError, 'URL disagree'):
            intake.work_from(row, 209)
        row = source_row(1)
        row['PC-88 发行年'] = True
        with self.assertRaisesRegex(RuntimeError, 'integers or unknown'):
            intake.work_from(row, 209)

    def test_refuses_partial_group_and_changed_baseline(self):
        old = {'id': 'original'}
        rows = [source_row(1)]
        registry = {'works': [old], 'summary': {'accepted': 1}, 'batches': [{'id': intake.PREFIX + '209'}]}
        manifest = {'baseWorksCanonicalSha256': intake.canonical_hash([old])}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root/'registry.json'
            db.write_text(json.dumps(registry))
            with patch.multiple(intake, ROOT=root, DB=db, EXPECTED_BASE=1), patch.object(intake, 'source_rows', return_value=(rows, manifest)):
                with self.assertRaisesRegex(RuntimeError, 'Partial group'):
                    intake.run()
                registry['works'][0]['title'] = 'changed'
                db.write_text(json.dumps(registry))
                with self.assertRaisesRegex(RuntimeError, 'Existing basic records changed'):
                    intake.run()


if __name__ == '__main__':
    unittest.main()
