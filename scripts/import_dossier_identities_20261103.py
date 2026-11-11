#!/usr/bin/env python3
"""Register identities explicitly present in dossier work lists; hold uncertain matches."""
from registry_store import read_json as read_registry_json, write_json as write_registry_json, write_text as write_registry_text
import json,re,unicodedata,hashlib,collections,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def load(n):return read_registry_json(R/n)
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKC',str(s or '')).casefold() if c.isalnum())
def names(w):
 vals=[w.get('title'),w.get('originalTitle'),w.get('chineseTitle'),*(w.get('titleAliases') or []),*(w.get('aliases') or [])];out=[]
 for v in vals:
  if isinstance(v,str):
   for t in [v,*re.split(r'\s+/\s+|／',v),re.split(r'[:：]|\s+[–—-]\s+',v,maxsplit=1)[0]]:
    t=t.strip()
    if len(norm(t))>=3 and t not in out:out.append(t)
 return out
POS=re.compile(r'RPG|角色扮演|视觉小说|Galgame|ADV|叙事|剧情|文字冒险|图文冒险|互动动画|互动电影|推理冒险',re.I)
NEG=re.compile(r'麻将|桌面|棋牌|体育|赛车|射击|卡牌|益智|动作／休闲|非游戏',re.I)
ED=re.compile(r'(?i)\bcollection\b|\bbundle\b|\bremaster\b|\bdemo\b|\btrial\b|コレクション|体験版|完全版|リメイク|復刻|増刊|サントラ')
reg=load('data/main-adv-rpg-works-20261031.json'); assert not any(b['id']=='dossier-identity-link-20261103' for b in reg['batches']), 'Already applied'; main=load('data/games.json'); companies=load('data/company-coverage.json')['companies']; mainmap={w['id']:w for w in main['works']}; objs={}; raw=collections.Counter()
for c in companies:
 for wid in c.get('workIds',[]):
  raw['workIds']+=1
  if wid not in mainmap:continue
  q=objs.setdefault(wid,{'work':mainmap[wid],'places':set(),'companies':set()});q['places'].add('main');q['companies'].add(c['name'])
 for field in ('relatedGames','dossierOnlyWorks'):
  for w in c.get(field,[]):
   raw[field]+=1;q=objs.setdefault(w['id'],{'work':w,'places':set(),'companies':set()});q['places'].add(field);q['companies'].add(c['name'])
idx=collections.defaultdict(set); indexed={x['id']:x for x in reg['works']}; links=collections.defaultdict(set)
for w in reg['works']:
 for n in names(w):idx[norm(n)].add(w['id'])
 if w.get('linkedRecordId'):links[w['linkedRecordId']].add(w['id'])
suppidx=collections.defaultdict(set)
for item in load('data/non-rpg-creator-supplement-20261030.json')['works']:
 for name in names(item):suppidx[norm(name)].add(item['id'])
