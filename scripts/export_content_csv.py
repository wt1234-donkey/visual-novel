"""Export one row per content identity, never one row per platform."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def content_rows(data):
    works = {w['id']: w for w in data['works']}
    for content in data['contentVersions']:
        yield {
            '作品ID': content['workId'], '内容版本ID': content['id'],
            '作品名称': works[content['workId']].get('chineseTitle') or works[content['workId']]['title'],
            '内容名称': content['label'], '内容首次年份': content['firstYear'],
            '收录依据': '原作／首批内容' if content['basis'] == 'original' else '新增内容',
            '比较对象': content.get('comparedTo', ''),
            '具体内容与差异': content['evidence'],
            '新增内容': '；'.join(a['description'] for a in content['addedContent']),
            '内容来源': content['source'],
            '关联发行ID': '、'.join(r['id'] for r in data['platformReleases'] if r['contentVersionId'] == content['id']),
        }


def csv_text(rows):
    import io
    output = io.StringIO(newline='')
    rows = list(rows)
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


if __name__ == '__main__':
    data = json.loads((ROOT / 'data/games.json').read_text())
    (ROOT / 'data/content-versions.csv').write_text(csv_text(content_rows(data)), encoding='utf-8-sig')
    coverage = json.loads((ROOT / 'data/company-coverage.json').read_text())
    review = []
    for scope, releases in [('主库', data['platformReleases']), *[(company['id'], [r for work in company.get('relatedGames', []) for r in work['platformReleases']]) for company in coverage['companies']]]:
        for r in releases:
            if r['contentVersionId'] is None:
                review.append({'范围': scope, '作品ID': r['workId'], '发行ID': r['id'], '发行年份': r['year'], '平台': r['platform'], '发行方': r['publisher'], '发行类型': r['kind'], '原差异说明': r['differences'], '待核原因': r['contentNote'], '来源': r['source']})
    (ROOT / 'data/content-review.csv').write_text(csv_text(review), encoding='utf-8-sig')
    print(f"已生成 {len(data['contentVersions'])} 行内容版本")
