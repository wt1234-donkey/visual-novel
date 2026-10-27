import re
import subprocess
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate_entity_model import validate,read
from build_entity_model import build,render_json
from build_entity_pages import build as build_pages

class EntityMigrationTests(unittest.TestCase):
 def test_preserves_historical_data_and_all_scoped_relationships(self):self.assertEqual(validate()['dossiers'],len(read('data/company-coverage.json')['companies']))
 def test_generated_indexes_and_directory_are_reproducible(self):
  for path,value in build().items():self.assertEqual((ROOT/path).read_text(),render_json(value),path)
  for path,value in build_pages().items():self.assertEqual((ROOT/path).read_text(),value,path)
 def test_every_existing_dossier_anchor_survives_and_each_work_is_rendered_once(self):
  baseline=read('data/entity-migration-baseline.json')['baseCommit']
  historical=set(read('data/entity-migration-baseline.json')['originalDossiers'])
  for company in read('data/company-coverage.json')['companies']:
   path=company['id']+'.html';after=(ROOT/path).read_text()
   before=subprocess.check_output(['git','show',baseline+':'+path],cwd=ROOT,text=True) if company['id'] in historical else ''
   old=set(re.findall(r'\bid="([^"]+)"',before));new=re.findall(r'\bid="([^"]+)"',after)
   self.assertFalse(old-set(new),(path,old-set(new)));self.assertEqual(len(new),len(set(new)),path)
   ids=[*company['workIds'],*[w['id'] for w in company.get('relatedGames',[])],*[w['id'] for w in company.get('dossierOnlyWorks',[])]]
   self.assertEqual(after.count('<article class="card"'),len(ids),path)
 def test_year_groups_and_type_labels_are_separate_from_company_establishment(self):
  page=(ROOT/'index.html').read_text();period=re.search(r'aria-labelledby="dossier-period-1985">(.*?)</section>',page).group(1)
  self.assertIn('data-company="gainax" data-first-year="1989"',period)
  self.assertIn('data-company="gaina" data-first-year=""',page)
  self.assertNotIn('Key社</a>',page);self.assertIn('data-kind="publication"',page)

if __name__=='__main__':unittest.main()
