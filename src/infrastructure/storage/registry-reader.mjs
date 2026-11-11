import {readReleaseManifest,readReleaseJson,readReleaseText} from './release-reader.mjs';
import {blobDigest,digestText} from './digests.mjs';

export async function readRegistry(fetcher=fetch,path='./data/main-adv-rpg-works-20261031.json'){
 const manifest=await readReleaseManifest(fetcher);
 const header=await readReleaseJson(path,fetcher,manifest),storage=header.storage;
 if(!storage)return header;
 if(storage.format!=='registry-shards-v1'||storage.schemaVersion!==1)throw Error('基础源库格式无效');
 const works=[],ids=new Set();
 for(let start=0;start<storage.shards.length;start+=6){
  const parts=await Promise.all(storage.shards.slice(start,start+6).map(async(ref,offset)=>{
   if(ref.path!=='basic-registry/works-'+String(start+offset).padStart(5,'0')+'-'+ref.sha256.slice(0,12)+'.json')throw Error('基础源库分片路径无效');
   const text=await readReleaseText(manifest.resources['data/'+ref.path],manifest,fetcher);
   if(new TextEncoder().encode(text).length!==ref.bytes||await blobDigest(text)!==ref.gitSha||await digestText(text,'SHA-256')!==ref.sha256)throw Error('基础源库分片摘要不一致');
   const rows=JSON.parse(text);if(!Array.isArray(rows)||rows.length!==ref.count)throw Error('基础源库分片计数不一致');return rows;
  }));
  for(const rows of parts)for(const work of rows){if(ids.has(work.id))throw Error('基础源库身份重复');ids.add(work.id);works.push(work);}
 }
 if(works.length!==storage.count||works.length!==header.summary.accepted)throw Error('基础源库计数不一致');
 const {storage:ignored,...result}=header;return {...result,works};
}
