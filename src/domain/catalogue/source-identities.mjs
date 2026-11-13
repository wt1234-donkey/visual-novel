// Source records, work identities, explicit links and review cases are separate
// types. Names and dates produce candidates; they never establish identity.
import {workKey,nameKey} from './identity.mjs';
import {journalKey} from './journal.mjs';
const copy=value=>structuredClone(value),same=(a,b)=>journalKey(a)===journalKey(b);
const object=v=>v&&typeof v==='object'&&!Array.isArray(v);
const safe=v=>typeof v==='string'&&v.length>0&&v.length<=4096&&!['__proto__','constructor','prototype'].includes(v);
const fail=message=>{throw Error('来源身份：'+message);};
const names=w=>[w.title,w.originalTitle,w.chineseTitle,...(w.aliases||[]),...(w.titleAliases||[])].map(nameKey).filter(Boolean);
const unique=values=>[...new Set(values)];
const validSources=values=>Array.isArray(values)&&values.length>0&&values.length<=100&&values.every(v=>typeof v==='string'&&/^https?:\/\//.test(v));
export const emptyIdentityStore=()=>({schemaVersion:1,revision:0,links:{},cases:{},events:[]});
const state=s=>({revision:s.revision,links:copy(s.links),cases:copy(s.cases)});

export function validateIdentityStore(store){
 if(!store||store.schemaVersion!==1||!Number.isSafeInteger(store.revision)||store.revision<0||!object(store.links)||!object(store.cases)||!Array.isArray(store.events)||
  Object.keys(store).some(k=>!['schemaVersion','revision','links','cases','events'].includes(k)))fail('核对记录格式无效');
 const current={revision:0,links:{},cases:{}},seen=new Map();
 for(const event of store.events){
  if(event.schemaVersion!==1||!safe(event.id)||seen.has(event.id)||!safe(event.actor)||!Number.isFinite(Date.parse(event.at))||
   typeof event.reason!=='string'||event.reason.trim().length<5||event.reason.length>1000||!validSources(event.sources)||
   event.previousRevision!==current.revision||event.revision!==current.revision+1||!['resolve','undo'].includes(event.type)||event.intent?.type!==event.type||!Array.isArray(event.changes)||!event.changes.length)fail('事件身份、依据或顺序无效');
  if(event.type==='undo'){
   const target=seen.get(event.undoOf);
   if(!target||event.intent.targetId!==event.undoOf||!same(event.changes,target.changes.map(c=>({...c,before:c.after,after:c.before}))))fail('撤销目标或逆向修改不匹配');
  }
  if(event.type==='resolve'){
   const action=event.intent,caseChanges=event.changes.filter(c=>c.table==='cases');
   if(!Array.isArray(action.links)||caseChanges.length!==1||caseChanges[0].id!==action.caseId||caseChanges[0].after?.outcome!==action.outcome||caseChanges[0].after?.operationId!==event.id)fail('案件结论与事件不匹配');
   const c=caseChanges[0].after;
   if(!Array.isArray(c.sourceIds)||!Array.isArray(c.candidateWorkIds)||c.sourceIds.some(id=>!safe(id))||c.candidateWorkIds.some(id=>!safe(id)))fail('案件依据范围无效');
   if(action.links.some(link=>!c.sourceIds.includes(link.sourceId)))fail('核对链接超出案件范围');
   if(['same-work','distinct'].includes(action.outcome)&&(!action.links.length||!same(action.links.map(link=>link.sourceId).sort(),c.sourceIds)))fail('案件结案范围不完整');
   if(action.outcome==='same-work'&&new Set(action.links.map(link=>link.workId)).size!==1||action.outcome==='distinct'&&new Set(action.links.map(link=>link.workId)).size!==action.links.length)fail('身份结论与对应关系不匹配');
   const expected=action.links.map(link=>({table:'links',id:link.sourceId,before:current.links[link.sourceId]||null,
    after:{workId:link.workId,status:'confirmed',operationId:event.id,...(action.outcome==='distinct'?{distinctFrom:c.candidateWorkIds.filter(id=>id!==link.workId).sort()}:{})}}));
   if(!same(event.changes.filter(change=>change.table==='links'),expected))fail('身份链接与显式核对命令不匹配');
   if(['defer','not-admitted'].includes(action.outcome)&&action.links.length)fail('案件结论不能隐式改变身份');
  }
  const touched=new Set();
  for(const c of event.changes){
   if(!['links','cases'].includes(c.table)||!safe(c.id)||touched.has(c.table+':'+c.id)||!Object.hasOwn(c,'before')||!Object.hasOwn(c,'after')||!same(current[c.table][c.id]||null,c.before))fail('事件前值不匹配');
   touched.add(c.table+':'+c.id);
   if(c.after===null)delete current[c.table][c.id];
   else {
    if(!object(c.after))fail('核对结果无效');
    if(c.table==='links'&&(!['confirmed'].includes(c.after.status)||!safe(c.after.workId)||!safe(c.after.operationId)))fail('身份链接结果无效');
    if(c.table==='cases'&&(!['link','same-work','distinct','defer','not-admitted'].includes(c.after.outcome)||!Array.isArray(c.after.sourceIds)))fail('案件结果无效');
    Object.defineProperty(current[c.table],c.id,{value:copy(c.after),enumerable:true,writable:true,configurable:true});
   }
  }
  current.revision=event.revision;seen.set(event.id,event);
 }
 if(!same(current,state(store)))fail('事件回放与当前核对状态不一致');
 return store;
}

export function buildSourceIdentityCatalogue({registry,legacyRows=[],formalWorks=[],coverageWorks=[],decisions=emptyIdentityStore(),visible={}}){
 validateIdentityStore(decisions);
 const sources=new Map(),works=new Map(),links=new Map(),cases=new Map(),sourceCases=new Map();
 const addWork=(w,id,scope)=>{
  if(!safe(id))fail('作品身份缺失');
  const prior=works.get(id),labels=unique([...(prior?.labels||[]),w.title,w.originalTitle,w.chineseTitle,...(w.aliases||[]),...(w.titleAliases||[])].filter(Boolean));
  works.set(id,{id,title:w.displayTitle||w.title||prior?.title||id,firstYear:w.firstYear??w.year??prior?.firstYear??null,
   scopes:unique([...(prior?.scopes||[]),scope]),labels,sourceIds:[],profileIds:prior?.profileIds||[],status:'provisional'});
 };
 for(const row of registry.works)addWork(row,row.id,'registry-provisional');
 for(const row of legacyRows)addWork(row,workKey(row),'legacy-index');
 const originalByIndex=new Map(registry.works.filter(w=>w.indexId).map(w=>[w.indexId,w]));
 const knownIds=new Set([...works.keys(),...formalWorks.map(w=>w.id),...coverageWorks.map(w=>w.id)]);
 const formalByIndex=new Map(),profilesByIndex=new Map();
 for(const [rows,scope] of [[coverageWorks,'dossier'],[formalWorks,'formal']])for(const row of rows){
  const source=originalByIndex.get(row.basicRegistryId),decision=source&&decisions.links[source.id];
  if(decision&&!knownIds.has(decision.workId))fail('核对结果引用未知作品');
  const id=source?(decision?.status==='confirmed'?decision.workId:source.linkedRecordId||source.id):row.id;
  if(source){const previous=profilesByIndex.get(row.basicRegistryId);if(previous&&previous!==row.id)fail('同一来源已被多部正式作品声明');formalByIndex.set(row.basicRegistryId,id);profilesByIndex.set(row.basicRegistryId,row.id);}
  addWork(row,id,scope);works.get(id).profileIds=unique([...works.get(id).profileIds,row.id]);
 }
 const byIndex=new Map();
 for(const [ordinal,record] of registry.works.entries()){
  if(sources.has(record.id))fail('来源记录ID重复');
  const source={id:record.id,indexId:record.indexId||null,ordinal,record,scope:'registry',caseIds:[]};
  sources.set(record.id,source);if(record.indexId)byIndex.set(record.indexId,record.id);
  const explicit=formalByIndex.get(record.indexId)||record.linkedRecordId||(record.mainPlacement==='existing-complete'&&works.has(record.id)?record.id:null);
  const knownExplicit=explicit&&works.has(explicit);
  if(explicit&&!knownExplicit)addWork({title:explicit},explicit,'legacy-target-unresolved');
  const old={sourceId:record.id,workId:explicit||record.id,status:knownExplicit?'legacy-explicit':'unreviewed',basis:knownExplicit?'existing-explicit-id':explicit?'legacy-missing-target':'legacy-provisional-id'};
  const decision=decisions.links[record.id];
  if(decision&&decision.status==='confirmed'&&!works.has(decision.workId))fail('核对结果引用未知作品');
  links.set(record.id,decision?{...old,...copy(decision),sourceId:record.id,basis:'review-event'}:old);
 }
 for(const id of Object.keys(decisions.links))if(!sources.has(id))fail('核对结果引用未知来源');
 const groups=new Map(),workNames=new Map();
 for(const work of works.values())for(const name of unique(work.labels.map(nameKey).filter(Boolean))){const key=name+'|'+work.firstYear;if(!workNames.has(key))workNames.set(key,new Set());workNames.get(key).add(work.id);}
 for(const source of sources.values())for(const name of unique(names(source.record))){
  const key=name+'|'+(source.record.firstYear??null);let group=groups.get(key);if(!group){group={sourceIds:new Set(),workIds:new Set()};groups.set(key,group);}
  group.sourceIds.add(source.id);for(const id of workNames.get(key)||[])group.workIds.add(id);
 }
 const addCase=c=>{
  const decision=decisions.cases[c.id],membership=[...c.sourceIds].sort();
  const stale=decision&&(!same(decision.sourceIds,membership)||!same(decision.candidateWorkIds||[],[...c.candidateWorkIds].sort()));
  c.status=stale?'needs-recheck':decision?['same-work','distinct','not-admitted'].includes(decision.outcome)?'resolved':decision.outcome==='defer'?'deferred':'in-progress':'open';
  c.decision=decision?copy(decision):null;cases.set(c.id,c);
  for(const id of c.sourceIds){if(!sourceCases.has(id))sourceCases.set(id,[]);sourceCases.get(id).push(c.id);}
 };
 for(const [key,group] of groups)if(group.workIds.size>1){
  const sourceIds=[...group.sourceIds];addCase({id:'name-year:'+key,kind:'name-year-candidate',label:sources.get(sourceIds[0]).record.title,
   sourceIds,candidateWorkIds:[...group.workIds],basis:'名称/别名与登记年份相同，仅为候选；不自动合并'});
 }
 for(const [n,old] of (registry.identityReview||[]).entries()){
  const sourceId=sources.has(old.id)?old.id:byIndex.get(old.indexId);addCase({id:'legacy-review:'+(old.indexId||old.id||n),kind:'legacy-review',
   label:old.title||old.id||'历史待核',sourceIds:sourceId?[sourceId]:[],candidateWorkIds:sourceId?[links.get(sourceId).workId].filter(Boolean):[],basis:old.reason||'历史待核',legacyEvidence:copy(old)});
 }
 for(const [id,decision] of Object.entries(decisions.cases))if(!cases.has(id)){
  if(id.startsWith('source:')){
   const sourceId=id.slice(7);if(!sources.has(sourceId))fail('核对案件引用未知来源');
   addCase({id,kind:'source-review',label:sources.get(sourceId).record.title,sourceIds:[sourceId],candidateWorkIds:[sourceId],basis:'单条来源的显式身份核对'});
  }else{
   if(decision.sourceIds.some(sourceId=>!sources.has(sourceId))||decision.candidateWorkIds.some(workId=>!works.has(workId)))fail('历史核对引用的身份丢失');
   addCase({id,kind:decision.kind||'historical-resolution',label:decision.label||id,sourceIds:decision.sourceIds,candidateWorkIds:decision.candidateWorkIds,basis:decision.basis||'保留的既有身份核对；当前候选标签已变化'});
  }
 }
 for(const source of sources.values()){source.caseIds=sourceCases.get(source.id)||[];const link=links.get(source.id);if(link.workId)works.get(link.workId).sourceIds.push(source.id);}
 const resolved=new Set(),reviewed=new Set();let inherited=0,confirmed=0;
 for(const link of links.values())if(['legacy-explicit','confirmed'].includes(link.status)){resolved.add(link.workId);if(link.status==='legacy-explicit')inherited++;else{confirmed++;reviewed.add(link.workId);}}
 for(const w of works.values())w.status=reviewed.has(w.id)?'reviewed':resolved.has(w.id)?'legacy-confirmed':w.scopes.some(s=>['formal','dossier'].includes(s))?'catalogued':'provisional';
 const pending=[...cases.values()].filter(c=>c.status!=='resolved');
 const stats={sourceRecordCount:sources.size,workIdentityCount:works.size,resolvedWorkCount:resolved.size,reviewedWorkCount:reviewed.size,
  inheritedLinkedSources:inherited,reviewedLinkedSources:confirmed,unreviewedSources:sources.size-inherited-confirmed,
  pendingCases:pending.length,totalCases:cases.size,sourceRecordsInPendingCases:new Set(pending.flatMap(c=>c.sourceIds)).size,
  formalProfiles:formalWorks.length,legacyOnlyIndexIdentities:[...works.values()].filter(w=>w.scopes.includes('legacy-index')&&!w.scopes.includes('registry-provisional')).length,
  ...visible};
 return {schemaVersion:1,revision:decisions.revision,sources,works,links,cases,stats};
}

export function identityCase(catalogue,id){
 if(catalogue.cases.has(id))return catalogue.cases.get(id);
 if(id.startsWith('source:')&&catalogue.sources.has(id.slice(7))){const source=catalogue.sources.get(id.slice(7));return {id,kind:'source-review',label:source.record.title,sourceIds:[source.id],candidateWorkIds:[source.id]};}
 fail('待核案件不存在');
}

export function applyIdentityReview(store,catalogue,action,meta){
 validateIdentityStore(store);
 const old=store.events.find(e=>e.id===meta.id);
 if(old){if(!same(old.intent,action)||old.actor!==meta.actor||old.reason!==meta.reason.trim()||!same(old.sources,meta.sources))fail('操作ID用于不同核对');return copy(store);}
 if(meta.expectedRevision!==store.revision)fail('核对修订已变化，请重新读取');
 if(!safe(meta.id)||!safe(meta.actor)||!Number.isFinite(Date.parse(meta.at))||typeof meta.reason!=='string'||meta.reason.trim().length<5||!validSources(meta.sources))fail('身份核对须填写操作人、说明与来源');
 const changes=[];const change=(table,id,after)=>{const before=store[table][id]||null;if(!same(before,after))changes.push({table,id,before:copy(before),after:copy(after)});};
 if(action.type==='undo'){
  const target=store.events.find(e=>e.id===action.targetId);if(!target)fail('撤销目标不存在');
  for(const c of target.changes){if(!same(store[c.table][c.id]||null,c.after))fail('该身份在此后已有核对，不能覆盖后续修改');change(c.table,c.id,c.before);}
 }else if(action.type==='resolve'){
  const c=identityCase(catalogue,action.caseId),members=[...c.sourceIds].sort(),items=action.links;
  if(!Array.isArray(items)||items.length>500||new Set(items.map(l=>l.sourceId)).size!==items.length||!['link','same-work','distinct','defer','not-admitted'].includes(action.outcome))fail('案件结论或链接范围无效');
  if(['defer','not-admitted'].includes(action.outcome)){if(items.length)fail('暂缓或不准入不能改写身份链接');}
  else{
   if(!items.length||items.some(l=>!members.includes(l.sourceId)||!catalogue.works.has(l.workId)||catalogue.works.get(l.workId).scopes.every(scope=>scope==='legacy-target-unresolved')))fail('来源或目标作品不在核对范围');
   if(['same-work','distinct'].includes(action.outcome)&&!same(items.map(l=>l.sourceId).sort(),members))fail('结案须明确核对全部来源');
   if(action.outcome==='same-work'&&new Set(items.map(l=>l.workId)).size!==1)fail('同一作品结论须引用同一身份');
   if(action.outcome==='distinct'&&new Set(items.map(l=>l.workId)).size!==items.length)fail('独立作品结论不能重复目标身份');
   for(const link of items)change('links',link.sourceId,{workId:link.workId,status:'confirmed',operationId:meta.id,...(action.outcome==='distinct'?{distinctFrom:c.candidateWorkIds.filter(id=>id!==link.workId).sort()}:{})});
  }
  change('cases',c.id,{outcome:action.outcome,sourceIds:members,candidateWorkIds:[...c.candidateWorkIds].sort(),label:c.label,kind:c.kind,basis:c.basis||'显式身份核对',operationId:meta.id});
 }else fail('不支持的核对操作');
 if(!changes.length)fail('没有实际身份核对变化');
 const next=copy(store),event={schemaVersion:1,id:meta.id,actor:meta.actor,at:meta.at,reason:meta.reason.trim(),sources:copy(meta.sources),
  previousRevision:store.revision,revision:store.revision+1,type:action.type,intent:copy(action),changes,...(action.type==='undo'?{undoOf:action.targetId}:{})};
 for(const c of changes){if(c.after===null)delete next[c.table][c.id];else Object.defineProperty(next[c.table],c.id,{value:copy(c.after),enumerable:true,writable:true,configurable:true});}
 next.revision++;next.events.push(event);return validateIdentityStore(next);
}

export function identityFormalLinks(catalogue){
 return Object.fromEntries([...catalogue.links.values()].filter(l=>l.workId&&['legacy-explicit','confirmed'].includes(l.status)&&catalogue.works.get(l.workId)?.profileIds.length).map(l=>[l.sourceId,catalogue.works.get(l.workId).profileIds[0]]));
}
export function identityHistory(store,{before=Infinity,limit=20}={}){
 validateIdentityStore(store);if(!Number.isSafeInteger(limit)||limit<1||limit>100)fail('历史分页无效');
 const events=store.events.filter(e=>e.revision<before),page=events.slice(-limit).reverse();return {events:copy(page),nextBefore:events.length>limit?page.at(-1).revision:null,total:store.events.length};
}
