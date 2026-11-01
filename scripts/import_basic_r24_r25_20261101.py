#!/usr/bin/env python3
"""Drain reviewed candidate queues before resuming both public catalogue sources."""
import argparse
import json
import re
import subprocess
import time
import urllib.parse
from collections import Counter
from pathlib import Path

import import_basic_r22_cont_r23_20261101 as source
import import_basic_r20_r21_20261101 as previous

ROOT=Path(__file__).resolve().parents[1]
BASE='059f63c4f97aae3c02114093e9d619d00529de3c'
REG=source.REG
B24='vndb-kana-bulk-20261101-r24'
B25='nextmoe-galgame-bulk-20261101-r25'
A24=ROOT/'data/vndb-kana-bulk-review-20261101-r24.json'
A25=ROOT/'data/nextmoe-bulk-review-20261101-r25.json'
REPORT=ROOT/'data/basic-r24-r25-diversity-20261101.json'
CAP=500
load,save,norm=source.load,source.save,source.norm
WINDOWS=[('1976-01-01','1999-12-31'),('2000-01-01','2009-12-31'),('2010-01-01','2026-11-01')]


def context(kind,batch,input_path,output_path):
    return {'kind':kind,'batch':batch,'inputPath':input_path,'outputPath':output_path,
            'pending':[],'fresh':[],'reused':[],'held':[],'counts':Counter(),
            'queueReview':[],'liveScanned':0,'trace':[]}


def drain(ctx,index,refs):
    """Every saved row receives a disposition before any network request."""
    rows=load(ctx['inputPath'])['deferredEligible']
    ctx['pendingInput']=len(rows)
    for old in rows:
        work=old['work']
        item={'id':old['vndbId'],'released':old['sourceReleased'],
              'devstatus':old['sourceDevstatus'],'developers':old['developers']}
        reused_before,held_before=len(ctx['reused']),len(ctx['held'])
        row=source.candidate(item,ctx['kind'],old['sourceId'],[work['title'],*work['aliases']],
            index,refs,ctx['counts'],ctx['reused'],ctx['held'],ctx['batch'])
        review={'sourceId':old['sourceId'],'vndbId':old['vndbId'],'priorCandidateId':work['id']}
        if row:
            row.update({'intakeOrigin':'deferred','priorAudit':str(ctx['inputPath'].relative_to(ROOT))})
            if 'nextmoeSourceReleased' in old:
                row['nextmoeSourceReleased']=old['nextmoeSourceReleased']
            ctx['pending'].append(row)
            review['status']='eligible-deferred'
        elif len(ctx['reused'])>reused_before:
            review['status']='reused-identity'
            review['resolution']=ctx['reused'][-1]
        elif len(ctx['held'])>held_before:
            review['status']='held'
            review['resolution']=ctx['held'][-1]
        else:
            review['status']='invalid-date-or-name'
        ctx['queueReview'].append(review)
    print('QUEUE_RECHECK',ctx['batch'],'INPUT',len(rows),'ELIGIBLE',len(ctx['pending']),flush=True)


def reserve(rows,index,refs):
    for row in rows:
        work=row['work']
        for name in [work['title'],*work['aliases']]:
            index[norm(name)].add((work['id'],work['firstYear'],'reserved-deferred-queue'))
        for ref in work['sourceRefs']:
            refs[ref].add(work['id'])


def select_pending_first(pending,fresh,registry):
    selected_pending=source.diverse_select(pending,registry)[0][:CAP]
    room=CAP-len(selected_pending)
    selected_fresh=source.diverse_select(fresh,registry)[0][:room]
    selected=selected_pending+selected_fresh
    ids={r['work']['id'] for r in selected}
    remaining=[r for r in pending+fresh if r['work']['id'] not in ids]
    return selected,remaining


def add_fresh(ctx,item,source_id,names,index,refs,extra=None):
    row=source.candidate(item,ctx['kind'],source_id,names,index,refs,ctx['counts'],
        ctx['reused'],ctx['held'],ctx['batch'])
    if row:
        row.update({'intakeOrigin':'live',**(extra or {})})
        ctx['fresh'].append(row)


