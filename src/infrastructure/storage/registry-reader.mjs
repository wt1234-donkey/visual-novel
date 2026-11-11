import {blobDigest,digestText} from './digests.mjs';

export async function readRegistry(fetcher=fetch,path='./data/main-adv-rpg-works-20261031.json'){
 const response=await fetcher(path,{cache:'no-cache'});if(!response.ok)throw Error('基础源库清单不可读取');
 const header=await response.json(),storage=header.storage;
 if(!storage)return header;
 if(storage.format!=='registry-shards-v1'||storage.schemaVersion!==1)throw Error('基础源库格式无效');
 const works=[],ids=new Set(),directory=path.slice(0,path.lastIndexOf('/')+1);
 for(let start=0;start<storage.shards.length;start+=6){
  const parts=await Promise.all(storage.shards.slice(start,start+6).map(async(ref,offset)=>{
   if(ref.path!=='basic-registry/works-'+String(start+offset).padStart(5,'0')+'-'+ref.sha256.slice(0,12)+'.json')throw Error('基础源库分片路径无效');
   const file=await fetcher(directory+ref.path,{cache:'no-cache'});if(!file.ok)throw Error('基础源库分片不可读取');
   const text=await file.text();
   if(new TextEncoder().encode(text).length!==ref.bytes||await blobDigest(text)!==ref.gitSha||await digestText(text,'SHA-256')!==ref.sha256)throw Error('基础源库分片摘要不一致');
   const rows=JSON.parse(text);if(!Array.isArray(rows)||rows.length!==ref.count)throw Error('基础源库分片计数不一致');return rows;
  }));
  for(const rows of parts)for(const work of rows){if(ids.has(work.id))throw Error('基础源库身份重复');ids.add(work.id);works.push(work);}
 }
 if(works.length!==storage.count||works.length!==header.summary.accepted)throw Error('基础源库计数不一致');
 const {storage:ignored,...result}=header;return {...result,works};
}
