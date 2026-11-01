import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from import_basic_multisource_r16_r17_20261101 import tag_kind


class BangumiNarrativeTagFilterTests(unittest.TestCase):
    def test_rejects_action_adventure_without_story_markers(self):
        self.assertIsNone(tag_kind(["AVG", "AAVG", "ACT", "ARPG"])[0])
        self.assertIsNone(tag_kind(["ACT", "AAVG", "Platform", "AVG"])[0])

    def test_accepts_story_marked_adventure(self):
        self.assertEqual(tag_kind(["AVG", "AAVG", "悬疑"])[0], "ADV")
        self.assertEqual(tag_kind(["ADV", "ACT", "剧情"])[0], "ADV")

    def test_accepts_explicit_visual_novel_even_if_action_tag_is_present(self):
        self.assertEqual(tag_kind(["VN", "ACT"])[0], "ADV")
        self.assertEqual(tag_kind(["视觉小说", "AAVG"])[0], "ADV")

    def test_rejects_generic_rpg_and_strategy_or_action_only_tags(self):
        self.assertIsNone(tag_kind(["RPG", "RTS"])[0])
        self.assertIsNone(tag_kind(["RPG", "ARPG", "ACT"])[0])
        self.assertIsNone(tag_kind(["RPG", "MMORPG"])[0])

    def test_accepts_story_oriented_rpg_subgenres(self):
        self.assertEqual(tag_kind(["CRPG", "RPG", "网状叙事"])[0], "RPG")
        self.assertEqual(tag_kind(["RPG", "JRPG"])[0], "RPG")
        self.assertEqual(tag_kind(["RPG", "SRPG"])[0], "RPG")

    def test_action_rpg_requires_explicit_narrative_evidence(self):
        self.assertEqual(tag_kind(["RPG", "ARPG", "ACT", "剧情"])[0], "RPG")
        self.assertIsNone(tag_kind(["RPG", "ARPG", "ACT"])[0])

    def test_rpg_subgenre_takes_precedence_over_loose_galgame_tag(self):
        self.assertEqual(tag_kind(["RPG", "JRPG", "Galgame"])[0], "RPG")


if __name__ == "__main__":
    unittest.main()
