import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('promotion',Path(__file__).resolve().parents[1]/'scripts/promote_catalogue_command.py')
promotion=importlib.util.module_from_spec(spec);spec.loader.exec_module(promotion)

class CommandPromotionTests(unittest.TestCase):
    def test_data_paths_exclude_code_checkpoints_and_other_catalogue_facts(self):
        for path in ('data/basic-catalogue-edits.json','data/work-edit-history.json','data/basic-catalogue-journal/events/r31-r32.json','data/command-receipts/a.json'):
            self.assertTrue(promotion.allowed_path(path))
        for path in ('src/domain/catalogue/model.mjs','data/games.json','data/basic-catalogue-journal/checkpoints/r30.json','data/command-receipts/../../games.json'):
            self.assertFalse(promotion.allowed_path(path))

    def run_promotion(self,fail_status=False,stale=False):
        calls=[];head='a'*40
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'data/command-receipts').mkdir(parents=True)
            (root/'data/work-edit-history.json').write_text('{}');(root/'data/command-receipts/one.json').write_text('{}')
            def git(*args):
                return head if args[0]=='rev-parse' else 'data/work-edit-history.json\ndata/command-receipts/one.json\nunsafe.mjs'
            def api(path,method='GET',value=None):
                calls.append((path,method,value))
                if path=='/git/ref/heads/main':return {'object':{'sha':'b'*40 if stale else head}}
                if path.startswith('/git/commits/') and method=='GET':return {'tree':{'sha':'tree'}}
                if path.startswith('/statuses/') and fail_status:raise RuntimeError('status rejected')
                return {'sha':'c'*40}
            with patch.object(promotion,'ROOT',root),patch.object(promotion,'git',git),patch.object(promotion,'api',api):
                if stale or fail_status:
                    with self.assertRaises((ValueError,RuntimeError)):promotion.main()
                else:promotion.main()
        return calls

    def test_attestation_precedes_main_update_and_no_force_is_used(self):
        calls=self.run_promotion();status=next(i for i,row in enumerate(calls) if row[0].startswith('/statuses/'))
        update=next(i for i,row in enumerate(calls) if row[1]=='PATCH');self.assertLess(status,update)
        self.assertIs(calls[update][2]['force'],False)
        tree=next(row[2]['tree'] for row in calls if row[0]=='/git/trees')
        self.assertEqual({item['path'] for item in tree},{'data/work-edit-history.json','data/command-receipts/one.json'})

    def test_stale_main_or_failed_attestation_never_advances_main(self):
        for options in ({'stale':True},{'fail_status':True}):
            self.assertFalse(any(row[1]=='PATCH' for row in self.run_promotion(**options)))

if __name__=='__main__':unittest.main()
