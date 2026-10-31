#!/usr/bin/env python3
"""Fill only still-missing fields in seven evidence-reviewed works; never overwrite older annotations."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text(encoding='utf8'))
data=read('data/discovery-editorial.json')
catalogue={w['id']:w for w in read('data/games.json')['works']}
baseline=read('data/narrative-editorial-baseline-20261029.json')['works']
frozen=read('data/narrative-seven-r7-baseline-20261031.json')['records']
patches=read('data/narrative-evidence-seven-r7-20261031.json')['entries']
assert set(frozen)==set(patches)=={'g1452','g1455','g1462','g1464','g1490','g1492','g1500'}
fields=('position','style','theme','structure')
changed=0
for wid, patch in patches.items():
    assert wid not in baseline and wid in catalogue
    record=dict(data['works'].get(wid,{ }))
    assert record.get('status') in (None,'partial'),f'{wid}: already fully reviewed; inspect before edit'
    evidence=dict(record.get('fieldEvidence') or {})
    original_missing=set(frozen[wid]['missing'])
    for field in fields:
        value=patch.get(field)
        if not value:continue
        assert field in original_missing,f'{wid}/{field}: patch overwrites completed field'
        assert not record.get(field),f'{wid}/{field}: remote already filled; rebase needed'
        assert isinstance(value,str) if field=='position' else isinstance(value,list) and all(isinstance(x,str) and x.strip() for x in value)
        record[field]=value
        kind=patch['evidenceKind']
        rationale=f'原作级别限定补录，资料等级：{kind}。仅填此前缺项；不推断未明确证实的路线数量，亦不使用后发版新增剧情。'
        evidence[field]=dict(basis=rationale,sources=[patch['source'],*patch.get('supportingSources',[])],evidenceText=patch['evidenceText'],sourceFields=patch['sourceFields'])
        changed+=1
    record['fieldEvidence']=evidence
    record['sources']=list(dict.fromkeys([patch['source'],*patch.get('supportingSources',[]),*record.get('sources',[])]))
    record['basis']='在历史编目基础上逐字段补齐。'+patch.get('note','')+' '+record.get('basis','')
    record['reviewedAt']='2026-10-31'
    record['cover']=catalogue[wid]['title']
    missing=[f for f in fields if not record.get(f)]
    record['status']='partial' if missing else 'editorialObservation'
    if missing:
        record['openQuestions']=['仍缺'+','.join(missing)+'字段的具名原作证据']
    else:record.pop('openQuestions',None)
    data['works'][wid]=record
assert changed==20,f'Expected 20 new fields, got {changed}'
(ROOT/'data/discovery-editorial.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Seven original-scope narratives completed, 20 missing fields added; all old values retained.')
