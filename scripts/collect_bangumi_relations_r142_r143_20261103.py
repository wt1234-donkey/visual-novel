#!/usr/bin/env python3
"""Inspect edition relations only for potential new narrative identities."""
from registry_store import read_json as read_registry_json, write_json as write_registry_json, write_text as write_registry_text
import concurrent.futures
import json
import sys
import time
import tempfile
from collections import defaultdict
from pathlib import Path
import import_basic_r142_r143_20261103 as m
from collect_basic_r142_r143_20261103 import fetch

cache=Path(sys.argv[1])
out=Path(sys.argv[2])
registry=m.e.load(m.e.REG)
index=m.name_index(registry)
refs=defaultdict(set)
for k,v in m.e.full_refs(registry).items():refs[k.casefold()].update(v)
candidates=[]
for page in sorted(cache.glob('bangumi-*.json')):
    for row in read_registry_json(page)['data']:
        c,reason=m.bangumi_candidate(row)
        if reason is None and m.decide(c,index,refs) is None:candidates.append(row['id'])
if '--reverse' in sys.argv:
    candidates.reverse()

def run(sid):
    path=cache/f'relations-{sid}.json'
    if path.exists():return str(sid),read_registry_json(path)
    try:
        rows=fetch(f'https://api.bgm.tv/v0/subjects/{sid}/subjects')
        assert isinstance(rows,list)
        relevant=[{k:r[k] for k in ('id','name','name_cn','relation','type')} for r in rows if r['type']==4]
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=cache,delete=False) as tmp:
            tmp.write(json.dumps(relevant,ensure_ascii=False))
        Path(tmp.name).replace(path)
        time.sleep(1.5)
        return str(sid),relevant
    except Exception as exc:
        print('RELATION_UNAVAILABLE',sid,type(exc).__name__,flush=True)
        return str(sid),None

records={}
with concurrent.futures.ThreadPoolExecutor(max_workers=6 if '--reverse' in sys.argv else 2) as pool:
    for i,(sid,rows) in enumerate(pool.map(run,candidates)):
        records[sid]=rows
        if i%20==0:print('RELATION_PROGRESS',i+1,len(candidates),flush=True)
write_registry_text(out, json.dumps({'schema':1,'date':'2026-11-03','sourcePattern':'https://api.bgm.tv/v0/subjects/{id}/subjects','records':records},ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
print('RELATIONS_SAVED',len(records),flush=True)
