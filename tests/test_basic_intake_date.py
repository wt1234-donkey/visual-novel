import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import import_basic_r20_r21_20261101 as importer


class BasicIntakeDateTests(unittest.TestCase):
    def exercise(self, expected, **kwargs):
        old_work = {'id': 'old', 'title': 'Preserved', 'firstYear': 1998}
        old_batch = {'id': 'historical', 'source': 'historical-source'}
        registry = {'works': [copy.deepcopy(old_work)],
                    'batches': [copy.deepcopy(old_batch)],
                    'summary': {k: 1 for k in ('candidates', 'accepted',
                        'promotedBasic', 'addedToMainIdentityLayer')}}
        registry['summary']['promotedDossier'] = 0
        with patch.object(importer, 'ROOT', Path('/intake-test')), \
             patch.object(importer, 'save') as save:
            importer.append_batch(registry, [{'id': 'new'}], 'batch', 'source',
                Path('/intake-test/data/audit.json'), {}, [], [], 'docs',
                'license', **kwargs)
        audit = save.call_args_list[1].args[1]
        self.assertEqual(registry['updated'], expected)
        self.assertEqual(audit['date'], expected)
        self.assertEqual(registry['works'][0], old_work)
        self.assertEqual(registry['batches'][0], old_batch)
        self.assertEqual(registry['summary']['accepted'], 2)

    def test_new_intake_uses_explicit_date_in_registry_and_audit(self):
        self.exercise('2026-11-02', intake_date='2026-11-02')

    def test_historical_callers_retain_their_default_date(self):
        self.exercise('2026-11-01')
