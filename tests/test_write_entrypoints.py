from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]

class WriterBoundariesTests(unittest.TestCase):
    def test_workflow_git_pushes_only_target_proposal_branches(self):
        writers=0
        for path in (ROOT/'.github/workflows').glob('*.yml'):
            text=path.read_text()
            for line in text.splitlines():
                if 'git push' not in line:continue
                writers+=1
                self.assertNotRegex(line,r'HEAD:(?:refs/heads/)?main(?:[\s"\']|$)|origin\s+main(?:\s|$)',path.name)
                if '$TARGET_BRANCH' in line:self.assertIn('TARGET_BRANCH: ${{ github.head_ref }}',text,path.name)
                elif '$GITHUB_HEAD_REF' in line or '${{ github.head_ref }}' in line:self.assertIn('pull_request:',text,path.name)
                elif '"$BRANCH"' in line:self.assertEqual(path.name,'management-submit.yml')
                else:self.assertRegex(line,r'HEAD:(?:catalog/|editorial/|feature/)',path.name)
        self.assertGreater(writers,0)

    def test_main_writers_use_default_branch_validation_and_scoped_attestation(self):
        text=(ROOT/'.github/workflows/catalogue-command.yml').read_text()
        self.assertIn('persist-credentials: false',text);self.assertIn('statuses: write',text)
        self.assertIn('scripts/execute_catalogue_command.mjs',text);self.assertIn('scripts/promote_catalogue_command.py',text)
        editorial=(ROOT/'.github/workflows/editorial-publish.yml').read_text()
        self.assertIn('scripts/attest_editorial_commit.py',editorial);self.assertIn('scripts/wait_catalogue_publication.py',editorial)
        self.assertNotIn('git push origin HEAD:main',editorial)

if __name__=='__main__':unittest.main()
