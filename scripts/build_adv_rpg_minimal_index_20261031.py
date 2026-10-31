#!/usr/bin/env python3
"""Build a searchable title/year/gameplay-only narrative catalogue without fabricating full game profiles.

The existing strict main games.json schema and historical content/version records are not changed.
An existing main/dossier identity is linked instead of duplicated. All unmatched titles become
new basic-index works, with no fabricated characters, narrative profiles or creator credits.
"""
from pathlib import Path
from collections import Counter
import json, re, unicodedata, hashlib
ROOT=Path(__file__).resolve().parents[1]
def load(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKC',str(s or '')).casefold() if c.isalnum())
def names(w):return [w.get('title'),w.get('originalTitle'),w.get('chineseTitle'),*(w.get('titleAliases') or [])]
def allowed(w):
    desc=' '.join(str(w.get(k) or '') for k in ('category','subcategory','genre'))
    if re.search(r'RPG|角色扮演|战术冒险|视觉小说|Galgame|ADV|叙事|剧情|文字冒险|图文冒险|恋爱冒险|互动电影|推理冒险',desc,re.I):
        return True
    return False
seed=load('data/adv-rpg-minimal-candidates-20261031.json')
main=load('data/games.json')
company=load('data/company-coverage.json')
assert len(seed['records'])>=200
assert len({norm(x['title']) for x in seed['records']})==len(seed['records']),'candidate work duplicated'
assert all(x['title'].strip() and 1976<=x['year']<=2026 and x['gameplay'] in {'ADV','视觉小说','RPG','SRPG','ARPG','互动电影ADV'} and x['source'].startswith('https://') for x in seed['records'])
allworks={}; mainids=set()
for w in main['works']:
    allworks[w['id']]=(w,'main')
    mainids.add(w['id'])
for c in company['companies']:
    for field in ('relatedGames','dossierOnlyWorks'):
        for w in c.get(field,[]):
            allworks.setdefault(w['id'],(w,'dossier'))
existing={}
for wid,(w,placement) in allworks.items():
    for n in names(w):
        k=norm(n)
        if k:existing.setdefault(k,set()).add(wid)
new, linked, ambiguous, itemrows=[],[],[],[]
for i,x in enumerate(seed['records'],1):
    possible=set()
    for n in [x['title'],*(x.get('aliases') or [])]:
        possible.update(existing.get(norm(n),set()))
    year_matches={wid for wid in possible if abs(int(allworks[wid][0].get('firstYear',x['year']))-x['year'])<=2}
    if year_matches:possible=year_matches
    label='new-basic'
    ref=None
    if len(possible)==1:
        ref=next(iter(possible))
        label='main-linked' if ref in mainids else 'dossier-linked'
    elif possible:
        label='identity-review'
        ambiguous.append({'title':x['title'],'possibleIds':sorted(possible)})
    item={
       'id':'basic-'+hashlib.sha1((norm(x['title'])+':'+str(x['year'])).encode()).hexdigest()[:12],
       'title':x['title'],'aliases':x.get('aliases',[]),'year':x['year'],
       'gameplay':x['gameplay'],'group':x['group'],'source':x['source'],
       'status':label,'matchedWorkId':ref,
       'yearBasis':'historical company catalogue or linked source; exact region/platform date not fully verified',
       'creditScope':'company/brand association, not automatically developer or publisher',
       'narrativeDetails':'not requested / not catalogued'
    }
    itemrows.append(item)
    if label=='new-basic':new.append(item['id'])
    else:linked.append(item['id'])
# Also surface prior dossier-only narrative/RPG works not selected above: they are accessible without creating aliases.
allkeys=set()
for row in itemrows:
    allkeys.update(norm(n) for n in [row['title'],*row.get('aliases',[])])
extras=[]
for wid,(w,place) in allworks.items():
    if place!='dossier' or not allowed(w):continue
    if any(norm(n) in allkeys for n in names(w) if n):continue
    if not (1976<=int(w.get('firstYear',0))<=2026):continue
    rawsource=w.get('source','')
    if not isinstance(rawsource,str) or not rawsource.startswith('https://'):continue
    typ=(w.get('category') or w.get('subcategory') or '剧情RPG/ADV')
    extras.append({'id':'dossier-'+wid,'title':w['title'],
       'aliases':[n for n in names(w)[1:] if n],
       'year':w['firstYear'],'gameplay':typ,
       'group':'既有厂商专题','source':rawsource,
       'status':'dossier-linked','matchedWorkId':wid,
       'yearBasis':'pre-existing dossier record','creditScope':'dossier association',
       'narrativeDetails':'pre-existing dossier detail; not altered'})
    allkeys.update(norm(n) for n in names(w) if n)
extraids={x['matchedWorkId'] for x in extras}
# Keep deterministic ordering and two distinct notions: 208 reviewed input candidates and existing references.
itemrows.sort(key=lambda x:(x['year'],x['title'].casefold(),x['id']))
extras.sort(key=lambda x:(x['year'],x['title'].casefold(),x['id']))
counts=Counter(x['status'] for x in itemrows)
summary={'candidates':len(itemrows),'newBasic':counts['new-basic'],
         'alreadyMain':counts['main-linked'],'alreadyDossier':counts['dossier-linked'],
         'identityReview':counts['identity-review'],'additionalDossierLinks':len(extras),
         'displayTotal':len(itemrows)+len(extras),
         'groups':len({x['group'] for x in itemrows})}
out={'schema':1,'updated':'2026-10-31','summary':summary,'records':itemrows+extras,
     'identityReview':ambiguous,
     'notice':'Lightweight title/year/gameplay catalogue. Candidate association is not a verified development or publication credit. Main game records and content editions are untouched.'}
(ROOT/'data/adv-rpg-minimal-index-20261031.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
