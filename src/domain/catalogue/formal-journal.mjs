import {journalKey} from './journal.mjs';
import {formalFieldMeta,EDIT_FIELDS,CREATOR_NAME_FIELDS} from './effective.mjs';

const copy=value=>structuredClone(value);
const same=(a,b)=>journalKey(a)===journalKey(b);
const object=value=>value&&typeof value==='object'&&!Array.isArray(value);
const safeId=value=>typeof value==='string'&&value.trim()&&value.length<=500&&!['__proto__','constructor','prototype'].includes(value);
const fail=message=>{throw Error('正式审计日志：'+message);};
export const formalState=store=>({schemaVersion:1,records:copy(store.records)});

// Legacy snapshots are evidence of a checkpoint, never invented older events.
export function upgradeFormalHistory(store,{at,sourceCommit=null}={}){
 if(store?.schemaVersion===2)return copy(store);
 if(store?.schemaVersion!==1||!object(store.records))fail('迁移起点无效');
 if(!Number.isFinite(Date.parse(at)))fail('缺少迁移起点时间');
 return {...formalState(store),schemaVersion:2,journal:{schemaVersion:1,
  checkpoint:{at,sourceCommit,coverage:'checkpoint-forward'},baseline:formalState(store),events:[]}};
}

export function formalOperation(store,id){return store.journal?.events.find(event=>event.id===id)||null;}
export function confirmFormalOperation(store,workId,meta,commandType,intent){
 const event=formalOperation(store,meta.id);if(!event)return false;
 const expected={workId,at:meta.at,actor:meta.actor,reason:meta.reason.trim(),sources:meta.sources,
  previousRevision:meta.expectedRevision,commandType,intent};
 if(!same(Object.fromEntries(Object.keys(expected).map(key=>[key,event[key]])),expected))
  throw Object.assign(Error('操作ID已经用于不同正式修改'),{code:'OPERATION_CONFLICT'});
 return true;
}

export function appendFormalEvent(before,after,workId,meta,commandType,intent,values){
 if(!safeId(meta.id)||!safeId(meta.actor)||!Number.isFinite(Date.parse(meta.at))||
  typeof meta.reason!=='string'||meta.reason.trim().length<5||meta.reason.length>1000||!Array.isArray(meta.sources))fail('缺少操作身份、时间或说明');
 if(formalOperation(before,meta.id)||Object.values(before.journal.baseline.records).some(row=>row.recent.some(event=>event.id===meta.id)))fail('操作ID重复');
 const event={schemaVersion:1,id:meta.id,sequence:before.journal.events.length+1,workId,commandType,
  previousRevision:before.records[workId]?.revision||0,revision:after.records[workId].revision,
  at:meta.at,actor:meta.actor,reason:meta.reason.trim(),sources:copy(meta.sources),intent:copy(intent),
  before:copy(before.records[workId]||null),after:copy(after.records[workId]),values:copy(values),
  ...(commandType==='undo'?{undoOf:intent.targetId}:{})};
 after.journal.events.push(event);return after;
}

