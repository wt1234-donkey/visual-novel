import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from registry_store import NAME, read_json, write_json, migrate
from date_contract import is_recorded_year, is_published_year


class RegistryStorageTests(unittest.TestCase):
    def fixture(self, root):
        path = root/'data'/NAME
        path.parent.mkdir()
        value = {'schema': 1, 'summary': {'accepted': 1001}, 'works': [{'id': f'work-{i}', 'title': '名称'} for i in range(1001)], 'identityReview': []}
        path.write_text(json.dumps(value))
        migrate(root)
        return path, value

    def test_shards_roundtrip_and_node_reader_agree(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);path,value=self.fixture(root)
            self.assertEqual(read_json(path),value)
            physical=json.loads(path.read_text());self.assertNotIn('works',physical)
            self.assertEqual(len(physical['storage']['shards']),2)
            script="import {readJsonFileSync} from './src/infrastructure/filesystem/registry.mjs'; console.log(JSON.stringify(readJsonFileSync(process.argv[1])))"
            actual=json.loads(subprocess.check_output(['node','--input-type=module','-e',script,str(path)],cwd=ROOT))
            self.assertEqual(actual,value);self.assertEqual(migrate(root,check=True)['count'],1001)

    def test_append_keeps_sealed_bytes_and_digest_errors_stop_reading(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);path,value=self.fixture(root);before=json.loads(path.read_text())['storage']['shards']
            sealed=root/'data'/before[0]['path'];sealed_bytes=sealed.read_bytes()
            value=copy.deepcopy(value);value['works'].append({'id':'next','title':'下一条'});value['summary']['accepted']+=1
            write_json(path,value);after=json.loads(path.read_text())['storage']['shards']
            self.assertEqual(before[0],after[0]);self.assertEqual(sealed.read_bytes(),sealed_bytes)
            self.assertNotEqual(before[-1]['path'],after[-1]['path']);self.assertFalse((root/'data'/before[-1]['path']).exists())
            active=root/'data'/after[-1]['path'];active.write_bytes(active.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'checksum'):read_json(path)

    def test_date_contract_and_full_site_pr_gate(self):
        for year in (1965,1967,2050,None):self.assertTrue(is_recorded_year(year))
        for year in (True,'1965',1965.5,1899,2201):self.assertFalse(is_recorded_year(year))
        self.assertTrue(is_published_year(1965,2026));self.assertFalse(is_published_year(2050,2026))
        workflow=(ROOT/'.github/workflows/pages.yml').read_text()
        self.assertIn('python3 scripts/validate_catalogue.py',workflow)
        pr=workflow.split('  pull_request:',1)[1].split('  workflow_dispatch:',1)[0]
        self.assertNotIn('paths:',pr);self.assertNotIn('paths-ignore:',pr)
        from validate_catalogue import CHECKS
        self.assertIn(['python3','scripts/registry_store.py','--check'],CHECKS)


if __name__ == '__main__':unittest.main()
