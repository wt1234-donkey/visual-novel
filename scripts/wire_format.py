"""Lossless generated-resource compression; original downloads are never rewritten."""
import base64
import gzip
import json
from pathlib import Path

PREFIX = b'{"atlasWire":"gzip-base64-v1","data":"'


def decode_wire(raw):
    if not raw.startswith(PREFIX):
        return raw
    value = json.loads(raw)
    if value.get('atlasWire') != 'gzip-base64-v1' or set(value) != {'atlasWire', 'data'}:
        raise ValueError('Invalid generated resource envelope')
    return gzip.decompress(base64.b64decode(value['data'], validate=True))


def compact_generated(root):
    root = Path(root)
    original = packed = count = 0
    for name in ('basic-web', 'catalogue-web'):
        for path in (root / 'data' / name).rglob('*.json'):
            if path == root / 'data/basic-web/manifest.json':
                continue
            raw = path.read_bytes()
            if len(raw) < 1024 or raw.startswith(PREFIX):
                continue
            wrapped = PREFIX + base64.b64encode(gzip.compress(raw, compresslevel=9, mtime=0)) + b'"}\n'
            if len(wrapped) >= len(raw) * .8:
                continue
            if decode_wire(wrapped) != raw:
                raise ValueError('Generated resource compression changed bytes')
            path.write_bytes(wrapped)
            original += len(raw); packed += len(wrapped); count += 1
    return {'compressedGeneratedFiles': count, 'generatedOriginalBytes': original,
            'generatedPackedBytes': packed, 'generatedSavedBytes': original - packed}
