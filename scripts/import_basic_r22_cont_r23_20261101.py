#!/usr/bin/env python3
"""Source-ID reuse, diverse bounded selection and append-only basic identities."""
import argparse
import copy
import hashlib
import json
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict, deque
from pathlib import Path

import import_basic_r20_r21_20261101 as previous
import import_nextmoe_basic_20261101_r2 as common

ROOT = Path(__file__).resolve().parents[1]
REG = common.REGISTRY
BASE = 'b55a304792b57ee2822fb0a09a2cf476893dea42'
B22 = 'vndb-kana-bulk-20261101-r22-cont1'
B23 = 'nextmoe-galgame-bulk-20261101-r23'
A22 = ROOT / 'data/vndb-kana-bulk-review-20261101-r22-cont1.json'
A23 = ROOT / 'data/nextmoe-bulk-review-20261101-r23.json'
IFDB = ROOT / 'data/ifdb-supplement-candidates-20261101.json'
REPORT = ROOT / 'data/basic-r22-cont-r23-diversity-20261101.json'
PROTECTED = ['data/games.json', 'data/company-coverage.json', 'data/entities.json',
             'data/credits.json', 'data/non-rpg-creator-supplement-20261030.json',
             'data/curated-narrative-works.json']
POOL_CAP = 900
CAP = 500
VNDB_FIELDS = 'title,alttitle,aliases,released,devstatus,developers.id,developers.name,developers.original,developers.type'
DERIVATIVE = re.compile(r'(?i)(?:\bdlc\b|\bdemo\b|\btrial\b|\bfan.?disc\b|\bfandisk\b|\bcollection\b|\bbundle\b|\bremaster\b|体験版|ファンディスク|リマスター|合集)')
load, save, norm = previous.load, previous.save, common.norm


