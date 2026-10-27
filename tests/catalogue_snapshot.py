"""Read catalogue files at the end of the completed identity audit.

Historical batch assertions describe the pre-Leland catalogue. Current catalogue
preservation is checked independently in test_leland_dossier, including all old
objects and the exact generated navigation; the migration baseline is unchanged.
"""
from functools import lru_cache
import subprocess

PRE_LELAND = '0f2d278e17d631b85ed7e34e7dd378a361ff4695'
# Historical audits also predate the sourced annotation display in the app.
CHANGED_CATALOGUE = {'data/company-coverage.json', 'data/gameplay-catalogues.json', 'index.html', 'app.mjs'}

@lru_cache(maxsize=None)
def _snapshot_bytes(root, path):
    return subprocess.check_output(['git', 'show', f'{PRE_LELAND}:{path}'], cwd=root)


def catalogue_bytes(root, path):
    if str(path) in CHANGED_CATALOGUE:
        return _snapshot_bytes(root, path)
    return (root / path).read_bytes()
