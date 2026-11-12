import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,rmSync} from 'node:fs';
import {join,dirname} from 'node:path';
import {tmpdir} from 'node:os';
import {validateCommand,validateBasicAction,commandText} from '../src/application/commands/envelope.mjs';
import {planCommand} from '../src/application/commands/execute.mjs';
import {submitCommand} from '../src/infrastructure/github/command-transport.mjs';
import {dispatchReference} from '../scripts/execute_catalogue_command.mjs';
import {emptyStore,upgradeStore,valuesOf} from '../src/domain/catalogue/model.mjs';
import {editableValues} from '../work-edit-model.mjs';
import {gitFixture} from './helpers/catalogue-git-fixture.mjs';
import {receiptPath,executeCommand} from '../src/infrastructure/filesystem/command-executor.mjs';
import {sourceLeaseSync} from '../src/infrastructure/filesystem/effective-catalogue.mjs';
import {readBasicStoreSync} from '../src/infrastructure/filesystem/basic-store.mjs';
import {saveMode} from '../src/application/commands/policy.mjs';
import {parseStyleUpdates,STYLE_UPDATE_HEADERS} from '../src/application/catalogue/imports.mjs';
import {styleReviewRows} from '../basic-style-review.mjs';
const read=name=>JSON.parse(readFileSync(new URL('../data/'+name,import.meta.url)));
const work=read('games.json').works.find(work=>work.id==='g039'),taxonomy=read('taxonomy.json');
const row={id:'i1',matchedWorkId:'w1',title:'One',firstYear:1965,year:1965,group:'Maker',gameplay:'ADV',plotStyles:[],source:'https://example.org/one'};
const lease={schemaVersion:1,files:{'data/source.json':'a'.repeat(40),'src/validator.mjs':'b'.repeat(40)}};
const context=()=>({sourceLease:lease,basicRows:[row],basicStore:upgradeStore(emptyStore()),formalWorks:[work],reservedWorks:[work],formalStore:{schemaVersion:1,records:{}},taxonomy});
const basic=(action={type:'edit',id:'w1',values:{...valuesOf(row),title:'Changed'}})=>({schemaVersion:1,operationId:'test-command-1',kind:'basic',actor:'tester',at:'2026-11-12T01:00:00Z',reason:'更正基础资料',sources:[],expectedRevision:0,sourceLease:lease,action});
const formal=(action)=>({...basic(),kind:'formal',action});
test('one trusted basic edit validates against server data and preserves the input snapshot',()=>{
 const c=context(),before=structuredClone(c.basicStore),result=planCommand(basic(),c,'tester');
 assert.equal(result.store.records.w1.values.title,'Changed');assert.deepEqual(c.basicStore,before);assert.equal(result.receipt.actor,'tester');assert.equal(result.receipt.revision,1);
});
test('unknown fields, hidden payloads, forged actors, incomplete leases and stale revisions are rejected before persistence',()=>{
 const invalid=[{...basic(),arbitrary:'x'},basic({type:'edit',id:'w1',values:{...valuesOf(row),firstYear:1965,protectedIdentity:'new'}}),{...basic(),actor:'forged'},
  {...basic(),sourceLease:{schemaVersion:1,files:{'data/source.json':'a'.repeat(40)}}},{...basic(),expectedRevision:8},JSON.parse(JSON.stringify(basic()).replace('"reason":','"__proto__":{},"reason":'))];
 for(const command of invalid)assert.throws(()=>planCommand(command,context(),'tester'));
});
test('same operation confirms existing result after later edits; reuse with different payload fails',()=>{
 const command=basic(),result=planCommand(command,context(),'tester');
 const later={receipt:result.receipt,basicStore:{revision:99},sourceLease:{files:{different:'c'.repeat(40)}}};
 assert.equal(planCommand(command,later,'tester').alreadyApplied,true);assert.equal(later.basicStore.revision,99);
 assert.throws(()=>planCommand({...command,reason:'换一套内容'},later,'tester'),error=>error.code==='OPERATION_CONFLICT');
});
test('bulk, CSV and AI-confirmed tags share the same controlled tag validation',()=>{
 const tags={tone:'轻松'};
 const result=planCommand(basic({type:'style-update',rows:[{id:'w1',title:'One',mode:'set',tags}]}),context(),'tester');
 assert.ok(result.store.records.w1.style);
 assert.throws(()=>validateBasicAction({type:'style-update',rows:[{id:'w1',mode:'set',tags:{tone:'not-a-tag'}}]}));
 assert.throws(()=>validateBasicAction({type:'style-update',rows:[{id:'w1',mode:'set',tags,evidence:{},extra:'x'}]}));
 assert.throws(()=>validateBasicAction({type:'style-update',rows:[{id:'w1',mode:'set',tags},{id:'w1',mode:'append',tags}]}));
});
test('actual CSV parsing and AI-selected rows pass the common command without changing their formats',()=>{
 const cells=STYLE_UPDATE_HEADERS.map((_,index)=>index===0?'w1':index===1?'One':index===2?'轻松':'');
 const csv=STYLE_UPDATE_HEADERS.join(',')+'\n'+cells.join(',');
 assert.equal(planCommand(basic({type:'style-update',rows:parseStyleUpdates(csv)}),context(),'tester').receipt.revision,1);
 const item={id:'w1',title:'One',model:'manual-confirmed',candidates:[{dimension:'tone',tag:'轻松',quote:'轻松叙事',source:row.source}]};
 const rows=styleReviewRows([item],new Map([['w1',new Set(['轻松'])]]));
 assert.equal(planCommand(basic({type:'style-update',rows}),context(),'tester').receipt.revision,1);
});
test('only an explicit valid policy switches the writer; malformed policies never silently select legacy',()=>{
 assert.equal(saveMode(undefined),'legacy');assert.equal(saveMode({schemaVersion:1,mode:'trusted'}),'trusted');
 for(const policy of [null,{schemaVersion:2,mode:'trusted'},{schemaVersion:1,mode:'trussted'}])assert.throws(()=>saveMode(policy));
});
test('formal creator names still need no evidence; protected fields and mixed unproved changes fail',()=>{
 const names={writerNames:['作者甲'],artistNames:[],musicianNames:[]};
 const result=planCommand(formal({type:'creators',workId:work.id,names}),context(),'tester');
 assert.deepEqual(result.store.records[work.id].recent[0].sources,[]);
 assert.throws(()=>planCommand(formal({type:'creators',workId:work.id,names:{...names,title:'hidden'}}),context(),'tester'));
 assert.throws(()=>planCommand(formal({type:'edit',workId:work.id,values:{...editableValues(work),notes:'未经证明的同时修改'}}),context(),'tester'));
 assert.throws(()=>planCommand(formal({type:'edit',workId:work.id,values:{...editableValues(work),firstYear:2000}}),context(),'tester'));
});
test('basic undo is bound to the exact operation instead of silently undoing a newer save',()=>{
 const c=context(),saved=planCommand(basic(),c,'tester');c.basicStore=saved.store;
 assert.throws(()=>planCommand({...basic({type:'undo',targetId:'another-operation'}),operationId:'undo',expectedRevision:1},c,'tester'));
 const undone=planCommand({...basic({type:'undo',targetId:basic().operationId}),operationId:'undo',expectedRevision:1},c,'tester');
 assert.equal(undone.store.revision,2);assert.equal(undone.store.records.w1,undefined);
});
test('dispatch identity and blob references cannot redirect the executor to another repository, code ref or actor',()=>{
 const event={repository:{full_name:'wt1234-donkey/visual-novel'},action:'catalogue-command-v1',sender:{login:'tester'},client_payload:{schemaVersion:1,operationId:'one',commandSha:'a'.repeat(40)}};
 assert.equal(dispatchReference(event).actor,'tester');
 for(const changed of [{...event,repository:{full_name:'other/repo'}},{...event,client_payload:{...event.client_payload,ref:'untrusted'}},{...event,sender:{}}])assert.throws(()=>dispatchReference(changed));
});
test('transport reconciles a lost dispatch response, then repeated submission never dispatches twice',async()=>{
 const api=gitFixture(),command=basic();let dispatched=0;
 const request=async(path,method='GET',body)=>{
  if(path.endsWith('/dispatches')){dispatched++;api.changeFile(receiptPath(command.operationId),JSON.stringify({schemaVersion:1,operationId:command.operationId,kind:command.kind,actor:command.actor,revision:1,command:commandText(command)}));throw Error('response lost');}
  const result=await api.fetch('https://api.github.com'+path,{method,body:body?JSON.stringify(body):undefined});
  if(!result.ok)throw Object.assign(Error('not found'),{status:result.status});return result.json();
 };
 const result=await submitCommand(request,command,{timeout:0});assert.equal(result.revision,1);assert.equal(dispatched,1);
 await submitCommand(request,command,{timeout:0});assert.equal(dispatched,1);
 await assert.rejects(()=>submitCommand(request,{...command,reason:'different'},{timeout:0}),error=>error.code==='OPERATION_CONFLICT');
});
test('accepted dispatch without a verified receipt remains unknown rather than reporting saved',async()=>{
 const api=gitFixture();const request=async(path,method='GET',body)=>{
  if(path.endsWith('/dispatches'))return {};
  const result=await api.fetch('https://api.github.com'+path,{method,body:body?JSON.stringify(body):undefined});if(!result.ok)throw Object.assign(Error('not found'),{status:result.status});return result.json();
 };
 await assert.rejects(()=>submitCommand(request,basic(),{timeout:0}),error=>error.code==='COMMAND_PENDING');
});
test('script executor persists a replayable journal and receipt; duplicate retry preserves later edits',()=>{
 const root=mkdtempSync(join(tmpdir(),'trusted-command-'));
 try{
  const save=(path,value)=>{mkdirSync(dirname(join(root,path)),{recursive:true});writeFileSync(join(root,path),typeof value==='string'?value:JSON.stringify(value));};
  const api=gitFixture();for(const path of api.paths().filter(path=>path.startsWith('data/')))save(path,api.file(path));
  save('data/main-adv-rpg-works-20261031.json',{works:[{...row,id:'w1',indexId:'i1',mainPlacement:'promoted-basic'}],summary:{accepted:1,promotedBasic:1,promotedDossier:0,existingComplete:0}});
  for(const file of ['adv-rpg-minimal-index-20261031.json','adv-rpg-next-studio-review-20261031.json','adv-rpg-round3-review-20261031.json'])save('data/'+file,{records:[]});
  save('data/games.json',{works:[work]});save('data/non-rpg-creator-supplement-20261030.json',{works:[]});save('data/work-edit-history.json',{schemaVersion:1,records:{}});save('data/company-coverage.json',{companies:[]});save('data/taxonomy.json',taxonomy);
  const command={...basic(),sourceLease:sourceLeaseSync(root)};
  assert.equal(executeCommand(root,command,'tester').receipt.revision,1);
  const next={...command,operationId:'later',expectedRevision:1,action:{...command.action,values:{...command.action.values,title:'Later edit'}}};
  executeCommand(root,next,'tester');
  const before=readFileSync(join(root,'data/basic-catalogue-edits.json'),'utf8');
  assert.equal(executeCommand(root,command,'tester').alreadyApplied,true);
  assert.equal(readFileSync(join(root,'data/basic-catalogue-edits.json'),'utf8'),before);
  assert.equal(readBasicStoreSync(root).revision,2);
  assert.throws(()=>executeCommand(root,{...next,operationId:'invalid',expectedRevision:0},'tester'));
  assert.equal(readFileSync(join(root,'data/basic-catalogue-edits.json'),'utf8'),before);
 }finally{rmSync(root,{recursive:true,force:true});}
});
