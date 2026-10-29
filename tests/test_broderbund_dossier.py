"""Brøderbund catalogue admission and its historical acquisition boundary."""
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads(subprocess.check_output(['git','show','2c1e3874d369da741c42ef909bfcc5e24a6570c2:data/'+name],cwd=ROOT))


class BroderbundDossierTests(unittest.TestCase):
    def test_main_works_versions_and_parser_bibliography(self):
        games = read('games.json')
        dossier = next(c for c in read('company-coverage.json')['companies'] if c['id'] == 'broderbund')
        self.assertEqual(dossier['workIds'], ['g1060', 'g1286', 'g1287'])
        self.assertEqual({w['id'] for w in dossier['dossierOnlyWorks']},
                         {'broderbund-mask-sun', 'broderbund-serpents-star'})
        works = {w['id']: w for w in games['works']}
        versions = {v['id']: v for v in games['contentVersions']}
        releases = {r['id']: r for r in games['platformReleases']}
        for wid in ['g1286', 'g1287']:
            self.assertIn(wid, works)
            self.assertEqual(versions[wid + '-c-original']['workId'], wid)
            self.assertEqual(releases[wid + '-v1']['contentVersionId'], wid + '-c-original')
            self.assertEqual(releases[wid + '-v1']['publisherCompanies'], ['Brøderbund'])
        for w in dossier['dossierOnlyWorks']:
            self.assertNotIn(w['id'], works)
        self.assertEqual(sum(w['id'] == 'g1060' for w in games['works']), 1)

    def test_existing_identity_and_acquisition_are_sourced(self):
        entities = read('entities.json')
        org = read('organizations.json')
        dossier = next(d for d in entities['dossiers'] if d['id'] == 'broderbund')
        self.assertEqual(dossier['entityIds'], ['entity-name-e0c32a99a906'])
        edge = next(e for e in org['edges'] if e['id'] == 'broderbund-tlc-acquisition-1998')
        self.assertEqual((edge['parent'], edge['child']),
                         ('preview-learning-company-1998', 'entity-name-e0c32a99a906'))
        self.assertIn('museumofplay.org', edge['source'])
        parent = next(n for n in org['nodes'] if n['id'] == edge['parent'])
        self.assertTrue(parent['previewOnly'])
        self.assertEqual(parent['productionCount'], 0)
        self.assertEqual([e['year'] for e in org['organizationEvents']
                          if e['id'].startswith('broderbund-')], [1980, 1993, 1998])


if __name__ == '__main__':
    unittest.main()
