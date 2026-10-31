#!/usr/bin/env python3
"""Add independently supported fields to six of fifteen remaining historical works."""
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text(encoding='utf8'))
audit=read('data/narrative-pending-audit-legacy-20261030.json')['pending']
patches=read('data/narrative-legacy15-evidence-r10-20261031.json')['entries']
works={g['id']:g for g in read('data/games.json')['works']}
db=read('data/discovery-editorial.json')
protected=read('data/narrative-editorial-baseline-20261029.json')['works']
FIELDS=('position','style','theme','structure')
assert len(audit)==15 and len(patches)==6
frozen={x['id']:set(x['missing']) for x in audit}
added=0
completed=0
for wid,patch in patches.items():
    assert wid in frozen and wid in works and wid not in protected
    prior=dict(db['works'].get(wid,{}))
    missing={field for field in FIELDS if not prior.get(field)}
    assert missing==frozen[wid],f'{wid}: changed from frozen pending state'
    new=dict(prior)
    fe=dict(prior.get('fieldEvidence') or {})
    sources=list(dict.fromkeys([patch['source'],*patch.get('supportingSources',[])]))
    for field in FIELDS:
        v=patch.get(field)
        if not v:continue
        assert field in missing and not prior.get(field),f'{wid}/{field}: filled elsewhere'
        assert (isinstance(v,str) and v.strip()) if field=='position' else (isinstance(v,list) and all(isinstance(a,str) and a.strip() for a in v))
        new[field]=v
        fe[field]=dict(basis='原作资料限定补录，资料类别：'+patch['evidenceKind']+'。'+patch.get('note',''),sources=sources,evidenceText=patch['evidenceText'],sourceFields=patch['sourceFields'])
        added+=1
    new['fieldEvidence']=fe
    new['sources']=list(dict.fromkeys([*sources,*prior.get('sources',[])]))
    new['basis']='历史资料补证，优先明确叙事与非叙事形式的区别，未证明的作品路线和结局不推测。 '+str(prior.get('basis',''))
    new['cover']=works[wid]['title']
    new['reviewedAt']='2026-10-31'
    left=[f for f in FIELDS if not new.get(f)]
    new['status']='partial' if left else 'editorialObservation'
    if left:new['openQuestions']=['仍需找到该原作专属的'+f+'故事情节或流程信息' for f in left]
    else:
        new.pop('openQuestions',None)
        completed+=1
    db['works'][wid]=new
assert added==9 and completed==5,(added,completed)
(ROOT/'data/discovery-editorial.json').write_text(json.dumps(db,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'Added {added} fields for {len(patches)} works; {completed} now complete, without touching original game/source identities.')
