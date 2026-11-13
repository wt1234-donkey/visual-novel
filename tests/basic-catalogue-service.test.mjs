import test from 'node:test';
import assert from 'node:assert/strict';
import {emptyStore,applyChange,valuesOf} from '../basic-catalogue-model.mjs';
import {createCatalogueService} from '../src/application/catalogue/service.mjs';
import {upgradeStore} from '../basic-catalogue-model.mjs';
import {split} from './helpers/catalogue-git-fixture.mjs';

const base=[{id:'a',title:'Alpha',year:1990,group:'A',gameplay:'ADV'},{id:'b',title:'Beta',year:2000,group:'B',gameplay:'ADV'}];
const edit=(id,patch)=>({type:'edit',id,values:{...valuesOf(base.find(work=>work.id===id)),...patch}});
const iso='2026-11-11T09:00:00Z';
function fixture(){
 let store=emptyStore(),sha=1,serial=0;
 const writes=[],repository={async connect(){return 'tester';},async read(){return {store:structuredClone(store),sha:String(sha)};},
  async write(next,expected){assert.equal(expected,String(sha));store=structuredClone(next);sha++;writes.push(next);return {sha:String(sha)};}};
 const service=createCatalogueService({base,initial:store,repository,makeMeta:()=>({id:'operation-'+(++serial),at:iso})});
 return {service,repository,writes,get store(){return structuredClone(store);},replace(next){store=structuredClone(next);sha++;}};
}

test('initial history lookup is pinned to its live bootstrap head before connecting credentials',async()=>{
 const initial=split(upgradeStore(emptyStore())).store,head='a'.repeat(40),sha='b'.repeat(40);
 const repository={async history(snapshot){assert.equal(snapshot.head,head);assert.equal(snapshot.sha,sha);return {events:[],indexed:true};}};
 const service=createCatalogueService({base,initial,initialSnapshot:{head,sha},repository,makeMeta:()=>({id:'unused',at:iso})});
 assert.equal((await service.history({})).indexed,true);
});

test('service owns authorization, previews, immutable snapshots and one projected view',async()=>{
 const f=fixture(),before=f.service.snapshot;
 assert.throws(()=>{before.store.records.bad={};},TypeError);
 const preview=f.service.preview(edit('a',{title:'Draft'}));
 assert.equal(preview.records.a.values.title,'Draft');assert.deepEqual(f.service.snapshot,before);
 await assert.rejects(f.service.execute(edit('a',{title:'Saved'}),'修改名称'),/连接/);
 await f.service.connect(f.repository);
 await f.service.execute(edit('a',{title:'Saved'}),'修改名称');
 assert.equal(f.service.view.byId.get('a').title,'Saved');assert.equal((await f.service.history({})).events.length,1);
 f.service.disconnect(f.repository);assert.equal(f.service.actor,'');
 assert.equal(f.service.view.byId.get('a').title,'Saved');
});

test('uncertain response retries keep the same operation ID after later remote edits',async()=>{
 const f=fixture();await f.service.connect(f.repository);
 const write=f.repository.write.bind(f.repository),read=f.repository.read.bind(f.repository);let failRead=false,interrupted=true;
 f.repository.write=async(...args)=>{
  const result=await write(...args);
  if(interrupted){interrupted=false;
   f.replace(applyChange(f.store,base,edit('b',{title:'Remote B'}),{id:'remote-operation',at:iso,actor:'other',reason:'远程修改',expectedRevision:f.store.revision}));
   failRead=true;throw Error('response interrupted');
  }return result;
 };
 f.repository.read=async()=>{if(failRead){failRead=false;throw Error('read unavailable');}return read();};
 const action=edit('a',{title:'Local A'});
 await assert.rejects(f.service.execute(action,'本地修改'),/interrupted/);
 const operation=f.service.pendingOperation.id;
 const result=await f.service.execute(action,'本地修改');
 assert.equal(result.alreadyApplied,true);assert.equal(f.writes.length,1);
 assert.equal(f.store.journal.events.filter(event=>event.id===operation).length,1);
 assert.equal(f.service.view.byId.get('b').title,'Remote B');assert.equal(f.service.pendingOperation,null);
});

