#!/usr/bin/env python3
"""Append reviewed indie and PC-98 identities, with reproducible whole-catalogue checks."""
from registry_store import read_json as read_registry_json, write_json as write_registry_json, write_text as write_registry_text
import argparse
import copy
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
import import_basic_r134_r135_20261103 as e

ROOT=Path(__file__).resolve().parents[1]
BASE='273ad2cfd01276d06be76534486e5dd00fca23d8'
REVIEW=ROOT/'data/indiedb-itch-pc98-reviewed-r140-r141-20261103.json'
PENDING=ROOT/'data/pc98-catalogue-audit-r138-r139-20261103.json'
REPORT=ROOT/'data/basic-r140-r141-audit-summary-20261103.md'
ROUNDS=(140,141)

def old_file(path):
    return subprocess.check_output(['git','show',BASE+':'+str(path.relative_to(ROOT))],cwd=ROOT)

def build():
    original=json.loads(old_file(e.REG)); reg=copy.deepcopy(original); review=e.load(REVIEW)
    assert review['baseCommit']==BASE
    assert old_file(PENDING)==PENDING.read_bytes()
    pending=e.load(PENDING); prior={(r['catalogue'],r['sourceId']):r for r in pending['records'] if r['status'].endswith('-held') or r['status']=='needs-primary-year-and-alias-review'}
    assert len(prior)==pending['summary']['remainingUnresolvedRecords']==546
    index,refs=e.full_index(original),e.full_refs(original)
    history=[ROOT/'data/pc98-admission-review-20261103.json', ROOT/'data/pc98-admission-review-r136-r137-20261103.json',ROOT/'data/pc98-admission-review-r138-r139-20261103.json']
    e.reserve_reviewed_pc98_reuse(index,refs,history)
    folded=defaultdict(set)
    for ref,ids in refs.items():folded[ref.casefold()].update(ids)
    ids={w['id'] for w in e.catalogue.all_works(original)}
    seen_pc=set(); audits={}; report=[]
    for offset,n in enumerate(ROUNDS):
        batch=f'indiedb-itch-pc98-20261103-r{n}'
        source_rows=review['approved'][offset::2]
        assert 0<len(source_rows)<=500
        works=[]; audit_rows=[]
        for r in source_rows:
            assert r['id'] not in ids and len(r['evidence'])>=2 and 1970<=r['year']<=2026
            assert all(x.startswith('https://') for x in r['evidence'])
            assert not e.EDITION.search(' '.join([r['title'],*r.get('aliases',[])]))
            source_refs=list(dict.fromkeys([*r['refs'],*['source-url:'+x for x in r['evidence']]]))
            w={'id':r['id'],'indexId':'basic-'+batch+'-'+r['id'],'title':r['title'],'aliases':r.get('aliases',[]),
                'firstYear':r['year'],'gameplay':r['gameplay'],'gameplayNote':r['gameplayNote'],'group':r['group'],'source':r['source'],
                'sourceRefs':source_refs,'mainPlacement':'promoted-basic','linkedRecordId':None,
                'creditScope':'来源所列名称仅为检索关联，未建立正式职责。','yearBasis':r['basis'],
                'editorialScope':'仅登记作品基础身份与原作年；不建立内容版本或平台发行。','batch':batch}
            assert all(not index.get(e.norm(name)) for name in e.split_names(w)),w['title']
            assert all(not folded.get(ref.casefold()) for ref in e.refs_for(w)),w['title']
            for key in r.get('pc98Rows',[]):
                key=tuple(key); assert key in prior and key not in seen_pc
                assert prior[key]['catalogueYear']==w['firstYear'];seen_pc.add(key)
            e.reserve(w,index,folded);ids.add(w['id']);works.append(w);audit_rows.append({**w,'evidence':r['evidence'],'pc98Rows':r.get('pc98Rows',[])})
        before=len(reg['works']);reg['works'].extend(works)
        for key in ('candidates','accepted','promotedBasic','addedToMainIdentityLayer'):reg['summary'][key]+=len(works)
        reg['updated']='2026-11-03'
        path=ROOT/f'data/indiedb-itch-pc98-review-20261103-r{n}.json'
        counts=Counter('pc98' if r.get('pc98Rows') else 'indiedb' for r in source_rows)
        summary={'candidates':len(works),'promoted-basic':len(works),'sourceCounts':dict(counts)}
        reg['batches'].append({'id':batch,'source':['https://www.indiedb.com/','https://itch.io/','https://www.ikachi.org/pc9801/'],'review':str(path.relative_to(ROOT)),'summary':summary})
        audits[path]={'schema':1,'date':'2026-11-03','baseCommit':BASE,'summary':{'newDistinctWorks':len(works),'before':before,'after':len(reg['works']),'sourceCounts':dict(counts)},'records':audit_rows}
        report.append((n,len(works),counts['indiedb'],counts['pc98']))
    # Preserve every unprocessed raw row and make this audit the next resumable queue.
    queue=[]
    for key,item in prior.items():
        row=copy.deepcopy(item)
        if key in seen_pc:
            row.update(status='reviewed-candidate',candidateWorkId='pc98-igdb-239611')
        elif key==('ikachi-igdb','372561'):
            row.update(status='name-year-or-multiple-identity-held',basis='目录 1994，实物零售记录 1993；年份待核。')
        elif key in {('ikachi-igdb','194501'),('pc9801-archive','1674')}:
            row.update(status='possible-edition-or-dependent-content-held',basis='PC-98 16色版与 Windows 原作先后待核。')
        queue.append(row)
    counts=Counter(r['status'] for r in queue)
    unresolved=sum(v for k,v in counts.items() if k.endswith('-held') or k=='needs-primary-year-and-alias-review')
    assert len(queue)==546 and unresolved==545
    audits[ROOT/'data/pc98-catalogue-audit-r140-r141-20261103.json']={
        'schema':1,'date':'2026-11-03','baseCommit':BASE,'snapshotSha256':pending['snapshotSha256'],
        'inputPendingAudit':str(PENDING.relative_to(ROOT)),
        'inputPendingAuditSha256':hashlib.sha256(PENDING.read_bytes()).hexdigest(),
        'summary':{'rawRecords':len(queue),'reviewedNewWorks':len(seen_pc),'dispositions':dict(counts),
                   'snapshotRecords':pending['summary']['snapshotRecords'],'remainingUnresolvedRecords':unresolved},
        'records':queue,'scope':'仅复核明确列出的候选；未处理原始记录原样保留。'}
    assert len({w['id'] for w in reg['works']})==len(reg['works'])
    assert len({w['indexId'] for w in reg['works']})==len(reg['works'])
    assert reg['summary']['accepted']==len(reg['works'])
    lines=['# 第 140、141 批：IndieDB、itch.io 与 PC-98 人工核查','','本轮是少量逐条核查，并未穷尽任何来源；每批上限 500 部，不将待核条目计为新增。','','| 批次 | 独立游戏新增 | PC-98 新增 | 合计 |','|---|---:|---:|---:|']
    lines += [f'| {n} | {indie} | {pc} | {total} |' for n,total,indie,pc in report]
    lines += ['',f"基础身份库：{len(original['works']):,} → {len(reg['works']):,}。本次新增 5 部 IndieDB 作品，其中 4 部与 itch.io 开发者页面交叉核验；另新增 1 部 PC-98 作品。",'', '## 待核与隔离','']
    lines += [f"- {r['title']}：{r['reason']} [来源]({r['url']})" for r in review['held']]
    lines += ['',f'上轮 PC-98 待核原始记录 546 条，本次确认 1 条并入库，剩余 {len(prior)-len(seen_pc)} 条原始记录仍待核；其中若干记录可能属于同一作品。','', 'IndieDB 与 itch.io 目前没有可复现、稳定的全量续采游标。本轮从具名来源页面人工选取，保留逐条证据，不能以热门榜页码冒充稳定游标。','','逐项来源及原作年份依据见审核 JSON；历史记录与未处理队列保持不变。','']
    return original,reg,audits,'\n'.join(lines)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    old,expected,audits,report=build(); current=e.load(e.REG)
    if args.check:
        assert current==expected
        for path,value in audits.items(): assert e.load(path)==value
        assert REPORT.read_text()==report
        for name in e.catalogue.PROTECTED: assert old_file(ROOT/name)==(ROOT/name).read_bytes()
        print('BASIC_R140_R141_CHECK_OK',len(old['works']),len(expected['works']))
    else:
        assert current in (old,expected),'Unexpected registry state; refusing to overwrite'
        e.save(e.REG,expected)
        for path,value in audits.items():e.save(path,value)
        write_registry_text(REPORT, report,encoding='utf-8')
        print('BASIC_R140_R141_WRITTEN',len(old['works']),len(expected['works']))

if __name__=='__main__':main()
