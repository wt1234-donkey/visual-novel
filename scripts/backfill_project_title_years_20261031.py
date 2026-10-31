#!/usr/bin/env python3
"""Backfill known work titles and debut years from five project maker lists.

This is a title/year intake, NOT the four-field narrative catalogue. No writers,
artist credits, character identities, plots, voice casts, later editions or
platform transfers are inferred. Exact title/alias matches reuse the old ID.
"""
import json,unicodedata
from collections import defaultdict, Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def save(path,obj):(ROOT/path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKC',s or '').casefold() if c.isalnum())
db=read('data/games.json')
tax=read('data/taxonomy.json')
source=read('data/project-title-year-candidates-20261031.json')
works=db['works']
index=defaultdict(set)
for w in works:
    for name in [w.get('originalTitle'),w.get('title'),w.get('chineseTitle'),*(w.get('titleAliases') or [])]:
        if name:index[norm(name)].add(w['id'])
counter=max(int(x['id'][1:]) for x in works)+1
added=[];reused=[];ambiguous=[];conflicts=[];duplicates=[]
seen=set()
for item in source['items']:
    name=item['originalTitle'];key=norm(name)
    assert key and key not in seen,('duplicate seed',name)
    seen.add(key)
    matches=set()
    for label in [name,item.get('title'),*(item.get('aliases') or [])]:
        if label:matches.update(index.get(norm(label),set()))
    if len(matches)>1:
        ambiguous.append({'title':name,'year':item['year'],'candidates':sorted(matches),'group':item['group']})
        continue
    if matches:
        wid=next(iter(matches));old=next(w for w in works if w['id']==wid)
        reused.append({'title':name,'year':item['year'],'workId':wid,'group':item['group']})
        if old['firstYear']!=item['year']:
            conflicts.append({'workId':wid,'title':name,'existingYear':old['firstYear'],'candidateYear':item['year'],'source':item['source']})
        continue
    assert 1976<=item['year']<=2026 and item['source'].startswith('https://')
    wid='g'+str(counter);counter+=1
    cid=wid+'-c-original';rid=wid+'-v-original'
    brand=item['group']
    company=tax['publisherAliases'].get(brand,brand)
    title=name
    notes=('2026-10-31 项目厂商作品清单简目：目前仅核实作品原名、首发年份与厂牌关联。'
           ' 首发平台暂按原PC版归档、发行主体和角色等尚待逐作复核；后续版本与独立新剧情不在本轮建立。')
    work={'id':wid,'title':title,'chineseTitle':'','originalTitle':name,
          'titleAliases':list(dict.fromkeys(item.get('aliases') or [])),
          'firstYear':item['year'],'category':item['category'],
          'subcategory':'恋爱剧情冒险','genre':'剧情ADV（故事题材尚未编目）',
          'characters':['人物尚未编目'],
          'synopsis':'仅登记作品名称与首发年份，尚未进行独立剧情及人物编目。',
          'notes':notes,'source':item['source'],
          'interactionModes':['待核实'],
          'interactionNote':'主要操作、分支和机种控制未核实；本批只建立名称与年份简目。',
          'interactionBasis':'既有资料归纳','interactionSources':[item['source']]}
    version={'id':cid,'workId':wid,'label':'原作／首批内容','firstYear':item['year'],
         'basis':'original','evidence':'以厂牌官方产品目录核定首发年份，原作具体内容差异另行考据。',
         'source':item['source'],'evidenceReleaseIds':[rid],'addedContent':[]}
    rel={'id':rid,'workId':wid,'year':item['year'],'platform':item['platform'],
         'publisher':brand,'publisherCompanies':[company],
         'kind':'原作／首次内容发行','voice':'未核实',
         'differences':'原作首发年份来自具名厂牌作品目录；发行署名、机种及实际发售版本详细内容仍需复核。',
         'source':item['source'],'contentVersionId':cid,'contentRelation':'original',
         'contentNote':'仅作名称及首发年份简目，未建立任何后发内容。',
         'releaseRole':'contentDebut'}
    works.append(work);db['contentVersions'].append(version);db['platformReleases'].append(rel)
    index[key].add(wid)
    added.append({'workId':wid,'title':name,'year':item['year'],'group':brand,'source':item['source']})
db['meta']['updated']='2026-10-31'
save('data/games.json',db)
result={'batch':source['batch'],'candidateCount':len(source['items']),'groupCounts':source['groupCounts'],
        'added':added,'reused':reused,'ambiguous':ambiguous,'yearConflicts':conflicts,
        'suppressedReissueCount':len(source['exclusions']),
        'editorialStatus':'仅作品名／首发年／关联品牌；四项叙事编目与主要角色和主创不构成已完成。',
        'note':'使用原始题名及别名做唯一身份检索；不改已入库作品，年份冲突进入人工审核。'}
save('data/project-title-year-import-result-20261031.json',result)
print(f'Title/year: candidates {len(source["items"])}, added {len(added)}, reused {len(reused)}, ambiguous {len(ambiguous)}, year conflicts {len(conflicts)}')
print('Added by group:',dict(Counter(x['group'] for x in added)))
