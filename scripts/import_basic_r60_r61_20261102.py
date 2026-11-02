#!/usr/bin/env python3
"""Append exactly 500 VNDB and 500 NextMoe/IFDB basic identities, saved queues first."""
import argparse
import datetime as dt
import json
import re
import subprocess
from collections import Counter, defaultdict
from functools import partial

import import_basic_r24_r25_20261101 as e
import ifdb_archive_identity as ifdb
from basic_source_date_review import reviewed_add_fresh
from import_basic_r50_r51_20261101 import reviewed_candidate, original_add_fresh

BASE='ca86cffb7edbf0f572c6b6d4780e80c736193e1d'
DATE='2026-11-02'
B60='vndb-kana-bulk-20261102-r60'
B61='nextmoe-ifdb-bulk-20261102-r61'
A60=e.ROOT/'data/vndb-kana-bulk-review-20261102-r60.json'
A61=e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r61.json'
REPORT=e.ROOT/'data/basic-r60-r61-diversity-20261102.json'
NEXT_LIMIT=300
SEED_VNDB=e.ROOT/'data/vndb-kana-bulk-review-20261102-r58.json'
SEED_NEXTMOE=e.ROOT/'data/nextmoe-bulk-review-20261102-r59.json'
EXPECTED_VNDB_START='v23617'
IFDB_START_POSITION=1


def configure():
    e.INTAKE_DATE=DATE
    e.previous.CUTOFF=dt.date.fromisoformat(DATE)
    e.WINDOWS[-1]=('2010-01-01',DATE)
    e.source.candidate=reviewed_candidate
    e.add_fresh=partial(reviewed_add_fresh,original_add_fresh,e.previous.vndb_year)
    e.BASE=BASE
    e.B24=B60
    e.B25=B61
    e.A24=A60
    e.A25=A61
    e.REPORT=REPORT
    e.SEED_VNDB=SEED_VNDB
    e.SEED_NEXTMOE=SEED_NEXTMOE
    e.EXPECTED_VNDB_START=EXPECTED_VNDB_START


def select_next(ctx,registry):
    # Saved candidates retain priority even if they exceed the normal NextMoe quota.
    pending=e.source.diverse_select(ctx['pending'],registry)[0][:500]
    fresh=e.source.diverse_select(ctx['fresh'],registry)[0][:max(0,NEXT_LIMIT-len(pending))]
    selected=pending+fresh
    ids={r['work']['id'] for r in selected}
    return selected,[r for r in ctx['pending']+ctx['fresh'] if r['work']['id'] not in ids]


