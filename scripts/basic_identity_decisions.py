"""Use only explicitly reviewed source aliases and exact name-collision decisions."""
from functools import lru_cache
import json
from pathlib import Path

REVIEWS = [
    Path(__file__).resolve().parents[1] / 'data/basic-r92-r93-conflict-review-20261102.json',
    Path(__file__).resolve().parents[1] / 'data/basic-r118-r119-identity-review-20261102.json',
    Path(__file__).resolve().parents[1] / 'data/basic-r118-r119-last20-decisions-20261102.json',
]


@lru_cache(maxsize=1)
def decisions():
    rows = []
    for path in REVIEWS:
        if path.exists():
            rows.extend(json.loads(path.read_text(encoding='utf-8'))['decisions'])
    return rows


def reused_source_identities(known_ids):
    return {r['sourceIdentity']: r['registryId'] for r in decisions()
            if r['status'] == 'reuse-existing' and r['registryId'] in known_ids}


def reviewed_name_matches(work):
    for row in decisions():
        if (row['status'] == 'registered-distinct' and row['registryId'] == work['id']
                and row['title'] == work['title'] and row['firstYear'] == work['firstYear']
                and row['sourceIdentity'] in work.get('sourceRefs', [])):
            return {(m[0], m[1]) for m in row['currentNameMatches']}
    return set()
