import test from 'node:test';
import assert from 'node:assert/strict';
import {applyChange,valuesOf,emptyStore,upgradeStore} from '../basic-catalogue-model.mjs';
import {createBasicRepository} from '../src/infrastructure/github/basic-repository.mjs';
import {commitBasicCommand} from '../src/application/catalogue/commands.mjs';
import {gitFixture,STORE} from './helpers/catalogue-git-fixture.mjs';

const base=[{id:'a',title:'Alpha',year:1990,group:'A',gameplay:'ADV'},{id:'b',title:'Beta',year:2000,group:'B',gameplay:'ADV'}];
const meta={id:'local-operation',at:'2026-11-11T10:00:00Z',actor:'test',reason:'作品更正'};
const edit=(id,title)=>({type:'edit',id,values:{...valuesOf(base.find(work=>work.id===id)),title}});
const save=(repository,snapshot,action=edit('a','Saved'))=>commitBasicCommand({repository,snapshot,base,action,meta});
const external=(api,id='b',title='Remote B')=>api.publish(applyChange(api.store,base,edit(id,title),{...meta,id:'external',actor:'other',expectedRevision:api.store.revision}));

test('one ref update publishes the snapshot and shard together while preserving unrelated files',async()=>{
 const api=gitFixture(),repo=createBasicRepository('test-only',api.fetch),opened=await repo.read();
 assert.equal(api.calls.filter(call=>call.path.startsWith('/git/blobs/')).length,0,'initial read must not hydrate archives');
 const result=await save(repo,opened);
 assert.equal(api.store.schemaVersion,3);assert.equal(api.store.transaction,undefined);assert.equal(api.store.revision,1);
 assert.equal(result.store.journal.eventCount,1);assert.equal(result.store.transaction,undefined);
 assert.equal(api.file('unrelated.txt'),'original');
 const updates=api.calls.filter(call=>call.method==='PATCH');assert.equal(updates.length,1);assert.equal(updates[0].body.force,false);
 assert.equal(api.calls.filter(call=>call.method==='PUT').length,0);
 assert.ok(api.paths().includes(api.store.journal.shards[0].path));
 assert.ok(!JSON.stringify([...api.blobs.values()]).includes('test-only'));
});

test('failure at any Git object or ref stage leaves all visible files unchanged',async()=>{
 for(const stage of ['blob','tree','commit','ref']){
  const api=gitFixture(),repo=createBasicRepository('test-only',api.fetch),opened=await repo.read(),head=api.head,paths=api.paths(),snapshot=api.file(STORE);
  api.fail(stage);await assert.rejects(save(repo,opened));
  assert.equal(api.head,head,stage);assert.deepEqual(api.paths(),paths);assert.equal(api.file(STORE),snapshot);
 }
});

test('a competing unrelated commit rejects the old parent and bounded retry preserves both changes',async()=>{
 const api=gitFixture(),repo=createBasicRepository('test-only',api.fetch),opened=await repo.read();
 api.onRef(api=>api.changeFile('unrelated.txt','changed concurrently'));
 await save(repo,opened);
 assert.equal(api.file('unrelated.txt'),'changed concurrently');assert.equal(api.store.records.a.values.title,'Saved');
 assert.equal(api.calls.filter(call=>call.method==='PATCH').length,2);
});

test('a concurrent edit to the same field stops without publishing the stale transaction',async()=>{
 const api=gitFixture(),repo=createBasicRepository('test-only',api.fetch),opened=await repo.read();
 api.onRef(api=>external(api,'a','Remote A'));
 await assert.rejects(save(repo,opened),/字段冲突/);
 assert.equal(api.store.records.a.values.title,'Remote A');assert.equal(api.store.journal.eventCount,1);
 assert.equal(api.calls.filter(call=>call.method==='PATCH').length,1);
});

test('a lost final ref response is verified by operation ID without a second transaction',async()=>{
 const api=gitFixture();let lost=true;
 const fetch=async(url,options)=>{const response=await api.fetch(url,options);if(options.method==='PATCH'&&lost){lost=false;throw Error('reply lost');}return response;};
 const repo=createBasicRepository('test-only',fetch),opened=await repo.read();
 const result=await save(repo,opened);assert.equal(result.result.verifiedAfterError,true);
 assert.equal(api.store.journal.eventCount,1);assert.equal(api.calls.filter(call=>call.method==='PATCH').length,1);
 external(api);
 const duplicate=await save(repo,opened);assert.equal(duplicate.result.alreadyApplied,true);
 assert.equal(api.store.records.b.values.title,'Remote B');assert.equal(api.store.journal.eventCount,2);
});

test('history reads only required shards, caches by immutable blob SHA and paginates without loss',async()=>{
 let original=upgradeStore(emptyStore());
 for(let i=0;i<70;i++)original=applyChange(original,base,edit('a','Work '+i),{...meta,id:'event-'+i,expectedRevision:original.revision});
 const api=gitFixture(original),repo=createBasicRepository('',api.fetch),snapshot=await repo.read();
 assert.equal(api.calls.filter(call=>call.path.startsWith('/git/blobs/')).length,0);
 const first=await repo.history(snapshot,{limit:10});assert.deepEqual(first.events.map(event=>event.revision),[70,69,68,67,66,65,64,63,62,61]);
 assert.equal(api.calls.filter(call=>call.path.startsWith('/git/blobs/')).length,1);
 const second=await repo.history(snapshot,{before:first.nextBefore,limit:10});assert.equal(second.events[0].revision,60);
 assert.equal(second.events.at(-1).revision,51);
 const operation=await repo.findOperation(snapshot,'event-0');assert.equal(operation.revision,1);
 assert.equal(api.calls.filter(call=>call.path.startsWith('/git/blobs/')).length,2);
});

test('fast snapshot verification rejects an unlogged current-state change',async()=>{
 const api=gitFixture(),store=api.store;store.records.a={deleted:true};api.changeFile(STORE,JSON.stringify(store));
 const repo=createBasicRepository('',api.fetch);await assert.rejects(repo.read(),/摘要/);
});

test('static history fallback checks digests, omits credentials and can retry corrupt responses',async()=>{
 const original=applyChange(upgradeStore(emptyStore()),base,edit('a','Saved'),{...meta,expectedRevision:0});
 const api=gitFixture(original);let corrupt=true,staticCalls=0;
 const fetch=async(url,options)=>{
  if(url.includes('/git/blobs/'))return {ok:false,status:403,json:async()=>({message:'unavailable'})};
  if(url.startsWith('./')){
   staticCalls++;assert.equal(options.headers,undefined);
   const path=url.slice(2).split('?')[0],text=api.file(path);
   return {ok:true,text:async()=>text+(corrupt?' ':'')};
  }
  return api.fetch(url,options);
 };
 const repo=createBasicRepository('test-only',fetch),snapshot=await repo.read();
 await assert.rejects(repo.history(snapshot),/摘要/);corrupt=false;
 const page=await repo.history(snapshot);assert.equal(page.events[0].id,meta.id);assert.equal(staticCalls,2);
});
