import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from interaction_model import validate_interactions, iter_interaction_works
from export_interaction_csv import interaction_csv
D=json.loads((ROOT/'data/games.json').read_text())
C=json.loads((ROOT/'data/company-coverage.json').read_text())
T=json.loads((ROOT/'data/taxonomy.json').read_text())

class InteractionTests(unittest.TestCase):
    def test_all_main_and_related_works_have_valid_labels_and_evidence(self):
        validate_interactions(D,C,T)
        self.assertEqual(len(list(iter_interaction_works(D,C))),len(D['works'])+sum(len(c.get('relatedGames',[])) for c in C['companies']))
    def test_misspelled_unknown_or_unexplained_labels_rejected(self):
        for modes in [[],['文字輸入'],['待核实','菜单指令'],['菜单指令','菜单指令']]:
            data=copy.deepcopy(D);data['works'][0]['interactionModes']=modes
            with self.assertRaises(AssertionError):validate_interactions(data,C,T)
        data=copy.deepcopy(D);data['works'][0]['interactionSources']=[]
        with self.assertRaises(AssertionError):validate_interactions(data,C,T)
    def test_csv_and_every_static_card_include_labels(self):
        self.assertEqual((ROOT/'data/interaction-modes.csv').read_text(encoding='utf-8-sig'),interaction_csv(D,C))
        works={w['id']:w for w in D['works']}
        for company in C['companies']:
            page=(ROOT/(company['id']+'.html')).read_text()
            for w in [*(works[wid] for wid in company['workIds']),*company.get('relatedGames',[])]:
                card=page.split(f'<article class="card" id="{w["id"]}">')[1].split('</article>')[0]
                for mode in w['interactionModes']:self.assertIn('>'+mode+'</span>',card)
    def test_mixed_and_non_novel_controls_are_not_inferred_from_story_theme(self):
        main={w['id']:w for w in D['works']};related={w['id']:w for _,w in iter_interaction_works(D,C) if w['id'] not in main}
        self.assertEqual(main['g490']['interactionModes'],['选项分支','日程养成'])
        self.assertNotIn('即时动作',main['g616']['interactionModes'])
        self.assertEqual(main['g597']['interactionModes'],['选项分支'])
        self.assertEqual(main['g599']['interactionModes'],['选项分支'])
        self.assertIn('卡牌棋盘',main['g598']['interactionModes'])
        self.assertEqual(main['g595']['interactionModes'],['待核实'])
        self.assertEqual(related['ascii-rogue']['interactionModes'],['菜单指令','直接移动'])
        self.assertEqual(related['nitroplus-extra-togainu-typing']['interactionModes'],['打字操作'])
        self.assertEqual(related['koei-gitaroo']['interactionModes'],['节奏演奏'])
        self.assertNotIn('战术策略',related['alicesoft-extra-evenicle']['interactionModes'])

if __name__=='__main__':unittest.main()
