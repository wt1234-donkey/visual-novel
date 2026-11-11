import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_pages_release import select_release, unpack_verified, rollback_metadata

SHA = 'a'*40
RUN = {'repository': {'full_name': 'wt1234-donkey/visual-novel', 'id': 1},
       'head_repository': {'full_name': 'wt1234-donkey/visual-novel'},
       'path': '.github/workflows/pages.yml', 'event': 'push', 'head_branch': 'main',
       'conclusion': 'success', 'head_sha': SHA}


class PagesPromotionTests(unittest.TestCase):
    def test_only_latest_normal_build_is_promoted_but_explicit_rollback_can_select_an_older_build(self):
        self.assertFalse(select_release(RUN, 1, 'b'*40)['publish'])
        self.assertTrue(select_release(RUN, 1, SHA)['publish'])
        self.assertTrue(select_release(RUN, 1, 'b'*40, rollback=True)['publish'])

    def test_failed_pr_foreign_and_untrusted_artifacts_are_rejected(self):
        for change in ({'conclusion': 'failure'}, {'event': 'pull_request'}, {'head_branch': 'feature'},
                       {'path': '.github/workflows/other.yml'}, {'head_repository': {'full_name': 'other/repo'}}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                select_release({**RUN, **change}, 1, SHA)

    def archive(self, directory, revision=SHA, unsafe=False):
        archive=directory/'artifact.tar'
        with tarfile.open(archive, 'w') as stream:
            files={'deployment.json': {'revision': revision}, 'data/catalogue-release.json':
                   {'revision': revision, 'inputs': {'path': 'catalogue-web/'+revision+'/inputs.json', 'sha': '0'*40}}}
            for path, value in files.items():
                raw=json.dumps(value).encode();member=tarfile.TarInfo(path);member.size=len(raw);stream.addfile(member, io.BytesIO(raw))
            if unsafe:
                member=tarfile.TarInfo('../outside');member.size=0;stream.addfile(member, io.BytesIO())
        return archive

    def test_verified_rollback_changes_only_published_artifact_and_keeps_newer_saved_data(self):
        import hashlib
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);saved=root/'saved-main.json';saved.write_text('{"revision":"newer saved data"}')
            raw=b'{"historical":"verified"}';ref='catalogue-web/'+SHA+'/inputs.json'
            digest=hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()
            values={'deployment.json': json.dumps({'revision':SHA,'ancestors':[SHA]}).encode(),
                    'data/catalogue-release.json': json.dumps({'revision':SHA,'inputs':{'path':ref,'sha':digest}}).encode(),
                    'data/'+ref:raw}
            archive=root/'verified.tar'
            with tarfile.open(archive,'w') as stream:
                for path,value in values.items():
                    member=tarfile.TarInfo(path);member.size=len(value);stream.addfile(member,io.BytesIO(value))
            deployment=unpack_verified(archive,root/'published',SHA)
            rolled=rollback_metadata(deployment,{**RUN,'id':10,'html_url':'https://github.com/wt1234-donkey/visual-novel/actions/runs/10'},'b'*40,'2026-11-12T01:00:00Z')
            self.assertEqual(rolled['revision'],SHA);self.assertEqual(rolled['rollback']['repositoryHead'],'b'*40)
            self.assertEqual(saved.read_text(),'{"revision":"newer saved data"}')
            self.assertEqual((root/'published'/'data'/ref).read_bytes(),raw)

    def test_corrupt_provenance_and_unsafe_archive_cannot_be_published(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            with self.assertRaises(ValueError):unpack_verified(self.archive(root, revision='b'*40), root/'out', SHA)
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            with self.assertRaises(ValueError):unpack_verified(self.archive(root, unsafe=True), root/'out', SHA)
            self.assertFalse((root.parent/'outside').exists())


if __name__ == '__main__':
    unittest.main()
