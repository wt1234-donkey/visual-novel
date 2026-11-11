import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {emptyStore,upgradeStore,applyChange,valuesOf,undoLast,validateStore} from '../basic-catalogue-model.mjs';
import {catalogueState} from '../src/domain/catalogue/journal.mjs';
import {MAX_SHARD_BYTES} from '../src/domain/catalogue/journal-index.mjs';
import {readBasicStoreSync,readBasicJournalSync,saveBasicStoreSync} from '../src/infrastructure/filesystem/basic-store.mjs';
import {migrateBasicStorage} from '../scripts/migrate_basic_storage.mjs';
import {split,stateHash} from './helpers/catalogue-git-fixture.mjs';

const base=[{id:'a',title:'Alpha',year:1990,group:'A',gameplay:'ADV'}];
const meta=store=>({id:'op-'+(store.revision+1),at:'2026-11-11T10:00:00Z',actor:'test',reason:'核对资料',expectedRevision:store.revision});
const edit=(store,title)=>applyChange(store,base,{type:'edit',id:'a',values:{...valuesOf(base[0]),title}},meta(store));
function fixture(t,initial=upgradeStore(emptyStore())){
 const root=mkdtempSync(join(tmpdir(),'catalogue-storage-'));t.after(()=>rmSync(root,{recursive:true,force:true}));mkdirSync(join(root,'data'));
 writeFileSync(join(root,'data/basic-catalogue-edits.json'),JSON.stringify(initial));return root;
}

test('split migration preserves the reviewed checkpoint, current state and shortcut undo',t=>{
 const original=edit(upgradeStore(emptyStore()),'Before migration'),root=fixture(t,original);
 const result=migrateBasicStorage(root,{write:true});assert.equal(result.schemaVersion,3);
 const current=readBasicStoreSync(root),hydrated=readBasicJournalSync(root);
 assert.deepEqual(catalogueState(current),catalogueState(original));
 assert.deepEqual(hydrated,original);assert.equal(current.journal.shards.length,1);
 assert.equal(Object.hasOwn(current.journal,'events'),false);
 assert.equal(migrateBasicStorage(root,{write:true}).changed,false);
 const restored=saveBasicStoreSync(root,undoLast(current,current.revision,meta(current)));
 assert.deepEqual(restored.records,{});assert.equal(readBasicJournalSync(root).journal.events.length,2);
});

test('many operations are bounded by event count and preserve a complete replay',t=>{
 let original=upgradeStore(emptyStore());for(let i=0;i<105;i++)original=edit(original,'Work '+i);
 const root=fixture(t,original);migrateBasicStorage(root,{write:true});
 let store=readBasicStoreSync(root);
 assert.ok(store.journal.shards.length>=3);
 assert.ok(store.journal.shards.every(shard=>shard.operationIds.length<=50&&shard.bytes<=MAX_SHARD_BYTES));
 const sealed=store.journal.shards[0],bytes=readFileSync(join(root,sealed.path),'utf8');
 const oldActive=store.journal.shards.at(-1).path;
 store=saveBasicStoreSync(root,edit(store,'After split'));
 assert.equal(store.transaction,undefined);assert.equal(store.revision,106);
 assert.equal(readFileSync(join(root,sealed.path),'utf8'),bytes);
 assert.throws(()=>readFileSync(join(root,oldActive)),/ENOENT/);
 assert.deepEqual(catalogueState(readBasicJournalSync(root)),catalogueState(store));
 assert.equal(readBasicJournalSync(root).journal.events.length,106);
});

test('pending transactions validate locally and cannot modify the archive index',t=>{
 const root=fixture(t);migrateBasicStorage(root,{write:true});const current=readBasicStoreSync(root);
 const next=edit(current,'Pending');validateStore(next);
 assert.equal(next.transaction.events.length,1);assert.equal(next.journal.stateHash,stateHash(current));
 const bad=structuredClone(next);bad.records.a.values.title='Unlogged';assert.throws(()=>validateStore(bad),/事务/);
 const changedIndex=structuredClone(next);changedIndex.journal.baseline.sha='b'.repeat(40);
 assert.throws(()=>saveBasicStoreSync(root,changedIndex),/事务/);
 assert.throws(()=>saveBasicStoreSync(root,readBasicJournalSync(root)),/降级/);
 assert.deepEqual(saveBasicStoreSync(root,current),current);
 assert.equal(readBasicStoreSync(root).revision,0);
});

test('byte limits split small batches and retain an oversized atomic event intact',t=>{
 let original=upgradeStore(emptyStore());
 for(const [batch,count] of [[1,60],[2,60],[3,150]]){
  const works=Array.from({length:count},(_,i)=>({id:'manual-b'+batch+'-'+i,title:'Batch '+batch+' work '+i,firstYear:1990,group:'中'.repeat(500),gameplay:'文'.repeat(500),plotStyles:[],source:''}));
  original=applyChange(original,base,{type:'add',works},meta(original));
 }
 const root=fixture(t,original);migrateBasicStorage(root,{write:true});
 const store=readBasicStoreSync(root),shards=store.journal.shards;
 assert.equal(shards.length,3);assert.ok(shards.slice(0,2).every(shard=>shard.bytes<MAX_SHARD_BYTES));
 assert.ok(shards[0].bytes+shards[1].bytes>MAX_SHARD_BYTES);
 assert.ok(shards[2].bytes>MAX_SHARD_BYTES);assert.equal(shards[2].operationIds.length,1);
 assert.deepEqual(readBasicJournalSync(root),original);
});

test('digest mismatches, missing archives and invalid reference paths stop full audit',t=>{
 const root=fixture(t,edit(upgradeStore(emptyStore()),'Saved'));migrateBasicStorage(root,{write:true});
 const store=readBasicStoreSync(root),ref=store.journal.shards[0],path=join(root,ref.path),text=readFileSync(path,'utf8');
 writeFileSync(path,text+' ');assert.throws(()=>readBasicStoreSync(root),/摘要/);writeFileSync(path,text);
 rmSync(path);assert.throws(()=>readBasicStoreSync(root),/ENOENT/);
 const bad=structuredClone(store);bad.journal.baseline.path='../outside.json';assert.throws(()=>validateStore(bad),/索引/);
});
