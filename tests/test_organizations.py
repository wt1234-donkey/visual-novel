"""Verify generated read-only catalogue links and integration boundaries."""
import json
import re
import subprocess
import unittest
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_company_pages import build_dossier_navigation
from history_contracts import contracts


class OrganizationTests(unittest.TestCase):
    def test_retained_advanced_page_preserves_previous_catalogue(self):
        old = contracts()['retainedCatalogue']['html']
        # The work-first homepage replaces the old shell; its compatibility and
        # complete dossier navigation are checked in discovery.test.mjs.
        new = (ROOT / 'catalogue.html').read_text().replace('<title>高级发行检索 · ', '<title>', 1)
        # The direct editor updates the app asset cache key; retained catalogue markup stays identical.
        retained = new.replace('app.mjs?v=20261101-direct-edit', 'app.mjs?v=20261021-names')
        combined_link = '<a href="minimal-adv-rpg.html#query-advanced">基础库组合检索</a>'
        self.assertEqual(retained.count(combined_link), 1)
        retained = retained.replace(combined_link, '', 1).replace('<a href="organizations.html">组织与沿革</a>', '', 1)
        self.assertEqual(retained, build_dossier_navigation(old))
        self.assertEqual(new.count('href="organizations.html"'), 1)

    def test_catalogue_work_links_preserve_dossier_anchors(self):
        data = json.loads((ROOT / 'data/organizations.json').read_text())
        for w in data['works'].values():
            path, fragment = w['href'].split('#')
            if w['placement'] == 'main':
                self.assertIn('index.html?query=', path)
                continue
            text = (ROOT / path).read_text()
            self.assertIn(f'id="{fragment}"', text, w['id'])

    def test_canonical_page_controls_are_unique_and_preview_link_remains(self):
        page = (ROOT / 'organizations.html').read_text()
        ids = re.findall(r'\bid="([^"]+)"', page)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertRegex(page, r'data-source="data/organizations\.json\?v=[0-9a-f]{12}(?:-[a-z0-9]+)?"')
        self.assertTrue((ROOT / 'relationships-preview.html').exists())
