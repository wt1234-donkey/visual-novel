import {readReleaseManifest,readReleaseText} from './release-reader.mjs';
import {withDeadline} from './async-read.mjs';
import {createPublishedAuditAccess} from './audit-access.mjs';
export function createOnDemandReader(fetcher=fetch){
 let manifest;const cache=new Map(),pending=new Map(),MAX=24,audit=createPublishedAuditAccess(fetcher);
 const release=()=>manifest??=readReleaseManifest(fetcher).catch(error=>{manifest=null;throw error;});
 async function json(ref,options={}){
  const r=await withDeadline(()=>release(),options);if(!ref)throw Error('发布版本缺少按需目录，请刷新后重试');
  const key=ref.path;if(options.signal?.aborted)throw options.signal.reason||new DOMException('读取已取消','AbortError');
  if(cache.has(key)){const value=cache.get(key);cache.delete(key);cache.set(key,value);return value;}
  if(options.signal){const value=JSON.parse(await readReleaseText(ref,r,fetcher,options));cache.set(key,value);if(cache.size>MAX)cache.delete(cache.keys().next().value);return value;}
  // A consumer's cancellation must not cancel another consumer's shared read.
  if(!pending.has(key))pending.set(key,readReleaseText(ref,r,fetcher,{timeout:options.timeout}).then(text=>{
   const value=JSON.parse(text);cache.set(key,value);if(cache.size>MAX)cache.delete(cache.keys().next().value);return value;
  }).finally(()=>pending.delete(key)));
  const reading=pending.get(key);return withDeadline(()=>reading,options);
 }
 async function directory(kind,options){const r=await withDeadline(()=>release(),options),v=await json(r.catalogues?.[kind],options);if(v.revision!==r.revision||v.schemaVersion!==1)throw Error('按需目录版本无效');return v;}
 async function formal(id,family='formal',options){const d=await directory('formal',options),slot=d.ids.indexOf(id);if(slot<0)throw Error('作品身份不存在：'+id);const rows=await json(d.families[family]?.[Math.floor(slot/d.shardSize)],options);if(!Object.hasOwn(rows,id))throw Error('作品详情缺失：'+id);return rows[id];}
 async function bulkSlots(slots,d,options){
  const pages=[...new Set(slots.map(slot=>Math.floor(slot/d.shardSize)))],groups=new Map();
  for(let i=0;i<pages.length;i+=4)await Promise.all(pages.slice(i,i+4).map(async n=>groups.set(n,await json(d.shards[n],options))));
  return slots.map(slot=>{const row=groups.get(Math.floor(slot/d.shardSize))[slot%d.shardSize];if(!row?.work?.indexId)throw Error('基础身份详情缺失');return row;});
 }
 async function bulk(ids,options){
  const d=await directory('bulk',options),prefixes=await Promise.all(ids.map(async id=>new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(id)))[0]%64)),pages=[...new Set(prefixes)],lookups=new Map();for(let i=0;i<pages.length;i+=4)await Promise.all(pages.slice(i,i+4).map(async n=>lookups.set(n,await json(d.lookup[n],options))));const positions=ids.map((id,i)=>{const slot=lookups.get(prefixes[i])[id];if(!Number.isSafeInteger(slot))throw Error('基础身份不存在：'+id);return slot;});
  const rows=await bulkSlots(positions,d,options);return new Map(rows.map((row,i)=>{if(row.work.indexId!==ids[i])throw Error('基础身份详情不匹配');return [ids[i],row];}));
 }
 async function bulkPage({query='',status='all',year='',page=0,size=25},options){
  const d=await directory('bulk',options);let slots,total;
  if(query){const search=await json(d.search,{timeout:20000,...options});slots=search.filter(r=>r[1].includes(query)&&(status==='all'||r[3]===status)&&(!year||String(r[2])===year)).map(r=>r[0]);}
  else if(status!=='all'||year)slots=d.buckets[status==='all'?'year:'+year:status+(year?':'+year:'')]||[];
  total=slots?slots.length:d.count;page=Math.max(0,Math.min(page,Math.ceil(total/size)-1));
  const selected=slots?slots.slice(page*size,(page+1)*size):Array.from({length:Math.min(size,total-page*size)},(_,i)=>page*size+i);
  return {total,page,rows:await bulkSlots(selected,d,options)};
 }
 return {release,json,directory,formal,bulk,bulkPage,async current(kind,options){const opened=await audit.open(kind,{release:await release()});if(!opened)throw Error('此发布尚无按需当前状态，请刷新后重试');return opened.current(options);},async reserved(options){const d=await directory('bulk',options);return json(d.reserved,options);},async optional(name,options){const r=await release();return json(r.catalogues?.[name],options);}};
}