def fetch_vndb(ctx,index,refs):
    cursor=load(ctx['inputPath'])['summary']['cursorEnd']
    assert cursor=='v6280'
    ctx['resumeStart']={'cursor':cursor}
    for page in range(1,26):
        if len(ctx['pending'])+len(ctx['fresh'])>=CAP:
            break
        payload=source.vndb_page(cursor)
        for item in payload['results']:
            ctx['liveScanned']+=1
            cursor=item['id']
            add_fresh(ctx,item,cursor,previous.vndb_names(item),index,refs)
        ctx['trace'].append({'page':page,'cursorEnd':cursor,'returned':len(payload['results'])})
        print('R24_LIVE',page,'SCANNED',ctx['liveScanned'],'ELIGIBLE',len(ctx['fresh']),cursor,flush=True)
        if not payload['more']:
            break
        time.sleep(2)
    ctx['resumeNext']={'cursor':cursor}


def nextmoe_resume_plan(audit):
    trace=audit['summary']['paginationTrace']
    last=next(row for row in reversed(trace) if row['lane']=='era-keyset')
    window=(last['releasedAfter'],last['releasedBefore'])
    assert window in WINDOWS
    start=WINDOWS.index(window)
    cursor=last.get('nextCursor')
    if cursor:
        assert cursor.startswith('cur_')
    else:
        start+=1
    return [{'releasedAfter':after,'releasedBefore':before,
             'cursor':cursor if i==start else None}
            for i,(after,before) in enumerate(WINDOWS) if i>=start]


def nextmoe_requests(plan,trace):
    budget=25
    for entry in plan:
        cursor=entry['cursor']
        while budget>0:
            params={'limit':100,'sort':'id','nsfw':'true','include':'titles,refs',
                    'released_after':entry['releasedAfter'],'released_before':entry['releasedBefore']}
            if cursor:
                params['cursor']=cursor
            payload=source.request_json(previous.NEXTMOE_API+'?'+urllib.parse.urlencode(params))
            assert payload.get('object')=='list' and isinstance(payload.get('items'),list)
            trace.append({'lane':'era-keyset','releasedAfter':entry['releasedAfter'],
                'releasedBefore':entry['releasedBefore'],'cursorUsed':cursor,
                'nextCursor':payload.get('next_cursor'),'returned':len(payload['items'])})
            yield payload
            budget-=1
            cursor=payload.get('next_cursor')
            if not cursor:
                break


def fetch_nextmoe(ctx,index,refs):
    plan=nextmoe_resume_plan(load(ctx['inputPath']))
    ctx['resumeStart']={'windows':plan}
    iterator=nextmoe_requests(plan,ctx['trace'])
    while len(ctx['pending'])+len(ctx['fresh'])<CAP:
        payload=next(iterator,None)
        if payload is None:
            break
        fresh=[]
        for item in payload['items']:
            ctx['liveScanned']+=1
            vid=source.common.has_vndb_identity(item)
            sid=str(item.get('id',''))
            if item.get('medium')!='galgame' or not vid or not sid.isdecimal():
                ctx['counts']['invalid-medium-or-source-id']+=1
                continue
            hits=refs.get('vndb:'+vid,set())|refs.get('nextmoe:'+sid,set())
            if hits:
                ctx['counts']['reused-external-identity']+=1
                ctx['reused'].append({'sourceId':sid,'vndbId':vid,'matchedWorkIds':sorted(hits),'basis':'exact-source-id'})
                continue
            if sid in source.common.HELD_EDITION_IDS:
                ctx['counts']['derivative-held']+=1
                ctx['held'].append({'sourceId':sid,'vndbId':vid,'reason':'known-edition-review'})
                continue
            fresh.append((item,vid,sid))
        authoritative=source.lookup_vndb(list(dict.fromkeys(v for _,v,_ in fresh))) if fresh else {}
        for item,vid,sid in fresh:
            vn=authoritative.get(vid)
            if not vn:
                ctx['counts']['missing-vndb-record']+=1
                continue
            names=[]
            seen=set()
            for name in [*previous.vndb_names(vn),*source.common.source_names(item)]:
                if norm(name) not in seen:
                    names.append(name)
                    seen.add(norm(name))
            add_fresh(ctx,vn,sid,names,index,refs,{'nextmoeSourceReleased':item.get('release_date')})
        print('R25_LIVE','SCANNED',ctx['liveScanned'],'ELIGIBLE',len(ctx['fresh']),flush=True)
        time.sleep(2)
    ctx['resumeNext']={'paginationTrace':ctx['trace'],'unvisitedWindows':plan}


