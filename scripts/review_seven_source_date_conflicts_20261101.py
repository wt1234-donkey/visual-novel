#!/usr/bin/env python3
"""Verify seven held NextMoe/VNDB date contradictions; register only proven VNDB identities.

Never assert that the NextMoe entries are the same original works. Preserve the
earlier claimed NextMoe dates in a separate review, not as registry sourceRefs.
"""
import argparse
import json
import re
import subprocess
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

import import_basic_r22_cont_r23_20261101 as source
import import_basic_r20_r21_20261101 as previous

ROOT=Path(__file__).resolve().parents[1]
REG=source.REG
OLD_SHA='580890d4a16b4c5d862f04a74e6b1afc395e34ee'
BATCH='vndb-seven-held-date-conflicts-20261101'
AUDIT=ROOT/'data/vn-seven-source-date-review-20261101.json'
INPUT=ROOT/'data/nextmoe-bulk-review-20261101-r55.json'
EXPECTED={
    'v64717':('60167','2008-10-17','2007-04-17'),
    'v65847':('61289','2010-11-23','2009-02-16'),
    'v65850':('61292','2010-07-09','2008-05-26'),
    'v65851':('61293','2010-04-05','2008-03-31'),
    'v65867':('61309','2012','2007-08-20'),
    'v68592':('208363','2010-01-09','2009-08-01'),
    'v66801':('214903','2011-09-13','2008-04-14'),
}

def audit_input():
    original=source.load(INPUT)
    held={r['vndbId']:r for r in original['heldForIdentityReview']
          if r.get('reason','').startswith('VNDB original year is later')}
    assert set(held)==set(EXPECTED), 'Seven source conflicts differ from immutable r55 audit'
    for vid,(nid,date,other) in EXPECTED.items():
        r=held[vid]
        assert (r['sourceId'],r['sourceReleased'],r['nextmoeSourceReleased'])==(nid,date,other)
    return held

def fetch_vndb():
    # Read independently from the original VNDB API. Do not use NextMoe-provided
    # titles or release dates as a substitute for the VNDB entry.
    ids=list(EXPECTED)
    payload={'filters':['or', *[['id','=',vid] for vid in ids]],
             'fields':'title,alttitle,aliases,released,devstatus','results':20}
    request=urllib.request.Request(
        'https://api.vndb.org/kana/vn',
        data=json.dumps(payload).encode('utf-8'),method='POST',
        headers={'Content-Type':'application/json','Accept':'application/json',
                 'User-Agent':'NarrativeCatalogueResearch/1.0'})
    last=None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request,timeout=40) as response:
                value=json.load(response)
            assert isinstance(value.get('results'),list)
            return {r['id']:r for r in value['results']}
        except (OSError,ValueError) as exc:
            last=exc
            time.sleep(3*(attempt+1))
    raise RuntimeError('Official VNDB lookup failed; no unverified records will be added') from last

def verify_and_append():
    held=audit_input()
    registry,index,refs=source.state()
    if any(b['id']==BATCH for b in registry['batches']):
        print('ALREADY_REGISTERED',BATCH)
        return
    assert len(registry['works'])==27368, 'Unexpected main registry, rebase/review required'
    items=fetch_vndb()
    accepted=[]
    dispositions=[]
    counts=Counter()
    reused=[]
    pending=[]
    for vid,(next_id,recorded_vndb,recorded_next) in EXPECTED.items():
        original=held[vid]
        item=items.get(vid)
        review={'vndbId':vid,'nextmoeSourceId':next_id,
                'vndbOriginalRecorded':recorded_vndb,
                'nextmoeClaimedEarlierDate':recorded_next,
                'originalAuditTitle':original['title'],
                'crossSourceAssociation':'unverified; NextMoe reference not assigned'}
        if not item:
            review.update(status='held-missing-vndb-id')
        elif str(item.get('released'))!=recorded_vndb or previous.vndb_year(item)!=int(recorded_vndb[:4]):
            review.update(status='held-live-vndb-date-changed',
                          liveVndbReleased=item.get('released'))
        elif source.norm(original['title']) not in {
                source.norm(n) for n in previous.vndb_names(item)}:
            review.update(status='held-vndb-title-mismatch',
                          liveVndbTitle=item.get('title'))
        else:
            row=source.candidate(item,'vndb',vid,previous.vndb_names(item),
                                 index,refs,counts,reused,pending,BATCH)
            if row:
                work=row['work']
                assert work['sourceRefs']==['vndb:'+vid]
                work['yearBasis']='Official VNDB VN-level release year ('+recorded_vndb+'); earlier NextMoe date '+recorded_next+' remains disputed and is not merged.'
                accepted.append(work)
                review.update(status='registered-vndb-identity-only',registryId=work['id'],
                              liveVndbReleased=item['released'],
                              liveVndbTitle=item['title'])
            else:
                review.update(status='held-duplicate-or-other-identity-check',
                              checks=dict(counts),matches=reused[-1:] or pending[-1:])
        dispositions.append(review)
    summary={'candidatesReviewed':7,'officialVndbVerified':sum(r['status']=='registered-vndb-identity-only' for r in dispositions),
             'crossSourceAssociationsApproved':0,'remainingSourceAssociationDisputes':7}
    if not accepted:
        raise RuntimeError('No independently verified VNDB identities; leaving registry unchanged')
    source.previous.append_batch(registry,accepted,BATCH,previous.VNDB_API,
        AUDIT,summary,
        [{**w,'vndbId':w['id'][5:],
          'sourceReleased':next(x['liveVndbReleased'] for x in dispositions if x.get('registryId')==w['id']),
          'intakeOrigin':'independent-vndb-recheck'}
         for w in accepted],
        [dict(x) for x in dispositions if x['status']!='registered-vndb-identity-only'],
        'https://api.vndb.org/kana','https://vndb.org/d17')
    audit=source.load(AUDIT)
    audit['sourceConflictReview']=dispositions
    audit['reviewPolicy']='Register only independently verified VNDB identities; preserve but do NOT attach NextMoe earlier-date claims. Old r55 audit remains immutable.'
    audit['sourceAudit']='data/nextmoe-bulk-review-20261101-r55.json'
    source.save(AUDIT,audit)
    print('REVIEWED',len(dispositions),'REGISTERED',len(accepted),'HELD',len(dispositions)-len(accepted))

def check():
    audit_input()
    old=json.loads(subprocess.check_output(
        ['git','show',OLD_SHA+':'+str(REG.relative_to(ROOT))],cwd=ROOT))
    new=source.load(REG)
    assert new['works'][:len(old['works'])]==old['works']
    assert new['batches'][:len(old['batches'])]==old['batches']
    for k in old:
        if k not in {'works','batches','summary','updated'}:
            assert new[k]==old[k]
    audit=source.load(AUDIT)
    added=[w for w in new['works'] if w.get('batch')==BATCH]
    assert added and len(added)<=7
    assert len(added)==audit['summary']['newDistinctWorks']
    assert len({w['id'] for w in new['works']})==len(new['works'])
    assert len({w['indexId'] for w in new['works']})==len(new['works'])
    assert len(audit['sourceConflictReview'])==7
    assert not any('nextmoe:' in ref for w in added for ref in w['sourceRefs'])
    assert all(w['id'][5:] in EXPECTED and w['firstYear']==int(EXPECTED[w['id'][5:]][1][:4]) for w in added)
    assert new['summary']['accepted']==len(new['works'])
    print('VERIFIED_SEVEN_SOURCE_CONFLICTS',len(added),'REGISTERED',len(new['works']))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--check',action='store_true')
    args=p.parse_args()
    check() if args.check else verify_and_append()
