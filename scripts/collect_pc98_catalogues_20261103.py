#!/usr/bin/env python3
"""Collect minimal factual metadata from two public PC-98 historical catalogues."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import html
import json
from pathlib import Path
import re
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'data/pc98-catalogue-snapshot-20261103.json'


def plain(value):
    return ' '.join(html.unescape(re.sub('<[^>]+>', ' ', value)).split())


def span(block, name):
    m = re.search(r'<span class="' + name + r'">(.*?)</span>', block, re.S)
    return plain(m[1]) if m else ''


def request(url):
    cache = Path('/tmp/pc98-catalogue-cache')
    cache.mkdir(exist_ok=True)
    path = cache / (hashlib.sha256(url.encode()).hexdigest() + '.bin')
    if path.exists():
        body = path.read_bytes()
    else:
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'NarrativeCatalogueResearch/1.2 (minimal title/year metadata; wt1234-donkey/visual-novel)'})
                with urllib.request.urlopen(req, timeout=35) as response:
                    body = response.read(8_000_001)
                assert len(body) <= 8_000_000
                path.write_bytes(body)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(3 * (attempt + 1))
    return body, {'url': url, 'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)}


def ikachi(page):
    url = f'https://www.ikachi.org/pc9801/index.php?page={page}'
    body, trace = request(url)
    source = body.decode('utf-8')
    rows = []
    for block in re.findall(r'<li class="pc-card">(.*?)</li>', source, re.S):
        link = re.search(r'class="pc-card-link" href="([^"]+)"', block)
        assert link
        uid = re.search(r'game/(\d+)/', link[1])[1]
        meta = span(block, 'pc-card-meta')
        year = re.search(r'(\d{4})年', meta)
        rows.append({'catalogue': 'ikachi-igdb', 'sourceId': uid,
            'source': urllib.parse.urljoin('https://www.ikachi.org/pc9801/', html.unescape(link[1])),
            'title': span(block, 'pc-card-title'), 'latin': span(block, 'pc-card-title-en'),
            'catalogueYear': int(year[1]) if year else None,
            'genre': span(block, 'pc-card-genre'), 'brand': span(block, 'pc-card-maker'),
            'sourceRefs': ['igdb:' + uid], 'snapshotPage': url})
    trace['returned'] = len(rows)
    print('PC98_IKACHI', page, len(rows), flush=True)
    return rows, trace


def archive(page):
    params = urllib.parse.urlencode({'categories': '93,94', 'per_page': 100,
        'page': page, 'orderby': 'id', 'order': 'asc', '_fields': 'id,link,title,content'})
    url = 'https://pc-9801.com/wp-json/wp/v2/posts?' + params
    body, trace = request(url)
    records = json.loads(body)
    assert isinstance(records, list)
    rows = []
    for item in records:
        content = item['content']['rendered']
        en = re.search(r'<span class="En">(.*?)</span>', content, re.S)
        metadata = plain(content)
        year_genre = re.search(r'([^/<>]+)/\s*(\d{4})[・･](AVG|RPG)', metadata)
        rows.append({'catalogue': 'pc9801-archive', 'sourceId': str(item['id']),
            'source': item['link'], 'title': plain(item['title']['rendered']),
            'latin': plain(en[1]) if en else '',
            'catalogueYear': int(year_genre[2]) if year_genre else None,
            'genre': year_genre[3] if year_genre else '', 'brand': '',
            'pc9801Explicit': bool(re.search(r'PC[-－]?9801', metadata, re.I)),
            'sourceRefs': ['pc9801archive:' + str(item['id'])], 'snapshotPage': url})
    trace['returned'] = len(rows)
    print('PC98_ARCHIVE', page, len(rows), flush=True)
    return rows, trace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        data = json.loads(OUTPUT.read_text())
        assert len(data['records']) == data['summary']['rawRecords']
        assert len({(r['catalogue'], r['sourceId']) for r in data['records']}) == len(data['records'])
        assert sum(t['returned'] for t in data['paginationTrace']) == len(data['records'])
        print('PC98_SNAPSHOT_CHECK_OK', len(data['records']))
        return
    jobs = [(ikachi, n) for n in range(1, 17)] + [(archive, n) for n in range(1, 11)]
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(lambda pair: pair[0](pair[1]), jobs))
    rows = [r for records, _ in results for r in records]
    data = {'schema': 1, 'date': '2026-11-03', 'summary': {'rawRecords': len(rows)},
        'paginationTrace': [trace for _, trace in results], 'records': rows,
        'scope': 'Public title, aliases, catalogue year, genre and stable catalogue IDs only; no images or descriptions copied.',
        'caveats': ['Catalogue years may describe a platform release or reissue. A new original identity needs separate evidence; existing-name year conflicts remain held.',
            'IKACHI metadata is credited to IGDB. The second catalogue is an independent historical platform index, not a primary release certificate.']}
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print('PC98_SNAPSHOT_SAVED', len(rows), flush=True)


if __name__ == '__main__':
    main()
