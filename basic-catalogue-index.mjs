import {withDeadline} from './src/infrastructure/storage/async-read.mjs';
import {readReleaseManifest,readReleaseText,releaseFailure,releaseChanged} from './src/infrastructure/storage/release-reader.mjs';
import {blobDigest} from './src/infrastructure/storage/digests.mjs';
import {decodePublishedText} from './src/infrastructure/storage/wire-format.mjs';
// Browser index format. The release ID in each path binds details to their index.
import {catalogueState} from './src/domain/catalogue/journal.mjs';
const directory='data/basic-web/';
export {compareBasicOrder,normalizeBasicQuery} from './src/domain/catalogue/order.mjs';

export function unpackBasicIndex({rows,groups,gameplay,statuses}){
 return rows.map(([id,matchedWorkId,title,year,group,play,status,aliases,otherGroups,plotStyles,plotTags,gameplayTags,formal,fieldEvidence],slot)=>({
  id,matchedWorkId,title,year,group:groups[group],gameplay:gameplay[play],status:statuses[status],
  ...(fieldEvidence?{fieldEvidence}:{}),...(formal?{formalTitle:formal.title,formalOverride:formal.override,formalAt:formal.at}:{}),...(aliases?{aliases}:{}),...(otherGroups?{groups:otherGroups.map(i=>groups[i])}:{}),
  ...(plotStyles?{plotStyles}:{}),...(plotTags?{plotTags}:{}),...(gameplayTags?{gameplayTags}:{}),slot
 }));
}

export function withBasicDetails(work,detail,store){
 if(!detail)return work;
 const record=store.records[work._key];
 return {...work,...detail,source:record?.values?work.source:detail.source,
  plotTagEvidence:record?.style||record?.values?work.plotTagEvidence:detail.plotTagEvidence};
}

export function createBasicWebIndex(fetcher=fetch,{release:providedRelease}={}){
 let manifest,advanced;
 const cache=new Map(),pending=new Map();
 async function json(path,options){return withDeadline(async signal=>{
  const response=await fetcher(directory+path,{...options,signal});
  if(!response.ok)throw Error('索引读取失败（HTTP '+response.status+'）');
  return response.json();});
 }
 function meta(){
  manifest??=(async()=>{
   const release=providedRelease===null?null:providedRelease||await readReleaseManifest(fetcher);
   return release?.basic?JSON.parse(await readReleaseText(release.basic,release,fetcher)):json('manifest.json',{cache:'no-cache'});
  })().then(value=>{
   if(value.schema!==1||!/^[a-f0-9]{40,64}$/.test(value.revision)||!Number.isSafeInteger(value.shardSize)||value.shardSize<=0||
    !Number.isSafeInteger(value.home?.total)||!Number.isSafeInteger(value.basic?.total))throw Error('基础索引格式无效');
   return value;
  }).catch(error=>{manifest=null;throw error;});
  return manifest;
 }
 async function asset(path,compressed=false,expectedRevision){
  const metadata=await meta(),{revision}=metadata;
  if(expectedRevision&&revision!==expectedRevision)throw releaseChanged(expectedRevision,revision);
  const verify=async text=>{
   text=await decodePublishedText(text);
   if(metadata.assets&&(!metadata.assets[path]||await blobDigest(text)!==metadata.assets[path].sha))throw Error('索引资源摘要不匹配');
   return JSON.parse(text);
  };
  try{return await withDeadline(async signal=>{
   if(compressed&&typeof DecompressionStream!=='undefined'){
    const response=await fetcher(directory+revision+'/'+path+'.gz',{signal});
    if(response.ok&&response.body){
     const stream=response.body.pipeThrough(new DecompressionStream('gzip'));
     return await verify(await new Response(stream).text());
    }
   }
   const response=await fetcher(directory+revision+'/'+path,{signal});
   if(!response.ok)throw Error('索引读取失败（HTTP '+response.status+'）');
   if(metadata.assets)return verify(await response.text());
   return response.json();
  });}catch(error){
   if(providedRelease===null)throw error;
   return releaseFailure(error,revision,fetcher);
  }
 }
 async function shard(kind,n){
  const key=kind+'-'+n;
  if(cache.has(key)){
   const value=cache.get(key);
   cache.delete(key);cache.set(key,value);
   return value;
  }
  if(!pending.has(key))pending.set(key,asset(key+'.json').then(data=>{
   if(!Array.isArray(data))throw Error('作品详情分片格式无效');
   cache.set(key,data);
   if(cache.size>48)cache.delete(cache.keys().next().value);
   return data;
  }).finally(()=>pending.delete(key)));
  return pending.get(key);
 }
 async function details(kind,slots,{signal}={}){return withDeadline(async()=>{
  const {shardSize,[kind]:{total}}=await meta();
  if(slots.some(slot=>!Number.isSafeInteger(slot)||slot<0||slot>=total))throw Error('作品索引已变化，请刷新页面');
  const groups=[...new Set(slots.map(slot=>Math.floor(slot/shardSize)))];
  const shards=new Map();
  // Large batch edits can span many shards. Limit parallel requests.
  for(let i=0;i<groups.length;i+=12){
   await Promise.all(groups.slice(i,i+12).map(async n=>shards.set(n,await shard(kind,n))));
  }
  return new Map(slots.map(slot=>{
   const row=shards.get(Math.floor(slot/shardSize))[slot%shardSize];
   if(!row)throw Error('作品详情缺失，请刷新页面');
   return [slot,row];
  }));
 },{signal});}
 return {
  meta,
  async basicRows(revision){
   const {basic}=await meta();
   const rows=unpackBasicIndex(await asset('basic-index.json',true,revision));
   if(rows.length!==basic.total)throw Error('基础索引记录数不一致');
   return rows;
  },
  async advancedRows(revision){
   if(revision&&(await meta()).revision!==revision)throw Error('索引版本已更新，请刷新页面');
   advanced??=asset('basic-advanced.json',true,revision).then(value=>{
    if(!value||typeof value!=='object'||Array.isArray(value))throw Error('高级检索索引格式无效');
    return value;
   }).catch(error=>{advanced=null;throw error;});
   return advanced;
  },
  async homeSearch(revision){
   const {home}=await meta(),rows=await asset('home-search.json',true,revision);
   if(!Array.isArray(rows)||rows.length!==home.total)throw Error('首页索引记录数不一致');
   return rows;
  },
  details
 };
}

