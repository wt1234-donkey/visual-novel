import test from 'node:test';
import assert from 'node:assert/strict';
import {emptyStore,upgradeStore,validateStore,applyChange,undoLast,valuesOf} from '../basic-catalogue-model.mjs';
import {catalogueState,replayJournal,journalHistory,journalKey} from '../src/domain/catalogue/journal.mjs';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';

const base=[{id:'a',title:'Alpha',year:1990,group:'A',gameplay:'ADV'},{id:'b',title:'Beta',year:2000,group:'B',gameplay:'ADV'}];
const meta=(store,extra={})=>({id:'operation-'+(store.revision+1),at:'2026-11-11T09:00:00Z',actor:'test',reason:'核对作品资料',expectedRevision:store.revision,...extra});
const change=(store,action)=>applyChange(store,base,action,meta(store));
const edit=(id,patch)=>({type:'edit',id,values:{...valuesOf(base.find(work=>work.id===id)),...patch}});

test('checkpoint migration preserves current state, existing undo and original inputs',()=>{
 const legacy=change(emptyStore(),edit('a',{title:'Existing edit'})),original=structuredClone(legacy);
 const current=upgradeStore(legacy);
 assert.equal(current.schemaVersion,2);assert.equal(current.revision,legacy.revision);
 assert.deepEqual(catalogueState(current),legacy);
 assert.deepEqual(current.journal.baseline,legacy);assert.deepEqual(current.journal.events,[]);
 assert.deepEqual(upgradeStore(current),current);assert.deepEqual(legacy,original);
 const undone=undoLast(current,current.revision,meta(current));
 assert.equal(undone.journal.events[0].commandType,'undo');
 assert.equal(undone.journal.events[0].undoOf,legacy.recent[0].id);
 assert.deepEqual(undone.records,{});
});

test('journal survives more than three operations and all shortcut undos remain new events',()=>{
 let store=upgradeStore(emptyStore());
 for(let i=0;i<6;i++)store=change(store,edit('a',{title:'Title '+i}));
 assert.equal(store.recent.length,3);assert.equal(store.journal.events.length,6);
 const history=journalHistory(store,{limit:2});
 assert.deepEqual(history.events.map(event=>event.revision),[6,5]);
 assert.equal(history.nextBefore,5);
 assert.deepEqual(journalHistory(store,{before:history.nextBefore,limit:2}).events.map(event=>event.revision),[4,3]);
 assert.equal(journalHistory(store,{workId:'b'}).events.length,0);
 for(let i=0;i<3;i++)store=undoLast(store,store.revision,meta(store));
 assert.equal(store.journal.events.length,9);assert.equal(store.recent.length,0);
 assert.equal(store.records.a.values.title,'Title 2');
 assert.deepEqual(replayJournal(store.journal,validateStore),catalogueState(store));
 assert.deepEqual(validateStore(JSON.parse(JSON.stringify(store))),store);
});

test('add, merge, detach and delete have replayable before and after records',()=>{
 let store=upgradeStore(emptyStore());
 store=change(store,{type:'add',works:[{id:'manual-one',...valuesOf({...base[0],title:'Manual'})}]});
 store=change(store,{type:'merge',mainId:'a',ids:['manual-one'],relation:{type:'unverified',label:'版本'}});
 store=change(store,{type:'detach',id:'manual-one'});
 store=change(store,{type:'delete',id:'manual-one'});
 store=undoLast(store,store.revision,meta(store));
 assert.equal(store.journal.events[0].added[0].title,'Manual');
 assert.equal(store.journal.events[1].changes.find(row=>row.id==='manual-one').after.relation.type,'unverified');
 assert.deepEqual(replayJournal(store.journal,validateStore),catalogueState(store));
});

test('undoing a batch addition records the removed identities and rebuilds its exact state',()=>{
 let store=upgradeStore(emptyStore());
 store=change(store,{type:'add',works:['one','two'].map(id=>({id:'manual-'+id,...valuesOf({...base[0],title:id})}))});
 store=undoLast(store,store.revision,meta(store));
 assert.deepEqual(store.journal.events[1].removed.map(work=>work.id),['manual-one','manual-two']);
 assert.deepEqual(store.additions,[]);assert.equal(store.journal.events.length,2);
 assert.deepEqual(replayJournal(store.journal,validateStore),catalogueState(store));
});

test('corruption, revision gaps, duplicate operation IDs and mismatched snapshots reject the entire journal',()=>{
 const store=change(upgradeStore(emptyStore()),edit('a',{title:'Changed'}));
 for(const corrupt of [
  s=>s.records.a.values.title='Unlogged',
  s=>s.journal.events[0].previousRevision=99,
  s=>s.journal.events[0].changes[0].before={deleted:true},
  s=>s.journal.events.push(structuredClone(s.journal.events[0])),
  s=>s.journal.events[0].intent.type='delete',
  s=>s.journal.events[0].id='__proto__',
  s=>delete s.journal
 ]){const bad=structuredClone(store);corrupt(bad);assert.throws(()=>validateStore(bad));}
 assert.throws(()=>applyChange(store,base,edit('b',{title:'Other'}),meta(store,{id:store.journal.events[0].id})),/日志/);
 assert.throws(()=>validateStore({...store,schemaVersion:3}),/格式/);
});

test('committed migration retains every existing correction and identity from the phase one checkpoint',()=>{
 const current=JSON.parse(readFileSync(new URL('../data/basic-catalogue-edits.json',import.meta.url)));
 validateStore(current);assert.equal(current.schemaVersion,2);
 // SHA-256 of the canonical schema-1 state at bc123909, independently
 // checked during migration; no Git-history dependency in shallow CI jobs.
 assert.equal(createHash('sha256').update(journalKey(current.journal.baseline)).digest('hex'),
  '91c1446f7266c5e04ce7ef46c1c9f60b7d226021d9ca2ddc48c8fed7dacc43c2');
 // Future entries change the current state, while retaining the reviewed checkpoint.
 assert.equal(current.journal.baseline.revision,30);
});
