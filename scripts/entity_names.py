"""Display names only: never use this table to resolve or merge identities."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'data/entity-display-names.json').read_text(encoding='utf-8'))
NAMES = CONFIG['names']


def display_name(raw):
    parts = NAMES.get(raw)
    return f'{parts["english"]}（{parts["japanese"]}）' if parts else raw


def apply_names(entities, dossiers):
    # Run AFTER all historical credits have been resolved and recorded.
    for entity in entities.values():
        raw = entity['name']
        parts = NAMES.get(raw)
        if not parts:
            continue
        entity['name'] = display_name(raw)
        entity['nameParts'] = dict(parts)
        entity['aliases'] = list(dict.fromkeys([
            *entity['aliases'], raw, parts['english'], parts['japanese'], entity['name']]))
    for dossier in dossiers:
        dossier['name'] = display_name(dossier['name'])
