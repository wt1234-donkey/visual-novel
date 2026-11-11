import {buildEffectiveCatalogue} from '../../domain/catalogue/effective.mjs';
import {blobDigest} from './digests.mjs';
import {readReleaseManifest,readReleaseText,readReleaseJson} from './release-reader.mjs';

export async function loadEffectiveCatalogue(fetcher=fetch){
 const manifest=await readReleaseManifest(fetcher);
 if(manifest.schemaVersion!==1||!/^[a-f0-9]{40}$/.test(manifest.revision)||manifest.inputs?.path!=='catalogue-web/'+manifest.revision+'/inputs.json'||manifest.sourceLease?.schemaVersion!==1||!Object.keys(manifest.sourceLease.files||{}).length)throw Error('当前作品快照清单无效');
 const text=await readReleaseText(manifest.inputs,manifest,fetcher);
 const raw=JSON.parse(text);if(raw.schemaVersion!==1||JSON.stringify(raw.sourceLease)!==JSON.stringify(manifest.sourceLease))throw Error('当前作品快照格式无效');
 return {...buildEffectiveCatalogue(raw),raw,sourceLease:manifest.sourceLease,revision:manifest.revision,release:manifest};
}

export async function readPublishedSource(path,lease,fetcher=fetch){
 const manifest=await readReleaseManifest(fetcher);
 if(manifest.resources?.[path]){
  if(lease&&manifest.resources[path].sha!==lease.files[path])throw Error('来源资料与当前快照不一致，请刷新后重试：'+path);
  return readReleaseJson(path,fetcher,manifest);
 }
 const response=await fetcher('./'+path,{cache:'no-store'});if(!response.ok)throw Error('来源资料不可读取：'+path);
 if(!lease)return response.json();
 const text=await response.text();if(!lease.files[path]||await blobDigest(text)!==lease.files[path])throw Error('来源资料与当前快照不一致，请刷新后重试：'+path);
 return JSON.parse(text);
}
