import {createOnDemandReader} from './on-demand-reader.mjs';
import {readReleaseJson} from './release-reader.mjs';
export function createFieldEvidenceReader(fetcher=fetch){
 const reader=createOnDemandReader(fetcher);let meta;
 const info=async()=>meta??=reader.optional('fieldEvidence').catch(e=>{meta=null;throw e;});
 return {info,async store(){return readReleaseJson('data/field-evidence.json',fetcher);},async targets(id,options){const m=await info(),canonical=m.aliases[id]||id,n=new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonical)))[0]%64,part=await reader.json(m.lookups[n],options);if(!Object.hasOwn(part,canonical))throw Error('作品ID不存在，请使用原作品ID或已明示关联的档案ID');return {workId:canonical,targets:part[canonical]};}};
}
