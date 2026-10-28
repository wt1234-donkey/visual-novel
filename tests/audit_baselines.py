"""Distinguish reproducible audit snapshots from lost local Git objects."""
from functools import lru_cache
import json
import os
import subprocess
import unittest


@lru_cache(maxsize=None)
def _available(root, ref):
    # Some early commit blobs are malformed JSON; their lost local working-tree
    # snapshots cannot be recreated by fetching more Git history.
    for path in ('data/credits.json', 'data/organizations.json'):
        try:
            data = subprocess.check_output(
                ['git', 'show', f'{ref}:{path}'], cwd=root,
                env={**os.environ, 'GIT_NO_LAZY_FETCH': '1'},
                stderr=subprocess.DEVNULL)
            json.loads(data)
        except (OSError, subprocess.CalledProcessError, UnicodeError, ValueError):
            return False
    return True


def requires_baseline(root, ref):
    return unittest.skipUnless(
        _available(str(root), ref),
        f'archived exact-delta audit requires unpublished or malformed Git snapshot {ref}; current audit manifest is checked separately')
