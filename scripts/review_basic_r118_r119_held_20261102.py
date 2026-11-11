#!/usr/bin/env python3
"""Conservative provenance review of the 67 quarantined rows (56 source identities).

Never treat title/date disagreement as sufficient proof of independence.
The 2026-11-02 IFDB decisions were checked against the named IFDB work pages;
VNDB decisions also compare live producers and VN-to-VN relations.
All historic queues, audits and cursors remain unchanged.
"""
from registry_store import read_json as read_registry_json, write_json as write_registry_json, write_text as write_registry_text
import argparse
import copy
import datetime as dt
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import import_basic_r22_cont_r23_20261101 as src

ROOT=src.ROOT
R118='data/vndb-kana-bulk-review-20261102-r118.json'
R119='data/nextmoe-ifdb-bulk-review-20261102-r119.json'
OUT=ROOT/'data/basic-r118-r119-identity-review-20261102.json'
BATCH='r118-r119-held-identity-review-20261102'
TODAY=dt.date(2026,11,2)

# First-party IFDB detail pages compared with the ambiguous titles, years
# and separately attributed older games. Only indisputably original entries
# are approved; probable platform/revision duplicates stay quarantined.
IFDB_DISTINCT={
'jtyzvv97m8irt63s','fk8xds3a66pyx208','68mdw9k76x61fuyb',
'd5jcsz4mn1bdqpxr','o8iqwwgchaobbuhz','ti3xxdw11e1zlbe6',
'bnvzf6d0czmbk5ps','gaaxee2mvysvsaxd','u16mpjnk07d3l8i2',
'url6d1j3aj61qmhp','zgauwdi6ie4u4pqc','2752o3sh6y05ob1p',
'awzxljw8p7cwlkd0','7mlyo81bc9pk2txv','9lzmypxgtirgznc7'
}
IFDB_UNCERTAIN={'iq9wxtd9a7vpcy2g','x7cvej7bm7ixiz0a'}
IFDB_ALL=IFDB_DISTINCT | IFDB_UNCERTAIN

def load(path):
    return read_registry_json(Path(path))

