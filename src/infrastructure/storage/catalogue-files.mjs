import {validateStore,upgradeStore} from '../../domain/catalogue/model.mjs';
import {catalogueState,journalKey} from '../../domain/catalogue/journal.mjs';
import {JOURNAL_DIRECTORY,MAX_SHARD_EVENTS,MAX_SHARD_BYTES,validateShard} from '../../domain/catalogue/journal-index.mjs';

export const jsonText=value=>JSON.stringify(value,null,2)+'\n';
export const utf8Bytes=text=>new TextEncoder().encode(text);
const clone=value=>structuredClone(value);
const segment=events=>({schemaVersion:1,startRevision:events[0].revision,endRevision:events.at(-1).revision,events});
const segmentPath=events=>JOURNAL_DIRECTORY+'events/r'+events[0].revision+'-r'+events.at(-1).revision+'.json';

// Pure packing plan shared by browser transactions and filesystem tooling.
// Hashing and I/O belong to the adapters, never the domain model.
export function planCatalogueFiles(input,activeShard=null){
 const store=upgradeStore(input),state={...catalogueState(store),schemaVersion:3},files=[],remove=[];
 let index,events,active=[];
 if(store.schemaVersion===3){
  if(!store.transaction)throw Error('分片写入缺少待保存事务');
  index=clone(store.journal);events=clone(store.transaction.events);
  const last=index.shards.at(-1);
  if(last&&last.operationIds.length<MAX_SHARD_EVENTS&&last.bytes<MAX_SHARD_BYTES){
   active=clone(validateShard(last,activeShard).events);index.shards.pop();remove.push(last.path);
  }
 }else{
  const baseline=store.journal.baseline;
  index={schemaVersion:2,baseline:{path:JOURNAL_DIRECTORY+'checkpoints/r'+baseline.revision+'.json',sha:'',revision:baseline.revision},shards:[],eventCount:0,stateHash:''};
  files.push({path:index.baseline.path,content:jsonText(baseline)});events=clone(store.journal.events);
 }
 const flush=()=>{
  if(!active.length)return;
  const value=segment(active),path=segmentPath(active),content=jsonText(value);
  files.push({path,content});
  index.shards.push({path,sha:'',startRevision:value.startRevision,endRevision:value.endRevision,operationIds:active.map(event=>event.id),bytes:utf8Bytes(content).length});
  active=[];
 };
 for(const event of events){
  if(active.length&&(active.length>=MAX_SHARD_EVENTS||utf8Bytes(jsonText(segment([...active,event]))).length>MAX_SHARD_BYTES))flush();
  active.push(event);
 }
 flush();index.eventCount=index.shards.reduce((count,shard)=>count+shard.operationIds.length,0);
 state.journal=index;
 return {store:state,files,remove:remove.filter(path=>!files.some(file=>file.path===path))};
}

export function finishCatalogueFiles(plan,hashes,stateHash){
 const store=clone(plan.store);
 for(const ref of [store.journal.baseline,...store.journal.shards])if(hashes.has(ref.path))ref.sha=hashes.get(ref.path);
 store.journal.stateHash=stateHash;validateStore(store);return store;
}

export function hydrateCatalogueJournal(store,baseline,shards){
 validateStore(store);
 if(store.schemaVersion!==3)return store;
 if(store.transaction)throw Error('未提交事务不能作为持久化快照读取');
 if(baseline.revision!==store.journal.baseline.revision)throw Error('日志检查点修订不一致');
 const events=store.journal.shards.flatMap((ref,i)=>validateShard(ref,shards[i]).events);
 const result={...catalogueState(store),schemaVersion:2,journal:{schemaVersion:1,baseline,events}};
 validateStore(result);return result;
}

export function assertTransactionBase(next,current){
 if(current.schemaVersion!==3)return;
 if(next.schemaVersion!==3||journalKey(next.journal)!==journalKey(current.journal)||
  journalKey(next.transaction?.baseline)!==journalKey(catalogueState(current)))throw Error('分片事务与最新基础库快照不匹配');
}
