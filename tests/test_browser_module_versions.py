import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from version_browser_modules import version_modules


class BrowserModuleVersionTests(unittest.TestCase):
    def test_html_imports_workers_and_nested_modules_share_the_release_revision(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            (root/'index.html').write_text('<script type="module" src="entry.mjs?v=old"></script>')
            (root/'entry.mjs').write_text("import {x} from './src/core.mjs?v=old';\nnew Worker(new URL('./worker.mjs?v=old',import.meta.url));\nimport('https://example.org/external.mjs');")
            (root/'core.json').write_text('{"source":"./data.mjs"}')
            (root/'src').mkdir()
            (root/'src/core.mjs').write_text("export * from '../model.mjs?mode=test&v=old';")
            self.assertEqual(version_modules(root,'release_123'),3)
            self.assertIn('src="entry.mjs?v=release_123"',(root/'index.html').read_text())
            entry=(root/'entry.mjs').read_text()
            self.assertIn('./src/core.mjs?v=release_123',entry)
            self.assertIn('./worker.mjs?v=release_123',entry)
            self.assertIn('https://example.org/external.mjs',entry)
            self.assertIn('mode=test&v=release_123',(root/'src/core.mjs').read_text())
            self.assertEqual((root/'core.json').read_text(),'{"source":"./data.mjs"}')
            self.assertEqual(version_modules(root,'release_123'),0)

    def test_invalid_revision_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(ValueError):version_modules(temporary,'../bad')
