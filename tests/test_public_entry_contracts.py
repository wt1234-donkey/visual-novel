import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate_public_entries import validate
from verify_public_displays import Rows
class PublicEntryContracts(unittest.TestCase):
 def test_each_shipped_page_has_startup_contract(self):self.assertEqual(validate(),106)
 def test_rendered_parser_reads_text_not_an_independent_metadata_copy(self):
  p=Rows();p.feed('<article class="card" id="w"><div><span class="year">1981</span></div><h3>A &amp; B</h3><p>1999</p></article><table><tr data-work-id="other"><th><a href="#other">C &lt; D</a><small>1978 · Raw name</small></th></tr></table>')
  self.assertEqual(p.rows,[{'id':'w','title':'A & B','year':'1981'},{'id':'other','title':'C < D','year':'1978 · Raw name'}])
 def test_unregistered_or_duplicate_entry_is_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);(root/'config').mkdir();(root/'config/release-policy.json').write_text(json.dumps({'publicFiles':['new.html']}));(root/'config/public-entrypoints.json').write_text(json.dumps({'schemaVersion':1,'entries':[]}))
   with self.assertRaisesRegex(AssertionError,'inventory drift'):validate(root)
