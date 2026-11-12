import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from workflow_governance import check_scripts

class ScriptPolicyTests(unittest.TestCase):
    def test_unregistered_scripts_and_changed_frozen_scripts_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'scripts').mkdir();(root/'config').mkdir()
            script=root/'scripts/frozen.py';script.write_text('original')
            (root/'config/script-policy.json').write_text(json.dumps({'schemaVersion':1,'scripts':[{'path':'scripts/frozen.py','role':'historical','sha256':hashlib.sha256(script.read_bytes()).hexdigest()}]}))
            self.assertEqual(check_scripts(root)['historical'],1)
            script.write_text('changed')
            with self.assertRaisesRegex(ValueError,'Frozen historical'):check_scripts(root)
            script.write_text('original');(root/'scripts/unregistered.py').write_text('new')
            with self.assertRaisesRegex(ValueError,'inventory'):check_scripts(root)
