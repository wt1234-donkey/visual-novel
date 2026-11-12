"""Prepare one declared batch from an immutable normalized source snapshot."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from datetime import date
from date_contract import is_recorded_year
from registry_store import read_json, write_json, logical_digest
from source_urls import source_url_valid

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = 'data/main-adv-rpg-works-20261031.json'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def scoped(root, path, prefix):
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root / prefix) or resolved.suffix != '.json' or resolved.is_symlink():
        raise ValueError('Invalid batch input path: ' + str(path))
    return resolved


def title_key(value):
    return re.sub(r'[^\w]', '', unicodedata.normalize('NFKC', value).casefold())


def prepare(plan_path, root=ROOT, apply=False):
    root = Path(root).resolve()
    plan_file = scoped(root, plan_path, 'config/intake-plans')
    plan_raw = plan_file.read_bytes()
    plan = json.loads(plan_raw)
    if plan.get('schemaVersion') != 1 or not re.fullmatch(r'[a-z0-9][a-z0-9-]{2,79}', plan.get('batchId', '')):
        raise ValueError('Invalid batch plan identity')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', plan.get('date', '')):
        raise ValueError('Batch date is required')
    date.fromisoformat(plan['date'])
    source = scoped(root, plan['sourceSnapshot'], 'data/intake')
    raw = source.read_bytes()
    if digest(raw) != plan['sourceSha256']:
        raise ValueError('Source snapshot changed')
    payload = json.loads(raw)
    rows = payload['records']
    limit = plan.get('batchSize', 500)
    if payload.get('schemaVersion') != 1 or type(limit) != int or not 1 <= limit <= 500 or not isinstance(rows, list) or len(rows) > limit:
        raise ValueError('One batch must contain at most its declared limit (maximum 500)')
    store = read_json(root / REGISTRY)
    completed = next((b for b in store.get('batches', []) if b['id'] == plan['batchId']), None)
    if completed:
        if completed.get('planSha256') != digest(plan_raw) or completed.get('sourceSha256') != digest(raw):
            raise ValueError('Batch ID was already used for different input')
        audit = json.loads((root / completed['review']).read_text())
        current = {w['id']: w for w in store['works']}
        if any(current.get(w['id']) != w for w in audit['acceptedRecords']):
            raise ValueError('Applied batch records no longer match their audit')
        return {**audit, 'alreadyApplied': True}
    if logical_digest(store) != plan['expectedRegistryLogicalSha256']:
        raise ValueError('Registry baseline moved; prepare a fresh plan')
    ids = {w['id'] for w in store['works']}
    indexes = {w.get('indexId') for w in store['works']}
    names = {}
    sources = {}
    for w in store['works']:
        for name in [w['title'], *w.get('aliases', [])]:
            names.setdefault(title_key(name), set()).add(w.get('firstYear'))
        if w.get('sourceIdentity'):
            sources.setdefault(w['sourceIdentity'], set()).add(w.get('firstYear'))
    accepted, duplicate, held = [], [], []
    for number, original in enumerate(rows, 1):
        w = deepcopy(original)
        for key in ('id', 'indexId', 'title', 'gameplay', 'group', 'source'):
            if not isinstance(w.get(key), str) or not w[key].strip():
                raise ValueError(f'Row {number} lacks {key}')
        year = w.get('firstYear')
        if not is_recorded_year(year):
            raise ValueError('Invalid registered year')
        if not source_url_valid(w['source']) or not isinstance(w.get('aliases', []), list) or any(not isinstance(a, str) for a in w.get('aliases', [])):
            raise ValueError('Invalid source URL or aliases')
        if w['id'] in ids or w['indexId'] in indexes:
            raise ValueError('Identity collision; existing records cannot be overwritten')
        ids.add(w['id']); indexes.add(w['indexId'])
        if w.get('sourceIdentity') is not None and (not isinstance(w['sourceIdentity'], str) or not w['sourceIdentity'].strip()):
            raise ValueError('Source identity must be an explicit stable external key')
        previous = set().union(*(names.get(title_key(n), set()) for n in [w['title'], *w.get('aliases', [])]))
        source_years = sources.get(w.get('sourceIdentity'), set())
        if w.get('identityStatus') != 'independent' or (source_years and year not in source_years):
            held.append({'row': number, 'record': w, 'reason': 'identity/version or year conflict requires separate resolution'})
            continue
        if source_years:
            duplicate.append({'row': number, 'record': w, 'reason': 'same explicit source identity and registered year'})
            continue
        if previous:
            held.append({'row': number, 'record': w, 'reason': 'name or alias overlaps; independent identity requires separate resolution'})
            continue
        for name in [w['title'], *w.get('aliases', [])]:
            names.setdefault(title_key(name), set()).add(year)
        if w.get('sourceIdentity'):
            sources.setdefault(w['sourceIdentity'], set()).add(year)
        w.update({'batch': plan['batchId'], 'sourceSnapshot': plan['sourceSnapshot'], 'sourceSnapshotRow': number, 'mainPlacement': 'promoted-basic', 'linkedRecordId': None})
        w.setdefault('aliases', [])
        accepted.append(w)
    result = deepcopy(store)
    result['works'].extend(accepted)
    summary = {'candidates': len(rows), 'accepted': len(accepted), 'duplicates': len(duplicate), 'quarantined': len(held), 'before': len(store['works']), 'after': len(result['works'])}
    audit = {'schemaVersion': 1, 'batchId': plan['batchId'], 'planSha256': digest(plan_raw), 'sourceSha256': digest(raw), 'summary': summary, 'acceptedRecords': accepted, 'duplicates': duplicate, 'quarantined': held, 'alreadyApplied': False}
    if apply:
        for key in ('accepted', 'promotedBasic', 'addedToMainIdentityLayer'):
            result['summary'][key] += len(accepted)
        result['summary']['candidates'] += len(rows)
        review = 'data/intake-results/' + plan['batchId'] + '.json'
        result.setdefault('batches', []).append({'id': plan['batchId'], 'source': plan['sourceSnapshot'], 'sourceSha256': digest(raw), 'planSha256': digest(plan_raw), 'review': review, 'summary': summary})
        result['updated'] = plan['date']
        # Both paths are staged in one candidate Git commit by the workflow.
        write_json(root / review, audit)
        write_json(root / REGISTRY, result)
    return audit


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--report', required=True)
    args = parser.parse_args()
    report = prepare(args.plan, apply=args.apply)
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report['summary'], ensure_ascii=False))
