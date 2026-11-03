#!/usr/bin/env python3
"""Capture public metadata once; imports use the committed snapshot, never a live rank."""
import argparse
import hashlib
import json
import time
import urllib.request
from pathlib import Path

UA = 'wt1234-donkey/visual-novel (https://github.com/wt1234-donkey/visual-novel; catalogue metadata)'

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=45) as res:
        return json.load(res)

def collect(cache, pages):
    cache.mkdir(parents=True, exist_ok=True)
    rows = []
    for offset in range(0, pages * 50, 50):
        path = cache / f'bangumi-{offset:06d}.json'
        if path.exists():
            page = json.loads(path.read_text())
        else:
            page = fetch(f'https://api.bgm.tv/v0/subjects?type=4&limit=50&offset={offset}')
            path.write_text(json.dumps(page, ensure_ascii=False), encoding='utf-8')
            time.sleep(1)
        assert page['offset'] == offset and page['limit'] == 50
        for row in page['data']:
            assert row['type'] == 4
            rows.append({k: row.get(k) for k in ('id', 'name', 'name_cn', 'date', 'infobox', 'summary', 'meta_tags', 'tags')})
        print('BANGUMI_SNAPSHOT', offset, len(page['data']), 'lastId', rows[-1]['id'], flush=True)
        if len(page['data']) < 50:
            break
    assert len({x['id'] for x in rows}) == len(rows), 'Source shifted; do not advance cursor'
    assert [x['id'] for x in rows] == sorted(x['id'] for x in rows), 'Observed ordering changed'
    snapshot = {'schema': 1, 'date': '2026-11-03', 'source': 'https://api.bgm.tv/v0/subjects',
                'query': {'type': 4, 'limit': 50, 'startOffset': 0},
                'nextCursor': {'offset': len(rows), 'lastSubjectId': rows[-1]['id'],
                               'boundaryIds': [r['id'] for r in rows[-50:]],
                               'continuationPolicy': 're-read previous page and verify boundaryIds before resuming offset'},
                'records': rows}
    return snapshot

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--cache', type=Path, required=True)
    p.add_argument('--pages', type=int, default=60)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    data = collect(a.cache, a.pages)
    # Keep only required facts and short scope/version excerpts, with full-text hashes.
    import import_basic_r142_r143_20261103 as policy
    for r in data['records']:
        text = r.get('summary') or ''
        snippets = []
        for pattern in (policy.NARRATIVE, policy.DERIVATIVE, policy.CANCELLED):
            match = pattern.search(text)
            if match:
                snippets.append(text[max(0,match.start()-35):match.end()+75])
        r['summarySha256'] = hashlib.sha256(text.encode()).hexdigest()
        r['summary'] = ' … '.join(snippets)
        r['infobox'] = [x for x in r.get('infobox') or [] if x['key'] in {'别名','游戏类型','发行日期','开发','游戏开发商','开发商'}]
        r.pop('tags',None)
    a.output.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':'))+'\n', encoding='utf-8')
    print('SAVED', len(data['records']), hashlib.sha256(a.output.read_bytes()).hexdigest())
