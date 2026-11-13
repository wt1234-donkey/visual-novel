import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from effective_catalogue import load_effective,effective_title

class EffectiveDirectoryTests(unittest.TestCase):
    def test_display_adapters_do_not_mutate_another_generators_cached_inputs(self):
        first=load_effective(ROOT);name=first['coverage']['companies'][0]['name']
        first['coverage']['companies'][0]['name']='local presentation mutation'
        self.assertEqual(load_effective(ROOT)['coverage']['companies'][0]['name'],name)

    def test_every_organization_and_classification_display_uses_current_work_values(self):
        effective=load_effective(ROOT)
        works={w['id']:w for w in [*effective['main']['works'],*effective['supplement']['works'],*(w for c in effective['coverage']['companies'] for f in ['relatedGames','dossierOnlyWorks'] for w in c.get(f,[]))]}
        org=json.loads((ROOT/'data/organizations.json').read_text())
        for wid,row in org['works'].items():
            self.assertEqual((row['title'],row['year']),(effective_title(works[wid]),works[wid]['firstYear']),wid)
        page=(ROOT/'classification.html').read_text()
        from html.parser import HTMLParser
        class Rows(HTMLParser):
            def __init__(self):super().__init__();self.rows=[];self.row=None
            def handle_starttag(self,tag,attrs):
                a=dict(attrs)
                if tag=='tr' and a.get('class')=='classification-row':self.row={'text':'','href':None}
                if self.row is not None and tag=='a' and self.row['href'] is None:self.row['href']=a.get('href')
            def handle_data(self,s):
                if self.row is not None:self.row['text']+=s
            def handle_endtag(self,t):
                if t=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
        parser=Rows();parser.feed(page)
        for row in parser.rows:
            wid=(row['href'] or '').split('#')[-1]
            if wid in works:
                self.assertIn(effective_title(works[wid]),row['text']);self.assertIn(str(works[wid]['firstYear'])+' · ',row['text'])

if __name__=='__main__':unittest.main()
