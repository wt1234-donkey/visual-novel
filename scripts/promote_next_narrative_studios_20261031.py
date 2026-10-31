#!/usr/bin/env python3
"""Screen and promote the next studio-narrative candidates into the *same* primary identity layer.

Keep the strict detailed historical database unchanged. This script is idempotent; both
previous master IDs and previously promoted basic IDs remain the canonical identities.
"""
import hashlib,json,re,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT/path).read_text(encoding='utf-8'))
def norm(v): return ''.join(c for c in unicodedata.normalize('NFKC',str(v or '')).casefold() if c.isalnum())
def names(w): return [w.get('title'),w.get('originalTitle'),w.get('chineseTitle'),*(w.get('titleAliases') or []),*(w.get('aliases') or [])]
registry_path=ROOT/'data/main-adv-rpg-works-20261031.json'
registry=load('data/main-adv-rpg-works-20261031.json')
seed=load('data/adv-rpg-next-studio-candidates-20261031.json')
main=load('data/games.json')
coverage=load('data/company-coverage.json')
extra=load('data/non-rpg-creator-supplement-20261030.json')
prior=load('data/adv-rpg-minimal-index-20261031.json')
assert len(seed['records'])==59 and len({(norm(x['title']),x['year']) for x in seed['records']})==59
assert len(registry['works'])>=207
assert len(registry['identityReview'])>=1
old_before=registry['works'][:207]
existing_by_name={}
def register(w,location):
    for title in names(w):
        key=norm(title)
        if key:
            existing_by_name.setdefault(key,[]).append((w['id'],int(w.get('firstYear') or w.get('year') or 0),location))
for w in main['works']:register(w,'complete-main')
for w in extra['works']:register(w,'supplement-complete')
for c in coverage['companies']:
    for field in ('relatedGames','dossierOnlyWorks'):
        for w in c.get(field,[]):register(w,'company-dossier')
for w in registry['works']:register(w,'primary-identity')
first_batch_keys=set()
for w in prior['records'][:208]:
    for title in [w.get('title'),*(w.get('aliases') or [])]:
        if norm(title):first_batch_keys.add(norm(title))
base_ids={w['id'] for w in registry['works']}
hold_ids={w['indexId'] for w in registry['identityReview']}
status=Counter()
decisions=[]
for row in seed['records']:
    title=row['title'];year=row['year'];key=norm(title)
    assert title and 1976<=year<=2026 and row['source'].startswith('https://')
    assert row['gameplay'] in {'ADV','视觉小说','RPG','SRPG','ARPG','互动电影ADV'}
    possible={}
    for n in [title,*(row.get('aliases') or [])]:
        for wid,matched_year,location in existing_by_name.get(norm(n),[]):
            if wid not in possible or location=='primary-identity':
                possible[wid]=(matched_year,location)
    candidates=[(wid,yr,loc) for wid,(yr,loc) in possible.items()]
    # A company dossier and registry may refer to the same underlying record; by ID this stays one match.
    identical=[(wid,yr,loc) for wid,yr,loc in candidates if yr==year]
    close=[(wid,yr,loc) for wid,yr,loc in candidates if abs(yr-year)<=1]
    usable=identical or close
    if len(usable)>1 or (candidates and not usable):
        decision='identity-review'
        detail='Ambiguous matching work identity or original-year discrepancy: '+repr(candidates)
        wid=None
    elif len(usable)==1:
        wid,foundyear,where=usable[0]
        if wid in hold_ids:
            decision='identity-review';detail='Previously held for edition-versus-work review.'
        elif wid in base_ids:
            decision='linked-existing-registry';detail='Title/alias links to an existing unified primary work ID; not duplicated.'
        else:
            decision='linked-existing-full-or-dossier';detail=f'Existing work at {where}, linked without changing its full record.'
            location='existing-complete' if where in ('complete-main','supplement-complete') else 'promoted-dossier'
            entry={
                'id':wid,'indexId':'next-'+hashlib.sha1((key+str(year)).encode()).hexdigest()[:14],
                'title':title,'aliases':row.get('aliases',[]),'firstYear':year,'gameplay':row['gameplay'],
                'group':row['group'],'source':row['source'],'mainPlacement':location,'linkedRecordId':wid,
                'creditScope':'Studio group indicates research association only; full production and publishing roles unverified.',
                'editorialScope':'Lightweight story-first catalogue title, original year, gameplay and provenance only.'
            }
            registry['works'].append(entry);base_ids.add(wid)
    else:
        wid='basic-narr-'+hashlib.sha1((key+'|'+str(year)).encode()).hexdigest()[:16]
        assert wid not in base_ids
        registry['works'].append({
            'id':wid,'indexId':'next-'+hashlib.sha1((key+str(year)).encode()).hexdigest()[:14],
            'title':title,'aliases':row.get('aliases',[]),'firstYear':year,'gameplay':row['gameplay'],
            'group':row['group'],'source':row['source'],'mainPlacement':'promoted-basic','linkedRecordId':None,
            'creditScope':'Studio group is a curated association; no publishing or production role asserted.',
            'editorialScope':'Basic work identity only; no invented characters, story metadata or content versions.'
        })
        base_ids.add(wid)
        decision='promoted-basic';detail='No corresponding work found in full main/dossier/previous registry by exact normalized title or aliases.'
    status[decision]+=1
    decisions.append({**row,'status':decision,'matchedWorkId':wid,'auditNote':detail,
                      'registryId':wid if decision!='identity-review' else None})
assert sum(status.values())==59
assert len({w['id'] for w in registry['works']})==len(registry['works'])
assert registry['works'][:207]==old_before
statuses=Counter(w['mainPlacement'] for w in registry['works'])
registry['summary']={
    'candidates':208+len(seed['records']),
    'accepted':len(registry['works']),
    'existingComplete':statuses['existing-complete'],
    'promotedDossier':statuses['promoted-dossier'],
    'promotedBasic':statuses['promoted-basic'],
    'identityReview':len(registry['identityReview'])+status['identity-review'],
    'addedToMainIdentityLayer':statuses['promoted-dossier']+statuses['promoted-basic'],
    'nextBatchCandidates':59,
    'nextBatchNewBasic':status['promoted-basic'],
    'nextBatchLinkedExisting':status['linked-existing-registry']+status['linked-existing-full-or-dossier'],
    'nextBatchHeld':status['identity-review']
}
registry['updated']='2026-10-31'
registry['nextBatch']={'source':'data/adv-rpg-next-studio-candidates-20261031.json',
                       'review':'data/adv-rpg-next-studio-review-20261031.json','summary':dict(status)}
registry_path.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review={'schema':1,'reviewedAt':'2026-10-31','summary':dict(status),'records':decisions,
        'policy':'Role claims require specific credits; no full narrative or edition creation. Source URLs for some catalogue-level entries do not independently prove a particular release platform.'}
(ROOT/'data/adv-rpg-next-studio-review-20261031.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Screened next batch:',json.dumps(dict(status),ensure_ascii=False),'total primary works',len(registry['works']))
