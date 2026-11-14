from entity_credit_rules import apply_credit_rules
from historical_rules import load_historical_rules, reference_path, resolve_evidence
"""Build additive entity/credit/classification indexes without rewriting historical records."""
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from entity_names import apply_names, NAMES as DISPLAY_NAMES, display_name
from round28_corrections import corrected_coverage, review as round28_review
from jhv_content_review import historical_record

ROOT = Path(__file__).resolve().parents[1]
RULES = load_historical_rules(ROOT)
BASE, DATE = RULES['constants']['BASE'], RULES['constants']['DATE']
TYPE_LABELS, ROLE_LABELS, BRANDS, HISTORIES, NAMES, EXTRAS, SUBBRANDS = [RULES['constants'][key] for key in ['TYPE_LABELS','ROLE_LABELS','BRANDS','HISTORIES','NAMES','EXTRAS','SUBBRANDS']]

def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
def canonical(x): return re.sub(r'\s+','',x.replace('’',"'").casefold())
def digest(x): return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def render_json(d): return json.dumps(d,ensure_ascii=False,indent=2)+'\n'

def build():
 d=read('data/games.json'); coverage=corrected_coverage(read('data/company-coverage.json')); taxonomy=read('data/taxonomy.json'); companies={c['id']:c for c in coverage['companies']}
 review_batches = [read(reference_path(RULES, key)) for key in RULES['sequences']['entityReviews']]








 identity_reviews={x['entityId']:x for batch in review_batches for x in batch['identityCorrections']}
 assert len(identity_reviews)==sum(len(batch['identityCorrections']) for batch in review_batches),'重复的主体订正'
 entities={}; aliases={}; dossiers=[]; relations=[]; credits=[]; memberships=[]; reviews=[]; placements=[]; names_review=[]; conflicts=[]
 def add_entity(eid,name,kind,names,source,basis='existingDossier',note=''):
  eid='entity-'+eid
  if eid not in entities:entities[eid]={'id':eid,'name':name,'type':kind,'aliases':list(dict.fromkeys([name,*names])),'sources':[source],'verification':basis,'historyNote':note,'dates':[]}
  for n in [name,*names]:aliases[canonical(n)]=eid
  return eid
 for cid,c in companies.items():
  eid = RULES['dossiers']['entityKeys'].get(cid,cid)
  kind = 'brand' if cid in BRANDS else RULES['dossiers']['types'].get(cid,'company')
  name = RULES['dossiers']['names'].get(cid,c['name'])
  # Leland already has a reviewed stable ID from its historical release name.
  # A new dossier must attach to that identity instead of manufacturing entity-leland.
  ident = RULES['dossiers']['stableIdentities'].get(cid) or add_entity(eid,name,kind,NAMES.get(cid,[]),c['source'],note=c['publisherNote'])
  dossiers.append({'id':cid,'name':c['name'],'dossierType':'history' if cid in HISTORIES else kind,'entityIds':[ident],'scope':c['scope'],'sources':[c['source']],'firstYearBasis':'关联主库作品最早原作首发年','firstYear':min((w['firstYear'] for w in d['works'] if w['id'] in c['workIds']),default=None)})
 # Independently reviewed existing dossier identities are checked before release resolution.
 for reviewed in identity_reviews.values():
  if not reviewed.get('applyToExistingDossier'):continue
  entity=entities[reviewed['entityId']]
  assert entity['name']==reviewed['rawName'] and reviewed['status']=='sourceReviewed'
  assert all(entity[key]==value for key,value in reviewed['before'].items()),'专题主体旧值与独立订正记录不符'
  assert reviewed['type']=='company' and reviewed['sources'] and reviewed['note']
  entity.update(type=reviewed['type'],verification=reviewed['status'],historyNote=reviewed['note'])
  entity['sources']=list(dict.fromkeys([*entity['sources'],*reviewed['sources']]))
 for eid,name,kind,names,source in EXTRAS:add_entity(eid,name,kind,names,source,'sourceReviewed')
 banpresto_additions=read('data/banpresto-source-review-20261029.json')
 game_label = add_entity(*RULES['supplementalEntities']['game_label'])
 next(x for x in dossiers if x['id']=='banpresto')['entityIds'].append(game_label)
 red_orb = add_entity(*RULES['supplementalEntities']['red_orb'])
 next(x for x in dossiers if x['id']=='broderbund')['entityIds'].append(red_orb)
 relations.append(resolve_evidence(RULES['supplementalRelations']['redOrb'], companies))
 # Publisher brand/company homographs remain distinct. Raw AQUAPLUS alone is a publishing-brand signature.
 for raw, target in RULES['publisherAliases'].items():aliases[canonical(raw)]=target
 for eid,name,parent,names in SUBBRANDS:
  add_entity(eid,name,'brand',names,companies[parent]['source'],note='历史品牌／子品牌署名独立保存；不等于法人公司。')
  if eid in RULES['subbrandRelations']:
   relations.append(resolve_evidence(RULES['subbrandRelations'][eid],companies))
  else:
   relations.append({'from':'entity-'+eid,'to':'entity-'+parent,'type':'brandFamily','period':{'from':None,'to':None,'precision':'unknown'},'status':'existingDossier','source':companies[parent]['source'],'note':'既有专题的品牌家族关系，未知时段不外推为历年经营归属。'})
 def relation(child,parent,source,note,status='sourceReviewed',start=None):
  relations.append({'from':'entity-'+child,'to':'entity-'+parent,'type':'operatedBy','period':{'from':start,'to':None,'precision':'year' if start else 'unknown','openEnd':'notAsserted'},'status':status,'source':source,'note':note})
 for fact in RULES['operatedBy']:
  relation(*resolve_evidence(fact['args'], companies), **fact['options'])

















 # Preserve source-level alias distinctions; only use old aliases where they do not collapse a declared child brand.
 def resolve(raw,source):
  key=canonical(raw)
  if key in aliases:return aliases[key]
  previous=taxonomy['publisherAliases'].get(raw)
  if previous and canonical(previous) in aliases:
   target=aliases[canonical(previous)]; aliases[key]=target
   if raw not in entities[target]['aliases']:entities[target]['aliases'].append(raw)
   return target
  eid='entity-name-'+hashlib.sha256(raw.encode()).hexdigest()[:12]
  if eid not in entities:
   entities[eid]={'id':eid,'name':raw,'type':'unknown','aliases':[raw],'sources':[source],'verification':'unresolved','historyNote':'发行原文已保留；法人／品牌身份尚待核实。','dates':[]}
   reviewed=identity_reviews.get(eid)
   if reviewed:
    assert reviewed['status']=='sourceReviewed' and reviewed['rawName']==raw
    assert all(entities[eid][key]==value for key,value in reviewed['before'].items()),'主体旧值与独立订正记录不符'
    assert reviewed['type'] in {'company','team','brand','individual'} and reviewed['sources'] and reviewed['note']
    assert reviewed['type']!='brand' or reviewed.get('preserveReleaseRoles') is True,'身份核定不能自动改写旧发行职责'
    entities[eid].update(type=reviewed['type'],verification='sourceReviewed',historyNote=reviewed['note'])
    entities[eid]['sources']=list(dict.fromkeys([source,*reviewed['sources']]))
   else:
    names_review.append({'entityId':eid,'rawName':raw,'status':'pendingIdentity','source':source,'reason':'未以名称后缀推定法人或品牌；保留原发行署名。'})
  aliases[key]=eid;return eid
 def credit(eid,level,target,role,source,raw=None,status='existingCredit',note='',work_id=None):
  key=(eid,level,target,role)
  if key in credit_seen:return
  credit_seen.add(key)
  credits.append({'id':'credit-'+hashlib.sha256('|'.join(key).encode()).hexdigest()[:16],'entityId':eid,'targetType':level,'targetId':target,'workId':work_id or target,'role':role,'rawCredit':raw or entities[eid]['name'],'status':status,'source':source,'note':note,'territory':None})
 credit_seen=set(); allworks={w['id']:w for w in d['works']}; allreleases=list(d['platformReleases']); allcontents=list(d['contentVersions']); locations={w['id']:'main' for w in d['works']}
 for c in coverage['companies']:
  for field,loc in [('relatedGames','related'),('dossierOnlyWorks','bibliography')]:
   for w in c.get(field,[]):
    if w['id'] in allworks and digest(w)!=digest(allworks[w['id']]):conflicts.append({'id':w['id'],'dossierId':c['id'],'status':'pendingDuplicate'})
    allworks.setdefault(w['id'],w);locations.setdefault(w['id'],loc)
    if loc=='related':allreleases.extend(w['platformReleases']);allcontents.extend(w['contentVersions'])
 # Reviewed historical dossier identity cannot silently absorb a later same-name company.
 for reviewed in identity_reviews.values():
  if not reviewed.get('applyToExistingDossier'):continue
  scope=reviewed['historicalPublisherScope']
  scoped=[r for r in allreleases if r['publisher']==scope['rawPublisher']]
  expected=set(scope['releaseIds'])
  if reviewed['entityId']=='entity-banpresto':
   additions=banpresto_additions['historicalPublisherAdditions']
   actual={r['id']:r for r in scoped}
   assert len(additions)==len({a['release']['id'] for a in additions}),'万普追加审核ID重复'
   for addition in additions:
    r=addition['release']
    assert addition['entityId']=='entity-banpresto' and addition['source']==r['source'] and addition['reason']
    assert r['id'] not in expected and actual.get(r['id'])==r,'万普追加发行与独立审核记录不符'
    assert r['publisher']==scope['rawPublisher'] and r['year']<2008,'新主体不能倒填旧万普'
    expected.add(r['id'])
  assert {r['id'] for r in scoped}==expected and scoped,'历史发行范围与主体订正记录不符'
  assert all(r['year']<scope['beforeYear'] for r in scoped),'不能把同名后继发行倒填旧公司'
 # The publisher and the later game label are separately evidenced for this first batch only.
 for r in allreleases:
  if r['workId']=='banpresto-accel1':
   assert r['publisher']=='バンダイナムコゲームス' and r['year']==2012
   credit(game_label,'release',r['id'],'publishingBrand',
          'https://www.4gamer.net/games/154/G015459/20120517059/',
          raw='バンプレストレーベル',status='sourceReviewed',work_id=r['workId'],
          note='メーカー发文明确区分発売元与厂牌，仅限定2012首批，不追溯归旧万普公司。')
 # Explicit splitting rules preserve raw brands that the legacy corporate index previously flattened.
 def release_entities(r):
  scoped_resolution=next((x for x in banpresto_additions['scopedPublisherResolutions'] if x['releaseId']==r['id']),None)
  if scoped_resolution:
   assert r['publisher']==scoped_resolution['rawPublisher']=='バンダイナムコゲームス'
   assert scoped_resolution['entityId']==aliases[canonical('Bandai Namco Games')]=='entity-name-40ed6431d1a6'
   assert scoped_resolution['source'] and scoped_resolution['reason']
   return [scoped_resolution['entityId']]
  raw=r['publisher']; key=canonical(raw)
  if key in aliases:return [aliases[key]]
  if raw in taxonomy['nonCompanyCredits']:return []
  if raw in taxonomy['jointCredits']:return [resolve(n,r['source']) for n in taxonomy['jointCredits'][raw]]
  return [resolve(raw,r['source'])]
 for r in allreleases:
  eids=list(dict.fromkeys(release_entities(r)))
  for eid in eids:
   preserve_role=identity_reviews.get(eid,{}).get('preserveReleaseRoles',False)
   role='publishingBrand' if entities[eid]['type']=='brand' and not preserve_role else 'publisher'
   credit(eid,'release',r['id'],role,r['source'],r['publisher'],note='仅规范化此条历史发行署名；不据此推定开发职责。',work_id=r['workId'])
   if role=='publishingBrand' and r['year']==allworks[r['workId']]['firstYear'] and r['contentRelation']=='original':
    credit(eid,'work',r['workId'],'originalPublishingBrand',r['source'],r['publisher'],note='原作首发品牌署名；不等于该品牌独立完成全部程序、美术或剧本。')
 closure=round28_review(); edition=closure['scopedEdition']
 assert edition['workId']=='g089' and edition['id'] not in {r['id'] for r in allreleases}
 for record_id,release_id in [('identity-37','g209-v2'),('identity-36','g209-v3')]:
  item=next(r for r in closure['records'] if r['recordId']==record_id)
  source=item['sources'][1]['url']
  assert next(r for r in allreleases if r['id']==release_id)['workId']=='g209'
  credit('entity-nextninja','release',release_id,'serviceProvider',source,
         raw='株式会社NextNinja',status='sourceReviewed',work_id='g209',
         note='2016年对应移动应用页的提供方；平台名称与原始发行字段保持，不推定PC版或其他移动渠道的出版法人。')
  credits[-1].update(reviewId=record_id,reviewRecord=closure['audit'])
 credit('entity-sinclair','edition',edition['id'],'publisher',edition['source'],
        raw=edition['publisher'],status='sourceReviewed',work_id='g089',note=edition['note'])
 credits[-1].update(reviewId='duty-558',reviewRecord=closure['audit'])
 # Regional publication evidence does not create ordinary port releases or work copies.
 ultra_editions=read('data/ultra-scoped-editions-20261029.json')
 scoped_editions=[edition]
 assert len(ultra_editions['editions'])==len({e['id'] for e in ultra_editions['editions']})==6
 for reviewed in ultra_editions['editions']:
  assert reviewed['workId'] in allworks and reviewed['publisher']=='Ultra Games'
  assert reviewed['id'] not in {r['id'] for r in allreleases}
  assert reviewed['contentVersionId'] is None and reviewed['contentRelation']=='unverified'
  assert reviewed['platform'] in {'NES（北美）','Game Boy（北美）'}
  scoped_editions.append(reviewed)
  credit('entity-name-c87c2b9662fc','edition',reviewed['id'],'publisher',reviewed['source'],
         raw=reviewed['publisher'],status='sourceReviewed',work_id=reviewed['workId'],note=reviewed['note'])
  credits[-1].update(reviewId='ULTRA-20261029-'+reviewed['workId'],reviewRecord=ultra_editions['audit'])
 broderbund_editions=read('data/broderbund-scoped-editions-20261029.json')
 for reviewed in broderbund_editions['editions']:
  assert reviewed['workId']=='g1342' and reviewed['workId'] in allworks
  assert reviewed['publisher']=='Red Orb Entertainment' and reviewed['actualPublisher']=='Mindscape, Inc.'
  assert reviewed['year']==1999 and reviewed['contentVersionId'] is None and reviewed['contentRelation']=='unverified'
  assert reviewed['id'] not in {r['id'] for r in allreleases} and reviewed['id'] not in {e['id'] for e in scoped_editions}
  scoped_editions.append(reviewed)
  credit(red_orb,'edition',reviewed['id'],'publishingBrand',reviewed['source'],
         raw=reviewed['publisher'],status='sourceReviewed',work_id=reviewed['workId'],note=reviewed['note'])
  credits[-1].update(reviewId='BRODERBUND-20261029-RING-US',reviewRecord=broderbund_editions['audit'])
 apply_credit_rules(RULES,'initial',companies=companies,works=allworks,releases=allreleases,contents=allcontents,release_entities=release_entities,credit=credit,credits=credits)
 # Apply independently sourced contributions; later-content development never becomes original-work production.
 reviewed_memberships={}
 for reviewed,audit in [(x,batch['audit']) for batch in review_batches for x in batch['creditAdditions']]:
  eid=reviewed['entityId'];wid=reviewed['workId'];cid=reviewed['dossierId']
  assert reviewed['status']=='sourceReviewed' and eid in entities and wid in allworks
  level=reviewed['targetType'];target=wid if level=='work' else reviewed.get('targetId')
  if level=='work':
   assert reviewed['role'] in {'coDeveloper','originalProduction','supervisor','productionBrand'}
   before_roles=reviewed.get('beforeWorkRoles',[])
  elif level=='release':
   assert reviewed['role'] in {'developer','localizer'} and cid is None,'发行开发／本地化须独立限定发行ID，不能直接解除专题待核'
   release=next((r for r in allreleases if r['id']==target),None)
   assert release and release['workId']==wid,'发行职责追加必须命中同作品既有发行'
   before_roles=reviewed['beforeTargetRoles']
  else:
   assert level=='content' and reviewed['role']=='developer' and cid is None,'后发内容开发须独立限定内容ID，不能直接解除专题待核'
   content=next((cv for cv in allcontents if cv['id']==target),None)
   assert content and content['workId']==wid and content['basis']=='added','内容开发追加必须命中同作品既有增补内容'
   before_roles=reviewed['beforeTargetRoles']
  assert locations[wid]==reviewed['expectedPlacement']
  current_roles=sorted({x['role'] for x in credits if x['entityId']==eid and x['targetType']==level and x['targetId']==target})
  assert current_roles==before_roles,'目标职责旧值与独立追加记录不符'
  assert (eid,level,target,reviewed['role']) not in credit_seen,'已存在职责不能由追加记录覆盖'
  if cid:
   assert wid in [*companies[cid]['workIds'],*[w['id'] for field in ['relatedGames','dossierOnlyWorks'] for w in companies[cid].get(field,[])]]
   assert eid in next(d['entityIds'] for d in dossiers if d['id']==cid)
   assert not any(x['entityId']==eid and x['workId']==wid for x in credits),'专题解除待核须单独审核旧职责'
   assert reviewed['before']=={'roles':['catalogueAssociation'],'group':'unresolved','status':'pendingRole'}
   assert (cid,wid) not in reviewed_memberships
  credit(eid,level,target,reviewed['role'],reviewed['source'],raw=reviewed['rawCredit'],status='sourceReviewed',note=reviewed['note'],work_id=wid)
  credits[-1].update(reviewId=reviewed['reviewId'],reviewRecord=audit)
  if cid:reviewed_memberships[(cid,wid)]=reviewed
 assert set(identity_reviews)<=entities.keys(),'主体订正记录未命中既有身份'
 leland=entities['entity-name-547f933b0469']
 assert leland['type']=='company' and leland['verification']=='sourceReviewed'
 leland['historyNote']='原版Dragon’s Lair II传单具名The Leland Corporation，1991年街机发行沿用g045。1988年同期Play Meter报道：1987年Tradewest收购Cinematronics资产后，业务重组为The Leland Corporation；资产交易日不等同Leland法人成立日，旧公司作品、动画合作和开发职责也不由此转归Leland。详见data/leland-audit.md。'
 leland['sources']=list(dict.fromkeys([*leland['sources'],'https://elibrary.arcade-museum.com/magazines/pm/PlayMeter-1988-06/PlayMeter-1988-06-026.pdf']))
 if 'broderbund' in companies:
  broderbund=entities['entity-name-e0c32a99a906']
  assert broderbund['type']=='company' and broderbund['verification']=='sourceReviewed'
  broderbund['historyNote']=companies['broderbund']['publisherNote']
  broderbund['sources']=list(dict.fromkeys([*broderbund['sources'],companies['broderbund']['source']]))
  broderbund['aliases']=list(dict.fromkeys([*broderbund['aliases'],'Broderbund','Brøderbund Software']))
  broderbund['dates']=[{'kind':'established','value':'1980','precision':'year','source':companies['broderbund']['establishedSource'],'status':'sourceReviewed'}]
 apply_credit_rules(RULES,'chunsoft',companies=companies,works=allworks,releases=allreleases,contents=allcontents,release_entities=release_entities,credit=credit,credits=credits)
 # Source-scoped Chunsoft catalogue additions; no developer inference from publisher.
 for reviewed in read('data/chunsoft-scoped-credits-20261029.json')['credits']:
  assert reviewed['workId'] in allworks and locations[reviewed['workId']]=='related'
  credit('entity-name-21365baf366d','work',reviewed['workId'],reviewed['role'],reviewed['source'],status='sourceReviewed',note=reviewed['note'])
 # New Ultra memberships cite each game's evidence, not the dossier's Nightshade source.
 for row in read('data/ultra-source-review-20261029.json')['rows']:
  if row['decision'] not in {'addMain','addRelated'}:continue
  assert row['workId'] in allworks and row['source']
  reviewed_memberships[('ultra_games',row['workId'])]={'source':row['source']}
 # Dossier memberships are separate from production assertions. Every existing member remains present.
 bywork=defaultdict(list)
 for x in credits:bywork[x['workId']].append(x)
 if 'takeru' in companies:
  # TAKERU dossier reuses the already reviewed sales-service identity. No game creation is inferred.
  takeru=entities['entity-name-08cbddd5e450']
  assert takeru['type']=='brand' and takeru['verification']=='sourceReviewed'
  takeru['historyNote']=companies['takeru']['publisherNote']+' 既有冻结核查记录原文保留；本轮新增渠道专题与限定组织关系，见data/takeru-audit.md。'
  takeru['aliases']=list(dict.fromkeys([*takeru['aliases'],'ソフトベンダーTAKERU','武尊']))
  brother=add_entity('brother','Brother Industries','company',['Brother Industries','ブラザー工業株式会社'],'https://global.brother/ja/digest/history/takeru','sourceReviewed',note='TAKERU系统开发及服务主体；不由终端开发推定游戏开发。')
  relations.append({'from':takeru['id'],'to':brother,'type':'operatedBy','period':{'from':1986,'to':None,'precision':'year','openEnd':'notAsserted'},'status':'sourceReviewed','source':companies['takeru']['source'],'note':'1986年服务由Brother推出；关系只说明初始运营来源，不声称持续至今。1994年向XING移交的精确时间仍待同期原件，1997是服务结束而非Brother注销。'})
  takeru['dates']=[{'kind':'serviceStarted','value':'1986','precision':'year','source':companies['takeru']['source'],'status':'sourceReviewed'},{'kind':'serviceEnded','value':'1997','precision':'year','source':companies['takeru']['source'],'status':'sourceReviewed'}]
 dossier_lookup={x['id']:x for x in dossiers}
 for c in coverage['companies']:
  subject=set(dossier_lookup[c['id']]['entityIds'])
  for wid in [*c['workIds'],*[w['id'] for w in c.get('relatedGames',[])],*[w['id'] for w in c.get('dossierOnlyWorks',[])]]:
   roles=sorted({x['role'] for x in bywork[wid] if x['entityId'] in subject}) or ['catalogueAssociation']
   if 'originalProduction' in roles or 'productionBrand' in roles or 'developer' in roles:group='original'
   elif 'coDeveloper' in roles:group='cooperation'
   elif any(x in roles for x in ['publisher','publishingBrand','originalPublishingBrand','portDeveloper']):group='release'
   elif any(x in roles for x in ['licensor','supervisor','copyrightCredit']):group='licensed'
   else:group='unresolved'
   membership_source=reviewed_memberships.get((c['id'],wid),{}).get('source',c['source'])
   memberships.append({'dossierId':c['id'],'workId':wid,'placement':locations[wid],'roles':roles,'group':group,'source':membership_source,'status':'pendingRole' if group=='unresolved' else 'existingEvidence'})
 ascii_member=next(m for m in memberships if m['dossierId']=='ascii' and m['workId']=='ascii-anearth')
 assert ascii_member['roles']==['catalogueAssociation'] and ascii_member['status']=='pendingRole'
 ascii_member.update(roles=[],group='reference',status='sourceReviewedCorrection',source=closure['asciiCorrection']['source'])
 for wid,w in allworks.items():
  loc=locations[wid]
  record={'workId':wid,'placement':loc,'narrativeAssessment':'notReassessed','decision':'retainExistingPlacement','source':w['source'],'reason':'本轮为实体与关系迁移，沿用既有收录；不从类型标签或互动方式自动推定叙事主次。','interactionModes':w['interactionModes']}
  placements.append(record)
  if loc!='main':reviews.append({**record,'status':'needsNarrativeEvidence' if loc=='related' else 'existingScopeRestriction','nextStep':'逐作比较叙事与系统主次；仅有ADV／RPG或IP标签不足以转入主库。' if loc=='related' else '区分原有范围限制与资料不足；输入标签本身不触发自动增删。'})
 # Every alias is inventoried, including compatibility-only raw spellings not present in current releases.
 mapping=[]
 for raw in sorted({r['publisher'] for r in allreleases} | set(taxonomy['publisherAliases']) | set(taxonomy['jointCredits'])):
  candidates=[r for r in allreleases if r['publisher']==raw]
  if candidates:ids=release_entities(candidates[0])
  elif canonical(raw) in aliases:ids=[aliases[canonical(raw)]]
  elif raw in taxonomy['publisherAliases'] and canonical(taxonomy['publisherAliases'][raw]) in aliases:ids=[aliases[canonical(taxonomy['publisherAliases'][raw])]]
  else:ids=[]
  mapping.append({'rawName':raw,'entityIds':ids,'legacyCanonical':taxonomy['publisherAliases'].get(raw),'status':'mapped' if ids else 'pendingOrNoncommercial','source':candidates[0]['source'] if candidates else None})
 baseline={'baseCommit':BASE,'preservedFiles':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['data/games.json','data/company-coverage.json','data/taxonomy.json','data/gameplay-catalogues.json']},'counts':{'works':len(d['works']),'contentVersions':len(d['contentVersions']),'platformReleases':len(d['platformReleases']),'dossiers':len(companies)},'relatedRecordCount':sum(len(c.get('relatedGames',[])) for c in companies.values()),'bibliographyRecordCount':sum(len(c.get('dossierOnlyWorks',[])) for c in companies.values())}
 date_facts = resolve_evidence(RULES['entityDates'], companies)
 for eid,(kind,value,precision,src) in date_facts.items():entities[eid]['dates'].append({'kind':kind,'value':value,'precision':precision,'source':src,'status':'existingEvidence'})
 date_reviews=[fact for batch in review_batches for fact in batch.get('dateFacts',[])]
 assert len({fact['entityId'] for fact in date_reviews})==len(date_reviews),'重复的主体日期订正'
 for fact in date_reviews:
  entity=entities[fact['entityId']]
  assert entity['dates']==fact['before'] and fact['status']=='sourceReviewed','主体日期旧值与审查不符'
  assert fact['kind'] in {'established','brandActivityStarted'} and fact['precision'] in {'day','month','year'}
  assert fact['source'] and fact['note'] and fact['value']
  entity['dates'].append({key:fact[key] for key in ['kind','value','precision','source','status']})
  entity['sources']=list(dict.fromkeys([*entity['sources'],fact['source']]))
 # Appending releases must not silently erase evidence sources already preserved
 # in the published entity catalogue. Stable union makes a second build identical.
 previous_path=ROOT/'data/entities.json'
 if previous_path.exists():
  previous_entities={e['id']:e for e in read('data/entities.json')['entities']}
  for eid,entity in entities.items():
   prev=previous_entities.get(eid)
   if prev is not None:
    entity['sources']=list(dict.fromkeys([*prev.get('sources',[]),*entity.get('sources',[])]))
 apply_names(entities,dossiers)
 model={'schemaVersion':1,'updated':DATE,'typeLabels':TYPE_LABELS,'roleLabels':ROLE_LABELS,'entities':list(entities.values()),'relations':relations,'dossiers':dossiers,'displayNames':{raw:display_name(raw) for raw in DISPLAY_NAMES},'policy':'实体、参与角色、收录位置相互独立；不以当前品牌归属倒填历史署名。'}
 existing_baseline=ROOT/'data/entity-migration-baseline.json'
 if existing_baseline.exists():
  baseline=read('data/entity-migration-baseline.json')
  for field in ['works','contentVersions','platformReleases']:
   current={x['id']:digest(historical_record(field,x)) for x in d[field]}
   assert all(current.get(wid)==value for wid,value in baseline['objects'][field].items()),'既有记录变化需独立订正审核；不能重新生成覆盖基线'
 else:
  baseline['objects']={field:{x['id']:digest(x) for x in d[field]} for field in ['works','contentVersions','platformReleases']}
  baseline['originalDossiers']={cid:{'workIds':c['workIds'],'relatedIds':[w['id'] for w in c.get('relatedGames',[])],'bibliographyIds':[w['id'] for w in c.get('dossierOnlyWorks',[])]} for cid,c in companies.items()}

 return {'data/entities.json':model,'data/credits.json':{'schemaVersion':1,'updated':DATE,'credits':credits,'dossierMemberships':memberships,'scopedEditions':scoped_editions},'data/work-classification.json':{'schemaVersion':1,'updated':DATE,'placements':placements,'reviewQueue':reviews,'policy':'保留既有位置；未重新核定叙事主次，不自动转入主库。'},'data/entity-migration-review.json':{'updated':DATE,'nameMappings':mapping,'pendingIdentities':names_review,'pendingMembershipCount':sum(x['status']=='pendingRole' for x in memberships),'identityConflicts':conflicts,'aliasPolicy':'旧taxonomy别名仅作兼容归档；新实体索引保留子品牌，所有实体关系单独记录。'},'data/entity-migration-baseline.json':baseline}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 for path,value in build().items():
  output=render_json(value);target=ROOT/path
  if args.check:assert target.read_text()==output,f'{path} 未同步'
  else:target.write_text(output,encoding='utf-8')
  print(path)

if __name__=='__main__':main()
