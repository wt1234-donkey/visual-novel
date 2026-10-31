#!/usr/bin/env python3
"""Append source-scoped four-field annotations only for the six currently unresolved studio works."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
P=read('data/narrative-six-final-r8-20261031.json')
db=read('data/games.json')
ed=read('data/discovery-editorial.json')
old8=read('data/narrative-editorial-baseline-20261029.json')['works']
works={w['id']:w for w in db['works']}
FIELDS=('position','style','theme','structure')
expected={'g1418':set(FIELDS),'g1419':{'structure'},'g1420':set(FIELDS),'g1421':set(FIELDS),'g1448':set(FIELDS),'g1482':set(FIELDS)}
assert set(P['entries'])==set(expected)
filled=0
for wid,patch in P['entries'].items():
    assert wid in works and wid not in old8
    prior=ed['works'].get(wid,{})
    missing={f for f in FIELDS if not prior.get(f)}
    assert missing==expected[wid],f'{wid}: field state changed since review: {missing}'
    record=dict(prior)
    record['fieldEvidence']=dict(prior.get('fieldEvidence') or {})
    e_source=list(dict.fromkeys([patch['source'],*patch.get('supportingSources',[])]))
    for field in FIELDS:
        value=patch.get(field)
        if not value:continue
        assert field in missing,f'{wid}/{field}: nonempty field cannot be replaced'
        assert isinstance(value,str) if field=='position' else isinstance(value,list) and all(isinstance(z,str) and z.strip() for z in value)
        record[field]=value
        record['fieldEvidence'][field]={
            'basis':'本次核验资料性质：'+patch['evidenceKind']+'；仅处理原版叙事内容，保留历史说明与媒介边界。'+patch['note'],
            'sources':e_source,
            'evidenceText':patch['evidenceText'],
            'sourceFields':patch['sourceFields']
        }
        filled+=1
    record['sources']=list(dict.fromkeys([*e_source,*prior.get('sources',[])]))
    record['basis']='原版具名剧情及叙事结构资料补录；逐字段区分出版社故事简介、原厂分支说明与玩家实玩证据。'+patch['note']
    record['cover']=works[wid]['title']
    record['reviewedAt']='2026-10-31'
    left=[f for f in FIELDS if not record.get(f)]
    record['status']='partial' if left else 'editorialObservation'
    if left:record['openQuestions']=['仍缺少'+f+'的原作专属结构证据' for f in left]
    else:record.pop('openQuestions',None)
    ed['works'][wid]=record
assert filled==21,f'Expected 21 new fields, got {filled}'
(ROOT/'data/discovery-editorial.json').write_text(json.dumps(ed,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Completed six studio works and 21 missing narrative fields without overwriting existing work reviews.')
