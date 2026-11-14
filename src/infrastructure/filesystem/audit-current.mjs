import {createHash} from 'node:crypto';
import {fieldKey,fieldCounts} from '../../domain/catalogue/field-evidence.mjs';
import {auditEvents} from '../../domain/audit/events.mjs';
import {journalKey} from '../../domain/catalogue/journal.mjs';
import {setAuditMap,auditMapEntries} from './audit-indexes.mjs';
const hash=id=>createHash('sha256').update(id).digest('hex');
const revision=(kind,store)=>kind==='formal'?auditEvents(kind,store).length:store.revision;

function rowsFor(kind,store,put){
 if(kind==='formal')return {records:Object.fromEntries(Object.entries(store.records||{}).map(([id,record])=>[id,{record,baseline:store.journal?.baseline.records[id]||null}]))};
 if(kind==='identity')return {links:store.links,cases:store.cases};
 if(kind!=='field')return {};
 const groups={};
 for(const assertion of Object.values(store.assertions)){
  const key=fieldKey(assertion.scope,assertion.field);
  (groups[key]??={assertions:[],choice:store.choices[key]||null}).assertions.push(assertion);
 }
 for(const key of Object.keys(store.choices))groups[key]??={assertions:[],choice:store.choices[key]};
 return {groups:Object.fromEntries(Object.entries(groups).map(([key,group])=>{
  // A current-value group is paged independently from event history. Hash
  // buckets confine insertion/removal shifts to a small part of a large group.
  const buckets=Array.from({length:64},()=>[]),pages=[];
  for(const a of group.assertions)buckets[parseInt(hash(a.id).slice(0,2),16)%64].push(a);
  const partitions=group.assertions.length<=50?[group.assertions]:buckets;
  for(const bucket of partitions){bucket.sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);for(let i=0;i<bucket.length;i+=50)pages.push(put({schemaVersion:1,type:'current-field-page',assertions:bucket.slice(i,i+50)}));}
  return [key,{count:group.assertions.length,pages,choice:group.choice,selected:group.choice?store.assertions[group.choice.assertionId]:null}];
 }))};
}
function metadata(kind,store,source,tables){return {schemaVersion:1,type:'current-state',kind,source,revision:revision(kind,store),eventCount:auditEvents(kind,store).length,
 checkpoint:kind==='formal'?store.journal?.checkpoint||null:null,stats:kind==='field'?fieldCounts(store):null,tables};}

export async function buildAuditCurrent(kind,store,source,old,events,reader,writer,limits){
 if(kind==='basic')return null;
 const prior=old?await reader.read(old):null,tables={...prior?.tables};
 // Only touched current rows are persisted. Source replay and full independent
 // verification still inspect the authoritative store, never a browser view.
 let wanted=null;
 if(prior){
  wanted={};
  for(const e of events){
   if(kind==='formal')(wanted.records??=new Set()).add(e.workId);
   else for(const c of e.changes){
    if(kind==='identity')(wanted[c.table]??=new Set()).add(c.id);
    else {const key=c.table==='choices'?c.id:fieldKey((c.after||c.before).scope,(c.after||c.before).field);(wanted.groups??=new Set()).add(key);}
   }
  }
 }
 // Delay page writes for unchanged field groups as well as unchanged rows.
 const filtered=kind==='field'&&wanted?{...store,assertions:Object.fromEntries(Object.entries(store.assertions).filter(([,a])=>wanted.groups?.has(fieldKey(a.scope,a.field)))),choices:Object.fromEntries(Object.entries(store.choices).filter(([key])=>wanted.groups?.has(key)))}:store;
 const rows=rowsFor(kind,filtered,value=>writer.put(value));
 for(const table of new Set([...Object.keys(rows),...Object.keys(wanted||{})])){
  const ids=wanted?.[table]||Object.keys(rows[table]||{}),updates=[];
  for(const id of ids){const value=rows[table]?.[id];updates.push([id,value===undefined?null:writer.put({schemaVersion:1,type:'current-row',kind,table,id,value})]);}
  tables[table]=await setAuditMap(tables[table]||null,updates,reader,writer,limits);
 }
 return writer.put(metadata(kind,store,source,tables));
}

export async function verifyAuditCurrent(kind,store,source,pointer,reader,writer){
 if(!pointer)return; // Old generations remain independently readable.
 const state=await reader.read(pointer),expected=rowsFor(kind,store,value=>writer.put(value));
 if(journalKey({...state,tables:{}})!==journalKey(metadata(kind,store,source,{})))throw Error('当前状态投影与资料版本不一致');
 if(journalKey(Object.keys(state.tables).sort())!==journalKey(Object.keys(expected).sort()))throw Error('当前状态投影表不完整');
 for(const [table,rows] of Object.entries(expected)){
  const entries=state.tables[table]?await auditMapEntries(reader,state.tables[table]):[];
  const actual=new Map(entries.filter(([,ref])=>ref));
  if(actual.size!==Object.keys(rows).length)throw Error('当前状态投影条目不完整');
  for(const [id,value] of Object.entries(rows)){
   const ref=actual.get(id);if(!ref)throw Error('当前状态投影缺少条目');
   const row=await reader.read(ref);
   if(journalKey(row)!==journalKey({schemaVersion:1,type:'current-row',kind,table,id,value}))throw Error('当前状态投影与来源快照不一致');
  }
 }
}
