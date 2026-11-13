import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,rmSync,readdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,dirname} from 'node:path';
import {spawnSync} from 'node:child_process';
import {editableValues,projectWork,saveEdit,saveCreatorNames,undoEdit,validateHistory} from '../work-edit-model.mjs';
import {formalState,upgradeFormalHistory,formalHistoryPage,replayFormalJournal,formalOperation} from '../src/domain/catalogue/formal-journal.mjs';
import {createFormalCommandSession,commitFormalCommand,applyFormalCommand} from '../src/application/catalogue/formal-commands.mjs';
import {planCommand} from '../src/application/commands/execute.mjs';
import {executeCommand,receiptPath} from '../src/infrastructure/filesystem/command-executor.mjs';
import {sourceLeaseSync} from '../src/infrastructure/filesystem/effective-catalogue.mjs';
import {emptyStore} from '../src/domain/catalogue/model.mjs';
import {buildEffectiveCatalogue} from '../src/domain/catalogue/effective.mjs';
const read=name=>JSON.parse(readFileSync(new URL('../data/'+name+'.json',import.meta.url)));
const base=read('games').works.find(w=>w.id==='g039'),other=read('games').works.find(w=>w.id==='g001'),taxonomy=read('taxonomy');
const empty=()=>({schemaVersion:1,records:{}});
const meta=(n,revision)=>({id:'formal-test-'+n,actor:'tester',at:'2026-11-13T02:00:00Z',expectedRevision:revision,reason:'核对完整正式作品历史 '+n,sources:[base.source]});
const edit=(store,n,work=base)=>saveEdit(store,work,{...editableValues(projectWork(work,store)),notes:'核对后的完整正式备注 '+n},meta(n,store.records[work.id]?.revision||0),taxonomy,[base,other]);
const lease={schemaVersion:1,files:{'data/source.json':'a'.repeat(40)}};
const command=(store,n)=>({schemaVersion:1,kind:'formal',actor:'tester',operationId:'command-'+n,at:'2026-11-13T02:00:00Z',reason:'核对完整正式作品历史',sources:[base.source],expectedRevision:store.records[base.id]?.revision||0,sourceLease:lease,action:{type:'edit',workId:base.id,values:{...editableValues(projectWork(base,store)),notes:'原命令备注 '+n}}});

test('migration retains current projection, identities and all evidenced legacy snapshots without inventing events',()=>{
 const current=read('work-edit-history'),legacy=structuredClone(current.journal.baseline),before=structuredClone(legacy);
 const next=upgradeFormalHistory(legacy,{at:'2026-11-13T02:00:00Z',sourceCommit:'a'.repeat(40)});
 assert.deepEqual(formalState(next),legacy);assert.deepEqual(legacy,before);assert.deepEqual(next.journal.events,[]);
 const inputs={main:read('games'),supplement:read('non-rpg-creator-supplement-20261030'),basicStore:read('basic-catalogue-edits')};
 assert.deepEqual(buildEffectiveCatalogue({...inputs,history:legacy}),buildEffectiveCatalogue({...inputs,history:next}));
 const id=Object.keys(legacy.records)[0],page=formalHistoryPage(next,{workId:id});
 assert.equal(page.events.length,0);assert.deepEqual(page.legacyRecent,legacy.records[id].recent);
});

test('47 same-work edits and interleaved works remain fully queryable after reload and across 20-event pages',()=>{
 let store=empty();for(let n=1;n<=47;n++){store=edit(store,n);if(n%10===0)store=edit(store,'other-'+n,other);}
 store=JSON.parse(JSON.stringify(store));assert.equal(store.records[base.id].recent.length,3);
 let before=Infinity,ids=[];do{const page=formalHistoryPage(store,{workId:base.id,before});assert.equal(page.total,47);ids.push(...page.events.map(e=>e.id));before=page.nextBefore;}while(before!==null);
 assert.equal(ids.length,47);assert.equal(new Set(ids).size,47);assert.equal(ids[0],'formal-test-47');assert.equal(ids.at(-1),'formal-test-1');
 assert.deepEqual(replayFormalJournal(store.journal),formalState(store));assert.ok(validateHistory(store,[base,other],taxonomy));
 const prior=formalHistoryPage(store,{workId:base.id});store=edit(store,48);
 assert.equal(formalHistoryPage(store,{workId:base.id,before:prior.nextBefore}).events[0].id,'formal-test-27');
 for(const options of [{limit:0},{limit:101},{before:0}])assert.throws(()=>formalHistoryPage(store,{workId:base.id,...options}));
});

