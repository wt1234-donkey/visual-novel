import {readFileSync,writeFileSync,existsSync,mkdirSync,mkdtempSync,renameSync,rmSync} from 'node:fs';
import {join,dirname} from 'node:path';
import {createHash} from 'node:crypto';
import {validateStore} from '../../domain/catalogue/model.mjs';
import {catalogueState,journalKey} from '../../domain/catalogue/journal.mjs';
import {MAX_SHARD_EVENTS,MAX_SHARD_BYTES} from '../../domain/catalogue/journal-index.mjs';
import {jsonText,planCatalogueFiles,finishCatalogueFiles,hydrateCatalogueJournal,assertTransactionBase} from '../storage/catalogue-files.mjs';

export const BASIC_STORE_PATH='data/basic-catalogue-edits.json';
export const gitBlobHash=text=>createHash('sha1').update('blob '+Buffer.byteLength(text)+'\0').update(text).digest('hex');
const stateHash=store=>createHash('sha256').update(journalKey(catalogueState(store))).digest('hex');
const raw=(root,path)=>readFileSync(join(root,path),'utf8');
function readReference(root,ref){
 const text=raw(root,ref.path);
 if(gitBlobHash(text)!==ref.sha||(ref.bytes!==undefined&&Buffer.byteLength(text)!==ref.bytes))throw Error('日志文件摘要不匹配：'+ref.path);
 return JSON.parse(text);
}

export function readBasicStoreSync(root,{audit=true}={}){
 const store=validateStore(JSON.parse(raw(root,BASIC_STORE_PATH)));
 if(store.schemaVersion===3){
  if(store.transaction||stateHash(store)!==store.journal.stateHash)throw Error('基础库快照摘要校验失败');
  if(audit)readBasicJournalSync(root,store);
 }
 return store;
}

export function readBasicJournalSync(root,store=readBasicStoreSync(root,{audit:false})){
 if(store.schemaVersion!==3)return store;
 return hydrateCatalogueJournal(store,readReference(root,store.journal.baseline),store.journal.shards.map(ref=>readReference(root,ref)));
}

export function saveBasicStoreSync(root,next,{migrate=false}={}){
 validateStore(next);
 const current=readBasicStoreSync(root);
 if(current.schemaVersion===3&&next.schemaVersion!==3)throw Error('不能将分片基础库降级为旧格式');
 if(next.schemaVersion!==3&&!migrate){writeFileSync(join(root,BASIC_STORE_PATH),jsonText(next));return next;}
 if(next.schemaVersion===3&&!next.transaction){
  if(journalKey(next)!==journalKey(current))throw Error('分片写入缺少待保存事务');
  return current;
 }
 assertTransactionBase(next,current);
 const last=next.schemaVersion===3?next.journal.shards.at(-1):null;
 const active=last&&last.operationIds.length<MAX_SHARD_EVENTS&&last.bytes<MAX_SHARD_BYTES?readReference(root,last):null;
 const plan=planCatalogueFiles(next,active),hashes=new Map(plan.files.map(file=>[file.path,gitBlobHash(file.content)]));
 const store=finishCatalogueFiles(plan,hashes,stateHash(next));
 const writes=[...plan.files,{path:BASIC_STORE_PATH,content:jsonText(store)}];
 const paths=[...writes.map(file=>file.path),...plan.remove];
 const backups=new Map(paths.map(path=>[path,existsSync(join(root,path))?readFileSync(join(root,path)):null]));
 const temporary=mkdtempSync(join(root,'.basic-storage-'));
 try{
  writes.forEach((file,i)=>writeFileSync(join(temporary,String(i)),file.content));
  // New shards first, snapshot last. Old active files are retained until the
  // snapshot points at the replacement; an interrupted local staging is safe.
  writes.forEach((file,i)=>{mkdirSync(dirname(join(root,file.path)),{recursive:true});renameSync(join(temporary,String(i)),join(root,file.path));});
  for(const path of plan.remove)rmSync(join(root,path));
  readBasicStoreSync(root);
 }catch(error){
  for(const [path,bytes] of backups){if(bytes===null)rmSync(join(root,path),{force:true});else{mkdirSync(dirname(join(root,path)),{recursive:true});writeFileSync(join(root,path),bytes);}}
  throw error;
 }finally{rmSync(temporary,{recursive:true,force:true});}
 return store;
}
