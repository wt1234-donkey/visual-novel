"""Reproduce the completed A–H audit snapshot for historical batch tests.

The current batch has its own exact delta test. Older tests compare the data as it
stood when their last expected progress (H3) was recorded.
"""
import json
import subprocess

SNAPSHOT = '37a7d92010796ef272b69985bb7c514fdfdd0769'
DERIVED = {'data/entities.json', 'data/credits.json',
           'data/organizations.json', 'data/entity-migration-review.json'}


def load_snapshot(root, path):
    if path in DERIVED:
        return json.loads(subprocess.check_output(
            ['git', 'show', f'{SNAPSHOT}:{path}'], cwd=root))
    return json.loads((root / path).read_text())
