import {createOnDemandReader} from './on-demand-reader.mjs';
import {readReleaseJson} from './release-reader.mjs';
import {nameKey} from '../../domain/catalogue/identity.mjs';
export function createSourceIdentityReader(fetcher=fetch){
 const reader=createOnDemandReader(fetcher);let meta;
 const info=async()=>meta??=reader.optional('sourceIdentities').catch(e=>{meta=null;throw e;});
 const bucket=async id=>new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(id)))[0]%64;
 const load=(ref,options)=>reader.json(ref,options);
 async function byIds(view,ids,options){
  const m=await info(),buckets=await Promise.all(ids.map(bucket)),lookup=new Map(),wanted=[...new Set(buckets)];
  for(let i=0;i<wanted.length;i+=4)await Promise.all(wanted.slice(i,i+4).map(async n=>lookup.set(n,await load(m.lookups[view][n],options))));
  const positions=ids.map((id,n)=>Object.hasOwn(lookup.get(buckets[n]),id)?lookup.get(buckets[n])[id]:null),pages=new Map(),pageIds=[...new Set(positions.filter(Boolean).map(p=>p[0]))];
  for(let i=0;i<pageIds.length;i+=4)await Promise.all(pageIds.slice(i,i+4).map(async n=>pages.set(n,await load(m.pages[view][n],options))));
  return positions.map(position=>position?pages.get(position[0])[position[1]]:null);
 }
 return {info,byIds,
  async page(view,{page=0,query='',year=''}={},options){
   const m=await info();if(!m.pages[view])throw Error('身份目录类型无效');
   if(!query){const p=Math.max(0,Math.min(page,m.pages[view].length-1));return {rows:m.pages[view][p]?await load(m.pages[view][p],options):[],page:p,pages:m.pages[view].length,total:m.totals[view]};}
   const direct=(await byIds(view,[query],options)).filter(Boolean);let ids=[];
   if(!direct.length){const key=nameKey(query),table=await load(m.nameLookups[await bucket(key)],options);ids=Object.hasOwn(table,key)?table[key][view]||[]:[];}
   let rows=direct.length?direct:(await byIds(view,ids.slice(0,500),options)).filter(Boolean);
   if(year)rows=rows.filter(row=>String(row.firstYear??row.id.split('|').at(-1))===year);
   return {rows,page:0,pages:1,total:direct.length||ids.length,truncated:ids.length>500};
  },
  async original(source,options){const raw=await readReleaseJson('data/'+source.recordRef.path,fetcher,undefined,options);const row=Array.isArray(raw)?raw[source.recordRef.slot]:raw.works[source.recordRef.slot];if(row?.id!==source.id)throw Error('来源原文身份不匹配');return row;},
  async decisions(options){return reader.current('identity',options);}
 };
}
