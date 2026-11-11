"""Logical registry I/O; the legacy filename is now a checked shard manifest."""
import hashlib
import json
import os
from pathlib import Path

NAME = 'main-adv-rpg-works-20261031.json'
FORMAT = 'registry-shards-v1'
SHARD_SIZE = 1000


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n'


def logical_digest(value):
    return hashlib.sha256((json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()).hexdigest()


def blob_sha(raw):
    return hashlib.sha1(('blob ' + str(len(raw)) + '\0').encode() + raw).hexdigest()


def read_json(path):
    path = Path(path)
    value = json.loads(path.read_text(encoding='utf-8'))
    storage = value.get('storage') if isinstance(value, dict) else None
    if not storage or storage.get('format') != FORMAT:
        return value
    if path.name != NAME or storage.get('schemaVersion') != 1:
        raise ValueError('Invalid registry manifest')
    works = []
    seen = set()
    for index, ref in enumerate(storage['shards']):
        expected = f'basic-registry/works-{index:05}-' + ref['sha256'][:12] + '.json'
        if ref['path'] != expected:
            raise ValueError('Invalid registry shard path')
        raw = (path.parent / expected).read_bytes()
        if len(raw) != ref['bytes'] or hashlib.sha256(raw).hexdigest() != ref['sha256'] or blob_sha(raw) != ref['gitSha']:
            raise ValueError('Registry shard checksum mismatch: ' + expected)
        rows = json.loads(raw)
        if not isinstance(rows, list) or len(rows) != ref['count']:
            raise ValueError('Registry shard count mismatch')
        for work in rows:
            if work['id'] in seen:
                raise ValueError('Duplicate registry identity')
            seen.add(work['id'])
        works.extend(rows)
    result = {k: v for k, v in value.items() if k != 'storage'}
    result['works'] = works
    if len(works) != storage['count'] or len(works) != result['summary']['accepted']:
        raise ValueError('Registry accounting mismatch')
    if logical_digest(result) != storage['logicalSha256']:
        raise ValueError('Logical registry checksum mismatch')
    return result


def _atomic(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == raw:
        return
    temp = path.with_name(path.name + '.tmp-' + str(os.getpid()))
    temp.write_bytes(raw)
    temp.replace(path)


def write_json(path, value, *, compact_output=False, sharded=None):
    path = Path(path)
    if sharded is None:
        sharded = path.name == NAME and path.exists() and json.loads(path.read_text()).get('storage', {}).get('format') == FORMAT
    if path.name != NAME or not sharded:
        text = compact(value) if compact_output else json.dumps(value, ensure_ascii=False, indent=2) + '\n'
        _atomic(path, text.encode())
        return
    works = value['works']
    if len({w['id'] for w in works}) != len(works) or value['summary']['accepted'] != len(works):
        raise ValueError('Invalid registry identities or accounting')
    refs = []
    for offset in range(0, len(works), SHARD_SIZE):
        rows = works[offset:offset + SHARD_SIZE]
        raw = compact(rows).encode()
        name = f'basic-registry/works-{offset // SHARD_SIZE:05}-' + hashlib.sha256(raw).hexdigest()[:12] + '.json'
        _atomic(path.parent / name, raw)
        refs.append({'path': name, 'count': len(rows), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'gitSha': blob_sha(raw)})
    manifest = {k: v for k, v in value.items() if k not in {'works', 'storage'}}
    manifest['storage'] = {'format': FORMAT, 'schemaVersion': 1, 'count': len(works), 'shardSize': SHARD_SIZE,
                           'logicalSha256': logical_digest(value), 'shards': refs,
                           'formalLinks': {w['id']: w.get('linkedRecordId') or w['id'] for w in works if w.get('linkedRecordId') or w.get('mainPlacement') == 'existing-complete'}}
    # Shards are staged before the manifest. Publish all changed files in one Git commit.
    _atomic(path, (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode())
    expected = {ref['path'] for ref in refs}
    for old in (path.parent / 'basic-registry').glob('works-*.json'):
        if old.relative_to(path.parent).as_posix() not in expected:
            old.unlink()


def write_text(path, text, *args, **kwargs):
    path = Path(path)
    if path.name == NAME:
        write_json(path, json.loads(text))
        return len(text)
    return path.write_text(text, *args, **kwargs)


def migrate(root, check=False):
    path = Path(root) / 'data' / NAME
    physical = json.loads(path.read_text())
    if check and physical.get('storage', {}).get('format') != FORMAT:
        raise ValueError('Registry must use sharded storage')
    value = read_json(path)
    if not check:
        write_json(path, value, sharded=True)
    return {'count': len(value['works']), 'logicalSha256': logical_digest(value)}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--root', default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(migrate(args.root, args.check)))