def request_json(url, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={
        'Accept':'application/json', 'Content-Type':'application/json',
        'User-Agent':'NarrativeCatalogueResearch/1.1 (wt1234-donkey/visual-novel; minimal metadata)'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code not in {429,500,502,503,504} or attempt == 3:
                raise
            time.sleep(max(10, min(60, int(exc.headers.get('Retry-After') or 0)), 10*(attempt+1)))
        except (urllib.error.URLError, TimeoutError):
            if attempt == 3:
                raise
            time.sleep(10*(attempt+1))
    raise RuntimeError('request retries exhausted')


def vndb_page(cursor):
    result = request_json(previous.VNDB_API, {'fields':VNDB_FIELDS, 'results':100,
        'sort':'id', 'reverse':False, 'filters':['id','>',cursor]})
    assert isinstance(result.get('results'),list) and isinstance(result.get('more'),bool)
    return result


def lookup_vndb(ids):
    found = {}
    for start in range(0,len(ids),100):
        block = ids[start:start+100]
        result = request_json(previous.VNDB_API, {'fields':VNDB_FIELDS,'results':100,
            'filters':['or', *[['id','=',value] for value in block]]})
        assert isinstance(result.get('results'),list)
        found.update({r['id']:r for r in result['results']})
        time.sleep(2)
    return found


def all_works(registry):
    rows = list(registry['works'])
    rows += load(ROOT/'data/games.json')['works']
    rows += load(ROOT/'data/non-rpg-creator-supplement-20261030.json')['works']
    for company in load(ROOT/'data/company-coverage.json')['companies']:
        for key in ('relatedGames','dossierOnlyWorks'):
            rows += company.get(key,[])
    return rows


def identity_map(registry):
    index = defaultdict(set)
    for work in all_works(registry):
        for ref in work.get('sourceRefs',[]):
            index[str(ref)].add(str(work['id']))
        if re.fullmatch(r'vndb-v\d+',str(work.get('id',''))):
            index['vndb:'+work['id'][5:]].add(str(work['id']))
    return index


def state():
    registry = load(REG)
    return registry, common.existing_index(registry), identity_map(registry)


def producers(item):
    return [{key:p.get(key) for key in ('id','name','original','type')}
            for p in item.get('developers',[]) if re.fullmatch(r'p\d+',str(p.get('id','')))]


def creator_type(row):
    kinds = {p.get('type') for p in row['developers']}
    return 'individual-or-amateur-signal' if kinds & {'in','ng'} else 'company' if 'co' in kinds else 'unknown'


def diverse_select(pool, registry):
    """Round-robin decade/type strata, then developers; retain every deferred row."""
    prior = Counter((int(w['firstYear'])//10)*10 for w in registry['works'])
    groups = defaultdict(lambda: defaultdict(deque))
    for row in pool:
        decade = (row['work']['firstYear']//10)*10
        maker = tuple(sorted(p['id'] for p in row['developers'])) or ('unknown',)
        groups[(decade,creator_type(row))][maker].append(row)
    buckets = {}
    for key, makers in groups.items():
        q = deque()
        while any(makers.values()):
            for maker in sorted(makers):
                if makers[maker]:
                    q.append(makers[maker].popleft())
        buckets[key] = q
    order = sorted(buckets,key=lambda k:(prior[k[0]], k[1]!='individual-or-amateur-signal', k[0], k[1]))
    selected = []
    while len(selected)<CAP and any(buckets.values()):
        for key in order:
            if buckets[key]:
                selected.append(buckets[key].popleft())
                if len(selected)==CAP:
                    break
    chosen = {r['work']['id'] for r in selected}
    return selected,[r for r in pool if r['work']['id'] not in chosen]


def already_exists(registry,batch,audit):
    if not any(b['id']==batch for b in registry.get('batches',[])):
        return False
    assert audit.exists(), 'Batch marker without audit'
    old = load(audit)
    assert sum(w.get('batch')==batch for w in registry['works'])==old['summary']['newDistinctWorks']
    return True


def candidate(item, source_kind, source_id, names, index, refs, counts, reused, held, batch):
    vid = str(item.get('id',''))
    source_refs = ['vndb:'+vid]
    if source_kind=='nextmoe':
        source_refs.insert(0,'nextmoe:'+source_id)
    hits = set().union(*(refs.get(ref,set()) for ref in source_refs))
    if hits:
        counts['reused-external-identity']+=1
        reused.append({'sourceId':source_id,'vndbId':vid,'matchedWorkIds':sorted(hits),'basis':'exact-source-id'})
        return None
    year = previous.vndb_year(item)
    if year is None or not names:
        counts['missing-name-year-or-unreleased']+=1
        return None
    if DERIVATIVE.search(' '.join(names)) or common.is_non_work_pack(names[0]):
        counts['derivative-held']+=1
        held.append({'sourceId':source_id,'vndbId':vid,'title':names[0],'reason':'possible-edition-or-dependent-content'})
        return None
    hits = set().union(*(index.get(norm(name),set()) for name in names))
    if hits:
        same = all(h[1]==year for h in hits) and len({h[0] for h in hits})==1
        counts['reused-title-alias' if same else 'name-year-conflict-held']+=1
        row = {'sourceId':source_id,'vndbId':vid,'title':names[0],'firstYear':year,
               'matches':[list(h) for h in sorted(hits)]}
        (reused if same else held).append({**row,'basis':'normalized-name-alias-year' if same else 'ambiguous-name-year'})
        return None
    wid = 'vndb-'+vid
    source = 'https://vndb.org/'+vid if source_kind=='vndb' else previous.NEXTMOE_API+'/'+source_id
    work = {'id':wid,'indexId':batch+'-'+source_id,'title':names[0],'aliases':names[1:],
        'firstYear':year,'gameplay':'视觉小说','group':'创作品牌待核','source':source,'sourceRefs':source_refs,
        'mainPlacement':'promoted-basic','linkedRecordId':None,
        'creditScope':'来源元数据；开发主体仅在独立审计中记录，不推断正式创作或发行职责。',
        'yearBasis':'VNDB VN-level released 年份；NextMoe条目回查同一VNDB ID。首次地区/版次待核。',
        'editorialScope':'基础身份；叙事、创作者职责、具体玩法与内容版本待核。','batch':batch}
    for name in names:
        index[norm(name)].add((wid,year,'candidate-pool'))
    for ref in source_refs:
        refs[ref].add(wid)
    return {'work':work,'sourceId':source_id,'vndbId':vid,'sourceReleased':item['released'],
            'sourceDevstatus':item.get('devstatus'),'developers':producers(item)}


def append(registry,pool,batch,audit_path,summary,counts,reused,held):
    selected,deferred = diverse_select(pool,registry)
    assert selected, 'No distinct eligible identities'
    before = len(registry['works'])
    records = [{**r['work'], 'sourceId':r['sourceId'],'vndbId':r['vndbId'],
        'sourceReleased':r['sourceReleased'],'sourceDevstatus':r['sourceDevstatus'],
        **({'nextmoeSourceReleased':r['nextmoeSourceReleased']} if 'nextmoeSourceReleased' in r else {}),
        'developers':r['developers'],'developerClassification':creator_type(r)} for r in selected]
    source = previous.VNDB_API if batch==B22 else previous.NEXTMOE_API
    previous.append_batch(registry,[r['work'] for r in selected],batch,source,audit_path,
        {**summary,'eligiblePool':len(pool),'deferredEligible':len(deferred),**dict(counts)},
        records,held,'https://api.vndb.org/kana',
        'https://vndb.org/d17; NextMoe minimal factual metadata with source attribution')
    audit = load(audit_path)
    audit.update({'reusedExisting':reused,'deferredEligible':deferred,
        'selection':'Round-robin decade and developer-type strata; round-robin developer IDs within each stratum.',
        'resumePolicy':'Drain deferredEligible before fetching after cursorEnd/endPage. Deferred rows are candidates, not added identities.',
        'priorBaseCommit':BASE})
    save(audit_path,audit)
    print('APPENDED',batch,before,len(registry['works']),'DEFERRED',len(deferred),flush=True)


def round22():
    registry,index,refs = state()
    if already_exists(registry,B22,A22):
        return
    assert load(ROOT/'data/vndb-kana-bulk-review-20261101-r22.json')['summary']['cursorEnd']=='v4819'
    cursor='v4819'
    pool,reused,held = [],[],[]
    counts=Counter()
    scanned=0
    for page in range(1,26):
        payload=vndb_page(cursor)
        for item in payload['results']:
            scanned+=1
            cursor=item['id']
            row=candidate(item,'vndb',cursor,previous.vndb_names(item),index,refs,counts,reused,held,B22)
            if row:
                pool.append(row)
        print('R22_CONT_POOL',page,scanned,len(pool),cursor,flush=True)
        if len(pool)>=POOL_CAP or not payload['more']:
            break
        time.sleep(2)
    append(registry,pool,B22,A22,{'scanned':scanned,'cursorStart':'v4819','cursorEnd':cursor},counts,reused,held)


def nextmoe_pages(trace):
    # Official page mode has a 10,000-row ceiling. Do not request page 101.
    for page in range(93,101):
        payload=common.get_page(page,100)
        trace.append({'lane':'rating-vndb-page','page':page,'returned':len(payload['items'])})
        yield 'page-'+str(page),payload
    windows=[('1976-01-01','1999-12-31'),('2000-01-01','2009-12-31'),('2010-01-01','2026-11-01')]
    budget=60
    for after,before in windows:
        cursor=None
        while budget>0:
            params={'limit':100,'sort':'id','nsfw':'true','include':'titles,refs',
                    'released_after':after,'released_before':before}
            if cursor:
                params['cursor']=cursor
            url=previous.NEXTMOE_API+'?'+urllib.parse.urlencode(params)
            payload=request_json(url)
            assert payload.get('object')=='list' and isinstance(payload.get('items'),list)
            trace.append({'lane':'era-keyset','releasedAfter':after,'releasedBefore':before,
                'cursorUsed':cursor,'nextCursor':payload.get('next_cursor'),'returned':len(payload['items'])})
            yield after+'-cursor-'+str(budget),payload
            budget-=1
            cursor=payload.get('next_cursor')
            if not cursor:
                break


def round23():
    registry,index,refs=state()
    if already_exists(registry,B23,A23):
        return
    pool,reused,held=[],[],[]
    counts=Counter()
    scanned=0
    trace=[]
    for page,payload in nextmoe_pages(trace):
        items=payload['items']
        fresh=[]
        for item in items:
            scanned+=1
            vid=common.has_vndb_identity(item)
            sid=str(item.get('id',''))
            if item.get('medium')!='galgame' or not vid or not sid.isdecimal():
                counts['invalid-medium-or-source-id']+=1
                continue
            matched=refs.get('vndb:'+vid,set())|refs.get('nextmoe:'+sid,set())
            if matched:
                counts['reused-external-identity']+=1
                reused.append({'sourceId':sid,'vndbId':vid,'matchedWorkIds':sorted(matched),'basis':'exact-source-id'})
                continue
            if sid in common.HELD_EDITION_IDS:
                counts['derivative-held']+=1
                held.append({'sourceId':sid,'vndbId':vid,'reason':'known-edition-review'})
                continue
            fresh.append((item,vid,sid))
        authoritative=lookup_vndb(list(dict.fromkeys(v for _,v,_ in fresh))) if fresh else {}
        for item,vid,sid in fresh:
            vn=authoritative.get(vid)
            if not vn:
                counts['missing-vndb-record']+=1
                continue
            names=[]
            seen=set()
            for name in [*previous.vndb_names(vn), *common.source_names(item)]:
                if norm(name) not in seen:
                    names.append(name)
                    seen.add(norm(name))
            row=candidate(vn,'nextmoe',sid,names,index,refs,counts,reused,held,B23)
            if row:
                row['nextmoeSourceReleased']=item.get('release_date')
                pool.append(row)
        print('R23_POOL',page,scanned,len(pool),flush=True)
        if len(pool)>=POOL_CAP:
            break
        time.sleep(2)
    append(registry,pool,B23,A23,{'scanned':scanned,'startPage':93,'endPage':100,
        'paginationTrace':trace,
        'yearMethod':'VNDB released; NextMoe date is not used as original year'},counts,reused,held)


def ifdb_sample():
    if IFDB.exists():
        return
    registry,index,_=state()
    samples=[]
    requests=[]
    # Three low-volume user-driven requests; no result paging or database crawling.
    for query in ['published:1976-1989','published:1990-2009','published:2010-2026']:
        url='https://ifdb.org/search?json&game&'+urllib.parse.urlencode({'searchfor':query})
        result=request_json(url)
        assert isinstance(result.get('games'),list)
        requests.append({'query':query,'url':url,'returned':len(result['games'])})
        for item in result['games'][:20]:
            raw=(item.get('published') or {}).get('machine','')
            title=item.get('title','')
            tuid=item.get('tuid','')
            if not title or not re.fullmatch(r'[a-z0-9]{16}',str(tuid)) or not re.match(r'^\d{4}(?:-\d\d-\d\d)?$',raw):
                continue
            year=int(raw[:4])
            if not 1976<=year<=2026:
                continue
            hits=index.get(norm(title),set())
            samples.append({'sourceId':tuid,'title':title,'firstYear':year,'sourcePublished':raw,
                'source':'https://ifdb.org/viewgame?id='+tuid,'sourceAuthor':item.get('author'),
                'developmentSystem':item.get('devsys'),
                'status':'existing-name-needs-identity-review' if hits else 'candidate-not-imported',
                'matches':[list(h) for h in sorted(hits)],'readyForIdentityImport':False})
        time.sleep(3)
    save(IFDB,{'schema':1,'date':'2026-11-01','source':'https://ifdb.org/',
        'sourceDocs':'https://ifdb.org/api/search','attribution':'Interactive Fiction Database (IFDB), linked per listing; minimal factual metadata.',
        'licenseBasis':'https://ifdb.org/tos','requests':requests,'records':samples,
        'summary':{'sampled':len(samples),'newIdentityImports':0},
        'scope':'Small metadata sample only. For future bulk analysis use IF Archive SQL exports; do not crawl the API.'})


def report():
    records=[]
    by_batch={}
    for batch,path in [(B22,A22),(B23,A23)]:
        audit=load(path)
        rows=audit['records']
        by_batch[batch]={'new':len(rows),'pool':audit['summary']['eligiblePool'],
            'deferred':len(audit['deferredEligible']),
            'decades':dict(sorted(Counter(str(r['firstYear']//10*10)+'s' for r in rows).items())),
            'creatorTypes':dict(Counter(r['developerClassification'] for r in rows)),
            'distinctDeveloperIds':len({p['id'] for r in rows for p in r['developers']})}
        records.extend(rows)
    maker_counts=Counter(p['id'] for r in records for p in r['developers'])
    makers={p['id']:p for r in records for p in r['developers']}
    save(REPORT,{'schema':1,'date':'2026-11-01','byBatch':by_batch,
        'summary':{'newDistinctWorks':len(records),'uniqueVndbIds':len({r['vndbId'] for r in records}),
            'distinctDeveloperIds':len(makers),
            'individualOrAmateurSignalWorks':sum(r['developerClassification']=='individual-or-amateur-signal' for r in records)},
        'topDevelopers':[dict(makers[pid],workCount=count) for pid,count in maker_counts.most_common(30)],
        'caveats':['VNDB in=individual, ng=amateur group: signals only, not proof of independent status.',
            'Coverage is bounded by the requested source ranges, not global representativeness.',
            'No developer, publisher or narrative-quality claims were added to formal catalogue credits.']})


def check():
    old=json.loads(subprocess.check_output(['git','show',BASE+':'+str(REG.relative_to(ROOT))],cwd=ROOT))
    current=load(REG)
    additions=current['works'][len(old['works']):]
    assert current['works'][:len(old['works'])]==old['works']
    assert len(additions)<=1000
    assert len(current['works'])==len({w['id'] for w in current['works']})
    assert len(current['works'])==len({w['indexId'] for w in current['works']})
    for name in PROTECTED:
        assert subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)==(ROOT/name).read_bytes(),name
    index=common.existing_index(old)
    refs=identity_map(old)
    for batch,path in [(B22,A22),(B23,A23)]:
        audit=load(path)
        rows=[w for w in additions if w['batch']==batch]
        assert 1<=len(rows)<=CAP
        assert len(rows)==len(audit['records'])==audit['summary']['newDistinctWorks']
        assert audit['summary']['eligiblePool']==len(rows)+len(audit['deferredEligible'])
        assert audit['summary']['scanned']==audit['summary']['eligiblePool']+sum(v for k,v in audit['summary'].items()
            if isinstance(v,int) and k not in {'before','after','newDistinctWorks','scanned','startPage','endPage','eligiblePool','deferredEligible'})
        evidence={r['id']:r for r in audit['records']}
        for w in rows:
            r=evidence[w['id']]
            assert previous.vndb_year({'released':r['sourceReleased'],'devstatus':r['sourceDevstatus']})==w['firstYear']
            assert all(w[k]==r[k] for k in ('title','aliases','source','sourceRefs'))
            assert w['id']=='vndb-'+r['vndbId']
            assert not set().union(*(refs.get(ref,set()) for ref in w['sourceRefs']))
            assert all(not index.get(norm(n)) for n in [w['title'],*w['aliases']])
            for n in [w['title'],*w['aliases']]:
                index[norm(n)].add((w['id'],w['firstYear'],'new-batch'))
            for ref in w['sourceRefs']:
                refs[ref].add(w['id'])
        assert len({r['work']['id'] for r in audit['deferredEligible']})==len(audit['deferredEligible'])
    assert current['summary']['accepted']==len(current['works'])
    assert load(REPORT)['summary']['uniqueVndbIds']==len(additions)
    print('BATCH22_CONT_23_CHECK_OK',len(old['works']),'+',len(additions),'=',len(current['works']),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if not args.check:
        round22()
        round23()
        try:
            ifdb_sample()
        except (urllib.error.URLError, TimeoutError, ValueError, AssertionError) as exc:
            save(IFDB, {'schema':1,'source':'https://ifdb.org/',
                'summary':{'sampled':0,'newIdentityImports':0},'records':[],
                'status':'source-unavailable-or-schema-changed','error':str(exc)[:300]})
            print('IFDB_SAMPLE_UNAVAILABLE',str(exc),flush=True)
        report()
    check()

if __name__=='__main__':
    main()