def append(ctx,registry):
    selected,remaining=select_pending_first(ctx['pending'],ctx['fresh'],registry)
    assert selected
    selected_ids={r['work']['id'] for r in selected}
    for row in ctx['queueReview']:
        if row['status']=='eligible-deferred':
            row['status']='selected-from-deferred' if row['priorCandidateId'] in selected_ids else 'remaining-deferred'
    records=[]
    for row in selected:
        records.append({**row['work'],**{k:v for k,v in row.items() if k!='work'},
            'developerClassification':source.creator_type(row)})
    stats={'scanned':ctx['pendingInput']+ctx['liveScanned'],
        'pendingInput':ctx['pendingInput'],'pendingEligible':len(ctx['pending']),
        'liveScanned':ctx['liveScanned'],'liveEligible':len(ctx['fresh']),
        'selectedFromDeferred':sum(r['intakeOrigin']=='deferred' for r in selected),
        'selectedFromLive':sum(r['intakeOrigin']=='live' for r in selected),
        'remainingDeferred':len(remaining),**dict(ctx['counts'])}
    if ctx['kind']=='vndb':
        stats.update({'cursorStart':ctx['resumeStart']['cursor'],'cursorEnd':ctx['resumeNext']['cursor']})
    else:
        stats['paginationTrace']=ctx['trace']
    previous.append_batch(registry,[r['work'] for r in selected],ctx['batch'],
        previous.VNDB_API if ctx['kind']=='vndb' else previous.NEXTMOE_API,
        ctx['outputPath'],stats,records,ctx['held'],'https://api.vndb.org/kana',
        'https://vndb.org/d17; NextMoe minimal identity metadata with source attribution')
    audit=load(ctx['outputPath'])
    audit.update({'priorBaseCommit':BASE,'inputDeferredAudit':str(ctx['inputPath'].relative_to(ROOT)),
        'pendingQueueReview':ctx['queueReview'],'reusedExisting':ctx['reused'],
        'deferredEligible':remaining,'resumeStart':ctx['resumeStart'],'resumeNext':ctx['resumeNext'],
        'selection':'All eligible saved candidates before live candidates; diverse selection only within each priority tier.',
        'resumePolicy':'Recheck deferredEligible against the current registry before using the saved source cursor.'})
    save(ctx['outputPath'],audit)


