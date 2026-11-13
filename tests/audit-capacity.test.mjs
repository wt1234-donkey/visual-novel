import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {performance} from 'node:perf_hooks';
import {emptyStore,applyChange,valuesOf,validateStore} from '../basic-catalogue-model.mjs';
import {catalogueState,journalKey} from '../src/domain/catalogue/journal.mjs';
import {AUDIT_PATH} from '../src/domain/audit/events.mjs';
import {buildAuditLedger,restoreAuditKind,verifyAuditGraph,publishAuditLedger,AUDIT_LIMITS} from '../src/infrastructure/filesystem/audit-ledger.mjs';
import {createAuditReader} from '../src/infrastructure/storage/audit-reader.mjs';
import {assertSmallLegacyHistory} from '../src/infrastructure/storage/audit-access.mjs';
import {emptyIdentityStore,buildSourceIdentityCatalogue,applyIdentityReview} from '../src/domain/catalogue/source-identities.mjs';
import {emptyFieldStore,applyFieldCommand} from '../src/domain/catalogue/field-evidence.mjs';
import {createFieldContext} from '../src/infrastructure/filesystem/field-evidence.mjs';
import {saveCreatorNames,undoEdit,validateHistory} from '../work-edit-model.mjs';

function fixture(t,count){
 const root=mkdtempSync(join(tmpdir(),'atlas-audit-capacity-'));t.after(()=>rmSync(root,{recursive:true,force:true}));mkdirSync(join(root,'data'));
 const base=[{id:'hot',title:'Hot',year:1980,group:'Maker',gameplay:'ADV'},{id:'cold',title:'Cold',year:1980,group:'Maker',gameplay:'ADV'}];
 const initial=emptyStore();let current=initial;const events=[];
 for(let i=1;i<=count;i++){
  const before={...catalogueState(current),schemaVersion:2,journal:{schemaVersion:1,baseline:catalogueState(current),events:[]}};
  const target=base[i%200===0?1:0];
  current=applyChange(before,base,{type:'edit',id:target.id,values:{...valuesOf(target),group:'Maker '+i}},
   {id:'capacity-'+i,actor:'capacity-test',at:'2026-11-13T08:00:00Z',reason:'容量测试修改资料',expectedRevision:current.revision});
  events.push(current.journal.events[0]);
 }
 const store={...catalogueState(current),schemaVersion:2,journal:{schemaVersion:1,baseline:initial,events}};validateStore(store);
 writeFileSync(join(root,'data/basic-catalogue-edits.json'),JSON.stringify(store,null,2)+'\n');
 return {root,store};
}
function measuredReader(root){
 const metrics={objects:0,indexBytes:0,bodyReads:0,bodyEvents:0,bodyBytes:0};
 const reader=createAuditReader(ref=>{const text=readFileSync(join(root,ref.path),'utf8'),value=JSON.parse(text);metrics.objects++;if(value.type==='events'){metrics.bodyReads++;metrics.bodyEvents+=value.events.length;metrics.bodyBytes+=ref.bytes;}else metrics.indexBytes+=ref.bytes;return text;});
 return {reader,metrics};
}

