import {buildEffectiveCatalogue} from '../../domain/catalogue/effective.mjs';
import {blobDigest} from './digests.mjs';

export async function loadEffectiveCatalogue(fetcher=fetch){
 const response=await fetcher('./data/catalogue-release.json',{cache:'no-cache'});
 if(!response.ok)throw Error('当前作品快照清单不可读取');
 const manifest=await response.json();
 if(manifest.schemaVersion!==1||!/^[a-f0-9]{40}$/.test(manifest.revision)||manifest.inputs?.path!=='catalogue-web/'+manifest.revision+'/inputs.json'||manifest.sourceLease?.schemaVersion!==1||!Object.keys(manifest.sourceLease.files||{}).length)throw Error('当前作品快照清单无效');
 const file=await fetcher('./data/'+manifest.inputs.path,{cache:'no-cache'});
 if(!file.ok)throw Error('当前作品快照不可读取，请刷新重试');
 const text=await file.text();if(await blobDigest(text)!==manifest.inputs.sha)throw Error('当前作品快照摘要不匹配');
 const raw=JSON.parse(text);if(raw.schemaVersion!==1||JSON.stringify(raw.sourceLease)!==JSON.stringify(manifest.sourceLease))throw Error('当前作品快照格式无效');
 return {...buildEffectiveCatalogue(raw),raw,sourceLease:manifest.sourceLease,revision:manifest.revision};
}

export async function readPublishedSource(path,lease,fetcher=fetch){
 const response=await fetcher('./'+path,{cache:'no-store'});if(!response.ok)throw Error('来源资料不可读取：'+path);
 if(!lease)return response.json();
 const text=await response.text();if(!lease.files[path]||await blobDigest(text)!==lease.files[path])throw Error('来源资料与当前快照不一致，请刷新后重试：'+path);
 return JSON.parse(text);
}
