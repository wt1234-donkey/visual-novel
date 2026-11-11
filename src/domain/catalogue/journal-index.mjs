import {catalogueState,journalKey,replayJournal} from './journal.mjs';

export const JOURNAL_DIRECTORY='data/basic-catalogue-journal/';
export const MAX_SHARD_EVENTS=50;
export const MAX_SHARD_BYTES=512*1024;
const sha=value=>typeof value==='string'&&/^[a-f0-9]{40}$/.test(value);
const path=value=>typeof value==='string'&&/^data\/basic-catalogue-journal\/(?:checkpoints\/r\d+|events\/r\d+-r\d+)\.json$/.test(value);
const integer=value=>Number.isSafeInteger(value)&&value>=0;

export function validateJournalIndex(store,validateState){
 const index=store.journal,base=index?.baseline;
 if(!index||index.schemaVersion!==2||!base||!integer(base.revision)||!path(base.path)||!sha(base.sha)||
  !Array.isArray(index.shards)||!integer(index.eventCount)||!/^[a-f0-9]{64}$/.test(index.stateHash||''))throw Error('基础库分片日志索引无效');
 let revision=base.revision,count=0;const ids=new Set(),paths=new Set([base.path]);
 for(const shard of index.shards){
  if(!shard||!path(shard.path)||paths.has(shard.path)||!sha(shard.sha)||!integer(shard.startRevision)||!integer(shard.endRevision)||
   shard.startRevision!==revision+1||shard.endRevision<shard.startRevision||!Array.isArray(shard.operationIds)||
   shard.operationIds.length!==shard.endRevision-shard.startRevision+1||shard.operationIds.length>MAX_SHARD_EVENTS||!integer(shard.bytes)||shard.bytes===0)throw Error('日志分片不连续或引用无效');
  for(const id of shard.operationIds){if(typeof id!=='string'||!id||ids.has(id))throw Error('分片日志含重复操作ID');ids.add(id);}
  paths.add(shard.path);revision=shard.endRevision;count+=shard.operationIds.length;
 }
 if(count!==index.eventCount)throw Error('分片日志计数不一致');
 if(store.transaction){
  const transaction=store.transaction;
  if(transaction.baseline?.revision!==revision||!Array.isArray(transaction.events)||!transaction.events.length)throw Error('基础库事务基准无效');
  for(const event of transaction.events)if(ids.has(event.id))throw Error('基础库事务重复操作ID');
  const replayed=replayJournal({schemaVersion:1,...transaction},validateState);
  if(journalKey(replayed)!==journalKey(catalogueState(store)))throw Error('基础库事务与快照不一致');
 }else if(store.revision!==revision)throw Error('基础库快照与分片修订不一致');
 return store;
}

export function validateShard(reference,value){
 if(!value||value.schemaVersion!==1||value.startRevision!==reference.startRevision||value.endRevision!==reference.endRevision||
  !Array.isArray(value.events)||journalKey(value.events.map(event=>event.id))!==journalKey(reference.operationIds)||
  value.events.some((event,i)=>event.revision!==reference.startRevision+i||event.previousRevision!==event.revision-1))throw Error('日志分片内容与索引不一致');
 return value;
}

export function journalSummary(store){
 return {baselineRevision:store.journal?.baseline.revision??store.revision,
  eventCount:store.schemaVersion===3?store.journal.eventCount+(store.transaction?.events.length||0):store.journal?.events.length??0};
}
