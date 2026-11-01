#!/usr/bin/env python3
"""Append audited historical identities; never overwrite or infer platform editions."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

import import_nextmoe_basic_20261101_r2 as common

ROOT = Path(__file__).resolve().parents[1]
INTAKE = ROOT / 'data/historical-western-jp-intake-20261101.json'
AUDIT = ROOT / 'data/historical-western-jp-audit-20261101.json'
REPORT = ROOT / 'docs/historical-western-jp-20261101.md'
BATCH = 'historical-western-jp-20261101'

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def validate_candidate(row):
    assert row['evidenceLevel'] == 'A-identity-year'
    assert row['yearPrecision'] == 'year'
    assert row['gameplay'] == 'ADV'
    assert row['evidenceNote'] and row['sourceRefs'] and row['title']
    assert (1990 <= row['firstYear'] <= 1999 if row['regionScope']=='欧美' else 1980 <= row['firstYear'] <= 1989)
    url = urlsplit(row['source'])
    assert url.scheme == 'https'
    if row['evidenceType'] == 'authorized-store-product':
        assert url.netloc == 'www.gog.com' and re.fullmatch('/en/game/[a-z0-9_]+', url.path)
    else:
        assert row['evidenceType'] == 'rightsholder-reissue-announcement'
        assert url.netloc in ('d4e.co.jp', 'prtimes.jp')
        assert url.path not in ('', '/', '/game/')

def check_existing(registry, intake):
    audit = load(AUDIT)
    batch = [b for b in registry.get('batches', []) if b['id']==BATCH]
    assert len(batch)==1
    assert audit['intakeSha256']==digest(intake), 'Intake changed after import'
    old_count = audit['summary']['before']
    assert digest(registry['works'][:old_count])==audit['existingWorksSha256'], 'Existing identity changed'
    added = [w for w in registry['works'] if w.get('batch')==BATCH]
    assert len(added)==audit['summary']['newDistinctWorks']==batch[0]['summary']['promoted-basic']
    assert {w['id'] for w in added}=={w['id'] for w in audit['records']}
    for work in added:
        assert work == next(r['registryRecord'] for r in audit['records'] if r['id']==work['id'])
    assert registry['summary']['accepted']==len(registry['works'])
    print('Verified imported batch:', len(added), 'works; existing objects preserved')

def report(audit):
    s=audit['summary']
    lines=['# 1990年代欧美图形冒险与日本早期AVG补录（2026-11-01）', '',
        f"基础身份库：{s['before']:,} → {s['after']:,}；新增 {s['newDistinctWorks']} 部，其中欧美 {s['byRegion'].get('欧美',0)} 部，日本 {s['byRegion'].get('日本',0)} 部。", '',
        '仅补充基本身份、原作年份、别名、粗粒度AVG玩法和来源。A-identity-year只表示本轮身份与年份的证据等级；不代表职员职责、全球首发平台、月日或内容版本已核实。', '',
        '授权销售页只采用作品原作年份；官方复刻公告只采用正文的原作年份。商店上架日、默认1月1日和现代兼容系统不转为历史发行记录。group仅作来源品牌关联，不产生正式开发/发行职责。', '',
        '| 作品 | 原作年 | 范围 | 来源 |', '| --- | --- | --- | --- |']
    for r in audit['records']:
        lines.append(f"| {r['title']} | {r['firstYear']} | {r['regionScope']} | [详情]({r['source']}) |")
    lines += ['', '## 已有作品去重', '', '下列作品已存在于基础身份、主库或专题关联库，复用已有身份，本轮不重复新增：', '']
    for r in audit['duplicates']:
        lines.append('- '+r['title']+'：'+', '.join(sorted({x[0] for x in r['matches']})))
    lines += ['', '## 暂缓项目', '']
    for r in audit['heldForReview']:
        lines.append('- '+r['title']+'：'+r['reason'])
    lines += ['', '## 审核与上线', '',
        '记录了逐条证据说明、别名匹配及批次前已有作品对象哈希。导入脚本可重复执行而不新增第二份。代码/数据验证通过后提交PR，审核合并main，由GitHub Pages发布；实际状态以PR与Pages工作流为准。', '',
        '此前的1970—1980年代草稿PR #221独立保留，本轮不将其未核来源和未生成身份一并合入。', '']
    REPORT.write_text('\n'.join(lines), encoding='utf-8')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args=parser.parse_args()
    intake=load(INTAKE)
    registry=load(common.REGISTRY)
    if any(b['id']==BATCH for b in registry.get('batches', [])):
        check_existing(registry, intake)
        return
    assert not args.check, 'Batch has not been imported'
    before=copy.deepcopy(registry)
    index=common.existing_index(registry)
    ids={w['id'] for w in registry['works']}
    index_ids={w['indexId'] for w in registry['works']}
    source_refs={r for w in registry['works'] for r in w.get('sourceRefs',[])}
    additions, records, duplicates = [], [], []
    held=copy.deepcopy(intake['heldForReview'])
    def matches(row):
        return set().union(*(index.get(common.norm(n), set()) for n in [row['title'],*row.get('aliases',[])]))
    for row in intake['records']:
        validate_candidate(row)
        hits=matches(row)
        if hits:
            if any(h[1]==row['firstYear'] for h in hits):
                duplicates.append(dict(title=row['title'],matches=[list(h) for h in sorted(hits)]))
            else:
                held.append(dict(title=row['title'],reason='同名或别名年份冲突',matches=[list(h) for h in sorted(hits)]))
            continue
        assert not source_refs.intersection(row['sourceRefs']), 'Source ref already exists; review canonical identity'
        key=hashlib.sha256(row['sourceRefs'][0].encode()).hexdigest()[:16]
        wid='historical-'+key
        iid='basic-historical-20261101-'+key
        assert wid not in ids and iid not in index_ids
        work=dict(id=wid,indexId=iid,title=row['title'],aliases=row['aliases'],firstYear=row['firstYear'],gameplay='ADV',gameplayNote=row['gameplayNote'],group=row['group'],source=row['source'],sourceRefs=row['sourceRefs'],mainPlacement='promoted-basic',linkedRecordId=None,creditScope='来源中的品牌关联，仅用于检索；未断言个人创作者或历史开发、发行职责。',yearBasis=row['evidenceNote'],editorialScope='基本作品身份及年粒度原作年份；详细剧情、创作者及版本内容尚待专门编目。',batch=BATCH)
        additions.append(work)
        records.append({**row,'id':wid,'registryRecord':work})
        ids.add(wid);index_ids.add(iid);source_refs.update(row['sourceRefs'])
        for n in [row['title'],*row['aliases']]:
            index[common.norm(n)].add((wid,row['firstYear'],'current-batch'))
    for row in intake['knownDuplicateCandidates']:
        hits=matches(row)
        assert hits, 'Expected historical identity not found: '+row['title']
        duplicates.append(dict(title=row['title'],matches=[list(h) for h in sorted(hits)]))
    assert additions and len(additions)<=500
    n=len(additions)
    registry['works'].extend(additions)
    registry['updated']='2026-11-01'
    for key in ('candidates','accepted','promotedBasic','addedToMainIdentityLayer'):
        registry['summary'][key]+=n
    registry['batches'].append(dict(id=BATCH,source='Reviewed authorized-store and rightsholder announcements',review=str(AUDIT.relative_to(ROOT)),summary={'candidates':n,'promoted-basic':n,'reviewedCandidates':len(intake['records']),'deduplicated':len(duplicates),'held':len(held)}))
    assert registry['works'][:len(before['works'])]==before['works']
    assert registry['summary']['accepted']==len(registry['works'])
    assert len(ids)==len(registry['works'])
    audit=dict(schema=1,date='2026-11-01',batch=BATCH,intakeSha256=digest(intake),existingWorksSha256=digest(before['works']),criteria=intake['criteria'],summary=dict(before=len(before['works']),after=len(registry['works']),newDistinctWorks=n,byRegion=dict(Counter(r['regionScope'] for r in records)),duplicates=len(duplicates),held=len(held)),records=records,duplicates=duplicates,heldForReview=held)
    save(common.REGISTRY,registry)
    save(AUDIT,audit)
    report(audit)
    check_existing(registry,intake)
    print(json.dumps(audit['summary'],ensure_ascii=False))

if __name__=='__main__':
    main()
