import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,readdirSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {performance} from 'node:perf_hooks';
import {basicScale,appendBasicScale} from './helpers/audit-scale-fixture.mjs';
import {buildAuditLedger,restoreAuditKind,publishAuditLedger} from '../src/infrastructure/filesystem/audit-ledger.mjs';
import {createAuditReader} from '../src/infrastructure/storage/audit-reader.mjs';

test('10,040 event baseline plus 100 saves freezes old bodies and bounds incremental writes; a batched append and old roots replay', {timeout:480000},async t=>{
 const root=mkdtempSync(join(tmpdir(),'atlas-append-'));t.after(()=>rmSync(root,{recursive:true,force:true}));mkdirSync(join(root,'data'));
 let {store,base}=basicScale(10040);const path=join(root,'data/basic-catalogue-edits.json'),save=()=>writeFileSync(path,JSON.stringify(store)+'\n');save();
 const initial=structuredClone(store),first=await buildAuditLedger(root),initialFiles=new Map(readdirSync(join(root,'data/audit-ledger/objects')).map(name=>[name,readFileSync(join(root,'data/audit-ledger/objects',name))]));
 const samples=[];let last=first;
 for(let i=10041;i<=10140;i++){
  store=appendBasicScale(store,base,i);save();
  const start=performance.now();last=await buildAuditLedger(root);samples.push({events:i,newObjects:last.newObjects,newBytes:last.newBytes,ms:Math.round(performance.now()-start)});
  assert.ok(last.newObjects<=16,JSON.stringify(samples.at(-1)));assert.ok(last.newBytes<=192*1024,JSON.stringify(samples.at(-1)));
 }
 for(const [name,bytes] of initialFiles)assert.deepEqual(readFileSync(join(root,'data/audit-ledger/objects',name)),bytes,'prior objects are never changed');
 const reader=createAuditReader(ref=>readFileSync(join(root,ref.path),'utf8')),old=await reader.open(first.pointer.root,{kind:'basic'}),now=await reader.open(last.pointer.root,{kind:'basic'});
 assert.deepEqual(await reader.lookup(old.descriptor.operations,'scale-10040'),await reader.lookup(now.descriptor.operations,'scale-10040'),'the formerly active tail keeps its exact body address and posting');
 assert.deepEqual(await restoreAuditKind(root,first.pointer.root,'basic'),initial);
 assert.deepEqual(await restoreAuditKind(root,last.pointer.root,'basic'),store);
 for(let i=10141;i<=10240;i++)store=appendBasicScale(store,base,i);save();
 const batch=await buildAuditLedger(root);assert.ok(batch.newObjects<=128&&batch.newBytes<=2*1024*1024,JSON.stringify({message:'a batch writes grouped paths, not one intermediate index per event',newObjects:batch.newObjects,newBytes:batch.newBytes}));
 await buildAuditLedger(root,{check:true});
 const output=mkdtempSync(join(tmpdir(),'atlas-append-public-'));t.after(()=>rmSync(output,{recursive:true,force:true}));const published=await publishAuditLedger(root,output);assert.deepEqual(await restoreAuditKind(output,published.pointer.root,'basic'),store);
 mkdirSync('test-results',{recursive:true});const report={baselineEvents:10040,continuousSaves:100,budgets:{newObjects:16,newBytes:192*1024},samples,batch:{events:100,newObjects:batch.newObjects,newBytes:batch.newBytes},oldRootReplayEqual:true,currentReplayEqual:true,publishedReplayEqual:true,oldBodyReferencesUnchanged:true};writeFileSync('test-results/audit-incremental.json',JSON.stringify(report,null,2)+'\n');console.log('AUDIT_INCREMENTAL',JSON.stringify(report));
});
