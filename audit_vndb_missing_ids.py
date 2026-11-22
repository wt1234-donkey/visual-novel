#!/usr/bin/env python3
"""Read-only VNDB vs. basic registry vID audit for wt1234-donkey/visual-novel.

Run from repository root (no third-party Python packages required):
  python3 audit_vndb_missing_ids.py
  python3 audit_vndb_missing_ids.py --repo /workspaces/visual-novel

Produces JSON, CSV, and Markdown in --output. Resumes API scanning from checkpoint.
Does not change existing repository data.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

STATS = 'https://api.vndb.org/kana/stats'
API = 'https://api.vndb.org/kana/vn'
USER_AGENT = 'NarrativeCatalogue-VID-Audit/1.0 (metadata-only; github.com/wt1234-donkey/visual-novel)'
V = re.compile(r'^v([0-9]+)$', re.I)
VNDB = re.compile(r'^vndb(?:[:-])v([0-9]+)$', re.I)
URL = re.compile(r'^https?://(?:www\.)?vndb\.org/v([0-9]+)(?:[/?#].*)?$', re.I)


def canonical(x):
    if not isinstance(x, str):
        return None
    s = x.strip()
    for rx in (V, VNDB, URL):
        m = rx.fullmatch(s)
        if m:
            return 'v' + str(int(m.group(1)))
    return None


def ids_from_work(w):
    fields = [w.get('id'), w.get('indexId'), w.get('vndbId'), w.get('source')]
    fields.extend(w.get('sourceRefs') or [])
    for k in ('vndb', 'vndb_id', 'vndbID'):
        if k in w:
            fields.append(w[k])
    return {v for x in fields if (v := canonical(x))}


def get_json(url, data=None, retry=7):
    body = None if data is None else json.dumps(data, ensure_ascii=False).encode('utf-8')
    for attempt in range(retry):
        req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json', 'Accept': 'application/json', 'User-Agent': USER_AGENT}, method='POST' if body is not None else 'GET')
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retry - 1:
                raise
            raw = exc.headers.get('Retry-After', '')
            retry_after = int(raw) if raw.isdigit() else 0
            delay = max(retry_after, min(100, 12 * (attempt + 1)))
            print(f'API {exc.code}; retrying after {delay}s', file=sys.stderr, flush=True)
            time.sleep(delay)
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == retry - 1:
                raise
            time.sleep(min(90, (attempt + 1) * 10))
    raise RuntimeError('API retries exhausted')


def load_registry(repo):
    path = repo / 'data' / 'main-adv-rpg-works-20261031.json'
    if not path.exists():
        raise FileNotFoundError(f'Cannot find registry: {path}; pass --repo PATH')
    with path.open(encoding='utf-8') as f:
        reg = json.load(f)
    works = reg['works'] if isinstance(reg, dict) else reg
    if not isinstance(works, list):
        raise ValueError('Registry has no works array')
    return path, works


def load_official(output, interval, fresh=False):
    cache = output / 'vndb_official_cache.json'
    if cache.exists() and not fresh:
        with cache.open(encoding='utf-8') as f:
            state = json.load(f)
    else:
        state = {'complete': False, 'last_id': 'v0', 'rows': [], 'started': dt.datetime.now(dt.timezone.utc).isoformat()}
    if state['complete']:
        return state['rows'], state

    seen = {r['id'] for r in state['rows']}
    count = 0
    while True:
        query = {'filters': ['id', '>', state['last_id']],
                 'fields': 'title,released,devstatus', 'sort': 'id', 'reverse': False, 'results': 100}
        page = get_json(API, query)
        batch = page.get('results')
        if not isinstance(batch, list) or not isinstance(page.get('more'), bool):
            raise ValueError('VNDB API response schema differs from documentation')
        for r in batch:
            vid = canonical(r.get('id'))
            if not vid:
                raise ValueError('Unexpected official VNDB id: ' + repr(r.get('id')))
            if vid in seen:
                raise ValueError('Duplicate vID from official pagination: ' + vid)
            seen.add(vid)
            state['rows'].append({'id': vid, 'title': r.get('title') or '',
                                  'released': r.get('released'), 'devstatus': r.get('devstatus')})
        if batch:
            state['last_id'] = batch[-1]['id']
        count += 1
        if count % 10 == 0 or not page['more']:
            cache.write_text(json.dumps(state, ensure_ascii=False), encoding='utf-8')
            print(f'VNDB scanned {len(state["rows"])} IDs; last {state["last_id"]}', flush=True)
        if not page['more']:
            state['complete'] = True
            state['finished'] = dt.datetime.now(dt.timezone.utc).isoformat()
            cache.write_text(json.dumps(state, ensure_ascii=False), encoding='utf-8')
            return state['rows'], state
        if not batch:
            raise ValueError('more=true but empty page; refusing incomplete inventory')
        time.sleep(interval)  # respect API rate limits


def year_group(value):
    if not isinstance(value, str) or not re.match(r'^\d{4}', value):
        return 'unknown'
    y = int(value[:4]); return f'{(y//10)*10}s'


def write_csv(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['vndb_id', 'title', 'released', 'devstatus', 'url'])
        w.writeheader()
        for r in rows:
            vid = r['id']
            w.writerow({'vndb_id': vid, 'title': r['title'], 'released': r.get('released') or '',
                        'devstatus': r.get('devstatus'), 'url': f'https://vndb.org/{vid}'})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path.cwd(), help='Path to local visual-novel repo')
    p.add_argument('--output', type=Path, default=Path('vndb-v-id-audit'), help='Directory for reports and resumable cache')
    p.add_argument('--interval', type=float, default=1.8, help='Minimum seconds between VNDB requests (default 1.8)')
    p.add_argument('--fresh', action='store_true', help='Discard saved VNDB API scan and fetch from beginning')
    args = p.parse_args()
    if args.interval < 1.6:
        p.error('interval must be at least 1.6 seconds for VNDB rate limit')
    repo = args.repo.resolve(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    path, works = load_registry(repo)
    covered = set(); duplicate_vids = Counter(); without_ref = 0
    for work in works:
        refs = ids_from_work(work)
        if not refs:
            without_ref += 1
        for vid in refs:
            covered.add(vid)
            duplicate_vids[vid] += 1
    print(f'Basic works: {len(works)}; works lacking vID: {without_ref}; unique referenced vIDs: {len(covered)}', flush=True)
    full_path = repo / 'data' / 'games.json'
    full_ids = set()
    if full_path.exists():
        with full_path.open(encoding='utf-8') as f:
            full = json.load(f)
        if isinstance(full, dict) and isinstance(full.get('works'), list):
            for work in full['works']:
                full_ids.update(ids_from_work(work))

    stats = get_json(STATS)
    official_rows, state = load_official(out, args.interval, fresh=args.fresh)
    official = {row['id'] for row in official_rows}
    if len(official) != len(official_rows):
        raise ValueError('Duplicate official vIDs; refusing report')
    missing = sorted((r for r in official_rows if r['id'] not in covered), key=lambda x: int(x['id'][1:]))
    extra = sorted(covered - official, key=lambda x: int(x[1:]))
    seen = official & covered
    missing_in_full = [r for r in missing if r['id'] in full_ids]
    missing_in_both_by_id = [r for r in missing if r['id'] not in full_ids]
    by_decade = dict(sorted(Counter(year_group(r.get('released')) for r in missing).items()))
    by_status = dict(sorted(Counter(str(r.get('devstatus')) for r in missing).items()))
    report = {
        'generated_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'registry': str(path), 'work_count': len(works),
        'works_without_explicit_vndb_id': without_ref,
        'base_unique_vndb_id_count': len(covered),
        'official_vndb_stats_vn_count': stats.get('vn'),
        'official_scan_vn_count': len(official),
        'official_total_mismatch_at_different_scan_times': len(official) != stats.get('vn'),
        'intersection_vndb_ids': len(seen),
        'full_main_unique_vndb_ids': len(full_ids),
        'missing_in_basic_but_linked_in_main': len(missing_in_full),
        'missing_vndb_id_link_in_both_basic_and_main': len(missing_in_both_by_id),
        'official_missing_from_basic_count': len(missing),
        'official_missing_from_basic_ratio': round(len(missing)/len(official), 6) if official else None,
        'base_vndb_ids_not_in_official': len(extra),
        'base_vndb_ids_not_in_official_list': extra,
        'vndb_id_reused_by_more_than_one_basic_work_count': sum(c > 1 for c in duplicate_vids.values()),
        'missing_by_release_decade': by_decade,
        'missing_by_devstatus': by_status,
        'caveats': [
            'Strict basic works layer only; full games.json and dossier-only identities excluded.',
            'An unlinked work may already exist in basic layer without vID; missing is an ID-linkage gap until title/year review.',
            'Official inventory is a live scan, not necessarily a synchronized snapshot with GitHub registry.',
            'No automatic merge is performed and all existing data are unchanged.'
        ],
    }
    (out / 'summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    write_csv(out / 'vndb_missing_from_basic.csv', missing)
    write_csv(out / 'missing_basic_but_linked_in_main.csv', missing_in_full)
    write_csv(out / 'missing_id_link_in_both_layers.csv', missing_in_both_by_id)
    (out / 'vndb_missing_ids.txt').write_text('\n'.join(row['id'] for row in missing) + '\n', encoding='utf-8')
    (out / 'vndb_registry_ids_not_current.txt').write_text('\n'.join(extra) + '\n', encoding='utf-8')
    md = [
        '# VNDB 与基础身份库 vID 覆盖率核查', '',
        f'- 基础库作品总数：**{len(works):,}**',
        f'- 基础库引用的不同 VNDB vID：**{len(covered):,}**',
        f'- VNDB 官方当前扫描的有效 vID：**{len(official):,}**',
        f'- vID 交集：**{len(seen):,}**',
        f'- 缺少基础库 vID，但在完整主库有关联：**{len(missing_in_full):,}**',
        f'- 基础库和完整主库均无显式 vID：**{len(missing_in_both_by_id):,}**',
        f'- VNDB 有、基础库未建立 vID 关联：**{len(missing):,}**',
        f'- 基础库引用但 VNDB 当前不存在：**{len(extra):,}**',
        f'- 没有显式 vID 的基础库作品记录：**{without_ref:,}**', '',
        '## 缺失 ID 按年代', '',
        '| 年代 | 数量 |', '|---|---:|',
        *[f'| {k} | {v:,} |' for k,v in by_decade.items()], '',
        '## 解释', '',
        '这里的“缺失”表示未建立可核验的 vID 关联；不能仅凭 ID 差集认定作品本身完全不在库中。',
        '需要再以标题、别名、原作首发年、厂商核查才能认定真正漏收。',
        '详细清单：`vndb_missing_from_basic.csv`；单列 ID：`vndb_missing_ids.txt`。',
    ]
    (out / 'report.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print('\n'.join(md[:9]), flush=True)
    print('Output directory:', out, flush=True)


if __name__ == '__main__':
    main()
