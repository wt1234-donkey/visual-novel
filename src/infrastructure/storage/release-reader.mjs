import {withDeadline,interrupted} from './async-read.mjs';
import {blobDigest} from './digests.mjs';
import {decodePublishedText} from './wire-format.mjs';

const sessions=new WeakMap();
const revision=/^[a-f0-9]{40}$/;
const moduleRevision=new URL(import.meta.url).searchParams.get('v');
export function releaseChanged(previous,next,cause){
 const error=Object.assign(Error('网站或索引版本已更新，请恢复到新的发布版本；当前查询与未保存输入将保留。'),{code:'RELEASE_CHANGED',previousRevision:previous,nextRevision:next,cause});
 if(typeof window!=='undefined'){
  window.__catalogueReleaseChange=error;
  window.dispatchEvent(new CustomEvent('catalogue-release-change',{detail:{previousRevision:previous,nextRevision:next}}));
 }
 return error;
}
export async function readReleaseManifest(fetcher=fetch,{refresh=false,checkCode=true}={}){
 if(refresh)sessions.delete(fetcher);
 if(!sessions.has(fetcher))sessions.set(fetcher,(async()=>{
  const value=await withDeadline(async signal=>{const response=await fetcher('./data/catalogue-release.json',{cache:'no-store',signal});if(!response.ok)throw Error('发布清单不可读取');return response.json();});
  if(value.schemaVersion!==1||!revision.test(value.revision))throw Error('发布清单格式无效');
  return value;
 })().catch(error=>{sessions.delete(fetcher);throw error;}));
 const manifest=await sessions.get(fetcher);
 if(checkCode&&revision.test(moduleRevision||'')&&moduleRevision!==manifest.revision)throw releaseChanged(moduleRevision,manifest.revision);
 return manifest;
}
export async function releaseFailure(error,previous,fetcher=fetch){
 if(interrupted(error))throw error;
 try{
  const next=await readReleaseManifest(fetcher,{refresh:true,checkCode:false});
  if(next.revision!==previous)throw releaseChanged(previous,next.revision,error);
 }catch(nextError){if(nextError.code==='RELEASE_CHANGED')throw nextError;}
 throw error;
}
export async function readReleaseText(ref,manifest,fetcher=fetch,options={}){
 if(!ref||typeof ref.path!=='string'||!ref.path.startsWith('catalogue-web/'+manifest.revision+'/')||ref.path.includes('..')||!/^[a-f0-9]{40}$/.test(ref.sha))throw Error('发布资源引用无效');
 try{
  const text=await withDeadline(async signal=>{if(ref.gzip===ref.path+'.gz'&&typeof DecompressionStream!=='undefined'){const zipped=await fetcher('./data/'+ref.gzip,{signal});if(zipped.ok&&zipped.body)return decodePublishedText(await new Response(zipped.body.pipeThrough(new DecompressionStream('gzip'))).text());}const response=await fetcher('./data/'+ref.path,{cache:'no-cache',signal});if(!response.ok)throw Error('发布资源读取失败（HTTP '+response.status+'）');return decodePublishedText(await response.text());},options);
  if(await blobDigest(text)!==ref.sha)throw Error('发布资源摘要不匹配');
  return text;
 }catch(error){return releaseFailure(error,manifest.revision,fetcher);}
}
export async function readReleaseJson(path,fetcher=fetch,manifest,options={}){
 const release=manifest||await readReleaseManifest(fetcher);
 const key=path.replace(/^\.\//,'').split('?')[0];
 const ref=release.resources?.[key];
 if(!ref){
  if(release.resources)throw Error('发布清单未声明资源：'+key);
  // Read-only compatibility for pre-contract published snapshots.
  const response=await fetcher('./'+key,{cache:'no-cache'});if(!response.ok)throw Error('来源资料不可读取：'+key);
  return response.json();
 }
 return JSON.parse(await readReleaseText(ref,release,fetcher,options));
}