def append_mixed(ctx,registry,index,refs,archive):
    next_rows,remaining=select_next(ctx,registry)
    candidates,rejected=ifdb.prepare(ifdb.read_archive(archive),dt.date.fromisoformat(DATE))
    supplement,review=ifdb.choose(candidates,500-len(next_rows),index,refs,e.norm,B61,
        start_position=IFDB_START_POSITION)
    selected=next_rows+supplement
    selected_ids={r['work']['id'] for r in selected}
    for row in ctx['queueReview']:
        if row['status']=='eligible-deferred':
            row['status']='selected-from-deferred' if row['priorCandidateId'] in selected_ids else 'remaining-deferred'
    records=[{**r['work'],**{k:v for k,v in r.items() if k!='work'},
        'sourceKind':r.get('sourceKind','nextmoe'),
        'developerClassification':r.get('developerClassification',e.source.creator_type(r))} for r in selected]
    stats={'pendingInput':ctx['pendingInput'],'pendingEligible':len(ctx['pending']),
        'liveScanned':ctx['liveScanned'],'liveEligible':len(ctx['fresh']),
        'selectedFromDeferred':len(ctx['pending'][:len(next_rows)]),
        'selectedFromLive':500-sum(r['intakeOrigin']=='deferred' for r in selected),
        'remainingDeferred':len(remaining),'sourceCounts':{'nextmoe':len(next_rows),'ifdb':len(supplement)},
        'nextmoeDispositions':dict(ctx['counts']),'paginationTrace':ctx['trace']}
    # IFDB statistics are separate: they are not NextMoe network/eligibility counters.
    stats['selectedFromDeferred']=sum(r['intakeOrigin']=='deferred' for r in selected)
    e.previous.append_batch(registry,[r['work'] for r in selected],B61,
        [e.previous.NEXTMOE_API,ifdb.ARCHIVE_URL],A61,stats,records,ctx['held']+review['heldForIdentityReview'],
        ['https://api.vndb.org/kana','https://ifdb.org/api/','https://ifarchive.org/indexes/if-archive/info/ifdb/'],
        'VNDB d17; NextMoe/IFDB minimal identity facts with per-record source attribution; no descriptions or game files copied.',intake_date=DATE)
    audit=e.load(A61)
    audit.update({'priorBaseCommit':BASE,'inputDeferredAudit':str(ctx['inputPath'].relative_to(e.ROOT)),
        'pendingQueueReview':ctx['queueReview'],'reusedExisting':ctx['reused']+review.pop('reusedExisting'),
        'deferredEligible':remaining,'resumeStart':ctx['resumeStart'],'resumeNext':ctx['resumeNext'],
        'ifdbArchiveReview':{'url':ifdb.ARCHIVE_URL,'sha256':ifdb.ARCHIVE_SHA256,
            'cataloguePreparationDispositions':rejected,**{k:v for k,v in review.items() if k!='heldForIdentityReview'}},
        'selection':'Saved candidates first; up to 300 NextMoe identities, remaining slots from IFDB, round-robin decades and authors. IFDB checked against all live NextMoe candidates including deferred ones.',
        'resumePolicy':'Recheck deferredEligible before resuming exact saved NextMoe query/cursor; IFDB nextPosition is bound to archive SHA and deterministic decade/author ordering. Recheck the whole catalogue on resume.'})
    audit['caveats']+=['IFDB published is a catalogue work date, not independently verified original-region release evidence.',
        'IFDB author/system metadata is audit-only. Neither system nor tags establish formal interaction modes or credits.',
        'Redirects and IFIDs identify known aliases; ports, translations, remakes, flagged entries, explicit VNDB links and shared IFIDs are held. Unknown unlinked aliases remain subject to later review.']
    e.save(A61,audit)