test('10,000 valid events use operation and sparse work indexes; archived replay is identical', {timeout:180000},async t=>{
 const {root,store}=fixture(t,10000),started=performance.now(),source=readFileSync(join(root,'data/basic-catalogue-edits.json'));
 const built=await buildAuditLedger(root);assert.equal(built.kinds.basic.events,10000);
 assert.deepEqual(await restoreAuditKind(root,built.pointer.root,'basic'),store);
 assert.equal((await buildAuditLedger(root,{check:true})).changed,false);
 assert.deepEqual(readFileSync(join(root,'data/basic-catalogue-edits.json')),source,'archiving never rewrites source facts or audit events');
 const samples={};
 for(const [name,query] of [
  ['operation',opened=>opened.findOperation('capacity-200')],
  ['missingOperation',opened=>opened.findOperation('not-an-operation')],
  ['sparseWorkPage',opened=>opened.history({workId:'cold',limit:20})],
  ['globalPage',opened=>opened.history({limit:20})]
 ]){
  const {reader,metrics}=measuredReader(root),start=performance.now(),opened=await reader.open(built.pointer.root,{kind:'basic'}),result=await query(opened);
  if(name==='operation'){assert.equal(result.id,'capacity-200');assert.equal(metrics.bodyReads,1);assert.ok(metrics.bodyEvents<=50);}
  if(name==='missingOperation'){assert.equal(result,null);assert.equal(metrics.bodyReads,0);}
  if(name==='sparseWorkPage'){assert.equal(result.events.length,20);assert.equal(result.total,50);assert.equal(result.nextBefore,6200);assert.ok(metrics.bodyReads<=20);assert.ok(metrics.bodyEvents<=1000);}
  if(name==='globalPage'){assert.equal(result.events.length,20);assert.ok(metrics.bodyReads<=2);}
  assert.ok(metrics.bodyEvents<10000);assert.ok(metrics.indexBytes<512*1024);
  samples[name]={...metrics,ms:Math.round((performance.now()-start)*100)/100};
 }
 const {reader}=measuredReader(root),opened=await reader.open(built.pointer.root,{kind:'basic'}),ids=[];let before=Infinity;
 do{const page=await opened.history({workId:'cold',before,limit:20});ids.push(...page.events.map(e=>e.id));before=page.nextBefore;}while(before!==null);
 assert.equal(ids.length,50);assert.equal(new Set(ids).size,50);assert.equal(ids.at(-1),'capacity-200');
 assert.throws(()=>assertSmallLegacyHistory('basic',store),/不会扫描全部正文/);
 const report={schemaVersion:1,events:10000,limits:AUDIT_LIMITS,samples,archiveAndReplayMs:Math.round(performance.now()-started),logicalReplayEqual:true,sourceBytesUnchanged:true};
 mkdirSync('test-results',{recursive:true});writeFileSync('test-results/audit-capacity.json',JSON.stringify(report,null,2)+'\n');console.log('AUDIT_CAPACITY',JSON.stringify(report));
});

test('archive corruption, missing objects, stale source leases and rewritten prefixes fail closed',async t=>{
 const {root,store}=fixture(t,3),built=await buildAuditLedger(root),{reader}=measuredReader(root),opened=await reader.open(built.pointer.root,{kind:'basic'});
 await assert.rejects(reader.open(built.pointer.root,{kind:'basic',sourceSha:'0'.repeat(40)}),/版本不一致/);
 const posting=await reader.lookup(opened.descriptor.operations,'capacity-1'),path=join(root,posting.segment.path),text=readFileSync(path,'utf8');
 writeFileSync(path,text+' ');await assert.rejects(restoreAuditKind(root,built.pointer.root,'basic'),/摘要不匹配/);writeFileSync(path,text);
 rmSync(path);await assert.rejects(verifyAuditGraph(root,built.pointer.root),/ENOENT/);writeFileSync(path,text);
 const rewritten=structuredClone(store);rewritten.journal.events[0].reason='改写旧的说明理由';
 // Even a semantically valid rewrite of both current shortcut metadata and its
 // old event must not replace an already archived prefix.
 for(const row of rewritten.recent)if(row.id==='capacity-1')row.reason='改写旧的说明理由';
 writeFileSync(join(root,'data/basic-catalogue-edits.json'),JSON.stringify(rewritten,null,2)+'\n');
 await assert.rejects(buildAuditLedger(root),/不能改写/);
 assert.equal(JSON.parse(readFileSync(join(root,AUDIT_PATH))).root.sha256,built.pointer.root.sha256);
 assert.notEqual(journalKey(rewritten),journalKey(store));
});

