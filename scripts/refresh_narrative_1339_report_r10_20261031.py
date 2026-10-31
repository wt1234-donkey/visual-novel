#!/usr/bin/env python3
"""Update living 1,339-work editorial counts without changing frozen source hashes."""
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
path='data/narrative-cataloguing-20261030.json'
report=read(path)
d=read('data/discovery-editorial.json')['works']
games={w['id']:w for w in read('data/games.json')['works']}
fields=('position','style','theme','structure')
assert len(report['countedWorkIds'])==1339
count=Counter({'complete':0,'partial':0,'missing':0})
pending=[]
for wid in report['countedWorkIds']:
    rec=d.get(wid,{})
    missing=[f for f in fields if not rec.get(f)]
    n=len(missing)
    count['complete' if n==0 else 'missing' if n==4 else 'partial']+=1
    if missing:pending.append({'workId':wid,'title':games[wid]['title'],'missingFields':missing,'openQuestions':rec.get('openQuestions',[])})
assert count==Counter({'complete':1329,'partial':9,'missing':1}),dict(count)
report['counts']=dict(count)
report['newlyComplete']=count['complete']-8
report['remaining']=sorted(pending,key=lambda r:int(r['workId'][1:]))
report['lastRefreshedAt']='2026-10-31'
assert 'historicalCountsBeforeR9' in report
(ROOT/path).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Updated living reviewed-work counts:',dict(count),'remaining',len(pending))
