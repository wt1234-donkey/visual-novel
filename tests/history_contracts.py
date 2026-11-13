"""Load compact projections, with integrity checked outside historical Git."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def contracts():
    policy = json.loads((ROOT/'config/test-capabilities.json').read_text())
    fixture = policy['fixtures'][0]
    data = (ROOT/fixture['path']).read_bytes()
    if hashlib.sha256(data).hexdigest() != fixture['sha256']:
        raise ValueError('Historical contract fixture checksum mismatch')
    return json.loads(data)
