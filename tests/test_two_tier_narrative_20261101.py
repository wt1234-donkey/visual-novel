"""Two independent catalog layers: broad basic identities and evidence-linked curation."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class TwoTierNarrativeLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full = load("data/games.json")
        cls.editorial = load("data/discovery-editorial.json")
        cls.basic = load("data/main-adv-rpg-works-20261031.json")
        cls.curated = load("data/curated-narrative-works.json")

    def test_basics_preserve_all_prior_identities(self):
        self.assertGreaterEqual(len(self.basic["works"]), 1310)
        self.assertEqual(self.basic["summary"]["accepted"], len(self.basic["works"]))
        ids = [w["id"] for w in self.basic["works"]]
        self.assertEqual(len(set(ids)),len(ids))
        self.assertGreaterEqual(len([w for w in self.basic["works"] if w.get("batch") == "nextmoe-galgame-bulk-20261031"]),500)
        self.assertGreaterEqual(len([w for w in self.basic["works"] if w.get("batch") == "nextmoe-galgame-bulk-20261101-r2"]),500)

    def test_curation_is_explicit_evidence_linked_subset(self):
        selected = self.curated["entries"]
        complete = {w["id"]:w for w in self.full["works"]}
        self.assertGreaterEqual(len(selected), 8)
        self.assertEqual(len({w["workId"] for w in selected}), len(selected))
        self.assertEqual(self.curated["summary"]["seedCount"], len([w for w in selected if w["status"] == "editorial-seed"]))
        for row in selected:
            with self.subTest(work=row["workId"]):
                self.assertIn(row["workId"],complete)
                self.assertEqual(row["firstYear"],complete[row["workId"]]["firstYear"])
                self.assertTrue(row["whyRead"].strip())
                self.assertTrue(row["source"].startswith("https://"))
                self.assertIn(row["source"],self.editorial["works"][row["workId"]]["sources"])
                self.assertTrue(row["detailUrl"].endswith("#work/"+row["workId"]))
                self.assertIn(row["status"],("editorial-seed","watchlist","reviewed"))
                self.assertNotIn("rating",row)
        self.assertTrue(set(w["workId"] for w in selected).issubset(set(self.editorial["featuredWorkIds"])))

    def test_site_separates_broad_collection_from_curated(self):
        self.assertIn('href="curated.html"',(ROOT/"index.html").read_text(encoding="utf-8"))
        self.assertIn('href="curated.html"',(ROOT/"minimal-adv-rpg.html").read_text(encoding="utf-8"))
        self.assertIn('curated-narrative-works.json',(ROOT/"curated.mjs").read_text(encoding="utf-8"))
        self.assertIn('registry.works',(ROOT/"minimal-adv-rpg.mjs").read_text(encoding="utf-8"))
        self.assertIn("查看精选叙事初选",(ROOT/"discovery.mjs").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
