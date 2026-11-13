"""One-time, reproducible projections of committed evidence; never run by current tests."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT/'tests/fixtures/history-contracts.json'


def snapshot(ref, path):
    value = subprocess.check_output(['git', 'show', f'{ref}:{path}'], cwd=ROOT)
    return value, {'commit': subprocess.check_output(['git', 'rev-parse', ref], cwd=ROOT, text=True).strip(),
                   'path': path, 'sha256': hashlib.sha256(value).hexdigest(), 'bytes': len(value)}


def build():
    baseline = json.loads((ROOT/'data/entity-migration-baseline.json').read_text())
    anchors = {}
    for name in baseline['originalDossiers']:
        raw, provenance = snapshot(baseline['baseCommit'], name+'.html')
        anchors[name+'.html'] = {'source': provenance, 'anchors': sorted(set(re.findall(r'\bid="([^"]+)"', raw.decode())))}
    ref = '42d02604a6648be5d512b607d902292c4ac587e4'
    raw, coverage_source = snapshot(ref, 'data/company-coverage.json')
    company = next(row for row in json.loads(raw)['companies'] if row['id'] == 'banpresto')
    page, page_source = snapshot(ref, 'banpresto.html')
    page = page.decode()
    shell, shell_source = snapshot('6f2e754', 'index.html')
    queue = json.loads((ROOT/'data/entity-verification-evidence-index-20261026.json').read_text())
    raw, queue_source = snapshot(queue['baselineTree'], 'data/credits.json')
    pending = [f"role:{m['dossierId']}:{m['workId']}" for m in json.loads(raw)['dossierMemberships'] if m['status'] == 'pendingRole']
    raw, enix_source = snapshot('2c1e3874d369da741c42ef909bfcc5e24a6570c2', 'data/games.json')
    enix = json.loads(raw);ids = {'g996','g997','g998','g999','g1000','g1001','g1002'}
    enix_data = {'works': [w for w in enix['works'] if w['id'] in ids],
                 'contentVersions': [v for v in enix['contentVersions'] if v['workId'] in ids],
                 'platformReleases': [v for v in enix['platformReleases'] if v['workId'] in ids]}
    return {'schemaVersion': 1, 'dossierAnchors': anchors,
        'enix': {'source': enix_source, 'data': enix_data},
        'banpresto': {'sources': [coverage_source, page_source],
            'company': {key: company[key] for key in ['workIds', 'relatedGames', 'historicalArchive']},
            'articleIds': re.findall(r'<article class="card" id="([^"]+)"', page),
            'listIds': re.findall(r'<li id="([^"]+)"', page),
            'hrefs': re.findall(r'href="([^"]+)"', page)},
        'retainedCatalogue': {'source': shell_source, 'html': shell.decode()},
        'pendingRoleClaims': {'source': queue_source, 'claims': sorted(pending)}}


if __name__ == '__main__':
    value = json.dumps(build(), ensure_ascii=False, sort_keys=True, separators=(',', ':'))+'\n'
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(value)
    print(json.dumps({'path': str(TARGET.relative_to(ROOT)), 'bytes': len(value.encode()), 'sha256': hashlib.sha256(value.encode()).hexdigest()}))