def finalize_report():
    registry=load(REG)
    registered={w['id'] for w in source.all_works(registry)}
    audits=[load(A24),load(A25)]
    deferred_ids={r['work']['id'] for a in audits for r in a['deferredEligible']}
    all_records=[]
    by_batch={}
    for path,audit in zip([A24,A25],audits):
        resolution_counts=Counter()
        for event in audit['reusedExisting']:
            hits=set(event.get('matchedWorkIds',[]))|{r[0] for r in event.get('matches',[])}
            assert hits
            assert hits<=registered|deferred_ids
            event['targetState']='registered-work' if hits<=registered else 'deferred-candidate'
            resolution_counts[event['targetState']]+=1
        audit['reuseResolutionSummary']=dict(resolution_counts)
        save(path,audit)
        records=audit['records']
        all_records.extend(records)
        by_batch[records[0]['batch']]={
            **audit['summary'],'reuseTargets':dict(resolution_counts),
            'decades':dict(sorted(Counter(str(r['firstYear']//10*10)+'s' for r in records).items())),
            'creatorTypes':dict(Counter(r['developerClassification'] for r in records)),
            'distinctDeveloperIds':len({p['id'] for r in records for p in r['developers']})}
    save(REPORT,{'schema':1,'date':'2026-11-01','byBatch':by_batch,
        'summary':{'newDistinctWorks':len(all_records),'uniqueVndbIds':len({r['vndbId'] for r in all_records}),
            'selectedFromDeferred':sum(r['intakeOrigin']=='deferred' for r in all_records),
            'selectedFromLive':sum(r['intakeOrigin']=='live' for r in all_records),
            'distinctDeveloperIds':len({p['id'] for r in all_records for p in r['developers']}),
            'individualOrAmateurSignalWorks':sum(r['developerClassification']=='individual-or-amateur-signal' for r in all_records)},
        'caveats':['Personal/amateur producer types are source signals, not proof of independent status.',
            'Saved source metadata is reused for deferred candidates; dates still require original-region/edition review.',
            'Developer metadata remains in audit only; no formal credits were created.']})


def check():
    def base(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
    old=json.loads(base(str(REG.relative_to(ROOT))))
    current=load(REG)
    assert current['works'][:len(old['works'])]==old['works']
    assert current['batches'][:len(old['batches'])]==old['batches']
    for key in old:
        if key not in {'works','batches','summary','updated'}:
            assert current[key]==old[key]
    for path in source.PROTECTED:
        assert base(path)==(ROOT/path).read_bytes(),path
    index=source.common.existing_index(old)
    refs=source.identity_map(old)
    added=current['works'][len(old['works']):]
    assert len(current['works'])==len({w['id'] for w in current['works']})
    assert len(current['works'])==len({w['indexId'] for w in current['works']})
    assert len(added)<=1000
    for batch,path in [(B24,A24),(B25,A25)]:
        audit=load(path)
        rows=[w for w in added if w['batch']==batch]
        stats=audit['summary']
        assert 1<=len(rows)<=CAP
        assert len(rows)==stats['newDistinctWorks']==len(audit['records'])
        assert len(audit['pendingQueueReview'])==stats['pendingInput']
        assert stats['selectedFromDeferred']==sum(r['status']=='selected-from-deferred' for r in audit['pendingQueueReview'])
        assert stats['selectedFromDeferred']+stats['selectedFromLive']==len(rows)
        assert stats['pendingEligible']+stats['liveEligible']==len(rows)+len(audit['deferredEligible'])
        accounting={'newDistinctWorks','before','after','scanned','pendingInput','pendingEligible',
            'liveScanned','liveEligible','selectedFromDeferred','selectedFromLive','remainingDeferred'}
        skipped=sum(v for k,v in stats.items() if isinstance(v,int) and k not in accounting)
        assert stats['scanned']==stats['pendingEligible']+stats['liveEligible']+skipped
        if stats['selectedFromLive']:
            assert stats['selectedFromDeferred']==stats['pendingEligible'],'Live candidates displaced saved candidates'
        evidence={r['id']:r for r in audit['records']}
        for w in rows:
            r=evidence[w['id']]
            assert w['id']=='vndb-'+r['vndbId']
            assert all(w[k]==r[k] for k in ['title','aliases','source','sourceRefs'])
            assert w['firstYear']==previous.vndb_year({'released':r['sourceReleased'],'devstatus':r['sourceDevstatus']})
            assert not set().union(*(refs.get(ref,set()) for ref in w['sourceRefs']))
            assert all(not index.get(norm(n)) for n in [w['title'],*w['aliases']])
            for n in [w['title'],*w['aliases']]:
                index[norm(n)].add((w['id'],w['firstYear'],'new'))
            for ref in w['sourceRefs']:
                refs[ref].add(w['id'])
        assert {r['status'] for r in audit['pendingQueueReview']}<={'selected-from-deferred','reused-identity','held','remaining-deferred','invalid-date-or-name'}
    summary=load(REPORT)['summary']
    assert summary['newDistinctWorks']==summary['uniqueVndbIds']==len(added)
    assert current['summary']['accepted']==len(current['works'])
    print('R24_R25_CHECK_OK',len(old['works']),'+',len(added),'=',len(current['works']),json.dumps(summary),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if not args.check:
        registry,index,refs=source.state()
        c24=context('vndb',B24,source.A22,A24)
        c25=context('nextmoe',B25,source.A23,A25)
        # Both queues are reviewed and reserved before either source is fetched.
        drain(c24,index,refs)
        drain(c25,index,refs)
        if not source.already_exists(registry,B24,A24):
            fetch_vndb(c24,index,refs)
            append(c24,registry)
        registry,index,refs=source.state()
        reserve(c25['pending'],index,refs)
        if not source.already_exists(registry,B25,A25):
            fetch_nextmoe(c25,index,refs)
            append(c25,registry)
        finalize_report()
    check()

if __name__=='__main__':
    main()
