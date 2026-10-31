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
if registry.get('nextBatch',{}).get('source')=='data/adv-rpg-next-studio-candidates-20261031.json':
    previous=ROOT/'data/adv-rpg-next-studio-review-20261031.json'
    assert previous.is_file() and len(load('data/adv-rpg-next-studio-review-20261031.json')['records'])==59
    print('Next batch already present; preserving existing canonical references and review classifications.')
    raise SystemExit(0)
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
report=[
'# 下一批叙事驱动 ADV／RPG 作品：11组厂商59部候选审核（2026-10-31）',
'',
'这是统一主库的基础作品身份层，独立于强制填写角色、版本和发行档案的\u0060data/games.json\u0060。所有记录保存首发年、玩法与来源。厂商组只表示本次清单检索关联；不自动判断实际制作、发行职责。',
'',
'## 实际入库与去重统计',
'',
'| 处理结果 | 作品数 |',
'|---|---:|']
for k,label in [('promoted-basic','全新基础作品身份'),('linked-existing-registry','上批主库身份已关联'),('linked-existing-full-or-dossier','已有完整主库或厂商专题身份关联'),('identity-review','版本或身份待核')]:
    report.append('| '+label+' | '+str(status[k])+' |')
report+=['| **合计** | **59** |','','## 59部逐作品审查清单','','| 创作/历史清单组 | 作品 | 首发年 | 玩法 | 状态 | 证据来源 |','|---|---|---:|---|---|---|']
labels={'promoted-basic':'新收录','linked-existing-registry':'去重：主库已存在','linked-existing-full-or-dossier':'关联已有主库/专题','identity-review':'同名或年份冲突待核'}
for r in decisions:
    report.append('| '+r['group']+' | '+r['title'].replace('|','/')+' | '+str(r['year'])+' | '+r['gameplay']+' | '+labels[r['status']]+' | [厂商或作品资料]('+r['source']+') |')
report+=['','## 身份与版次风险记录','','- 互动电影游戏以最早章节发行年份收录，后续合集、跨平台移植不自动新建作品。',
'- inkle 的 Sorcery! 四部游戏分别含独立剧情内容，保存首次独立篇章发布年份；PC平台的合集和后发版另行核对。',
'- Freebird To the Moon 系列采用系列单独完整作品与叙事独立短篇的区分，2024 Beach Episode 属于单独发行的原创附篇，不把它误记作既有作品同内容移植。',
'- Grasshopper《The Silver Case》《Flower, Sun, and Rain》《The 25th Ward》以1999、2001、2005年原始版为准；2018合集和重制版不重新作为独立作品。',
'- Telltale《The Expanse》列入 Deck Nine 的制作关联，厂商页可能还有Telltale发行关联，需逐游戏核对正式署名。',
'- DON’T NOD 的《Banishers》和《Vampyr》属于故事和角色抉择占重要地位的RPG，但有动作战斗；本次保留其玩法性质而不将其误写成纯选项式ADV。',
'- 所有缺少具体发行平台、版次、作者署名或角色资料的候选，仍仅为作品基础记录，不填造完整档案。','','## 验证入口','','`python3 scripts/promote_next_narrative_studios_20261031.py` 重新构建统一身份层与59条审计；`python3 -m unittest discover -s tests -p "test_next_narrative_studio_main_20261031.py"` 检查去重完整性。']
(ROOT/'data/adv-rpg-next-studio-review-20261031.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
print('Screened next batch:',json.dumps(dict(status),ensure_ascii=False),'total primary works',len(registry['works']))
