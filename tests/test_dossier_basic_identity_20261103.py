import sys as _registry_sys
from pathlib import Path as _RegistryPath
_registry_sys.path.insert(0, str(_RegistryPath(__file__).resolve().parents[1] / 'scripts'))
from registry_store import read_json as read_registry_json, write_json as write_registry_json, write_text as write_registry_text
import json, subprocess, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class DossierIdentityTest(unittest.TestCase):
 def test_append_preserves_registry_and_links_dossier(self):
  current=read_registry_json(R/'data/main-adv-rpg-works-20261031.json')
  base=json.loads(subprocess.check_output(['git','show','5c30913de8b656a7d534d54d731e08a4c5d52594:data/main-adv-rpg-works-20261031.json'],cwd=R))
  audit=read_registry_json(R/'data/dossier-basic-identity-audit-20261103.json')
  self.assertEqual(current['works'][:len(base['works'])],base['works'])
  extra=[x for x in current['works'][len(base['works']):] if x.get('batch')=='dossier-identity-link-20261103']
  self.assertEqual(len(extra),audit['summary']['newIdentityLinks'])
  self.assertEqual(len(current['works']),len({x['id'] for x in current['works']}))
  self.assertEqual(len(current['works']),len({x['indexId'] for x in current['works']}))
  self.assertTrue(all(x['id']==x['linkedRecordId'] for x in extra))
  self.assertIn('g089',{x['id'] for x in extra})
  self.assertNotIn('g002',{x['id'] for x in extra})
  zork=next(x for x in audit['matchedOrHeld'] if x['workId']=='g002')
  self.assertIn('ifdb-0dbnusxunq7fw5ro',zork['matches'])
  self.assertEqual(zork['status'],'已有同ID或名称候选，待核关联')
if __name__=='__main__':unittest.main()
