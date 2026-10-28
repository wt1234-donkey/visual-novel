"""Reconstruct the C–F audit checkpoint that was never committed as a Git tree.

The C–F catch-up and numeric tail were committed together (2c78e3b). Their
tests used a transient tree hash between the two stages. Rebuild that stage
from the committed before/after trees so the checks work in a fresh clone.
"""
import copy
from functools import lru_cache
import json
import subprocess

BEFORE = 'd261b71bc00c3e3632f0e20a8cbc54abd1cd9a6b'
AFTER = '7ea5d46efdfb5a36875fbc48ed3b287ac0dc0e3c'
SEVEN = 'entity-name-ee1a7668cd89'
NUMERIC_CREDIT_IDS = {'credit-1c20f782669492b4', 'credit-2ba48fd153d974a9'}


@lru_cache(maxsize=None)
def _git_json(root, ref, path):
    return json.loads(subprocess.check_output(['git', 'show', f'{ref}:{path}'], cwd=root))


def cf_applied(root, path):
    """Return the state after C–F catch-up, before the numeric tail."""
    before = _git_json(root, BEFORE, path)
    after = copy.deepcopy(_git_json(root, AFTER, path))
    if path == 'data/entities.json':
        previous = {e['id']: e for e in before['entities']}[SEVEN]
        after['entities'] = [previous if e['id'] == SEVEN else e for e in after['entities']]
    elif path == 'data/credits.json':
        after['credits'] = [c for c in after['credits'] if c['id'] not in NUMERIC_CREDIT_IDS]
    elif path == 'data/organizations.json':
        previous = {n['id']: n for n in before['nodes']}[SEVEN]
        after['nodes'] = [previous if n['id'] == SEVEN else n for n in after['nodes']]
        for credit_id in NUMERIC_CREDIT_IDS:
            del after['credits'][credit_id]
        progress = after['registrationProgress']
        for key in ('processedEntityIds', 'queue', 'reviewedEntities'):
            progress[key] = progress[key][:-6]
        progress.update(letter='C—F', total=320, letterTotal=8, letterProcessed=8,
                        nextEntityId='entity-5pb', nextName='5pb.',
                        audit='data/entity-creator-cf-catchup-review-20261026.md')
        progress['audits'] = progress['audits'][:-1]
    elif path == 'data/entity-migration-review.json':
        after['pendingIdentities'] = before['pendingIdentities']
    else:
        raise ValueError(path)
    return after
