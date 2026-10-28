"""SEGA project completion protects shared identities and first-content batches."""
import json
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'ed2d0034d56b001849a70bcb069e2e54dd5bc857'

def read(path):
    return json.loads((ROOT / path).read_text())

def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))

def sega(data):
    return next(c for c in data['companies'] if c['id'] == 'sega')

class SegaCompletionTests(unittest.TestCase):
    def test_only_eleven_new_main_originals_preserve_every_old_object(self):
        before, after = old('data/games.json'), read('data/games.json')
        added = {f'g{i}' for i in range(1320, 1331)}
        for field, suffix in [('works', ''), ('contentVersions', '-c-original'), ('platformReleases', '-v-original')]:
            b, a = ({x['id']: x for x in d[field]} for d in [before, after])
            self.assertEqual({i: a[i] for i in b}, b)
            self.assertEqual(set(a) - set(b), {i + suffix for i in added})
        for r in after['platformReleases'][-11:]:
            self.assertEqual((r['contentRelation'], r['releaseRole']), ('original', 'contentDebut'))
        self.assertFalse(any(w['originalTitle'].startswith('Candy Stripe') for w in after['works']))

    def test_old_company_objects_stay_unchanged_except_scoped_sega_catalogue(self):
        b, a = old('data/company-coverage.json'), read('data/company-coverage.json')
        bd, ad = ({c['id']: c for c in d['companies']} for d in [b, a])
        self.assertEqual(set(bd), set(ad))
        self.assertEqual({i for i in bd if bd[i] != ad[i]}, {'sega'})
        self.assertEqual(ad['sega']['relatedGames'][:3], bd['sega']['relatedGames'])
        self.assertEqual(ad['sega']['workIds'][:19], bd['sega']['workIds'])
        self.assertEqual((len(ad['sega']['workIds']), len(ad['sega']['relatedGames'])), (31, 36))
        for path in ['data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path))

    def test_shared_products_films_and_group_companies_do_not_create_duplicate_cards(self):
        rows = [r for g in read('data/gameplay-catalogues.json')['companies']['sega']['groups'] for r in g['rows']]
        self.assertEqual(len(rows), 124)
        references = {r.get('title'): r for r in rows if 'title' in r}
        self.assertEqual(references['Candy Stripe ～みならい天使～']['catalogueWorkId'], 'g450')
        self.assertEqual(references['龍が如く 極3']['catalogueWorkId'], 'sega-yakuza3')
        films = [r for r in rows if r.get('title', '').startswith('グラウエン')]
        self.assertEqual(len(films), 6)
        for r in films + [references['Shining Force CD'], references['Persona系列／Persona 3 Reload']]:
            self.assertNotIn('workId', r)
            self.assertNotIn('contentVersions', r)
            self.assertNotIn('platformReleases', r)

    def test_added_content_is_scoped_and_multi_platforms_share_one_content_id(self):
        works = {w['id']: w for w in sega(read('data/company-coverage.json'))['relatedGames']}
        for wid in ['sega-yakuza3', 'sega-judgeeyes', 'sega-lostjudgment', 'sega-sonic-frontiers']:
            w = works[wid]
            self.assertEqual(len(w['contentVersions']), 2)
            c = w['contentVersions'][1]
            self.assertEqual((c['basis'], c['comparedTo']), ('added', wid + '-c-original'))
            self.assertTrue(c['addedContent'])
            rs = [r for r in w['platformReleases'] if r['id'] in c['evidenceReleaseIds']]
            self.assertEqual({r['contentVersionId'] for r in rs}, {c['id']})
            self.assertTrue(all(r['releaseRole'] == 'contentDebut' for r in rs))
        self.assertEqual(works['sega-dark-ties']['firstYear'], 2026)
        self.assertEqual(len(works['sega-dark-ties']['contentVersions']), 1)
        self.assertNotIn('Windows（Steam）', {r['platform'] for r in works['sega-lostjudgment']['platformReleases'] if r['contentRelation'] == 'original'})

    def test_identity_and_developer_roles_are_not_inferred_from_sega_group(self):
        a, b = read('data/entities.json'), old('data/entities.json')
        self.assertEqual(a['entities'], b['entities'])
        self.assertEqual(a['relations'], b['relations'])
        b, a = ({c['id']: c for c in read_data['credits']} for read_data in [old('data/credits.json'), read('data/credits.json')])
        self.assertEqual({i: a[i] for i in b}, b)
        added = [c for i, c in a.items() if i not in b]
        self.assertEqual(len(added), 84)
        self.assertEqual({c['role'] for c in added}, {'publisher'})
        self.assertEqual({c['entityId'] for c in added}, {'entity-sega'})

    def test_old_anchors_and_1987_navigation_survive_current_output(self):
        class IDs(HTMLParser):
            def __init__(self):
                super().__init__()
                self.ids = []
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if 'id' in attrs:
                    self.ids.append(attrs['id'])
        page = (ROOT / 'sega.html').read_text()
        parser = IDs()
        parser.feed(page)
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        self.assertEqual(page.count('<article class="card"'), 67)
        baseline = sega(old('data/company-coverage.json'))
        for wid in baseline['workIds'] + [w['id'] for w in baseline['relatedGames']]:
            self.assertIn(wid, parser.ids)
        self.assertIn('data-company="sega" data-first-year="1987"', (ROOT / 'index.html').read_text())