def report():
    registry=e.load(e.REG)
    registered={w['id'] for w in e.source.all_works(registry)}
    audits=[e.load(A60),e.load(A61)]
    deferred={r['work']['id'] for a in audits for r in a['deferredEligible']}
    records=[]
    by_batch={}
    for path,audit in zip((A60,A61),audits):
        reuse=Counter()
        for event in audit['reusedExisting']:
            hits=set(event.get('matchedWorkIds',[]))|{r[0] for r in event.get('matches',[])}
            assert hits and hits<=registered|deferred
            event['targetState']='registered-work' if hits<=registered else 'deferred-candidate'
            reuse[event['targetState']]+=1
        audit['reuseResolutionSummary']=dict(reuse)
        e.save(path,audit)
        rows=audit['records']
        records+=rows
        by_batch[rows[0]['batch']]={**audit['summary'],'reuseTargets':dict(reuse),
            'decades':dict(sorted(Counter(str(r['firstYear']//10*10)+'s' for r in rows).items())),
            'creatorTypes':dict(Counter(r['developerClassification'] for r in rows)),
            'distinctSourceAuthorNames':len({r.get('ifdbAuthor') for r in rows if r.get('ifdbAuthor')}),
            'distinctDeveloperIds':len({p['id'] for r in rows for p in r['developers']})}
    e.save(REPORT,{'schema':1,'date':DATE,'byBatch':by_batch,'summary':{
        'newDistinctWorks':len(records),'uniqueVndbIds':len({r['vndbId'] for r in records if 'vndbId' in r}),
        'uniqueIfdbTuids':len({r['sourceId'] for r in records if r.get('sourceKind')=='ifdb'}),
        'selectedFromDeferred':sum(r['intakeOrigin']=='deferred' for r in records),
        'selectedFromLive':sum(r['intakeOrigin']=='live' for r in records)},
        'caveats':['Minimal identity intake only; source catalogue years retain per-record provenance.',
            'IFDB export is a fixed 2026-09-01 snapshot hosted by IF Archive; archive date is not work year.',
            'Creator types are VNDB source signals; IFDB author strings do not prove individual/independent status.',
            'All exact source identities and normalized names/aliases are checked across the catalogue and both candidate pools; uncertain relations remain held.']})


def check():
    def base(path): return subprocess.check_output(['git','show',BASE+':'+path],cwd=e.ROOT)
    old=json.loads(base(str(e.REG.relative_to(e.ROOT))))
    current=e.load(e.REG)
    assert current['works'][:len(old['works'])]==old['works']
    assert current['batches'][:len(old['batches'])]==old['batches']
    assert current['updated']==DATE
    for key in old:
        if key not in {'works','batches','summary','updated'}: assert current[key]==old[key]
    for path in e.source.PROTECTED: assert base(path)==(e.ROOT/path).read_bytes(),path
    assert base('data/vn-seven-source-date-review-20261101.json')==(e.ROOT/'data/vn-seven-source-date-review-20261101.json').read_bytes()
    added=current['works'][len(old['works']):]
    assert len(added)==1000
    assert len(current['works'])==len({w['id'] for w in current['works']})==len({w['indexId'] for w in current['works']})
    index=e.source.common.existing_index(old)
    refs=e.source.identity_map(old)
    folded=defaultdict(set)
    for ref,ids in refs.items(): folded[ref.casefold()].update(ids)
    allrecords=[]
    for batch,path in ((B60,A60),(B61,A61)):
        audit=e.load(path)
        rows=[w for w in added if w.get('batch')==batch]
        stats=audit['summary']
        assert len(rows)==500==stats['newDistinctWorks']==len(audit['records'])
        assert audit['date']==DATE
        assert len(audit['pendingQueueReview'])==stats['pendingInput']
        assert stats['selectedFromDeferred']==sum(r['status']=='selected-from-deferred' for r in audit['pendingQueueReview'])
        assert stats['selectedFromDeferred']==stats['pendingEligible'], 'Live displaced saved candidates'
        assert stats['selectedFromDeferred']+stats['selectedFromLive']==500
        source_counts=stats.get('sourceCounts',{'vndb':500})
        selected_next=source_counts.get('nextmoe',0) if batch==B61 else 500
        assert stats['pendingEligible']+stats['liveEligible']==selected_next+len(audit['deferredEligible'])
        dispositions=stats.get('nextmoeDispositions')
        if dispositions is not None:
            assert stats['pendingInput']+stats['liveScanned']==stats['pendingEligible']+stats['liveEligible']+sum(dispositions.values())
        else:
            noncounts={'newDistinctWorks','before','after','scanned','pendingInput','pendingEligible','liveScanned','liveEligible','selectedFromDeferred','selectedFromLive','remainingDeferred'}
            assert stats['scanned']==stats['pendingEligible']+stats['liveEligible']+sum(v for k,v in stats.items() if isinstance(v,int) and k not in noncounts)
        evidence={r['id']:r for r in audit['records']}
        for work in rows:
            r=evidence[work['id']]
            assert all(work[k]==r[k] for k in work)
            if r.get('sourceKind')=='ifdb':
                assert work['id']=='ifdb-'+r['sourceId']
                assert re.fullmatch('[a-z0-9]{16}',r['sourceId'])
                assert 'ifdb:'+r['sourceId'] in work['sourceRefs']
                assert work['firstYear']==dt.date.fromisoformat(r['ifdbPublished'][:10]).year
                assert dt.date.fromisoformat(r['ifdbPublished'][:10])<=dt.date.fromisoformat(DATE)
                assert r['archiveSha256']==ifdb.ARCHIVE_SHA256 and r['archiveUrl']==ifdb.ARCHIVE_URL
                assert not any(ref.startswith('vndb:') for ref in work['sourceRefs'])
            else:
                assert work['id']=='vndb-'+r['vndbId']
                assert 'vndb:'+r['vndbId'] in work['sourceRefs']
                assert work['firstYear']==e.previous.vndb_year({'released':r['sourceReleased'],'devstatus':r['sourceDevstatus']})
                if r.get('nextmoeSourceReleased'):
                    claimed=str(r['nextmoeSourceReleased'])[:4]
                    if claimed.isdecimal(): assert int(claimed)>=work['firstYear']
            assert not set().union(*(folded.get(ref.casefold(),set()) for ref in work['sourceRefs']))
            assert all(e.norm(n) and not index.get(e.norm(n)) for n in [work['title'],*work['aliases']])
            for n in [work['title'],*work['aliases']]: index[e.norm(n)].add((work['id'],work['firstYear'],'new'))
            for ref in work['sourceRefs']: folded[ref.casefold()].add(work['id'])
        allrecords+=audit['records']
        if batch==B61:
            assert sum(source_counts.values())==500 and source_counts['ifdb']>=200
            review=audit['ifdbArchiveReview']
            assert review['selected']==source_counts['ifdb']
            assert review['scanned']==review['selected']+sum(review['dispositions'].values())
            assert review['sha256']==ifdb.ARCHIVE_SHA256
            assert review.get('startPosition',1)==IFDB_START_POSITION
            assert review['nextPosition']==IFDB_START_POSITION+review['scanned']
    # Deferred identities also remain unique against the mixed intake and against one another.
    for path in (A60,A61):
        for row in e.load(path)['deferredEligible']:
            work=row['work']
            assert all(not index.get(e.norm(n)) for n in [work['title'],*work['aliases']])
            assert not any(folded.get(ref.casefold()) for ref in work['sourceRefs'])
            for n in [work['title'],*work['aliases']]: index[e.norm(n)].add((work['id'],work['firstYear'],'deferred'))
            for ref in work['sourceRefs']: folded[ref.casefold()].add(work['id'])
    summary=e.load(REPORT)['summary']
    assert summary['newDistinctWorks']==1000==summary['uniqueVndbIds']+summary['uniqueIfdbTuids']
    assert current['summary']['accepted']==len(current['works'])
    print('BASIC_MIXED_CHECK_OK',len(old['works']),'+1000 =',len(current['works']),json.dumps(summary),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--archive',default='/tmp/ifdb-archive-20260901.zip')
    args=parser.parse_args()
    configure()
    if not args.check:
        registry,index,refs=e.source.state()
        c60=e.context('vndb',B60,e.SEED_VNDB,A60)
        c61=e.context('nextmoe',B61,e.SEED_NEXTMOE,A61)
        if not e.source.already_exists(registry,B60,A60):
            # Both saved queues are reviewed before either source is fetched.
            e.drain(c60,index,refs)
            e.drain(c61,index,refs)
            e.fetch_vndb(c60,index,refs)
            assert len(c60['pending'])+len(c60['fresh'])>=500
            e.append(c60,registry)
        registry,index,refs=e.source.state()
        # Reserve all VNDB deferred identities as well as the NextMoe queue.
        e.reserve(e.load(A60)['deferredEligible'],index,refs)
        if not e.source.already_exists(registry,B61,A61):
            if 'pendingInput' not in c61: e.drain(c61,index,refs)
            else: e.reserve(c61['pending'],index,refs)
            e.fetch_nextmoe(c61,index,refs)
            append_mixed(c61,registry,index,refs,args.archive)
        report()
    check()

if __name__=='__main__': main()
