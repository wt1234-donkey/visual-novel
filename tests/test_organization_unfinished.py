import json,subprocess,unittest
from pathlib import Path
from historical_paths import shared_paths
ROOT=Path(__file__).resolve().parents[1]
BASE='f733af9f4295471570106d88487c4608d0cb78aa'
class OrganizationUnfinishedTests(unittest.TestCase):
    def test_list_only_change_preserves_formal_data_and_all_prior_evidence(self):
        paths=['data/entities.json','data/credits.json','data/games.json','data/company-coverage.json',
               'data/taxonomy.json','data/work-classification.json','data/work-notes.json',
               'data/entity-migration-baseline.json','data/content-migration-baseline.json',
               'data/relationships-preview-config.json','index.html']
        paths += shared_paths(ROOT, BASE, 'a1c4959cd7a2ef52460eebfa16388fea815c4642', ['organization-verification*.json','organization-context*.json'])
        for path in paths:self.assertEqual(subprocess.check_output(['git','show',f'a1c4959cd7a2ef52460eebfa16388fea815c4642:{path}'],cwd=ROOT),subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT),path)
        prior=json.loads(subprocess.check_output(['git','show',f'{BASE}:data/organizations.json'],cwd=ROOT))
        current=json.loads(subprocess.check_output(['git','show','a1c4959cd7a2ef52460eebfa16388fea815c4642:data/organizations.json'],cwd=ROOT));current.pop('unfinished')
        self.assertEqual(current,prior)
