"""Apply independently sourced corrections to the frozen historical dossier input."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def review():
    return json.loads((ROOT / 'data/organization-round28-closure-20261028.json').read_text())


def corrected_coverage(coverage):
    closure = review()
    correction = closure['asciiCorrection']
    company = next(c for c in coverage['companies'] if c['id'] == correction['dossierId'])
    work = next(w for w in company['relatedGames'] if w['id'] == correction['workId'])
    old = work['editionCredits']
    assert len(old) == 1 and old[0]['publisher'] == correction['oldEditionPublisher']
    assert old[0]['year'] == correction['year'] and old[0]['platform'] == correction['platform']
    work['editionCredits'] = [{**old[0], 'publisher': correction['newEditionPublisher'],
                               'source': correction['source'],
                               'reason': '1997年Saturn版T-27801G由SEGA官方表列メディアワークス；ASCII旧署名已纠正'}]
    work['notes'] = ('1995年PC Engine原版由Hudson发行；1997年Saturn版T-27801G由Media Works发行。'
                     'ASCII直接发行旧说已撤销，本卡只保留专题历史归属纠正与作品锚点。')
    for entry in company['entries']:
        if entry.get('title') == work['title']:
            assert correction['workId'] in entry['relatedIds']
            entry.update(status='归属纠正／历史对照', reason=work['notes'], source=correction['source'])
        elif entry.get('title') == '原作首年与ASCII代理年':
            entry['reason'] = entry['reason'].replace('AnEarth、', '').replace('后ASCII参与另记',
                '后ASCII参与仅在有逐版证据时另记；AnEarth旧归属已纠正')
    madosoft = next(c for c in coverage['companies'] if c['id'] == 'madosoft')
    mobile = next(e for e in madosoft['entries'] if e['title'] == 'ナマイキデレーション Mobage／GREE 版')
    mobile['reason'] = ('2016年Mobage g209-v2、GREE g209-v3的存档应用页均署服务提供方株式会社NextNinja；'
                        '平台与原始发行栏仍分开，PC首发和DMM Android版不继承该结论。')
    mobile['source'] = next(r for r in closure['records'] if r['recordId']=='identity-37')['sources'][1]['url']
    sinclair = next(c for c in coverage['companies'] if c['id'] == 'sinclair')
    ql = next(e for e in sinclair['entries'] if e['title'] == 'The Adventure／QL Classic Adventures')
    ql['reason'] = ('1985年QL合辑手册确认The Adventure为Crowther/Woods作品更新版，'
                    'Sinclair Research Ltd初版出版及包装文档版权，Abersoft Ltd软件署名；'
                    '限定版次补充索引，不猜配旧g089-v1—v4，也不新增未核内容版本。')
    return coverage