export function replayFormalJournal(journal,validateState=()=>{}){
 if(!journal||journal.schemaVersion!==1||journal.baseline?.schemaVersion!==1||!object(journal.baseline.records)||
  !Array.isArray(journal.events)||journal.checkpoint?.coverage!=='checkpoint-forward'||
  !Number.isFinite(Date.parse(journal.checkpoint.at)))fail('检查点格式无效');
 const state=copy(journal.baseline),seen=new Set(Object.values(journal.baseline.records).flatMap(row=>row.recent.map(event=>event.id)));validateState(state);
 for(const [index,event] of journal.events.entries()){
  if(!event||event.schemaVersion!==1||!safeId(event.id)||seen.has(event.id)||!safeId(event.workId)||
   !safeId(event.actor)||!Number.isFinite(Date.parse(event.at))||typeof event.reason!=='string'||event.reason.trim().length<5||
   event.reason.length>1000||!Array.isArray(event.sources)||event.sources.some(url=>typeof url!=='string'||!/^https?:\/\//.test(url))||
   event.sequence!==index+1||!['edit','creators','undo'].includes(event.commandType)||event.intent?.type!==event.commandType||
   event.previousRevision!==(state.records[event.workId]?.revision||0)||event.revision!==event.previousRevision+1||
   !same(state.records[event.workId]||null,event.before)||event.after?.revision!==event.revision)fail('事件不连续或修改前值不匹配');
  seen.add(event.id);
  const previous=event.before||{revision:0,overrides:{},recent:[]};
  for(const side of ['before','after']){
   if(!object(event.values?.[side])||!same(Object.keys(event.values[side]).sort(),[...EDIT_FIELDS].sort()))fail('缺少完整字段前后值');
   const patch=side==='before'?previous.overrides:event.after.overrides;
   if(Object.entries(patch).some(([key,value])=>!same(value,event.values[side][key])))fail('字段前后值与更正层不匹配');
  }
  if(event.commandType==='undo'){
   const slot=previous.recent.findIndex(entry=>entry.id===event.undoOf);
   if(slot<0||event.intent.targetId!==event.undoOf)fail('撤销目标不存在');
   const target=previous.recent[slot],recent=previous.recent.slice(0,slot);
   const expected={revision:event.revision,overrides:copy(target.before),
    fieldMeta:copy(target.beforeFieldMeta||formalFieldMeta({overrides:target.before,recent})),recent:copy(recent)};
   if(!same(expected,event.after))fail('撤销结果或目标不匹配');
  }else{
   if(event.commandType==='edit'&&!same(event.intent.values,event.values.after))fail('修改命令与字段值不匹配');
   if(event.commandType==='creators'&&(!same(event.intent.names,Object.fromEntries(Object.keys(CREATOR_NAME_FIELDS).map(key=>[key,event.values.after[key]])))||
    EDIT_FIELDS.some(key=>!(key in CREATOR_NAME_FIELDS)&&!same(event.values.before[key],event.values.after[key]))))fail('姓名命令混入其他修改');
   const entry={id:event.id,revision:event.revision,at:event.at,actor:event.actor,reason:event.reason,
    sources:event.sources,before:previous.overrides,after:event.after.overrides,beforeFieldMeta:formalFieldMeta(previous)};
   if(!same(event.after.recent,[...previous.recent,entry].slice(-3)))fail('修改快照与追加事件不匹配');
   const metadata=formalFieldMeta(previous);let changed=false;
   for(const field of EDIT_FIELDS){
    if(!Object.hasOwn(event.after.overrides,field))delete metadata[field];
    else if(!same(event.values.before[field],event.values.after[field]))metadata[field]={id:event.id,at:event.at};
    if(!same(event.values.before[field],event.values.after[field]))changed=true;
   }
   if(!changed||!same(event.after.fieldMeta,metadata))fail('字段更正时间或操作身份与事件不匹配');
   if(!event.sources.length&&event.commandType!=='creators'){
    const changed=new Set([...Object.keys(previous.overrides),...Object.keys(event.after.overrides)].filter(k=>!same(previous.overrides[k],event.after.overrides[k])));
    if(!changed.size||[...changed].some(k=>!['writerNames','artistNames','musicianNames'].includes(k)))fail('非姓名修改缺少来源');
   }
  }
  Object.defineProperty(state.records,event.workId,{value:copy(event.after),writable:true,configurable:true,enumerable:true});
  validateState(state);
 }
 return state;
}

export function validateFormalJournal(store,validateState){
 const replayed=replayFormalJournal(store.journal,validateState);
 if(!same(replayed,formalState(store)))fail('日志回放与当前状态不一致');
 return replayed;
}

export function formalHistoryPage(store,{workId,before=Infinity,limit=20}={}){
 if(!Number.isSafeInteger(limit)||limit<1||limit>100||!(before===Infinity||Number.isSafeInteger(before)&&before>0))fail('分页范围无效');
 const events=(store.journal?.events||[]).filter(event=>(!workId||event.workId===workId)&&event.sequence<before);
 const page=events.slice(-limit).reverse();
 return {events:copy(page),nextBefore:events.length>limit?page.at(-1).sequence:null,total:(store.journal?.events||[]).filter(event=>!workId||event.workId===workId).length,
  checkpoint:copy(store.journal?.checkpoint||null),baselineRevision:store.journal?.baseline.records[workId]?.revision||0,
  legacyRecent:copy((store.journal?.baseline||store).records[workId]?.recent||[])};
}
