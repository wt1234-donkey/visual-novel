import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from effective_catalogue import load_effective
from export_content_csv import content_rows
from export_interaction_csv import interaction_csv
from build_company_pages import card


class EffectiveViewTests(unittest.TestCase):
    def test_python_csv_and_static_cards_share_the_current_name_and_preserve_source(self):
        original=json.loads((ROOT/'data/games.json').read_text())
        work=copy.deepcopy(next(w for w in original['works'] if w['id']=='g039'))
        data={**original,'works':[work],'contentVersions':[c for c in original['contentVersions'] if c['workId']==work['id']],
              'platformReleases':[r for r in original['platformReleases'] if r['workId']==work['id']]}
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'data').mkdir()
            source=json.dumps(data,ensure_ascii=False)
            (root/'data/games.json').write_text(source)
            (root/'data/work-edit-history.json').write_text(json.dumps({'schemaVersion':1,'records':{work['id']:{'overrides':{'title':'当前更正名称'}}}}))
            current=load_effective(root)['main']
            self.assertTrue(all(row['作品名称']=='当前更正名称' for row in content_rows(current)))
            self.assertIn('当前更正名称',interaction_csv(current,{'companies':[]}))
            html=card(current['works'][0],current['platformReleases'])
            self.assertIn('当前更正名称',html)
            self.assertEqual(current['platformReleases'],data['platformReleases'])
            self.assertEqual((root/'data/games.json').read_text(),source)
            self.assertEqual(current['works'][0]['sourceTitle'],work['title'])


if __name__=='__main__':unittest.main()
