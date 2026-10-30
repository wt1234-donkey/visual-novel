#!/usr/bin/env python3
"""Apply six-studio round-four title-specific four-field narrative editing to unfinished work IDs.

Only patches explicitly keyed by existing work ID are considered.
No historical baseline records, game works, platform releases, credits or
previously authored nonempty narrative values are overwritten.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'data/games.json'
ED=ROOT/'data/discovery-editorial.json'
PATCH=ROOT/'data/narrative-evidence-giga-light-circus-r5-20261031.json'
BASE=ROOT/'data/narrative-editorial-baseline-20261029.json'
FIELDS=('position','style','theme','structure')
base=json.loads(BASE.read_text(encoding='utf8'))['works']
games=json.loads(DB.read_text(encoding='utf8'))['works']
workmap={w['id']:w for w in games}
editorial=json.loads(ED.read_text(encoding='utf8'))
patches=json.loads(PATCH.read_text(encoding='utf8'))['entries']
updated=[]
by_status={'complete':0,'partial':0}
for wid,patch in patches.items():
    if wid in base: raise ValueError(f'Protected baseline entry: {wid}')
    if wid not in workmap: raise ValueError(f'Unknown work: {wid}')
    old=editorial['works'].get(wid, {})
    if old.get('status')=='editorialObservation':
        # Never replace already-completed editorial annotations from other tasks.
        continue
    work=workmap[wid]
    inherit=False
    if inherit:
        source=work.get('source')
        evidence_text=(work.get('synopsis') or '').strip()
        if not source or not evidence_text or ('待依据该作品' in evidence_text or '叙事作品候选' in evidence_text):
            raise ValueError(f'{wid} has no substantive inherited work synopsis')
        source_fields=['games.works.synopsis']
        rationale='基于已有逐作品剧情梗概进行受限编辑归纳；原来源是继承存档，本轮未宣称另行核对官网。'
    else:
        if patch['evidenceKind'] not in ('contemporary-original-walkthrough','original-promotional-copy','licensed-port-announcement','contemporary-original-quote','licensed-port-original-premise','archived-original-summary','historical-promotional-republication','documented-original-playthrough','developer-and-contemporary-review','developer-retrospective-crossover','historical-original-credits'):
            raise ValueError(f'{wid}: unexpected evidence kind')
        source=patch['source']
        evidence_text=patch['evidenceText']
        source_fields=patch['sourceFields']
        rationale=('本轮据具名作品资料审查，材料性质为「'+patch['evidenceKind']+'」；按宣传文案、发行说明、原版实玩或历史署名的实际证据范围作限定归纳，不能视为全部原厂重新外核。')
    if not source.startswith('https://'): raise ValueError(f'{wid}: unsupported URL')
    note=patch.get('note','')
    record=dict(old)
    record['basis']=rationale+' '+note
    record['sources']=list(dict.fromkeys([source,*patch.get('supportingSources',[]),*old.get('sources',[])]))
    record['reviewedAt']='2026-10-31'
    record['cover']=work['title']
    record['fieldEvidence']=dict(old.get('fieldEvidence') or {})
    for field in FIELDS:
        value=patch.get(field)
        if field=='position':
            populated=isinstance(value,str) and bool(value.strip())
        else:
            populated=isinstance(value,list) and bool(value)
        if not populated:continue
        # Do not override an existing independently reviewed field.
        existing=record.get(field)
        if existing and (isinstance(existing,str) and existing.strip() or isinstance(existing,list) and len(existing)>0):
            continue
        record[field]=value
        record['fieldEvidence'][field]={
            'basis':rationale,
            'sources':list(dict.fromkeys([source,*patch.get('supportingSources',[])])),
            'evidenceText':evidence_text,
            'sourceFields':source_fields
        }
    not_filled=[]
    for field in FIELDS:
        val=record.get(field)
        ok=(bool(val.strip()) if isinstance(val,str) else bool(val) if isinstance(val,list) else False)
        if not ok: not_filled.append(field)
    record['status']='partial' if not_filled else 'editorialObservation'
    if not_filled:
        translate={'position':'叙事定位','style':'剧情风格','theme':'故事题材','structure':'叙事结构'}
        record['openQuestions']=[f'本作{translate[field]}缺乏足够的作品级剧情或篇章证据，需核验原作介绍、流程或文本。' for field in not_filled]
        by_status['partial']+=1
    else:
        record.pop('openQuestions',None)
        by_status['complete']+=1
    editorial['works'][wid]=record
    updated.append(wid)
ED.write_text(json.dumps(editorial,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f"GIGA-light-CIRCUS round-five narrative patches: {len(updated)} work records updated, {by_status}; historical baseline untouched.")
