"""Regression checks for the 67 raw rows / 56 isolated source identities."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import review_basic_r118_r119_conflicts_20261102 as review


class Round118119ConflictEvidenceTests(unittest.TestCase):
    def test_exact_row_and_identity_counts(self):
        groups = review.held_identities()
        self.assertEqual(sum(len(rows) for rows in groups.values()), 67)
        self.assertEqual(len(groups), 56)
        self.assertEqual(sum(key.startswith("vndb:") for key in groups), 39)
        self.assertEqual(sum(key.startswith("ifdb:") for key in groups), 17)

    def test_duplicate_discoveries_are_grouped_by_source_identity(self):
        groups = review.held_identities()
        repeated = {key: rows for key, rows in groups.items() if len(rows) > 1}
        self.assertEqual(len(repeated), 11)
        self.assertEqual(sum(len(rows) - 1 for rows in repeated.values()), 11)

    def test_conflict_and_dependent_content_categories_are_exact(self):
        groups = review.held_identities()
        versions = {
            key for key, rows in groups.items()
            if any("edition" in str(row["row"].get("reason") or row["row"].get("basis"))
                   or "dependent" in str(row["row"].get("reason") or row["row"].get("basis"))
                   for row in rows)
        }
        self.assertEqual(len(versions), 3)
        self.assertEqual(len(groups) - len(versions), 53)

    def test_every_raw_row_has_an_exact_audit_locator(self):
        groups = review.held_identities()
        locators = [
            (row["audit"], row["index"])
            for rows in groups.values() for row in rows
        ]
        self.assertEqual(len(locators), 67)
        self.assertEqual(len(set(locators)), 67)


if __name__ == "__main__":
    unittest.main()
