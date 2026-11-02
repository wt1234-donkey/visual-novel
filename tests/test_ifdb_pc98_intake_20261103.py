"""Guard cross-catalogue aliases and the PC-98 primary-evidence admission boundary."""
from collections import defaultdict
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import import_basic_r134_r135_20261103 as intake


class IFDBPC98IntakeTests(unittest.TestCase):
    def row(self, uid, title, year=1991):
        return {'tuid': uid * 16, 'title': title, 'aliases': [], 'firstYear': year,
            'published': f'{year}-01-01 00:00:00', 'author': 'Author', 'system': 'Inform',
            'language': 'en', 'sourceRefs': ['ifdb:' + uid * 16], 'archiveLinks': []}

    def index(self):
        old = {'id': 'existing-brandish', 'title': '撼天神塔',
            'originalTitle': 'ブランディッシュ / Brandish', 'firstYear': 1991}
        with patch.object(intake.catalogue, 'all_works', return_value=[old]):
            return intake.full_index({})

    def test_bilingual_aliases_are_split_but_episode_fractions_are_not(self):
        names = intake.split_names({'title': 'Memory 1/4',
            'originalTitle': 'ブランディッシュ / Brandish', 'aliases': ['日本語／Latin Name']})
        self.assertIn('Memory 1/4', names)
        self.assertNotIn('Memory 1', names)
        self.assertIn('Brandish', names)
        self.assertIn('ブランディッシュ', names)
        self.assertIn('Latin Name', names)

    def test_ifdb_cannot_duplicate_a_bilingual_historical_work(self):
        selected, review = intake.ifdb.choose([self.row('a', 'Brandish'), self.row('b', 'Fresh historical story')],
            1, self.index(), defaultdict(set), intake.norm, 'test')
        self.assertEqual(selected[0]['sourceId'], 'b' * 16)
        self.assertEqual(review['reusedExisting'][0]['matchedWorkIds'], ['existing-brandish'])
        self.assertEqual(review['dispositions'], {'reused-title-alias': 1})

    def test_alias_with_conflicting_year_is_held_instead_of_admitted(self):
        selected, review = intake.ifdb.choose([self.row('a', 'Brandish', 1992), self.row('b', 'Fresh historical story', 1993)],
            1, self.index(), defaultdict(set), intake.norm, 'test')
        self.assertEqual(selected[0]['sourceId'], 'b' * 16)
        self.assertEqual(review['heldForIdentityReview'][0]['sourceId'], 'a' * 16)

    def test_pc98_reservation_blocks_ifdb_case_insensitive_ifid_alias(self):
        index, refs = defaultdict(set), defaultdict(set)
        intake.reserve({'id': 'pc98-existing', 'title': 'Existing work', 'aliases': [],
            'firstYear': 1991, 'source': 'https://example.org/work', 'sourceRefs': ['ifid:ABC-123']}, index, refs)
        row = self.row('a', 'Different displayed title')
        row['sourceRefs'].append('ifid:abc-123')
        selected, review = intake.ifdb.choose([row, self.row('b', 'Fresh historical story')],
            1, index, refs, intake.norm, 'test')
        self.assertEqual(selected[0]['sourceId'], 'b' * 16)
        self.assertEqual(review['dispositions'], {'reused-external-identity': 1})

    def test_catalogue_genre_and_year_alone_do_not_admit_a_pc98_work(self):
        row = {'catalogue': 'ikachi-igdb', 'sourceId': '1', 'title': 'Unreviewed role playing story',
            'latin': '', 'catalogueYear': 1992, 'genre': 'RPG', 'source': 'https://example.org/catalogue/1'}
        snapshot = {'records': [row], 'summary': {'rawRecords': 1}}
        review = {'approved': [], 'manualAliasReuse': []}
        with patch.object(intake, 'load', side_effect=[snapshot, review]), \
                patch.object(intake, 'full_index', return_value=defaultdict(set)), \
                patch.object(intake, 'full_refs', return_value=defaultdict(set)), \
                patch.object(intake, 'save') as save, patch.object(Path, 'read_bytes', return_value=b'fixture'):
            self.assertEqual(intake.pc98_preflight({}), [])
        self.assertEqual(save.call_args.args[1]['records'][0]['status'], 'needs-primary-year-and-alias-review')

    def test_conflicting_catalogue_years_fail_approved_admission(self):
        a = {'catalogue': 'ikachi-igdb', 'sourceId': '1', 'catalogueYear': 1992}
        b = {'catalogue': 'pc9801-archive', 'sourceId': '2', 'catalogueYear': 1993}
        review = {'approved': [{'catalogueRows': [['ikachi-igdb', '1'], ['pc9801-archive', '2']], 'firstYear': 1992}]}
        with patch.object(intake, 'load', side_effect=[{'records': [a, b], 'summary': {'rawRecords': 2}}, review]), \
                patch.object(intake, 'full_index', return_value=defaultdict(set)), \
                patch.object(intake, 'full_refs', return_value=defaultdict(set)):
            with self.assertRaises(AssertionError):
                intake.pc98_preflight({})


if __name__ == '__main__':
    unittest.main()
