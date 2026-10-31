#!/usr/bin/env python3
"""Reconcile the already reviewed 1,339-work snapshot to actual evidence-driven field counts.

Never edit original work hashes, membership, review target or historical baseline.
"""
from pathlib import Path
from collections import Counter
import json
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
file='data/narrative-cataloguing-20261030.json'
report=read(file)
ed=read('data/discovery-editorial.json')['works']
games={x['id']:x for x in read('data/games.json')['works']}
fields=('position','style','theme','structure')
assert len(report['countedWorkIds'])==1339 and len(report['targetWorkIds'])==1331
base=read('data/narrative-editorial-baseline-20261029.json')['works']
assert len(base)==8
old=report['counts']
counts=Counter({'complete':0,'partial':0,'missing':0})
for wid in report['countedWorkIds']:
    filled=sum(bool(ed.get(wid,{}).get(f)) for f in fields)
    counts['complete' if filled==4 else 'partial' if filled else 'missing']+=1
if 'historicalCountsBeforeR9' not in report:
    report['historicalCountsBeforeR9']=old
    report['historicalRemainingCountBeforeR9']=len(report['remaining'])
report['counts']=dict(counts)
report['newlyComplete']=counts['complete']-len(base)
report['lastRefreshedAt']='2026-10-31'
pending=[]
for wid in report['countedWorkIds']:
    rec=ed.get(wid,{})
    missing=[f for f in fields if not rec.get(f)]
    if not missing:continue
    pending.append({'workId':wid,'title':games[wid]['title'],'missingFields':missing,'openQuestions':rec.get('openQuestions',[])})
pending.sort(key=lambda r:int(r['workId'][1:]))
report['remaining']=pending
assert counts['complete']==1324 and counts['partial']==14 and counts['missing']==1,counts
(ROOT/file).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'Reconciled protected reviewed-scope snapshot: {dict(counts)}, still pending {len(pending)}; original baseline counts separately preserved.')