export function searchHomeSlots(rows,query){
 const slots=[];
 for(let i=0;i<rows.length;i++)if(rows[i].includes(query))slots.push(i);
 return slots;
}

export function slotPage(total,page,size,slots){
 const current=Math.max(1,Math.min(page,Math.ceil(total/size)));
 const first=(current-1)*size,end=Math.min(first+size,total);
 return {total,page:current,slots:slots?slots.slice(first,end):Array.from({length:end-first},(_,i)=>first+i)};
}

export function createCatalogueWorker({timeout=4000,WorkerClass=globalThis.Worker}={}){
 let worker,failed=false,serial=0;
 const pending=new Map();
 function stop(error){failed=true;worker?.terminate();worker=null;for(const request of [...pending.values()])request.reject(error);pending.clear();}
 return async (payload,{signal}={})=>{
  if(signal?.aborted)throw signal.reason||new DOMException('查询已取消','AbortError');
  if(failed||!WorkerClass)return null;
  try{
   worker??=new WorkerClass(new URL('./basic-catalogue-search-worker.mjs?v=20261111-architecture',import.meta.url),{type:'module'});
   worker.onmessage=({data})=>{const request=pending.get(data.id);if(request){if(data.error)request.reject(Error(data.error));else request.resolve(data.result);}};
   worker.onerror=()=>stop(Error('搜索线程不可用'));
   return await new Promise((resolve,reject)=>{
    const id=++serial;
    const finish=(fn,value)=>{clearTimeout(timer);signal?.removeEventListener('abort',abort);pending.delete(id);fn(value);};
    const abort=()=>finish(reject,signal.reason||new DOMException('查询已取消','AbortError'));
    const timer=setTimeout(()=>stop(new DOMException('搜索线程超时，切换本地检索','TimeoutError')),timeout);
    pending.set(id,{resolve:value=>finish(resolve,value),reject:error=>finish(reject,error)});
    signal?.addEventListener('abort',abort,{once:true});
    worker.postMessage({id,...(payload.kind==='basic'?{...payload,store:catalogueState(payload.store)}:payload)});
   });
  }catch(error){if(error.name==='AbortError')throw error;stop(error);return null;}
 };
}

export function createHomeSearch(index){
 let searchRows;
 const search=createCatalogueWorker();
 return async(query,page,size,options={})=>{
  const {revision}=await index.meta();
  const result=await search({kind:'home',query,page,size,revision},options);
  if(result)return result;
  searchRows??=index.homeSearch(revision).catch(error=>{searchRows=null;throw error;});
  const slots=searchHomeSlots(await withDeadline(()=>searchRows,options),query);
  return slotPage(slots.length,page,size,slots);
 };
}