test('undo appends an independent event, keeps cancelled edits and replays exactly to current state',()=>{
 let store=empty();for(let n=1;n<=6;n++)store=edit(store,n);const previous=structuredClone(store.journal.events);
 store=undoEdit(store,base,'formal-test-4',6,taxonomy,[base],meta('undo',6));
 assert.equal(store.records[base.id].revision,7);assert.equal(projectWork(base,store).notes,'核对后的完整正式备注 3');
 assert.deepEqual(store.journal.events.slice(0,6),previous);
 const last=store.journal.events.at(-1);assert.equal(last.commandType,'undo');assert.equal(last.undoOf,'formal-test-4');assert.equal(last.id,'formal-test-undo');
 assert.equal(formalHistoryPage(store,{workId:base.id}).total,7);assert.deepEqual(replayFormalJournal(store.journal),formalState(store));
 assert.ok(validateHistory(store,[base],taxonomy));assert.throws(()=>undoEdit(store,base,'formal-test-3',7,taxonomy,[base]),/独立操作ID/);
});

test('legacy quick undo at a checkpoint is a new event with its own actor and target',()=>{
 const saved=edit(empty(),1),legacy=formalState(saved),store=upgradeFormalHistory(legacy,{at:'2026-11-13T02:00:00Z'});
 const result=undoEdit(store,base,'formal-test-1',1,taxonomy,[base],meta('legacy-undo',1));
 assert.equal(result.journal.events.length,1);assert.equal(result.journal.events[0].undoOf,'formal-test-1');
 assert.deepEqual(result.journal.baseline,legacy);assert.deepEqual(replayFormalJournal(result.journal),formalState(result));
});

test('replay rejects gaps, reused operation IDs, false undo targets and snapshot or event tampering',()=>{
 let store=edit(edit(empty(),1),2);store=undoEdit(store,base,'formal-test-2',2,taxonomy,[base],meta('undo',2));
 const mutations=[s=>s.journal.events[1].sequence++,s=>s.journal.events[1].id=s.journal.events[0].id,
  s=>s.journal.events[1].before=null,s=>s.journal.events[2].undoOf='unrelated',
  s=>s.records[base.id].overrides.notes='伪造当前快照',s=>s.journal.events[0].intent.values.notes='伪造命令',
  s=>s.journal.events[0].after.overrides.firstYear=2000,s=>s.journal.events[1].actor=''];
 for(const mutate of mutations){const changed=structuredClone(store);mutate(changed);assert.throws(()=>validateHistory(changed,[base],taxonomy));}
});

test('same domain operation retried after a later edit confirms only once and rejects different content',()=>{
 const first=edit(empty(),1),later=edit(first,2),original=first.journal.events[0];
 const result=saveEdit(later,base,original.values.after,meta(1,0),taxonomy,[base]);assert.deepEqual(result,later);assert.equal(result.journal.events.length,2);
 assert.throws(()=>saveEdit(later,base,{...original.values.after,notes:'同ID其他内容'},meta(1,0),taxonomy,[base]),error=>error.code==='OPERATION_CONFLICT');
});

test('lost legacy response followed by another editor update retries the immutable operation before current guards',async()=>{
 const session=createFormalCommandSession(),opened={store:empty(),sha:'old'},original=command(opened.store,1);let state=opened.store,writes=0,failConfirmation=false;
 const repository={commandMode:'legacy',async read(options){if(failConfirmation){failConfirmation=false;throw Error('reconciliation network unavailable');}return {store:structuredClone(state),sha:'current',head:'later-head'};},
  async write(next){writes++;state=edit(next,'later-editor');failConfirmation=true;throw Error('write response lost');}};
 const seen=[];const run=cmd=>{seen.push(structuredClone(cmd));return commitFormalCommand({repository,opened,command:cmd,base,taxonomy,works:[base]});};
 await assert.rejects(()=>session.execute(original,run),/response lost/);const later=structuredClone(state);
 const attempted={...original,operationId:'fresh-id-must-not-be-used',at:'2026-11-14T00:00:00Z',sourceLease:{schemaVersion:1,files:{different:'b'.repeat(40)}}};
 const result=await session.execute(attempted,run);
 assert.deepEqual(seen,[original,original]);assert.equal(writes,1);assert.deepEqual(result.store,later);assert.equal(result.revision,1);assert.equal(result.operationId,original.operationId);assert.equal(result.alreadyApplied,true);assert.equal(session.pending(base.id).length,0);
});