seenindex={x['indexId'] for x in reg['works']}; before=len(reg['works']); added=[]; held=[]; existing=[]
for wid,q in sorted(objs.items(),key=lambda x:(x[1]['work'].get('firstYear') or 9999,x[0])):
 w=q['work'];ns=names(w);year=w.get('firstYear');cats=' '.join(str(w.get(k) or '') for k in ('category','subcategory','genre'))
 hits=set(links[wid]);hits.update([wid] if wid in indexed else []);
 for n in ns:
  hits.update(idx[norm(n)])
  hits.update(x for x in suppidx[norm(n)] if x != wid)
 row={'workId':wid,'title':w.get('title'),'originalTitle':w.get('originalTitle'),'year':year,'category':w.get('category'),'source':w.get('source'),'dossiers':sorted(q['companies']),'matches':sorted(hits)}
 if hits:
  row['status']='已有同ID或名称候选，待核关联' if not (wid in indexed or links[wid]) else '已有ID关联';existing.append(row);continue
 if not isinstance(year,int) or not 1970<=year<=2026: row['status']='年份待核'
 elif not isinstance(w.get('source'),str) or not w['source'].startswith('https://'):row['status']='来源待核'
 elif not ns:row['status']='名称待核'
 elif NEG.search(str(w.get('category',''))):row['status']='范围待核'
 elif not POS.search(cats):row['status']='叙事与玩法待核'
 elif ED.search(' '.join(ns)):row['status']='版本合集待核'
 else:
  # Preserve known dossier identity and avoid creating a second identity.
  title=w.get('originalTitle') or w.get('title'); aliases=[n for n in names(w) if norm(n)!=norm(title)]
  place='existing-complete' if 'main' in q['places'] else 'promoted-dossier'
  work={'id':wid,'indexId':'basic-dossier-'+hashlib.sha256(wid.encode()).hexdigest()[:16], 'title':title,'aliases':aliases,'firstYear':year,'gameplay':('RPG' if re.search(r'RPG|角色扮演', cats,re.I) else '互动电影ADV' if re.search(r'互动动画|互动电影',cats) else '视觉小说' if re.search(r'视觉小说|Galgame',cats,re.I) else 'ADV'), 'gameplayNote':w.get('category') or '玩法待核','group':' / '.join(sorted(q['companies'])),'source':w['source'],'mainPlacement':place,'linkedRecordId':wid,'creditScope':'专题关联，不推断制作、发行或个人职责。','yearBasis':'沿用年鉴既有作品原作年和来源；具体平台、原作首发及版本关系仍以原记录证据为准。','editorialScope':'链接年鉴既有作品身份；未新增作品内容版本或创作职责。','batch':'dossier-identity-link-20261103'}
  if work['indexId'] in seenindex:raise ValueError('duplicate index ID')
  added.append(work);indexed[wid]=work;seenindex.add(work['indexId']);
  for n in names(work):idx[norm(n)].add(wid)
  row['status']='写入基础层并关联专题身份';row['placement']=place
 if row['status']=='写入基础层并关联专题身份':continue
 held.append(row)
reg['works'].extend(added);nmain=sum(x['mainPlacement']=='existing-complete' for x in added);ndoc=len(added)-nmain
reg['summary']['candidates']+=len(added);reg['summary']['accepted']+=len(added);reg['summary']['existingComplete']+=nmain;reg['summary']['promotedDossier']+=ndoc;reg['summary']['addedToMainIdentityLayer']+=ndoc
reg['batches'].append({'id':'dossier-identity-link-20261103','source':'data/company-coverage.json, data/games.json','review':'data/dossier-basic-identity-audit-20261103.json','summary':{'candidates':len(added),'sourceWorkIds':len(objs),'existing-complete':nmain,'promoted-dossier':ndoc,'name-or-id-hits':len(existing),'held':len(held)}})
assert len({w['id'] for w in reg['works']})==len(reg['works']);assert len({w['indexId'] for w in reg['works']})==len(reg['works']);assert reg['summary']['accepted']==len(reg['works'])
audit={'schema':1,'baseCommit':'5c30913de8b656a7d534d54d731e08a4c5d52594','source':'data/company-coverage.json + data/games.json','scope':'专题明确作品列表；entries目录项目未自动视作作品。名称命中为待核候选，未自动合并。','rawReferences':dict(raw),'summary':{'uniqueDossierIds':len(objs),'before':before,'newIdentityLinks':len(added),'existingComplete':nmain,'promotedDossier':ndoc,'nameOrIdHits':len(existing),'held':len(held),'after':len(reg['works'])},'added':[{'id':x['id'],'title':x['title'],'year':x['firstYear'],'source':x['source'],'placement':x['mainPlacement']} for x in added],'matchedOrHeld':existing+held}
for path,obj in [('data/main-adv-rpg-works-20261031.json',reg),('data/dossier-basic-identity-audit-20261103.json',audit)]: write_registry_text(R/path, json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(audit['summary'],ensure_ascii=False));print(collections.Counter(x['status'] for x in held))
