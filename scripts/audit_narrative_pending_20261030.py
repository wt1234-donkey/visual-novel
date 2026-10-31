#!/usr/bin/env python3
"""Produce a bounded, source-aware audit of genuinely unfilled four-field narrative metadata."""
import json
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
db=json.loads((ROOT/'data/games.json').read_text(encoding='utf8'))
ed=json.loads((ROOT/'data/discovery-editorial.json').read_text(encoding='utf8'))
fields=['position','style','theme','structure']
def has(r,f):
    v=r.get(f)
    return bool(v.strip()) if f=='position' and isinstance(v,str) else bool(v) if isinstance(v,list) else False
pending=[];counts=Counter()
for w in db['works']:
    e=ed['works'].get(w['id'],{})
    missing=[f for f in fields if not has(e,f)]
    if not missing:continue
    counts['pendingWork']+=1
    counts['missingFields']+=len(missing)
    for f in missing:counts[f]+=1
    row=dict(id=w['id'],title=w['title'],originalTitle=w.get('originalTitle'),year=w['firstYear'],
             category=w['category'],genre=w.get('genre'),source=w.get('source'),
             catalogueDepth=w.get('catalogueDepth','full'),
             synopsis=(w.get('synopsis') or '')[:850],notes=(w.get('notes') or '')[:650],
             characters=w.get('characters',[])[:4],existing={f:e.get(f) for f in fields if has(e,f)},
             missing=missing,reviewQuestions=e.get('openQuestions',[])[:2],editorSources=e.get('sources',[])[:3])
    pending.append(row)
pending.sort(key=lambda r:int(r['id'][1:]))
groups={'legacy':[r for r in pending if int(r['id'][1:])<=1339],
        'initial18':[r for r in pending if 1340<=int(r['id'][1:])<=1414],
        'six_studios':[r for r in pending if 1415<=int(r['id'][1:])<=1501],
        'recommended':[r for r in pending if int(r['id'][1:])>=1502 and r['catalogueDepth']!='titleYearOnly'],
        'name_year_only':[r for r in pending if r['catalogueDepth']=='titleYearOnly']}
for name,rows in groups.items():
    (ROOT/f'data/narrative-pending-audit-{name}-20261030.json').write_text(
       json.dumps({'group':name,'size':len(rows),'pending':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(ROOT/'data/narrative-pending-summary-20261030.json').write_text(
    json.dumps({'counts':dict(counts),'groups':{k:len(v) for k,v in groups.items()}},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(dict(counts),{k:len(v) for k,v in groups.items()})