test('formal, identity and field archives replay independent undo events and index stable work IDs',async t=>{
 const root=mkdtempSync(join(tmpdir(),'atlas-audit-kinds-'));t.after(()=>rmSync(root,{recursive:true,force:true}));mkdirSync(join(root,'data'));
 const data=JSON.parse(readFileSync(new URL('../data/games.json',import.meta.url))),work=data.works.find(w=>w.id==='g039'),taxonomy=JSON.parse(readFileSync(new URL('../data/taxonomy.json',import.meta.url)));
 const meta=(id,revision)=>({id,actor:'tester',at:'2026-11-13T08:00:00Z',reason:'归档保留独立撤销与完整证据',sources:[],expectedRevision:revision});
 let formal={schemaVersion:1,records:{}};
 for(let i=1;i<=2;i++)formal=saveCreatorNames(formal,work,{writerNames:['Manual '+i],artistNames:[],musicianNames:[]},meta('formal-'+i,i-1),taxonomy,[work]);
 formal=undoEdit(formal,work,'formal-2',2,taxonomy,[work],meta('formal-undo',2));validateHistory(formal,[work],taxonomy);
 const rows=['sa','sb'].map(id=>({id,title:'Twin',firstYear:1990,group:'Maker',gameplay:'ADV',source:'https://example.org/'+id}));
 const registry={works:rows,identityReview:[]},identity=buildSourceIdentityCatalogue({registry,formalWorks:[]});
 let identities=applyIdentityReview(emptyIdentityStore(),identity,{type:'resolve',caseId:'name-year:twin|1990',outcome:'same-work',links:rows.map(r=>({sourceId:r.id,workId:'sa'}))},{...meta('identity-1',0),sources:['https://example.org/review']});
 identities=applyIdentityReview(identities,buildSourceIdentityCatalogue({registry,formalWorks:[],decisions:identities}),{type:'undo',targetId:'identity-1'},{...meta('identity-undo',1),sources:['https://example.org/review']});
 const context=createFieldContext({identity,main:{works:[],contentVersions:[],platformReleases:[]},entities:[],people:[]});
 let fields=applyFieldCommand(emptyFieldStore(),context,{type:'assert',assertion:{id:'claim',scope:{type:'work',workId:'sa',id:'sa'},field:'group',value:'Reviewed Maker',sources:['https://example.org/claim'],sourceIds:['sa'],status:'supported',subjects:[]}},meta('field-1',0));
 fields=applyFieldCommand(fields,context,{type:'select',assertionId:'claim'},meta('field-2',1));
 fields=applyFieldCommand(fields,context,{type:'undo',targetId:'field-2'},meta('field-undo',2));
 for(const [name,value] of [['work-edit-history',formal],['source-identity-decisions',identities],['field-evidence',fields]])writeFileSync(join(root,'data',name+'.json'),JSON.stringify(value)+'\n');
 const built=await buildAuditLedger(root),reader=createAuditReader(ref=>readFileSync(join(root,ref.path),'utf8'));
 for(const [kind,value,id] of [['formal',formal,work.id],['identity',identities,'sa'],['field',fields,'sa']]){
  assert.deepEqual(await restoreAuditKind(root,built.pointer.root,kind),value);
  const opened=await reader.open(built.pointer.root,{kind}),page=await opened.history({workId:id});
  assert.equal(page.events.length,kind==='identity'?2:3);assert.ok(page.events[0].undoOf);
  assert.equal((await opened.findOperation(page.events[0].id)).id,page.events[0].id);
 }
});

test('a new generation extends the frozen prefix and the earlier archive remains independently replayable',async t=>{
 const {root,store}=fixture(t,3),first=await buildAuditLedger(root);
 const base=[{id:'hot',title:'Hot',year:1980,group:'Maker',gameplay:'ADV'}];
 const next=applyChange(store,base,{type:'edit',id:'hot',values:{...valuesOf(base[0]),group:'Maker 4'}},
  {id:'capacity-4',actor:'tester',at:'2026-11-13T08:00:00Z',reason:'追加下一代归档并保留起点',expectedRevision:3});
 writeFileSync(join(root,'data/basic-catalogue-edits.json'),JSON.stringify(next)+'\n');
 const second=await buildAuditLedger(root),reader=createAuditReader(ref=>readFileSync(join(root,ref.path),'utf8'));
 assert.notEqual(second.pointer.root.sha256,first.pointer.root.sha256);
 assert.deepEqual((await reader.read(second.pointer.root)).previous,first.pointer.root);
 assert.deepEqual(await restoreAuditKind(root,first.pointer.root,'basic'),store);
 assert.deepEqual(await restoreAuditKind(root,second.pointer.root,'basic'),next);
 assert.ok(await verifyAuditGraph(root,second.pointer.root)>0);
 const output=mkdtempSync(join(tmpdir(),'atlas-audit-published-'));t.after(()=>rmSync(output,{recursive:true,force:true}));
 const publication=await publishAuditLedger(root,output);
 const publishedReader=createAuditReader(ref=>readFileSync(join(output,ref.path),'utf8'));
 assert.equal((await publishedReader.read(publication.pointer.root)).previous,null);
 assert.deepEqual(await restoreAuditKind(output,publication.pointer.root,'basic'),next);
 assert.deepEqual(await restoreAuditKind(root,first.pointer.root,'basic'),store,'runtime pruning never removes repository archives');
});
