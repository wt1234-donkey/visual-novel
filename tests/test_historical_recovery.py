import ast,copy,hashlib,io,json,tarfile,tempfile,unittest
from pathlib import Path
from historical_baseline_recovery import load_plan,extract_source,canonical
ROOT=Path(__file__).resolve().parents[1]
class HistoricalRecoveryTests(unittest.TestCase):
 def test_all_original_42_assertions_are_preserved_with_registered_provenance(self):
  plan=load_plan(ROOT);self.assertEqual(len(plan['entries']),19);self.assertEqual(sum(r['tests'] for r in plan['entries']),42)
  for r in plan['entries']:
   methods=[n for n in ast.walk(ast.parse((ROOT/'tests'/(r['module']+'.py')).read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')];self.assertEqual(hashlib.sha256('\n'.join(ast.dump(n,include_attributes=False) for n in methods).encode()).hexdigest(),r['testsAstSha256']);self.assertEqual(len(methods),r['tests'])
 def test_unsealed_recovery_plan_and_unsafe_archives_are_rejected(self):
  with tempfile.TemporaryDirectory() as temporary:
   root=Path(temporary);(root/'config').mkdir();value=json.loads((ROOT/'config/historical-baseline-recovery.json').read_text());value['payload']['entries'][0]['baselineRef']='a'*40;(root/'config/historical-baseline-recovery.json').write_text(json.dumps(value))
   with self.assertRaisesRegex(ValueError,'checksum'):load_plan(root)
   for path,kind in [('../escape',tarfile.REGTYPE),('scripts/link',tarfile.SYMTYPE)]:
    data=io.BytesIO()
    with tarfile.open(fileobj=data,mode='w') as archive:
     entry=tarfile.TarInfo(path);entry.type=kind;entry.linkname='../escape';archive.addfile(entry)
    with self.assertRaisesRegex(ValueError,'unsafe'):extract_source(data.getvalue(),root)
