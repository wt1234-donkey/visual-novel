import {AUDIT_PATH,AUDIT_SOURCES,auditEvents} from '../../domain/audit/events.mjs';
import {createAuditReader} from './audit-reader.mjs';
import {readReleaseManifest,readReleaseJson} from './release-reader.mjs';
import {withDeadline} from './async-read.mjs';
const decode=value=>new TextDecoder().decode(Uint8Array.from(atob(value.replace(/\s/g,'')),c=>c.charCodeAt(0)));
const missing=error=>error.status===404||error.code==='NOT_FOUND';
export function assertSmallLegacyHistory(kind,store){
 const count=kind==='basic'&&store.schemaVersion===3?store.journal.eventCount:auditEvents(kind,store).length;
 if(count>1000)throw Object.assign(Error('大容量历史需要已验证索引；索引暂不可用，请同步或重新发布后重试，不会扫描全部正文'),{code:'AUDIT_REQUIRED'});
}
export function createPublishedAuditAccess(fetcher=fetch){
 const reader=createAuditReader(ref=>withDeadline(async signal=>{const response=await fetcher('./'+ref.path,{signal});if(!response.ok)throw Error('读取审计归档失败（HTTP '+response.status+'）');return response.text();}));
 return {async open(kind,{store}={}){
  const release=await readReleaseManifest(fetcher);
  if(!release?.resources?.[AUDIT_PATH])return null; // Explicit compatibility with older releases.
  const pointer=await readReleaseJson(AUDIT_PATH,fetcher);
  const opened=await reader.open(pointer.root,{kind,sourceSha:release.resources[AUDIT_SOURCES[kind]]?.sha});
  const revision=kind==='formal'?auditEvents(kind,store||{}).length:store?.revision;
  if(store&&revision!==opened.descriptor.currentRevision)throw Object.assign(Error('审计索引尚未发布当前修订，请连接并同步最新记录'),{code:'AUDIT_STALE'});
  return opened;
 }};
}
export function createGitAuditAccess(client,fetcher=fetch){
 const published=createPublishedAuditAccess(fetcher);
 const reader=createAuditReader(async ref=>{
  const value=await client.gitRequest('/repos/wt1234-donkey/visual-novel/git/blobs/'+ref.sha);
  return decode(value.content);
 });
 return {async open(kind,snapshot){
  if(!snapshot.head)return published.open(kind,{store:snapshot.store});
  let file;try{file=await client.readFile(AUDIT_PATH,snapshot.head);}catch(error){if(missing(error))return null;throw error;}
  const pointer=JSON.parse(file.text);if(pointer.schemaVersion!==1)throw Error('审计入口格式无效');
  return reader.open(pointer.root,{kind,sourceSha:snapshot.sha});
 }};
}
