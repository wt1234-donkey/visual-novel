#!/usr/bin/env python3
"""Apply only independently evidenced, previously missing narrative fields from the 22-work audit."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
base=read('data/narrative-22-baseline-r9-20261031.json')
patch=read('data/narrative-22-evidence-r9-20261031.json')['entries']
data=read('data/discovery-editorial.json')
works={x['id']:x for x in read('data/games.json')['works']}
protected=read('data/narrative-editorial-baseline-20261029.json')['works']
fields=('position','style','theme','structure')
assert len(base['records'])==22 and base['counts']['missingFields']==35
assert len(patch)==8
filled=0; complete=0
for id,e in patch.items():
    assert id in base['records'] and id not in protected and id in works
    before=data['works'].get(id,{})
    allowed=set(base['records'][id]['missing'])
    assert allowed=={f for f in fields if not before.get(f)},f'{id}: remote data diverged from frozen work state'
    record=dict(before)
    fe=dict(before.get('fieldEvidence') or {})
    urls=list(dict.fromkeys([e['source'],*e.get('supportingSources',[])]))
    for f in fields:
        v=e.get(f)
        if not v:continue
        assert f in allowed and not before.get(f),f'{id}/{f}: would overwrite prior result'
        assert (isinstance(v,str) and v.strip()) if f=='position' else (isinstance(v,list) and bool(v) and all(isinstance(a,str) and a.strip() for a in v))
        record[f]=v
        fe[f]={
            'basis':'本轮以「'+e['evidenceKind']+'」类别的作品独立材料归纳，不依据厂商或游戏类型推断未见内容。',
            'sources':urls,'evidenceText':e['evidenceText'],'sourceFields':['original title-specific story or scene arrangement','source genre and edition limits']
        }
        filled+=1
    record['fieldEvidence']=fe
    record['sources']=list(dict.fromkeys([*urls,*record.get('sources',[])]))
    record['basis']='原22部缺口专项。只处理新增可信资料支持的空缺，保留旧证据与版次边界；来源类型：'+e['evidenceKind']+'。'+str(record.get('basis',''))
    record['reviewedAt']='2026-10-31'
    record['cover']=works[id]['title']
    missing=[f for f in fields if not record.get(f)]
    record['status']='partial' if missing else 'editorialObservation'
    if missing:
        record['openQuestions']=['该作仍缺'+f+'的具体原作资料：需要说明书、原版叙事/流程或可复核的同代介绍。' for f in missing]
    else:
        record.pop('openQuestions',None);complete+=1
    data['works'][id]=record
assert filled==12 and complete==7,(filled,complete)
(R/'data/discovery-editorial.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'Backfilled {filled} source-scoped fields in {len(patch)} titles; {complete} newly complete; protected baseline unchanged.')