test('the same operation ID cannot be reused for a different intent or actor',async()=>{
 const f=fixture();await f.service.connect(f.repository);
 await f.service.execute(edit('a',{title:'Saved'}),'修改名称');
 const {commitBasicCommand}=await import('../src/application/catalogue/commands.mjs');
 const event=f.store.journal.events[0];
 await assert.rejects(commitBasicCommand({repository:f.repository,snapshot:{store:emptyStore()},base,action:edit('b',{title:'Wrong'}),meta:event}),/操作ID/);
 assert.equal(f.writes.length,1);
});

test('transport error can be confirmed even after another operation has advanced the snapshot',async()=>{
 const f=fixture();await f.service.connect(f.repository);
 const write=f.repository.write.bind(f.repository);
 f.repository.write=async(...args)=>{await write(...args);f.replace(applyChange(f.store,base,edit('b',{group:'New B'}),{id:'remote',at:iso,actor:'other',reason:'厂商更正',expectedRevision:f.store.revision}));throw Object.assign(Error('server response lost'),{status:502});};
 const result=await f.service.execute(edit('a',{title:'Saved A'}),'作品更正');
 assert.equal(result.verifiedAfterError,true);assert.equal(f.store.revision,2);
 assert.equal(f.service.view.byId.get('b').group,'New B');assert.equal(f.writes.length,1);
});

test('failed connection and sync retain the prior snapshot and active repository',async()=>{
 const f=fixture();await f.service.connect(f.repository);const before=f.service.snapshot;
 await assert.rejects(f.service.connect({connect:async()=>'bad',read:async()=>({store:{schemaVersion:99}})}));
 assert.equal(f.service.actor,'tester');assert.deepEqual(f.service.snapshot,before);
 await f.service.execute(edit('a',{title:'Still working'}),'核对资料');assert.equal(f.writes.length,1);
 const after=f.service.snapshot,read=f.repository.read;f.repository.read=async()=>{throw Error('offline');};
 await assert.rejects(f.service.sync(),/offline/);assert.deepEqual(f.service.snapshot,after);f.repository.read=read;
});

test('service rejects overlapping operations and always unlocks after failure',async()=>{
 const f=fixture();await f.service.connect(f.repository);
 let release;const hold=new Promise(resolve=>release=resolve),write=f.repository.write.bind(f.repository);
 f.repository.write=async(...args)=>{await hold;return write(...args);};
 const pending=f.service.execute(edit('a',{title:'Saved'}),'核对资料');
 await assert.rejects(f.service.sync(),error=>error.code==='BUSY');
 await assert.rejects(f.service.execute(edit('b',{title:'Other'}),'核对资料'),error=>error.code==='BUSY');
 release();await pending;assert.equal(f.service.busy,false);
});

test('added works and undo commands remain idempotent after leaving the three-operation shortcut window',async()=>{
 const {commitBasicCommand}=await import('../src/application/catalogue/commands.mjs');
 const f=fixture();await f.service.connect(f.repository);
 const opened=f.service.snapshot,action={type:'add',works:[{id:'manual-once',...valuesOf({...base[0],title:'One manual work'})}]};
 await f.service.execute(action,'添加作品');
 const original=f.store.journal.events[0];
 for(let i=0;i<5;i++)f.replace(applyChange(f.store,base,edit('a',{title:'Remote '+i}),{id:'remote-'+i,at:iso,actor:'other',reason:'其他更正',expectedRevision:f.store.revision}));
 const repeated=await commitBasicCommand({repository:f.repository,snapshot:opened,base,action,meta:original});
 assert.equal(repeated.result.alreadyApplied,true);assert.equal(f.store.additions.length,1);assert.equal(f.writes.length,1);
 await f.service.sync();const beforeUndo=f.service.snapshot;
 await f.service.execute(null,'撤销操作',{undo:true});const undo=f.store.journal.events.at(-1);
 f.replace(applyChange(f.store,base,edit('b',{title:'Later B'}),{id:'later',at:iso,actor:'other',reason:'后续更正',expectedRevision:f.store.revision}));
 const duplicateUndo=await commitBasicCommand({repository:f.repository,snapshot:beforeUndo,base,action:null,meta:undo,undo:true});
 assert.equal(duplicateUndo.result.alreadyApplied,true);assert.equal(f.writes.length,2);
 assert.equal(f.store.records.b.values.title,'Later B');assert.equal(f.store.records.a.values.title,'Remote 3');
});
