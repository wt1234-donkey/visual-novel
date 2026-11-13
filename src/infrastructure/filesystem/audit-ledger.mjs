import {readFileSync,writeFileSync,mkdirSync,existsSync,readdirSync,rmSync} from 'node:fs';
import {join,dirname} from 'node:path';
import {createHash} from 'node:crypto';
import {journalKey,replayJournal} from '../../domain/catalogue/journal.mjs';
import {replayFormalJournal} from '../../domain/catalogue/formal-journal.mjs';
import {validateFieldStore} from '../../domain/catalogue/field-evidence.mjs';
import {validateIdentityStore} from '../../domain/catalogue/source-identities.mjs';
import {AUDIT_PATH,AUDIT_SOURCES,auditEvents,auditOrder,auditWorkIds,replaceAuditEvents} from '../../domain/audit/events.mjs';
import {readBasicJournalSync} from './basic-store.mjs';
import {createAuditReader} from '../storage/audit-reader.mjs';
const hash=text=>createHash('sha256').update(text).digest('hex');
const blob=text=>createHash('sha1').update('blob '+Buffer.byteLength(text)+'\0'+text).digest('hex');
export const AUDIT_LIMITS={segmentEvents:50,segmentBytes:256*1024,indexEntries:64,indexBytes:128*1024};
const textOf=value=>JSON.stringify(value)+'\n';
function checkpoint(kind,store){
 const result=replaceAuditEvents(kind,store,[]);
 if(kind==='basic'&&store.journal)Object.assign(result,structuredClone(store.journal.baseline),{schemaVersion:2});
 else if(kind==='formal'&&store.journal)result.records=structuredClone(store.journal.baseline.records);
 else if(kind==='field'){result.revision=0;result.assertions={};result.choices={};}
 else if(kind==='identity'){result.revision=0;result.links={};result.cases={};}
 return result;
}
function replay(kind,baseline,events){
 const result=replaceAuditEvents(kind,baseline,events);
 if(kind==='basic'&&result.journal)Object.assign(result,replayJournal(result.journal),{schemaVersion:2});
 else if(kind==='formal'&&result.journal)result.records=replayFormalJournal(result.journal).records;
 else if(kind==='identity'||kind==='field'){
  for(const event of events){for(const change of event.changes){const table=result[change.table];if(!table||journalKey(Object.hasOwn(table,change.id)?table[change.id]:null)!==journalKey(change.before))throw Error('归档事件前值不一致');if(change.after===null)delete table[change.id];else Object.defineProperty(table,change.id,{value:structuredClone(change.after),writable:true,enumerable:true,configurable:true});}result.revision=event.revision;}
  (kind==='field'?validateFieldStore:validateIdentityStore)(result);
 }
 return result;
}
export function packAuditKind(kind,store,source,{put}){
 const events=auditEvents(kind,store),all=[],operations=[],byWork=new Map();let previous=null,active=[];
 const flush=()=>{
  if(!active.length)return;
  const segment=put({schemaVersion:1,type:'events',kind,previous,events:active});
  for(const [offset,event] of active.entries()){
   const workIds=auditWorkIds(kind,event),posting={id:event.id,order:auditOrder(kind,event),workHash:hash(JSON.stringify(workIds)),eventHash:hash(JSON.stringify(event)),segment,offset};
   all.push(posting);operations.push([event.id,posting]);
   for(const id of workIds){if(!byWork.has(id))byWork.set(id,[]);byWork.get(id).push(posting);}
  }
  previous=segment.sha256;active=[];
 };
 for(const event of events){
  if(active.length&&(active.length>=AUDIT_LIMITS.segmentEvents||Buffer.byteLength(textOf({schemaVersion:1,type:'events',kind,previous,events:[...active,event]}))>AUDIT_LIMITS.segmentBytes))flush();
  active.push(event);
 }flush();
 function range(entries){
  if(!entries.length)return null;
  let level=[];
  for(let i=0;i<entries.length;i+=AUDIT_LIMITS.indexEntries){const rows=entries.slice(i,i+AUDIT_LIMITS.indexEntries);level.push({...put({schemaVersion:1,type:'range-leaf',entries:rows}),min:rows[0].order,max:rows.at(-1).order,count:rows.length});}
  while(level.length>1){const next=[];for(let i=0;i<level.length;i+=AUDIT_LIMITS.indexEntries){const children=level.slice(i,i+AUDIT_LIMITS.indexEntries);next.push({...put({schemaVersion:1,type:'range-branch',children}),min:children[0].min,max:children.at(-1).max,count:children.reduce((n,r)=>n+r.count,0)});}level=next;}
  return level[0];
 }
 function trie(rows,depth=0){
  if(rows.length<=AUDIT_LIMITS.indexEntries&&Buffer.byteLength(textOf({schemaVersion:1,type:'map',entries:Object.fromEntries(rows)}))<=AUDIT_LIMITS.indexBytes)return put({schemaVersion:1,type:'map',entries:Object.fromEntries(rows)});
  if(depth>=64)throw Error('审计索引键碰撞超出容量');
  const buckets=new Map();for(const row of rows){const key=hash(row[0]).slice(depth,depth+2);if(!buckets.has(key))buckets.set(key,[]);buckets.get(key).push(row);}
  return put({schemaVersion:1,type:'branch',depth,children:Object.fromEntries([...buckets].sort(([a],[b])=>a<b?-1:a>b?1:0).map(([key,group])=>[key,trie(group,depth+2)]))});
 }
 const skeleton=checkpoint(kind,store);
 return {source,eventCount:events.length,currentRevision:kind==='formal'?events.length:store.revision,logicalHash:hash(journalKey(store)),eventChainHead:previous,
  baselineRevision:kind==='basic'?store.journal?.baseline.revision??store.revision:0,
  checkpoint:kind==='formal'?store.journal?.checkpoint||null:null,
  skeleton:put({schemaVersion:1,type:'skeleton',kind,store:skeleton}),history:range(all),
  operations:trie(operations.sort(([a],[b])=>a<b?-1:a>b?1:0)),
  works:trie([...byWork].sort(([a],[b])=>a<b?-1:a>b?1:0).map(([id,rows])=>[id,{count:rows.length,root:range(rows)}]))};
}
export function auditObjectWriter(root,{check=false,files=new Map()}={}){
 return {files,put(value){const content=textOf(value),sha256=hash(content),path='data/audit-ledger/objects/'+sha256+'.json';
  const ref={path,sha:blob(content),sha256,bytes:Buffer.byteLength(content)};files.set(path,content);
  if(check){if(!existsSync(join(root,path))||readFileSync(join(root,path),'utf8')!==content)throw Error('审计归档缺失或不一致：'+path);}
  else if(!existsSync(join(root,path))){mkdirSync(dirname(join(root,path)),{recursive:true});writeFileSync(join(root,path),content);}
  else if(readFileSync(join(root,path),'utf8')!==content)throw Error('不可改写既有审计归档：'+path);
  return ref;
 }};
}
export function auditSourceStores(root){
 const stores={},sources={};
 for(const [kind,path] of Object.entries(AUDIT_SOURCES)){
  if(!existsSync(join(root,path)))continue;
  const text=readFileSync(join(root,path),'utf8');sources[kind]={path,sha:blob(text)};
  stores[kind]=kind==='basic'?readBasicJournalSync(root):JSON.parse(text);
 }return {stores,sources};
}
export async function restoreAuditKind(root,pointer,kind){
 const reader=createAuditReader(ref=>readFileSync(join(root,ref.path),'utf8'),{cacheSize:256}),opened=await reader.open(pointer,{kind}),descriptor=opened.descriptor;
 const rows=await reader.postings(descriptor.history,{limit:Number.MAX_SAFE_INTEGER}),events=[];let previous=null;
 // Global order is checked independently of operation/work posting lists.
 for(const posting of [...rows].reverse()){
  const segment=await reader.read(posting.segment);
  if(posting.offset===0){if(segment.previous!==previous)throw Error('审计归档链不连续');previous=posting.segment.sha256;}
  const event=await reader.event(kind,posting);if(!event||auditOrder(kind,event)!==posting.order)throw Error('操作索引与归档不一致');events.push(event);
 }
 const skeleton=await reader.read(descriptor.skeleton),store=replay(kind,skeleton.store,events);
 if(events.length!==descriptor.eventCount||previous!==descriptor.eventChainHead||hash(journalKey(store))!==descriptor.logicalHash)throw Error('归档回放对象不一致');
 // Rebuild all postings from event bodies: omissions, false subject lists and
 // forged alternate indexes cannot pass merely by recomputing a file digest.
 const packed=packAuditKind(kind,store,descriptor.source,auditObjectWriter(root,{check:true}));
 if(journalKey(packed)!==journalKey(descriptor))throw Error('归档索引与事件全集不一致');
 return store;
}
export async function verifyAuditGraph(root,pointer){
 const reader=createAuditReader(ref=>readFileSync(join(root,ref.path),'utf8')),seen=new Set(),pending=[pointer];
 while(pending.length){const ref=pending.pop();if(seen.has(ref.sha256))continue;seen.add(ref.sha256);const value=await reader.read(ref);
  const visit=node=>{if(!node||typeof node!=='object')return;if(typeof node.path==='string'&&typeof node.sha256==='string'&&typeof node.sha==='string'){pending.push(node);return;}for(const child of Object.values(node))visit(child);};visit(value);
 }return seen.size;
}
// Publish one self-contained current archive. Older index generations remain
// immutable in Git; retaining all generations in every Pages artifact would
// grow the runtime independently of its complete current event history.
export async function publishAuditLedger(source,output){
 if(!existsSync(join(source,AUDIT_PATH)))return null;
 if(existsSync(join(output,'.git')))throw Error('审计发布目录不能是源码Git工作区');
 const original=JSON.parse(readFileSync(join(source,AUDIT_PATH),'utf8'));
 const reader=createAuditReader(ref=>readFileSync(join(source,ref.path),'utf8'));
 const manifest={...await reader.read(original.root),previous:null},writer=auditObjectWriter(output),root=writer.put(manifest),seen=new Set(),pending=[root];
 while(pending.length){const ref=pending.pop();if(seen.has(ref.sha256))continue;seen.add(ref.sha256);
  const value=ref.sha256===root.sha256?manifest:await reader.read(ref);
  const copied=writer.put(value);if(copied.sha256!==ref.sha256)throw Error('归档发布复制改变对象');
  const visit=node=>{if(!node||typeof node!=='object')return;if(typeof node.path==='string'&&typeof node.sha256==='string'&&typeof node.sha==='string'){pending.push(node);return;}for(const child of Object.values(node))visit(child);};visit(value);
 }
 const directory=join(output,'data/audit-ledger/objects');
 for(const name of readdirSync(directory))if(!seen.has(name.replace(/\.json$/,'')))rmSync(join(directory,name));
 const pointer={schemaVersion:1,root};writeFileSync(join(output,AUDIT_PATH),textOf(pointer));
 return {pointer,objects:seen.size};
}
export async function buildAuditLedger(root,{check=false}={}){
 const {stores,sources}=auditSourceStores(root),writer=auditObjectWriter(root,{check}),kinds={};
 let previous=null;
 if(existsSync(join(root,AUDIT_PATH)))previous=JSON.parse(readFileSync(join(root,AUDIT_PATH),'utf8'));
 for(const [kind,store] of Object.entries(stores))kinds[kind]=packAuditKind(kind,store,sources[kind],writer);
 let oldManifest=null;
 if(previous){
  const reader=createAuditReader(ref=>readFileSync(join(root,ref.path),'utf8'));oldManifest=await reader.read(previous.root);
  for(const [kind,old] of Object.entries(oldManifest.kinds)){
   if(!kinds[kind]||kinds[kind].eventCount<old.eventCount)throw Error('不能移除或截断归档事件');
   if(kinds[kind].logicalHash===old.logicalHash)continue;
   const original=await restoreAuditKind(root,previous.root,kind),a=auditEvents(kind,original),b=auditEvents(kind,stores[kind]);
   if(a.some((event,i)=>journalKey(event)!==journalKey(b[i])))throw Error('不能改写既有归档事件前缀');
   if(kind==='basic'||kind==='formal')if(journalKey(original.journal?.baseline)!==journalKey(stores[kind].journal?.baseline))throw Error('不能重置归档迁移起点');
  }
 }
 const unchanged=oldManifest&&journalKey(oldManifest.kinds)===journalKey(kinds);
 const manifest=unchanged?oldManifest:{schemaVersion:1,kinds,previous:previous?.root||null};
 const rootRef=writer.put(manifest),pointer={schemaVersion:1,root:rootRef},content=textOf(pointer);
 if(check){if(!previous||journalKey(previous)!==journalKey(pointer))throw Error('审计索引需要重新生成');}
 else if(!previous||journalKey(previous)!==journalKey(pointer)){mkdirSync(dirname(join(root,AUDIT_PATH)),{recursive:true});writeFileSync(join(root,AUDIT_PATH),content);}
 for(const kind of Object.keys(kinds)){
  const restored=await restoreAuditKind(root,rootRef,kind);
  if(journalKey(restored)!==journalKey(stores[kind]))throw Error('归档前后逻辑状态或完整日志不一致');
 }
 await verifyAuditGraph(root,rootRef);
 return {pointer,kinds:Object.fromEntries(Object.entries(kinds).map(([k,v])=>[k,{events:v.eventCount,sourceSha:v.source.sha,logicalHash:v.logicalHash}])),objects:writer.files.size,changed:!unchanged};
}
