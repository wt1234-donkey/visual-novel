// Browser index format. The release ID in each path binds details to their index.
const directory='data/basic-web/';
export {compareBasicOrder,normalizeBasicQuery} from './src/domain/catalogue/order.mjs';

export function unpackBasicIndex({rows,groups,gameplay,statuses}){
 return rows.map(([id,matchedWorkId,title,year,group,play,status,aliases,otherGroups,plotStyles,plotTags,gameplayTags],slot)=>({
  id,matchedWorkId,title,year,group:groups[group],gameplay:gameplay[play],status:statuses[status],
  ...(aliases?{aliases}:{}),...(otherGroups?{groups:otherGroups.map(i=>groups[i])}:{}),
  ...(plotStyles?{plotStyles}:{}),...(plotTags?{plotTags}:{}),...(gameplayTags?{gameplayTags}:{}),slot
 }));
}

export function withBasicDetails(work,detail,store){
 if(!detail)return work;
 const record=store.records[work._key];
 return {...work,...detail,source:record?.values?work.source:detail.source,
  plotTagEvidence:record?.style||record?.values?work.plotTagEvidence:detail.plotTagEvidence};
}

export function createBasicWebIndex(fetcher=fetch){
 let manifest,advanced;
 const cache=new Map(),pending=new Map();
 async function json(path,options){
  const response=await fetcher(directory+path,options);
  if(!response.ok)throw Error('索引读取失败（HTTP '+response.status+'）');
  return response.json();
 }
 function meta(){
  manifest??=json('manifest.json',{cache:'no-cache'}).then(value=>{
   if(value.schema!==1||!/^[a-f0-9]{40,64}$/.test(value.revision)||!Number.isSafeInteger(value.shardSize)||value.shardSize<=0||
    !Number.isSafeInteger(value.home?.total)||!Number.isSafeInteger(value.basic?.total))throw Error('基础索引格式无效');
   return value;
  }).catch(error=>{manifest=null;throw error;});
  return manifest;
 }
 async function asset(path,compressed=false,expectedRevision){
  const {revision}=await meta();
  if(expectedRevision&&revision!==expectedRevision)throw Error('索引版本已更新，请刷新页面');
  const url=revision+'/'+path;
  if(compressed&&typeof DecompressionStream!=='undefined'){
   try{
    const response=await fetcher(directory+url+'.gz');
    if(response.ok&&response.body){
     const stream=response.body.pipeThrough(new DecompressionStream('gzip'));
     return await new Response(stream).json();
    }
   }catch{
    // Older hosting setups can serve the uncompressed index.
   }
  }
  return json(url);
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
 async function details(kind,slots){
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
 }
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

export function createCatalogueWorker(){
 let worker,failed=false,serial=0;
 const pending=new Map();
 function workerSearch(payload){
  if(!worker){
   worker=new Worker(new URL('./basic-catalogue-search-worker.mjs?v=20261111-architecture',import.meta.url),{type:'module'});
   worker.onmessage=({data})=>{
    const request=pending.get(data.id);
    if(!request)return;
    pending.delete(data.id);
    if(data.error)request.reject(Error(data.error));
    else request.resolve(data.result);
   };
   worker.onerror=()=>{
    for(const request of pending.values())request.reject(Error('搜索线程不可用'));
    pending.clear();
    worker.terminate();worker=null;
   };
  }
  return new Promise((resolve,reject)=>{
   const id=++serial;
   pending.set(id,{resolve,reject});
   worker.postMessage({id,...payload});
  });
 }
 return async payload=>{
  if(failed||typeof Worker==='undefined')return null;
  try{return await workerSearch(payload);}
  catch{failed=true;return null;}
 };
}

export function createHomeSearch(index){
 let searchRows;
 const search=createCatalogueWorker();
 return async(query,page,size)=>{
  const {revision}=await index.meta();
  const result=await search({kind:'home',query,page,size,revision});
  if(result)return result;
  searchRows??=index.homeSearch(revision).catch(error=>{searchRows=null;throw error;});
  const slots=searchHomeSlots(await searchRows,query);
  return slotPage(slots.length,page,size,slots);
 };
}
