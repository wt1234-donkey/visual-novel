import json, subprocess, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class DossierIdentityTest(unittest.TestCase):
 def test_append_preserves_registry_and_links_dossier(self):
  current=json.loads((R/'data/main-adv-rpg-works-20261031.json').read_text())
  base=json.loads(subprocess.check_output(['git','show','5c30913de8b656a7d534d54d731e08a4c5d52594:data/main-adv-rpg-works-20261031.json'],cwd=R))
  audit=json.loads((R/'data/dossier-basic-identity-audit-20261103.json').read_text())
  self.assertEqual(current['works'][:len(base['works'])],base['works'])
  extra=current['works'][len(base['works']):]
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
