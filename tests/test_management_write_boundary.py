import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from manage_catalogue import apply_file

class ManagementWriteBoundaryTests(unittest.TestCase):
    def fixture(self,root):
        (root/'data').mkdir()
        for name in ['games.json','discovery-editorial.json','creator-credits.json','work-notes.json','narrative-editorial-baseline-20261029.json','entity-catalogue.json','management-history.json','narrative-cataloguing-20261030.json']:
            shutil.copyfile(ROOT/'data'/name,root/'data'/name)
        before=json.loads((root/'data/discovery-editorial.json').read_text())['works']['g089']
        after=copy.deepcopy(before);after['basis']+=' 补充本次隔离核对的适用范围。'
        return {'schemaVersion':1,'createdAt':'2026-11-14','reason':'核对管理更新包的回执与重试', 'operations':[{'resource':'editorial','key':'g089','before':before,'after':after}]}

    def test_applied_package_is_sealed_and_retry_after_later_package_does_not_rewrite_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);package=self.fixture(root);request=root/'request.json'
            request.write_text(json.dumps(package,ensure_ascii=False));apply_file(request,root)
            receipts=list((root/'data/command-receipts').glob('*.json'));self.assertEqual(len(receipts),1)
            receipt=json.loads(receipts[0].read_text());self.assertEqual(receipt['kind'],'management');self.assertIn('auditRoot',receipt)
            raw=(root/'data/discovery-editorial.json').read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            self.assertEqual(receipt['resultSources']['data/discovery-editorial.json'],blob)
            later=copy.deepcopy(package);later['operations'][0]['before']=copy.deepcopy(package['operations'][0]['after']);later['operations'][0]['after']['basis']+=' 保留随后一项核对的补充说明。'
            request.write_text(json.dumps(later,ensure_ascii=False));apply_file(request,root)
            saved={p.relative_to(root):p.read_bytes() for p in (root/'data').rglob('*') if p.is_file()}
            request.write_text(json.dumps(package,ensure_ascii=False));apply_file(request,root)
            self.assertEqual(saved,{p.relative_to(root):p.read_bytes() for p in (root/'data').rglob('*') if p.is_file()})

    def test_stale_package_rejects_before_any_data_or_receipt_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);package=self.fixture(root);package['operations'][0]['before']['basis']='stale input'
            before={p.name:p.read_bytes() for p in (root/'data').iterdir()};request=root/'request.json';request.write_text(json.dumps(package))
            with self.assertRaisesRegex(AssertionError,'数据库已变化'):apply_file(request,root)
            self.assertEqual(before,{p.name:p.read_bytes() for p in (root/'data').iterdir()});self.assertFalse((root/'data/command-receipts').exists())

if __name__=='__main__':unittest.main()
