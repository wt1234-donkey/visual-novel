import test from 'node:test';
import assert from 'node:assert/strict';
import {emptyStore,applyChange,valuesOf} from '../basic-catalogue-model.mjs';
import {commitBasicCommand} from '../src/application/catalogue/commands.mjs';

const base=[{id:'a',title:'Alpha',year:1990,group:'A',gameplay:'ADV'},{id:'b',title:'Beta',year:2000,group:'B',gameplay:'ADV'}];
const meta={id:'operation',at:'2026-11-11T08:00:00Z',actor:'test',reason:'核对作品信息'};
const edit=(id,patch)=>({type:'edit',id,values:{...valuesOf(base.find(row=>row.id===id)),...patch}});
const change=(store,action)=>applyChange(store,base,action,{...meta,id:'other-'+store.revision,expectedRevision:store.revision});
function repository(initial=emptyStore()){
 let store=structuredClone(initial),version=1;
 const writes=[];
 return {writes,get store(){return structuredClone(store);},
  async read(){return {store:structuredClone(store),sha:String(version)};},
  replace(next){store=structuredClone(next);version++;},
  async write(next,sha){assert.equal(sha,String(version));store=structuredClone(next);version++;writes.push(next);return {sha:String(version),commit:'commit'};}
 };
}
const save=(repo,action,snapshot=emptyStore(),extra={})=>commitBasicCommand({repository:repo,snapshot:{store:snapshot},base,action,meta,...extra});

test('independent commands rebase onto the latest repository without losing either edit',async()=>{
 const repo=repository(change(emptyStore(),edit('b',{group:'Remote B'})));
 const result=await save(repo,edit('a',{title:'Local A'}));
 assert.equal(result.store.records.a.values.title,'Local A');
 assert.equal(result.store.records.b.values.group,'Remote B');
 assert.equal(result.store.revision,2);
 assert.deepEqual(JSON.parse(JSON.stringify(repo.store)),result.store);
});

test('disjoint fields of the same identity merge, but conflicting fields never write',async()=>{
 const remote=change(emptyStore(),edit('a',{group:'Remote A'}));
 const repo=repository(remote);
 await save(repo,edit('a',{title:'Local A'}));
 assert.equal(repo.store.records.a.values.group,'Remote A');
 const conflict=repository(change(emptyStore(),edit('a',{title:'Remote title'})));
 await assert.rejects(save(conflict,edit('a',{title:'Local title'})),/字段冲突/);
 assert.equal(conflict.writes.length,0);
});

test('one SHA conflict retries a freshly validated command and uses the new SHA',async()=>{
 const repo=repository(),write=repo.write.bind(repo);let attempted=0;
 repo.write=async(next,sha)=>{if(!attempted++){repo.replace(change(emptyStore(),edit('b',{group:'Concurrent B'})));throw Object.assign(Error('conflict'),{status:409,code:'CONFLICT'});}return write(next,sha);};
 await save(repo,edit('a',{title:'Local A'}));
 assert.equal(attempted,2);
 assert.equal(repo.writes.length,1);
 assert.equal(repo.store.records.b.values.group,'Concurrent B');
});

test('a same-field change during SHA retry stops without a second write',async()=>{
 const repo=repository();let attempted=0;
 repo.write=async()=>{attempted++;repo.replace(change(emptyStore(),edit('a',{title:'Remote title'})));throw Object.assign(Error('conflict'),{status:409,code:'CONFLICT'});};
 await assert.rejects(save(repo,edit('a',{title:'Local title'})),/字段冲突/);
 assert.equal(attempted,1);
});

test('a lost success response is verified by reading persisted bytes without duplicate submission',async()=>{
 const repo=repository(),write=repo.write.bind(repo);let attempted=0;
 repo.write=async(...args)=>{attempted++;await write(...args);throw Error('connection interrupted');};
 const result=await save(repo,edit('a',{title:'Saved'}));
 assert.equal(result.result.verifiedAfterError,true);
 assert.equal(attempted,1);
 assert.equal(repo.store.revision,1);
});

test('an unconfirmed transport failure, denied permission or rate limit preserves local and remote data',async()=>{
 for(const error of [Error('offline'),Object.assign(Error('permission'),{status:403}),Object.assign(Error('rate limit'),{status:429})]){
  const repo=repository(),snapshot=emptyStore(),action=edit('a',{title:'Draft'}),before=structuredClone(action);let attempted=0;
  repo.write=async()=>{attempted++;throw error;};
  await assert.rejects(save(repo,action,snapshot));
  assert.deepEqual(action,before);assert.deepEqual(snapshot,emptyStore());assert.deepEqual(repo.store,emptyStore());assert.equal(attempted,1);
 }
});

test('stale destructive commands and undo require fresh review; style batches remain atomic',async()=>{
 const repo=repository(change(emptyStore(),edit('b',{group:'Updated'})));
 for(const action of [{type:'delete',id:'a'},{type:'detach',id:'a'},{type:'merge',mainId:'a',ids:['b'],relation:{type:'unverified',label:'版本'}}])await assert.rejects(save(repo,action),/重新核对/);
 await assert.rejects(save(repo,null,emptyStore(),{undo:true}),/撤销/);
 await assert.rejects(save(repo,{type:'style-update',rows:['a','b'].map(id=>({id,mode:'append',tags:{theme:'科幻'}}))}),/目标基础作品已变化/);
 assert.equal(repo.writes.length,0);
 await save(repo,{type:'style-update',rows:[{id:'a',mode:'append',tags:{theme:'科幻'}}]});
 assert.equal(repo.store.records.a.style.plotTags.theme,'科幻');
});

test('remote parent changes reject a stale edit and missing identity parents cannot be committed',async()=>{
 const merged=change(emptyStore(),{type:'merge',mainId:'b',ids:['a'],relation:{type:'unverified',label:'版本'}});
 const repo=repository(merged);
 await assert.rejects(save(repo,edit('a',{title:'Draft'})),/版本关系已变化/);
 assert.equal(repo.writes.length,0);
});
