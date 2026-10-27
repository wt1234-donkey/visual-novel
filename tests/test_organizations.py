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


class OrganizationTests(unittest.TestCase):
    def test_main_page_only_adds_navigation_link(self):
        old = subprocess.check_output(['git', 'show', '6f2e754:index.html'], cwd=ROOT, text=True)
        new = (ROOT / 'index.html').read_text()
        self.assertEqual(new.replace('<a href="organizations.html">组织与沿革</a>', '', 1), build_dossier_navigation(old))
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
