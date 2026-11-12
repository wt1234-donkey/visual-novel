import {createEditClient,EDIT_REPOSITORY,decodeContentText} from './contents-repository.mjs';
import {submitCommand} from './command-transport.mjs';
import {validateStore} from '../../domain/catalogue/model.mjs';
import {journalHistory} from '../../domain/catalogue/journal.mjs';
import {MAX_SHARD_EVENTS,MAX_SHARD_BYTES,validateShard} from '../../domain/catalogue/journal-index.mjs';
import {planCatalogueFiles,finishCatalogueFiles,jsonText,utf8Bytes,assertTransactionBase} from '../storage/catalogue-files.mjs';
import {blobDigest,stateDigest,verifySnapshot} from '../storage/digests.mjs';
import {createSourceGuard} from './source-lease.mjs';
export {TOKEN_SETUP_URL} from './contents-repository.mjs';

const PATH='data/basic-catalogue-edits.json',REPO=EDIT_REPOSITORY;
const conflict=()=>Object.assign(Error('数据库已变化或写入冲突；本次没有覆盖其他修改'),{code:'CONFLICT',status:409});
export function createBasicRepository(token = '', fetcher = fetch, {sourceLease=null,commandMode='legacy'}={}) {
 const client=createEditClient(token,fetcher,{historyPath:PATH,validate:validateStore,sourceLease});
 const request=client.gitRequest,cache=new Map();
 const guard=createSourceGuard(request,REPO);
 async function snapshotAt(head){
  await guard(head,sourceLease);
  const file=await client.readFile(PATH,head);
  if(await blobDigest(file.text)!==file.sha)throw Error('基础库文件摘要校验失败');
  return {head,sha:file.sha,store:await verifySnapshot(validateStore(JSON.parse(file.text)))};
 }
 async function reference(ref){
  if(!cache.has(ref.sha))cache.set(ref.sha,(async()=>{
   let text;
   try{text=decodeContentText((await request(REPO+'/git/blobs/'+ref.sha)).content);}
   catch(error){
    const response=await fetcher('./'+ref.path+'?blob='+ref.sha,{cache:'no-cache'});
    if(!response.ok)throw error;
    text=await response.text();
   }
   if(await blobDigest(text)!==ref.sha||(ref.bytes!==undefined&&utf8Bytes(text).length!==ref.bytes))throw Error('日志文件摘要校验失败：'+ref.path);
   return JSON.parse(text);
  })().catch(error=>{cache.delete(ref.sha);throw error;}));
  const value=await cache.get(ref.sha);
  if(cache.size>16)cache.delete(cache.keys().next().value);
  return value;
 }
 const shard=async ref=>validateShard(ref,await reference(ref));
 return {
  executeCommand:commandMode==='trusted'?async command=>{const result=await submitCommand(request,{...command,sourceLease});const snapshot=await snapshotAt((await request(REPO+'/git/ref/heads/main')).object.sha);return {...snapshot,result};}:undefined,
  connect:()=>client.connect(),
  async read(){const head=(await request(REPO+'/git/ref/heads/main')).object.sha;return snapshotAt(head);},
  async readPublished(){const value=await client.readPublished();await verifySnapshot(value.store);return {...value,source:'pages'};},
  async findOperation(snapshot,id){
   const ref=snapshot.store.journal.shards.find(shard=>shard.operationIds.includes(id));
   return ref?(await shard(ref)).events.find(event=>event.id===id):null;
  },
  async history(snapshot,{before=Infinity,limit=20,workId=null}={}){
   const store=snapshot.store;
   if(store.schemaVersion!==3)return journalHistory(store,{before,limit,workId});
   if(!Number.isSafeInteger(limit)||limit<1||limit>100)throw Error('每页历史须为1至100条');
   const found=[];
   for(const ref of [...store.journal.shards].reverse()){
    if(ref.startRevision>=before)continue;
    for(const event of [...(await shard(ref)).events].reverse()){
     if(event.revision>=before)continue;
     if(workId&&!event.changes.some(change=>change.id===workId)&&![...event.added,...event.removed].some(work=>work.id===workId))continue;
     found.push(event);if(found.length>limit)break;
    }
    if(found.length>limit)break;
   }
   const events=found.slice(0,limit);
   return {events:structuredClone(events),nextBefore:found.length>limit?events.at(-1).revision:null,
    baselineRevision:store.journal.baseline.revision,total:workId?null:Math.max(0,Math.min(store.revision,before-1)-store.journal.baseline.revision)};
  },
  async write(next,expectedSha,message){
   if(!token)throw Error('请先连接 GitHub 写入权限');
   if(!expectedSha)throw Error('请先读取 GitHub 最新修改记录后保存');
   validateStore(next);
   const head=(await request(REPO+'/git/ref/heads/main')).object.sha;
   const live=await snapshotAt(head);
   if(live.sha!==expectedSha)throw conflict();
   assertTransactionBase(next,live.store);
   if(next.revision<=live.store.revision)throw Error('本次事务没有新的修改');
   const last=next.schemaVersion===3?next.journal.shards.at(-1):null;
   const active=last&&last.operationIds.length<MAX_SHARD_EVENTS&&last.bytes<MAX_SHARD_BYTES?await shard(last):null;
   const plan=planCatalogueFiles(next,active),hashes=new Map(),tree=[];
   for(const file of plan.files){
    const blob=await request(REPO+'/git/blobs','POST',{content:file.content,encoding:'utf-8'});
    if(blob.sha!==await blobDigest(file.content))throw Error('GitHub 日志对象摘要不匹配');
    hashes.set(file.path,blob.sha);tree.push({path:file.path,mode:'100644',type:'blob',sha:blob.sha});
   }
   const store=finishCatalogueFiles(plan,hashes,await stateDigest(next));
   const content=jsonText(store),blob=await request(REPO+'/git/blobs','POST',{content,encoding:'utf-8'});
   if(blob.sha!==await blobDigest(content))throw Error('GitHub 快照对象摘要不匹配');
   tree.push({path:PATH,mode:'100644',type:'blob',sha:blob.sha});
   for(const path of plan.remove)tree.push({path,mode:'100644',type:'blob',sha:null});
   const parent=await request(REPO+'/git/commits/'+head);
   const createdTree=await request(REPO+'/git/trees','POST',{base_tree:parent.tree.sha,tree});
   const commit=await request(REPO+'/git/commits','POST',{message,tree:createdTree.sha,parents:[head]});
   // A competing head advancement rejects this update, including unrelated files.
   await request(REPO+'/git/refs/heads/main','PATCH',{sha:commit.sha,force:false});
   return {sha:blob.sha,commit:commit.sha,url:'https://github.com/wt1234-donkey/visual-novel/commit/'+commit.sha,store};
  }
 };
}
