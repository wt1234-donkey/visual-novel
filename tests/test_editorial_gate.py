import importlib.util
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts';sys.path.insert(0,str(SCRIPTS))
import attest_editorial_commit as gate
from wait_catalogue_publication import contains

class EditorialGateTests(unittest.TestCase):
    def test_editorial_attestation_excludes_code_and_is_tied_to_the_default_workflow(self):
        self.assertTrue(gate.allowed_path('data/basic-registry/works-001.json'))
        self.assertTrue(gate.allowed_path('index.html'))
        for path in ('data/../../app.mjs','data/worker.mjs','.github/workflows/pages.yml','scripts/evil.py'):
            self.assertFalse(gate.allowed_path(path))
        with patch.dict('os.environ',{'GITHUB_WORKFLOW_REF':'other','GITHUB_REF':'refs/heads/main'}):
            with self.assertRaises(ValueError):gate.main()

    def test_verified_candidate_is_uploaded_before_status_and_nonforce_main_update(self):
        calls=[];sha='b'*40;parent='a'*40
        def git(*args):
            calls.append(('git',args))
            if args==('rev-parse','HEAD'):return sha
            if args==('rev-parse','HEAD^'):return parent
            if args[0]=='diff':return 'data/editorial-publications.json\nindex.html'
            return ''
        def api(path,method='GET',value=None):
            calls.append(('api',path,method,value));return {'object':{'sha':parent}}
        env={'GITHUB_WORKFLOW_REF':'wt1234-donkey/visual-novel/.github/workflows/editorial-publish.yml@refs/heads/main','GITHUB_REF':'refs/heads/main','GITHUB_RUN_ID':'123','GITHUB_RUN_ATTEMPT':'1'}
        with patch.dict('os.environ',env),patch.object(gate,'git',git),patch.object(gate,'api',api):gate.main()
        push=next(i for i,row in enumerate(calls) if row[0]=='git' and row[1][0]=='push')
        status=next(i for i,row in enumerate(calls) if row[0]=='api' and row[1].startswith('/statuses/'))
        update=next(i for i,row in enumerate(calls) if row[0]=='api' and row[2]=='PATCH')
        self.assertLess(push,status);self.assertLess(status,update);self.assertFalse(calls[update][3]['force'])
        self.assertNotIn('HEAD:main',calls[push][1]);self.assertIn('editorial-verified/',calls[push][1][-1])

    def test_only_actual_deployment_ancestry_proves_publication(self):
        self.assertTrue(contains({'revision':'later','ancestors':['saved']},'saved'))
        self.assertFalse(contains({'revision':'older','rollback':{'at':'today'}},'saved'))

if __name__=='__main__':unittest.main()
