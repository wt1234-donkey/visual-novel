"""Check published bytes, identity accounting and artifact isolation."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_pages_artifact import build,REGISTRY


class PagesArtifactTests(unittest.TestCase):
    def fixture(self,base):
        root=base/'repo'
        root.mkdir()
        (root/'data').mkdir()
        (root/REGISTRY).write_text(json.dumps({'summary':{'accepted':1},'works':[{'id':'one','batch':'test'}]}))
        (root/'index.html').write_text('<h1>Catalogue</h1>')
        (root/'.github').mkdir()
        (root/'.github'/'not-a-site-file.yml').write_text('workflow')
        subprocess.run(['git','init','-q',str(root)],check=True)
        subprocess.run(['git','-C',str(root),'add','.'],check=True)
        (root/'untracked.txt').write_text('not part of this release')
        return root

    def test_artifact_keeps_exact_bytes_and_excludes_git_and_untracked_files(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);root=self.fixture(base);out=base/'site'
            manifest=build(root,out,'test-revision')
            self.assertEqual((out/REGISTRY).read_bytes(),(root/REGISTRY).read_bytes())
            self.assertEqual(manifest['registrySha256'],hashlib.sha256((root/REGISTRY).read_bytes()).hexdigest())
            self.assertEqual(manifest['basicWorkCount'],1)
            self.assertEqual(manifest['batchCounts'],{'test':1})
            self.assertFalse((out/'.git').exists())
            self.assertFalse((out/'.github').exists())
            self.assertFalse((out/'untracked.txt').exists())
            self.assertTrue((out/'.nojekyll').exists())

    def test_existing_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);root=self.fixture(base);out=base/'site';out.mkdir()
            (out/'keep.txt').write_text('keep')
            with self.assertRaises(ValueError):build(root,out,'test')
            self.assertEqual((out/'keep.txt').read_text(),'keep')

    def test_duplicate_identities_fail_before_publication(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);root=self.fixture(base)
            (root/REGISTRY).write_text(json.dumps({'summary':{'accepted':2},'works':[{'id':'one'},{'id':'one'}]}))
            with self.assertRaises(ValueError):build(root,base/'site','test')
            self.assertFalse((base/'site').exists())

    def test_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);root=self.fixture(base)
            (root/'link').symlink_to('index.html')
            subprocess.run(['git','-C',str(root),'add','link'],check=True)
            with self.assertRaises(ValueError):build(root,base/'site','test')


if __name__=='__main__':unittest.main()
