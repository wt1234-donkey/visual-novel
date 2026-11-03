#!/usr/bin/env python3
"""Append the requested right-only table in 500-record batches, without work deduplication."""
import argparse
import base64
import csv
import gzip
import hashlib
import io
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / 'data/main-adv-rpg-works-20261031.json'
SOURCE = ROOT / 'data/vndb-right-only-source-20261103.json.gz.b64'
MANIFEST = ROOT / 'data/vndb-right-only-manifest-20261103.json'
PREFIX = 'vndb-right-only-20261103-r'
POLICY = 'append-without-deduplication'
BASE = 'ea1fe133731527123e8f2e7de9115dc0940fa583'

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')

def source_rows():
    manifest=json.loads(MANIFEST.read_text())
    raw=gzip.decompress(base64.b64decode(SOURCE.read_bytes()))
    assert hashlib.sha256(raw).hexdigest()==manifest['sourceSha256']
    rows=json.loads(raw)
    assert len(rows)==manifest['sourceRecords']==11325
    return rows

def aliases(row):
    names=[row['原文标题'],*row['别名'].split(' | ')]
    for name in row['多语言标题'].split(' | '):
        name=re.sub(r'^\[[^]]+\]\s*','',name)
        name=re.sub(r'\s+主标题$','',name).strip()
        names.append(name)
        m=re.match(r'^(.*?)\s+\(([^()]*)\)$',name)
        if m:names.extend(m.groups())
    return list(dict.fromkeys(n for n in names if n and n!=row['VNDB主标题']))

def work_from(row, number):
    vid=row['vID']
    year=int(row['首发年份']) if row['首发年份'].isdigit() else None
    return {'id':'vndb-table-20261103-'+vid,'indexId':'basic-vndb-table-20261103-'+vid,
        'title':row['VNDB主标题'],'aliases':aliases(row),'firstYear':year,
        'gameplay':'Galgame（玩法待核）','gameplayNote':'VNDB来源条目；具体叙事定位与操作未作逐项复核。',
        'group':row['开发者（VNDB关联）'] or '创作主体待核',
        'source':row['VNDB链接'],'sourceRefs':['vndb:'+vid],
        'mainPlacement':'promoted-basic','linkedRecordId':None,
        'creditScope':'来源开发者关联仅供检索，不作为已核的正式创作职责。',
        'yearBasis':'保留上传VNDB表首发年份；空值保持null，未来年份为来源计划年，未确认实际发售。',
        'editorialScope':'用户指定右表暂独有全量追加；未作名称、年份、来源ID或版本去重。',
        'batch':PREFIX+str(number),'intakePolicy':POLICY,
        'sourceReleased':row['首发日期'],'sourceDevelopmentStatus':row['开发状态'],
        'sourceSnapshotRow':row['右表CSV行号'],
        'sourceSnapshot':'data/vndb-right-only-source-20261103.json.gz.b64',
        'priorComparisonStatus':row['比对状态']}

def append_pair(pair):
    assert 1<=pair<=12
    rows=source_rows()
    registry=json.loads(REG.read_text())
    first=145+(pair-1)*2
    batches=[n for n in (first,first+1) if n<=167]
    completed={b['id'] for b in registry['batches']}
    if all(PREFIX+str(n) in completed for n in batches):
        print('PAIR_ALREADY_IMPORTED',pair);return
    assert not any(PREFIX+str(n) in completed for n in batches),'Partial pair; inspect before resuming'
    expected_previous=PREFIX+str(first-1)
    if pair>1:assert expected_previous in completed,'Import pairs in order'
    before_pair=len(registry['works'])
    for number in batches:
        start=(number-145)*500
        block=rows[start:start+500]
        assert block and len(block)<=500
        additions=[work_from(row,number) for row in block]
        before=len(registry['works'])
        registry['works'].extend(additions)
        for k in ('candidates','accepted','promotedBasic','addedToMainIdentityLayer'):
            registry['summary'][k]+=len(block)
        audit_path=ROOT/f'data/vndb-right-only-review-20261103-r{number}.json'
        summary={'candidates':len(block),'promoted-basic':len(block),
            'appendedRecords':len(block),'before':before,'after':len(registry['works']),
            'deduplication':'not-performed','unknownYear':sum(w['firstYear'] is None for w in additions),
            'futureSourceYear':sum(w['firstYear'] is not None and w['firstYear']>2026 for w in additions)}
        registry['batches'].append({'id':PREFIX+str(number),'source':'https://vndb.org/',
            'review':str(audit_path.relative_to(ROOT)),'summary':summary})
        save(audit_path,{'schema':1,'date':'2026-11-03','intakePolicy':POLICY,
            'sourceSnapshot':str(SOURCE.relative_to(ROOT)),'sourceOffset':start,
            'summary':summary,'records':[{'vndbId':row['vID'],'workId':w['id'],
                'sourceSnapshotRow':row['右表CSV行号'],'sourceTitle':row['VNDB主标题'],
                'sourceYear':row['首发年份'],'sourceDevelopmentStatus':row['开发状态']}
                for row,w in zip(block,additions)],
            'notice':'新增条目数不是经去重确认的独立作品数；未知年份、开发中及取消项目均保留来源状态。'})
    registry['updated']='2026-11-03'
    registry['intakeOverrides']={'vndbRightOnly20261103':{
        'policy':POLICY,'sourceRecords':11325,'importedRecords':sum(w.get('intakePolicy')==POLICY for w in registry['works']),
        'scope':'仅2026-11-03用户指定的右表暂独有记录；不修改此前批次准入规则。'}}
    assert registry['summary']['accepted']==len(registry['works'])
    save(REG,registry)
    print('PAIR_IMPORTED',pair,'BATCHES',batches,'ADDED',len(registry['works'])-before_pair,'TOTAL',len(registry['works']))

def check():
    rows=source_rows();reg=json.loads(REG.read_text())
    old=json.loads(subprocess.check_output(['git','show',BASE+':data/main-adv-rpg-works-20261031.json'],cwd=ROOT))
    assert reg['works'][:len(old['works'])]==old['works'],'Historical objects changed'
    assert reg['batches'][:len(old['batches'])]==old['batches'],'Historical batches changed'
    extra=reg['works'][len(old['works']):]
    expected=[work_from(row,145+i//500) for i,row in enumerate(rows)]
    assert extra==expected,'Missing, reordered or modified source records'
    assert len(extra)==11325 and len(reg['works'])==81454
    assert reg['summary']['accepted']==len(reg['works'])
    # Internal primary keys remain valid; this is not a name/source-ID deduplication filter.
    assert len({w['id'] for w in reg['works']})==len(reg['works'])
    assert [b['summary']['appendedRecords'] for b in reg['batches'][-23:]]==[500]*22+[325]
    for key in ('candidates','accepted','promotedBasic','addedToMainIdentityLayer'):
        assert reg['summary'][key]==old['summary'][key]+11325
    assert sum(w['firstYear'] is None for w in extra)==4122
    assert all(row['首发年份']==str(w['firstYear']) if w['firstYear'] is not None else not row['首发年份'] for row,w in zip(rows,extra))
    print('VNDB_RIGHT_ONLY_CHECK_OK',len(old['works']),len(reg['works']),len(extra))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pair',type=int);p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.check:check()
    else:append_pair(a.pair)
