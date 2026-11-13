import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from build_pages_artifact import build, REGISTRY
from release_policy import verify_public,public_paths,read_policy
from workflow_governance import check, registry


class ReleaseGovernanceTests(unittest.TestCase):
    def test_runtime_keeps_source_downloads_and_dependency_closure_but_no_tools(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);root=base/'repo';root.mkdir()
            values={REGISTRY:json.dumps({'summary':{'accepted':1},'works':[{'id':'one'}]}),
                    'index.html':'<link href="styles.css"><script src="app.mjs"></script><a href="data/export.csv">CSV</a><a href="data/source.json.gz.b64">source</a>',
                    'app.mjs':"import './src/domain/test.mjs';",'styles.css':'body {}',
                    'src/domain/test.mjs':'export const value=1;',
                    'data/export.csv':'name,year\nOne,1980\n','data/source.json.gz.b64':'snapshot',
                    'scripts/dev.py':'raise Exception("not runtime")','tests/private.test.mjs':'test',
                    'editorial-service/server.mjs':'import "node:http";',
                    'archive/workflows/old.yml':'on: push',
                    'templates/basic-works-import.csv':'title,year\n',
                    'templates/basic-works-import.json':'[]',
                    'templates/basic-style-candidates-example.json':'[]',
                    'templates/basic-style-update.csv':'id,tag\n',
                    'templates/basic-style-update-example.csv':'id,tag\n'}
            for name,value in values.items():
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value)
            subprocess.run(['git','init','-q',str(root)],check=True)
            subprocess.run(['git','-C',str(root),'add','.'],check=True)
            stage,out=base/'build',base/'site'
            build(root,out,'test',workspace=stage)
            for name in ('data/export.csv','data/source.json.gz.b64','src/domain/test.mjs','templates/basic-works-import.csv'):
                self.assertEqual((out/name).read_bytes(),(root/name).read_bytes())
            self.assertTrue((stage/'scripts/dev.py').exists())
            for name in ('scripts','tests','editorial-service','archive'):
                self.assertFalse((out/name).exists())
            self.assertGreater(verify_public(out)['publicFileCount'],4)

    def test_missing_csv_and_server_import_fail_the_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'index.html').write_text('<a href="data/missing.csv">CSV</a>')
            with self.assertRaisesRegex(ValueError,'Broken public dependency'):verify_public(root)
            (root/'index.html').write_text('<h1>OK</h1>')
            (root/'app.mjs').write_text('import "node:fs";')
            with self.assertRaisesRegex(ValueError,'Server module'):verify_public(root)

    def test_archived_workflows_are_exact_and_cannot_trigger_in_actions(self):
        counts=check(ROOT)
        self.assertEqual(counts['frozenTasks'],106)
        self.assertEqual(counts['activeWorkflows'],12)
        for task in registry(ROOT).values():
            self.assertEqual(hashlib.sha256((ROOT/task['archivedWorkflow']).read_bytes()).hexdigest(),task['workflowSha256'])
            self.assertFalse((ROOT/task['originalWorkflow']).exists())
        replay=(ROOT/'.github/workflows/historical-replay.yml').read_text()
        self.assertNotIn('pull_request:',replay)
        self.assertNotIn('contents: write',replay)
        self.assertIn('persist-credentials: false',replay)

    def test_undeclared_root_asset_or_unused_module_cannot_enter_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'index.html').write_text('<h1>Catalogue</h1>')
            for name in ('unlisted.mjs','src/application/unused.mjs','data/catalogue-web/extra.mjs'):
                path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('export const unused=1;')
                with self.assertRaisesRegex(ValueError,'not in public allowlist'):
                    verify_public(root)
                path.unlink()

    def test_old_runtime_index_generations_can_be_pruned_without_hiding_source_downloads(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'index.html').write_text('<h1>OK</h1>')
            objects=root/'data/audit-ledger/objects';objects.mkdir(parents=True)
            current='data/audit-ledger/objects/'+'1'*64+'.json'
            archived='data/audit-ledger/objects/'+'0'*64+'.json'
            (root/current).write_text('{}')
            paths=public_paths(root,['index.html',archived,'data/original-source.json'],read_policy(root))
            self.assertIn(current,paths)
            self.assertNotIn(archived,paths)
            self.assertIn('data/original-source.json',paths,'ordinary source files are never silently pruned')


if __name__ == '__main__':unittest.main()
