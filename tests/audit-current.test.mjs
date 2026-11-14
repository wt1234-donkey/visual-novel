import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {performance} from 'node:perf_hooks';
import {formalScale,identityScale,fieldScale} from './helpers/audit-scale-fixture.mjs';
import {buildAuditLedger,restoreAuditKind,auditObjectWriter} from '../src/infrastructure/filesystem/audit-ledger.mjs';
import {createAuditReader} from '../src/infrastructure/storage/audit-reader.mjs';
import {AUDIT_SOURCES,auditWorkIds} from '../src/domain/audit/events.mjs';
import {journalKey} from '../src/domain/catalogue/journal.mjs';
const report={schemaVersion:1,eventCountPerKind:10000,scenarios:{}};
for(const [kind,make] of [['formal',formalScale],['identity',identityScale],['field',fieldScale]])test(kind+' current state, selected work, 20 history and undo evidence do not load other works or full event aggregates',{timeout:180000},async t=>{
 const root=mkdtempSync(join(tmpdir(),'atlas-current-'));t.after(()=>rmSync(root,{recursive:true,force:true}));mkdirSync(join(root,'data'));
 const {store}=make(10000);writeFileSync(join(root,AUDIT_SOURCES[kind]),JSON.stringify(store)+'\n');const built=await buildAuditLedger(root);
 assert.equal(journalKey(await restoreAuditKind(root,built.pointer.root,kind)),journalKey(store));
 const reads=[],reader=createAuditReader(ref=>{const text=readFileSync(join(root,ref.path),'utf8'),value=JSON.parse(text);reads.push({bytes:ref.bytes,type:value.type,events:value.events||[]});return text;});
 const start=performance.now(),opened=await reader.open(built.pointer.root,{kind}),empty=await opened.current();
 assert.equal(empty.eventCount,10000);assert.equal(empty.events,undefined);assert.equal(reads.some(r=>r.type==='events'),false);
 const startupBytes=reads.reduce((n,r)=>n+r.bytes,0);assert.ok(startupBytes<32*1024);
 const options=kind==='formal'?{workIds:['cold']}:kind==='identity'?{sourceIds:['cold'],caseIds:['source:cold']}:{scope:{type:'work',workId:'cold',id:'cold'},field:'firstYear'};
 const current=await opened.current(options);assert.equal(reads.some(r=>r.type==='events'),false);
 const page=await opened.history({workId:'cold',limit:20});assert.equal(page.events.length,20);assert.ok(page.nextBefore);
 assert.equal(reads.filter(r=>r.type==='events').length,20);
 assert.ok(reads.filter(r=>r.type==='events').every(r=>r.events.length===1&&auditWorkIds(kind,r.events[0]).includes('cold')),'no other work event body is downloaded');
 if(kind==='formal'){assert.deepEqual(current.records.cold,store.records.cold);assert.ok(current.records.cold.recent.length<=3);assert.equal(current.records.hot,undefined);}
 if(kind==='identity'){assert.deepEqual(current.links.cold,store.links.cold);assert.equal(current.links.hot,undefined);}
 if(kind==='field'){assert.deepEqual(Object.values(current.assertions).map(a=>a.scope.workId),['cold']);assert.equal(current.stats.events,10000);}
 assert.ok(page.events[0].before||page.events[0].changes,'undo preview is supported by the selected page, without any whole-log fetch');
 report.scenarios[kind]={startupBytes,totalObjectBytes:reads.reduce((n,r)=>n+r.bytes,0),objects:reads.length,historyBodies:20,historyEvents:20,unrelatedEventBodies:0,ms:Math.round(performance.now()-start),fullReplayEqual:true};
 mkdirSync('test-results',{recursive:true});writeFileSync('test-results/audit-current.json',JSON.stringify(report,null,2)+'\n');console.log('AUDIT_CURRENT',kind,JSON.stringify(report.scenarios[kind]));
});

test('rehashing forged operation indexes or current projections cannot bypass independent semantic verification',async t=>{
 const root=mkdtempSync(join(tmpdir(),'atlas-current-forged-'));t.after(()=>rmSync(root,{recursive:true,force:true}));mkdirSync(join(root,'data'));
 const {store}=fieldScale(5);writeFileSync(join(root,AUDIT_SOURCES.field),JSON.stringify(store)+'\n');const built=await buildAuditLedger(root),writer=auditObjectWriter(root),reader=createAuditReader(ref=>readFileSync(join(root,ref.path),'utf8'));
 const original=await reader.read(built.pointer.root),descriptor=original.kinds.field;
 const operations=writer.put({schemaVersion:1,type:'map',entries:{}}),forgedIndex=writer.put({...original,kinds:{field:{...descriptor,operations}}});
 await assert.rejects(restoreAuditKind(root,forgedIndex,'field'),/操作索引与事件全集不一致/);
 const meta=await reader.read(descriptor.current),current=writer.put({...meta,revision:meta.revision+1}),forgedCurrent=writer.put({...original,kinds:{field:{...descriptor,current}}});
 await assert.rejects(restoreAuditKind(root,forgedCurrent,'field'),/当前状态投影与资料版本不一致/);
 assert.equal(journalKey(await restoreAuditKind(root,built.pointer.root,'field')),journalKey(store));
});
