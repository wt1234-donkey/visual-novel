import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from wire_format import compact_generated, decode_wire

class WireFormatTests(unittest.TestCase):
    def test_compression_preserves_original_downloads_and_manifest_while_packing_derived_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            raw=(json.dumps({'evidence':['原始来源记录']*1000},ensure_ascii=False)+'\n').encode()
            for name in ('data/basic-registry/source.json','data/basic-web/manifest.json','data/basic-web/revision/detail.json','data/catalogue-web/revision/detail.json'):
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
            result=compact_generated(root)
            self.assertEqual(result['compressedGeneratedFiles'],2)
            self.assertGreater(result['generatedSavedBytes'],len(raw))
            self.assertEqual((root/'data/basic-registry/source.json').read_bytes(),raw)
            self.assertEqual((root/'data/basic-web/manifest.json').read_bytes(),raw)
            self.assertEqual(decode_wire((root/'data/catalogue-web/revision/detail.json').read_bytes()),raw)
            self.assertEqual(compact_generated(root)['compressedGeneratedFiles'],0)