test('an unapplied stale operation is rejected and cannot replace a later edit',async()=>{
 const opened={store:empty(),sha:'old'},state=edit(empty(),'another'),before=structuredClone(state);let writes=0;
 const repository={commandMode:'legacy',read:async()=>({store:structuredClone(state),sha:'new'}),write:async()=>{writes++;}};
 await assert.rejects(()=>commitFormalCommand({repository,opened,command:command(opened.store,1),base,taxonomy,works:[base]}),error=>error.code==='CATALOGUE_CONFLICT');
 assert.equal(writes,0);assert.deepEqual(state,before);
});

test('trusted formal retry returns the original receipt before new source/revision checks',()=>{
 const c={sourceLease:lease,formalWorks:[base],reservedWorks:[base],formalStore:empty(),taxonomy},first=command(empty(),1),result=planCommand(first,c,'tester');
 const later=edit(result.store,'later-editor');const retry=planCommand(first,{receipt:result.receipt,formalStore:later,sourceLease:{files:{}}},'tester');
 assert.equal(retry.alreadyApplied,true);assert.equal(retry.receipt.revision,1);assert.equal(later.records[base.id].revision,2);
 assert.throws(()=>planCommand({...first,action:{...first.action,values:{...first.action.values,notes:'换内容'}}},{receipt:result.receipt},'tester'),error=>error.code==='OPERATION_CONFLICT');
});

test('filesystem executor stages audit, current state and receipt together; duplicate retry leaves all files unchanged',()=>{
 const root=mkdtempSync(join(tmpdir(),'formal-audit-'));
 try{
  const put=(path,value)=>{mkdirSync(dirname(join(root,path)),{recursive:true});writeFileSync(join(root,path),JSON.stringify(value));};
  put('data/main-adv-rpg-works-20261031.json',{works:[],summary:{accepted:0}});
  for(const file of ['adv-rpg-minimal-index-20261031','adv-rpg-next-studio-review-20261031','adv-rpg-round3-review-20261031'])put('data/'+file+'.json',{records:[]});
  put('data/games.json',{works:[base]});put('data/non-rpg-creator-supplement-20261030.json',{works:[]});put('data/work-edit-history.json',empty());put('data/company-coverage.json',{companies:[]});put('data/taxonomy.json',taxonomy);put('data/basic-catalogue-edits.json',emptyStore());
  const first={...command(empty(),1),sourceLease:sourceLeaseSync(root)},result=executeCommand(root,first,'tester');
  assert.deepEqual(result.paths,['data/work-edit-history.json',receiptPath(first.operationId)]);
  const second={...command(result.store,2),sourceLease:sourceLeaseSync(root)};executeCommand(root,second,'tester');
  const file=join(root,'data/work-edit-history.json'),before=readFileSync(file,'utf8');
  assert.equal(executeCommand(root,first,'tester').alreadyApplied,true);assert.equal(readFileSync(file,'utf8'),before);
  assert.equal(JSON.parse(before).journal.events.length,2);assert.equal(readdirSync(join(root,'data/command-receipts')).length,2);
 }finally{rmSync(root,{recursive:true,force:true});}
});

test('Python independently replays JS edits and undo, and rejects an altered historical event',()=>{
 let store=empty();for(let n=1;n<=5;n++)store=edit(store,n);store=undoEdit(store,base,'formal-test-4',5,taxonomy,[base],meta('undo',5));
 const code="import json,sys;sys.path.insert(0,'scripts');from validate_work_edits import validate;validate(json.load(sys.stdin))";
 const valid=spawnSync('python3',['-c',code],{input:JSON.stringify(store),encoding:'utf8'});assert.equal(valid.status,0,valid.stderr);
 const altered=structuredClone(store);altered.journal.events[1].before={};
 assert.notEqual(spawnSync('python3',['-c',code],{input:JSON.stringify(altered),encoding:'utf8'}).status,0);
});

test('pending operations survive a page reload without credentials and retain their original ID and lease',async()=>{
 const items=new Map(),storage={getItem:key=>items.get(key)||null,setItem:(key,value)=>items.set(key,value),removeItem:key=>items.delete(key)};
 const original=command(empty(),1),first=createFormalCommandSession({storage});
 await assert.rejects(()=>first.execute(original,async()=>{throw Error('response interrupted');}));
 const recovered=createFormalCommandSession({storage});assert.deepEqual(recovered.pending(base.id),[original]);
 const result=await recovered.execute({...original,operationId:'replacement',at:'2026-11-14T00:00:00Z'},async saved=>saved);
 assert.deepEqual(result,original);assert.equal(items.size,0);assert.ok(!JSON.stringify([...items]).includes('credential'));
 await assert.rejects(()=>recovered.execute({...original,token:'must-never-persist'},async()=>assert.fail()),/未允许字段/);
});
