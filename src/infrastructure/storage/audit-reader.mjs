import {digestText,blobDigest} from './digests.mjs';
import {auditOrder,auditWorkIds} from '../../domain/audit/events.mjs';
import {readAuditCurrent} from './current-state-reader.mjs';
const validRef=ref=>ref&&/^data\/audit-ledger\/objects\/[a-f0-9]{64}\.json$/.test(ref.path)&&/^[a-f0-9]{40}$/.test(ref.sha)&&/^[a-f0-9]{64}$/.test(ref.sha256)&&Number.isSafeInteger(ref.bytes)&&ref.bytes>0;
export function createAuditReader(loadText,{cacheSize=48}={}){
 const cache=new Map();
 async function read(ref,options){
  if(!validRef(ref))throw Error('审计归档引用无效');
  if(!cache.has(ref.sha256))cache.set(ref.sha256,(async()=>{
   const text=await loadText(ref,options);
   if(new TextEncoder().encode(text).length!==ref.bytes||await blobDigest(text)!==ref.sha||await digestText(text)!==ref.sha256)throw Error('审计归档摘要不匹配：'+ref.path);
   return JSON.parse(text);
  })().catch(error=>{cache.delete(ref.sha256);throw error;}));
  const value=await cache.get(ref.sha256);
  if(cache.size>cacheSize)cache.delete(cache.keys().next().value);
  return value;
 }
 async function lookup(ref,id,options){
  const hash=await digestText(id);let depth=0;
  while(ref){const node=await read(ref,options);
   if(node.type==='map')return Object.hasOwn(node.entries,id)?node.entries[id]:null;
   if(node.type!=='branch'||node.depth!==depth||depth>=64)throw Error('审计索引层级无效');
   ref=node.children[hash.slice(depth,depth+2)];depth+=2;
  }return null;
 }
 async function postings(ref,{before=Infinity,limit=21,...options}={}){
  const found=[];
  async function visit(pointer){
   if(!pointer||pointer.min>=before||found.length>=limit)return;
   const node=await read(pointer,options);
   if(node.type==='range-leaf'){
    for(let i=node.entries.length-1;i>=0&&found.length<limit;i--)if(node.entries[i].order<before)found.push(node.entries[i]);
   }else if(node.type==='range-branch'){
    for(let i=node.children.length-1;i>=0&&found.length<limit;i--)await visit(node.children[i]);
   }else throw Error('审计分页索引格式无效');
  }
  await visit(ref);return found;
 }
 async function event(kind,posting,options){
  const segment=await read(posting.segment,options),value=segment.events?.[posting.offset];
  if(segment.type!=='events'||value?.id!==posting.id||auditOrder(kind,value)!==posting.order||await digestText(JSON.stringify(value))!==posting.eventHash||await digestText(JSON.stringify(auditWorkIds(kind,value)))!==posting.workHash)throw Error('审计事件与索引不一致');
  return structuredClone(value);
 }
 return {read,lookup,postings,event,
  async open(pointer,{kind,sourceSha,...options}){
   const manifest=await read(pointer,options),descriptor=manifest.kinds?.[kind];
   if(manifest.schemaVersion!==1||!descriptor||sourceSha&&descriptor.source.sha!==sourceSha)throw Object.assign(Error('审计索引与当前资料版本不一致，请同步后重试'),{code:'AUDIT_STALE'});
   return {
    descriptor,
    current:opts=>readAuditCurrent({read,lookup},descriptor,{kind,...opts}),
    async findOperation(id,opts={}){const posting=await lookup(descriptor.operations,id,opts);if(posting&&posting.id!==id)throw Error('操作索引身份不一致');return posting?event(kind,posting,opts):null;},
    async history({workId=null,before=Infinity,limit=20,...opts}={}){
     if(!Number.isSafeInteger(limit)||limit<1||limit>100||!(before===Infinity||Number.isSafeInteger(before)&&before>0))throw Error('审计分页范围无效');
     const target=workId?await lookup(descriptor.works,workId,opts):{root:descriptor.history,count:descriptor.eventCount};
     const rows=target?await postings(target.root,{before,limit:limit+1,...opts}):[];
     const selected=rows.slice(0,limit),events=[];
     // A page reads only bodies referenced by its postings, never unrelated bodies.
     for(const posting of selected){const value=await event(kind,posting,opts);if(workId&&!auditWorkIds(kind,value).includes(workId))throw Error('作品索引归属不一致');events.push(value);}
     return {events,nextBefore:rows.length>limit?selected.at(-1).order:null,total:target?.count||0,
      baselineRevision:descriptor.baselineRevision,checkpoint:descriptor.checkpoint||null,indexed:true};
    }
   };
  }
 };
}