def save(path,value):
    if Path(path).name == 'main-adv-rpg-works-20261031.json':
        return write_registry_json(path, value)
    write_registry_text(path, json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def groups():
    audits=[load(ROOT/R118),load(ROOT/R119)]
    gs=defaultdict(list)
    for path,a in zip((R118,R119),audits):
        for i,row in enumerate(a['heldForIdentityReview']):
            kind='vndb' if row.get('vndbId') else 'ifdb'
            identity=row['vndbId'] if kind=='vndb' else row['sourceId']
            gs[kind+':'+identity].append({'audit':path,'index':i,'row':row})
    assert [len(a['heldForIdentityReview']) for a in audits]==[23,44]
    assert len(gs)==56 and sum(map(len,gs.values()))==67
    assert {k.split(':')[1] for k in gs if k.startswith('ifdb:')}==IFDB_ALL
    return gs

def get_vndb(gs):
    ids={key.split(':')[1] for key in gs if key.startswith('vndb:')}
    for locators in gs.values():
        for e in locators:
            for wid,*_ in e['row'].get('matches',[]):
                if re.fullmatch(r'vndb-v\d+',wid):
                    ids.add(wid[5:])
    # The live API is mandatory for VNDB approvals; failure holds candidates.
    result={}
    errors=[]
    fields='id,title,alttitle,aliases,released,devstatus,developers.id,developers.name,developers.type,relations.id,relations.relation'
    for i in range(0,len(ids),60):
        chunk=sorted(ids)[i:i+60]
        try:
            payload=src.request_json('https://api.vndb.org/kana/vn',{
                'filters':['or',*[['id','=',vid] for vid in chunk]],
                'fields':fields,'results':100})
            result.update({r['id']:r for r in payload['results']})
        except Exception as exc:
            errors.append(str(exc)[:300])
    return result,errors

def classify_vndb(key,locators,snapshots,registry_rows,refs):
    vid=key.split(':')[1]
    item=snapshots.get(vid)
    row=locators[0]['row']
    if not item:
        return 'held',None,'VNDB API evidence unavailable or identity absent'
    year=src.previous.vndb_year(item)
    expected=row.get('firstYear')
    if expected is None or year!=expected or not 1970<=year<=TODAY.year:
        return 'held',item,'source release year unresolved or changed'
    names=src.previous.vndb_names(item)
    if not names or src.norm(row['title']) not in {src.norm(n) for n in names}:
        return 'held',item,'source title/alias is not corroborated'
    if src.DERIVATIVE.search(' '.join(names)) or src.common.is_non_work_pack(names[0]):
        return 'held',item,'edition/collection/dependent-content needs manual relation check'
    if refs.get(key):
        return 'reuse-existing',item,'exact source reference already attached'
    matched={m[0] for e in locators for m in e['row'].get('matches',[])}
    if not matched or any(m not in registry_rows for m in matched):
        return 'held',item,'match outside current registered identity layer'
    otherids=set()
    for wid in matched:
        for ref in registry_rows[wid].get('sourceRefs',[]):
            if re.fullmatch(r'vndb:v\d+',ref):
                otherids.add(ref.split(':')[1])
        if re.fullmatch(r'vndb-v\d+',wid):
            otherids.add(wid[5:])
    if not otherids or any(o not in snapshots for o in otherids):
        return 'held',item,'comparable VNDB creator evidence unavailable'
    this_creators={p['id'] for p in item.get('developers',[]) if p.get('id')}
    other_creators=set()
    for other in otherids:
        other_creators.update(p['id'] for p in snapshots[other].get('developers',[]) if p.get('id'))
    related={p['id'] for p in item.get('relations',[]) if p.get('id')}
    if otherids & related:
        return 'held',item,'VNDB explicitly links source and matched work'
    if not this_creators or not other_creators or this_creators & other_creators:
        return 'held',item,'shared or missing creator signal; content equivalence unproven'
    years={registry_rows[m].get('firstYear') for m in matched}
    if any(not isinstance(y,int) or abs(y-year)<2 for y in years):
        return 'held',item,'close release years require manual version verification'
    return 'registered-distinct',item,'different VNDB developer IDs, nonoverlapping release era, no explicit VN relation'

def evidence_for_ifdb(key,locators,refs):
    sid=key.split(':')[1]
    row=locators[0]['row']
    year=int(str(row.get('published',''))[:4])
    if key in refs:
        return 'reuse-existing','exact source reference already attached',year
    if year<1970 or year>TODAY.year:
        return 'held','first publication year outside source validity range',year
    if sid in IFDB_UNCERTAIN:
        return 'held','same-title historical edition or date relationship not resolved',year
    if sid in IFDB_DISTINCT:
        return 'registered-distinct','IFDB first-party title, author, year and compared earlier distinct title identity',year
    return 'held','no IFDB verification',year

def run():
    gs=groups()
    original=load(src.REG)
    if any(b['id']==BATCH for b in original['batches']):
        verify()
        print('REVIEW_ALREADY_IMPORTED',flush=True)
        return
    before=copy.deepcopy(original)
    registered={w['id']:w for w in src.all_works(original)}
    refs=src.identity_map(original)
    snapshots,api_errors=get_vndb(gs)
    input_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in (R118,R119)}
    decisions=[]
    added=[]
    for key,locators in gs.items():
        kind,sid=key.split(':',1)
        first=locators[0]['row']
        if kind=='ifdb':
            status,reason,year=evidence_for_ifdb(key,locators,refs)
            snap={'title':first['title'],'published':first.get('published'), 'source':'https://ifdb.org/viewgame?id='+sid}
            names=[first['title']]
            source_url=snap['source']
            devs=[]
        else:
            status,snap,reason=classify_vndb(key,locators,snapshots,registered,refs)
            year=src.previous.vndb_year(snap) if snap else first.get('firstYear')
            names=src.previous.vndb_names(snap) if snap else [first['title']]
            source_url='https://vndb.org/'+sid
            devs=src.producers(snap) if snap else []
        wid=kind+'-'+sid
        target=None
        if status=='reuse-existing':
            matches=sorted(refs.get(key,set()))
            if len(matches)==1: target=matches[0]
            else: status,reason='held','multiple registered matches on one source reference'
        row={'sourceIdentity':key,'title':first['title'],'firstYear':year,
             'status':status,'registryId':wid if status=='registered-distinct' else target,
             'reason':reason,'sourceUrls':[source_url],
             'originalRows':locators,'sourceSnapshot':snap,
             'sourceCreatorSignals':devs,
             'currentNameMatches':sorted({(str(m[0]),int(m[1])) for e in locators for m in e['row'].get('matches',[])}),
             'sourceAuditHash':{loc['audit']:input_hashes[loc['audit']] for loc in locators}}
        decisions.append(row)
        if status!='registered-distinct': continue
        assert isinstance(year,int) and names and wid not in registered
        assert not refs.get(key),key
        if kind=='vndb':
            work={'id':wid,'indexId':BATCH+'-'+sid,'title':names[0],
                'aliases':list(dict.fromkeys(names[1:])),
                'firstYear':year,'gameplay':'视觉小说','group':'创作品牌待核',
                'source':source_url,'sourceRefs':[key],
                'yearBasis':'VNDB VN-level released; original country/platform release not asserted.'}
        else:
            work={'id':wid,'indexId':BATCH+'-'+sid,'title':first['title'],
                'aliases':[],'firstYear':year,'gameplay':'互动小说（玩法待核）',
                'group':'创作品牌待核','source':source_url,'sourceRefs':[key],
                'yearBasis':'IFDB work first-publication year; region/version history not independently confirmed.'}
        work.update({'mainPlacement':'promoted-basic','linkedRecordId':None,
            'creditScope':'Creator/author signals retained in source review, not promoted as authoritative formal credits.',
            'editorialScope':'Audited basic identity only; independent from name collisions, full narrative and exact versions remain uncurated.',
            'identityReview':'data/'+OUT.name,'batch':BATCH})
        added.append(work)
    assert len(decisions)==56
    assert len({d['sourceIdentity'] for d in decisions})==56
    assert sum(len(d['originalRows']) for d in decisions)==67
    assert sum(d['sourceIdentity'].startswith('vndb:') for d in decisions)==39
    assert sum(d['sourceIdentity'].startswith('ifdb:') for d in decisions)==17
    assert len({w['id'] for w in added})==len(added)
    audit={'schema':1,'date':'2026-11-02','batchId':BATCH,
        'baseCommit':'15de08a41d36d99fd0bd56dac86129360144e505',
        'sourceAudits':input_hashes,'apiErrors':api_errors,
        'policy':'Add only independently evidenced originals; existing source ID reuses stay mapped; uncertain edition, same-author and unverified relations remain held. Source creator metadata is not formal credits. No historical queues/cursors or previous rows edited.',
        'summary':{'originalHeldRows':67,'reviewedIdentities':56,
                   'registeredDistinct':len(added),
                   'reusedExisting':sum(d['status']=='reuse-existing' for d in decisions),
                   'stillHeld':sum(d['status']=='held' for d in decisions)},
        'decisions':decisions}
    assert sum(audit['summary'][key] for key in ('registeredDistinct','reusedExisting','stillHeld'))==56
    save(OUT,audit)
    if not any(b['id']==BATCH for b in original['batches']):
        original['works'].extend(added)
        for key in ('candidates','accepted','promotedBasic','addedToMainIdentityLayer'):
            original['summary'][key]+=len(added)
        original['updated']='2026-11-02'
        original['batches'].append({'id':BATCH,'source':['https://api.vndb.org/kana/vn','https://ifdb.org/'],
            'review':str(OUT.relative_to(ROOT)),'summary':{'candidates':len(added),
                'promoted-basic':len(added),'reviewedIdentities':56,
                'reusedExisting':audit['summary']['reusedExisting'],
                'remainingHeld':audit['summary']['stillHeld']}})
        save(src.REG,original)
    assert original['works'][:len(before['works'])]==before['works']
    assert original['batches'][:len(before['batches'])]==before['batches']
    verify()
    print('REVIEW_RUN_COMPLETE',json.dumps(audit['summary'],ensure_ascii=False),flush=True)

def verify():
    gs=groups()
    audit=load(OUT)
    reg=load(src.REG)
    assert len(audit['decisions'])==len(gs)==56
    assert set(d['sourceIdentity'] for d in audit['decisions'])==set(gs)
    assert sum(len(d['originalRows']) for d in audit['decisions'])==67
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
               for p,h in audit['sourceAudits'].items())
    active={w['id']:w for w in src.all_works(reg)}
    rows=[w for w in reg['works'] if w.get('batch')==BATCH]
    assert len(rows)==audit['summary']['registeredDistinct']
    assert all(w['id'] in active for w in rows)
    assert len(rows)==len({w['id'] for w in rows})==len({w['indexId'] for w in rows})
    assert all(d['sourceIdentity'] in active[d['registryId']].get('sourceRefs',[])
               for d in audit['decisions'] if d['status']=='registered-distinct')
    assert all(d['registryId'] not in active for d in audit['decisions']
               if d['status']=='held' and d['registryId'])
    assert len(gs)==len({d['sourceIdentity'] for d in audit['decisions']})
    print('REVIEW_CHECK_OK',audit['summary'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--check',action='store_true')
    args=p.parse_args()
    verify() if args.check else run()
