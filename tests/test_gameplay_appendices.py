import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_company_pages as pages


class GameplayAppendixTests(unittest.TestCase):
    def test_complete_reference_tables_are_last_and_do_not_add_cards(self):
        expected = {'adventure_international', 'infocom', 'sierra', 'koei', 'ascii', 'melbournehouse', 'psk', 'sierra_on_line', 'sinclair', 'microcabin', 'cinematronics', 'dataeast', 'enix', 'hudson', 'legend_uk', 'legend_entertainment', 'te_soft', 'carry_lab', 'champion_soft', 'hummingbird_soft', 'riverhill_soft', 'falcom', 'ibm', 'mosaic', 'taito', 'square', 'toho', 'db_soft'}
        expected.update({'jast', 'comptiq', 'fairytale', 'konami', 'minatosoft', 'hawkeye', 'addison_wesley', 'alicesoft', 'gainax'})
        self.assertEqual(set(pages.gameplay_catalogues['companies']), expected)
        for company in pages.coverage['companies']:
            page = pages.build(company)
            if company['id'] not in expected:
                self.assertNotIn('id="gameplay-catalogue"', page)
                continue
            appendix = pages.gameplay_appendix(company)
            self.assertGreater(page.index('id="gameplay-catalogue"'), page.index('id="coverage"'))
            self.assertTrue(page.split('</main>')[0].endswith(appendix + '\n'))
            self.assertNotIn('<article class="card"', appendix)
            self.assertEqual(page.count('<article class="card"'), len(company['workIds']) + len(company.get('relatedGames', [])) + len(company.get('dossierOnlyWorks', [])))
            groups = pages.gameplay_catalogues['companies'][company['id']]['groups']
            self.assertEqual(appendix.count('<tr><th scope="row">'), sum(len(g['rows']) for g in groups))
            references = [r['workId'] for g in groups for r in g['rows'] if 'workId' in r]
            self.assertEqual(len(references), len(set(references)))
            self.assertEqual(set(references), set(company['workIds']) | {w['id'] for w in company.get('relatedGames', [])} | {w['id'] for w in company.get('dossierOnlyWorks', [])})

    def test_excluded_and_related_types_remain_reference_only(self):
        catalogues = pages.gameplay_catalogues['companies']
        examples = {'adventure_international': ['Preppie!', 'Kid Venture 1: Little Red Riding Hood'],
                    'infocom': ['Fooblitzky', 'Cornerstone'], 'sierra': ['Cubeit', 'Gelfling Adventure'],
                    'koei': ['信长之野望·新生', 'Winning Post World'],
                    'ascii': ['Gun-Nac', 'RPG Maker 2003', 'Professional Mahjong Gokuu'],
                    'melbournehouse': ['Hungry Horace', 'Test Drive Unlimited (PS2 / PSP)']}
        for cid, titles in examples.items():
            rows = [r for g in catalogues[cid]['groups'] for r in g['rows']]
            for title in titles:
                row = next(r for r in rows if r.get('title') == title)
                self.assertNotIn('workId', row)
                self.assertNotIn('platformReleases', row)
                self.assertNotIn('contentVersions', row)
                self.assertTrue(row['type'] and row['relation'])

    def test_plain_text_is_escaped_and_unknown_work_reference_is_rejected(self):
        company = next(c for c in pages.coverage['companies'] if c['id'] == 'sierra')
        entry = deepcopy(pages.gameplay_catalogues['companies']['sierra'])
        entry['groups'][0]['rows'] = [{'title': '<script>x</script>', 'type': 'A & B', 'relation': '参考', 'note': '<img onerror=x>'}]
        with patch.dict(pages.gameplay_catalogues['companies'], {'sierra': entry}):
            appendix = pages.gameplay_appendix(company)
            self.assertIn('&lt;script&gt;x&lt;/script&gt;', appendix)
            self.assertIn('A &amp; B', appendix)
            self.assertNotIn('<img onerror=', appendix)
            entry['groups'][0]['rows'] = [{'workId': 'not-a-company-work'}]
            with self.assertRaises(KeyError):
                pages.gameplay_appendix(company)


if __name__ == '__main__':
    unittest.main()
