import {applyChange,validateStore,workKey} from '../../domain/catalogue/model.mjs';
import {catalogueState,journalHistory,journalKey} from '../../domain/catalogue/journal.mjs';
import {createCatalogueView} from './view.mjs';
import {commitBasicCommand} from './commands.mjs';

// One session owner for the source rows, active snapshot, repository and actor.
// UI code owns presentation; repository code owns transport and credentials.
const freeze=value=>{if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.freeze(value);for(const child of Object.values(value))freeze(child);}return value;};
export function createCatalogueService({base,initial,repository,prepareBase,loadDetails=async()=>new Map(),makeMeta}) {
 if(typeof makeMeta!=='function')throw Error('目录服务缺少操作身份生成器');
 let snapshot={store:structuredClone(validateStore(initial)),sha:null},actor='',view,pending,busy=false;
 function update(next) {
  const accepted={...next,store:structuredClone(validateStore(next.store))};
  const projected=createCatalogueView(base,accepted.store);
  snapshot={...accepted,store:freeze(accepted.store)};view=projected;
 }
 function ensureIdle(){if(busy)throw Object.assign(Error('另一项基础库操作正在进行，请等待完成'),{code:'BUSY'});}
 async function exclusive(operation){ensureIdle();busy=true;try{return await operation();}finally{busy=false;}}
 update(snapshot);
 return {
  get actor(){return actor;},
  get snapshot(){return {store:snapshot.store,sha:snapshot.sha};},
  get view(){return view;},
  get busy(){return busy;},
  get pendingOperation(){return pending?{id:pending.meta.id,at:pending.meta.at}:null;},
  async connect(nextRepository){return exclusive(async()=>{
   const login=await nextRepository.connect(),fresh=await nextRepository.read();
   validateStore(fresh.store);
   repository=nextRepository;actor=login;pending=null;update(fresh);return login;
  });},
  disconnect(nextRepository){ensureIdle();repository=nextRepository;actor='';pending=null;},
  async sync(){return exclusive(async()=>{const fresh=await repository.read();update(fresh);pending=null;return snapshot.store.revision;});},
  preview(action){
   // A preview validates against current data without creating a real operation
   // or appending an audit entry to the active snapshot.
   return applyChange(catalogueState(snapshot.store),base,action,{actor:'preview',reason:'预览',expectedRevision:snapshot.store.revision});
  },
  history(options){return journalHistory(snapshot.store,options);},
  async execute(action,reason,{undo=false}={}){return exclusive(async()=>{
   if(!actor)throw Object.assign(Error('请先连接 GitHub 写入权限；当前填写保留'),{code:'NOT_CONNECTED'});
   const signature=journalKey({action,reason,undo,actor});
   if(!pending||pending.signature!==signature)pending={signature,action:structuredClone(action),undo,snapshot:{store:structuredClone(snapshot.store),sha:snapshot.sha},meta:{...makeMeta(),actor,reason}};
   const operation=pending;
   const result=await commitBasicCommand({repository,snapshot:operation.snapshot,
    base:undo?base:await (prepareBase?prepareBase(operation.action):hydrateCommandBase(base,view,operation.action,loadDetails)),action:operation.action,meta:operation.meta,undo:operation.undo});
   update(result);pending=null;return {revision:snapshot.store.revision,...result.result};
  });}
 };
}

export async function hydrateCommandBase(base,view,action,loadDetails){
 if(action.type==='add')return base;
 const ids=new Set(action.rows?.map(row=>row.id)||action.ids||[action.id]);
 if(action.mainId)ids.add(action.mainId);
 if(action.type==='merge')for(const row of view.all)if(action.ids.includes(row.parentId))ids.add(row._key);
 const targets=base.filter(row=>ids.has(workKey(row)));
 const details=await loadDetails(targets);
 return base.map(row=>details.has(row.slot)?{...row,...details.get(row.slot)}:row);
}
