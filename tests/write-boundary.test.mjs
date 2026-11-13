import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,dirname} from 'node:path';
import {executeCommand,receiptPath} from '../src/infrastructure/filesystem/command-executor.mjs';
import {sealCatalogueWrite,verifyCatalogueWrite} from '../src/infrastructure/filesystem/write-boundary.mjs';
import {sourceLeaseSync} from '../src/infrastructure/filesystem/effective-catalogue.mjs';
import {emptyStore} from '../basic-catalogue-model.mjs';
import {applyEditorialBatch} from '../scripts/apply_editorial_batch.mjs';
import {editableValues} from '../work-edit-model.mjs';
const read=name=>JSON.parse(readFileSync(new URL('../data/'+name,import.meta.url)));
function fixture(t){
 const root=mkdtempSync(join(tmpdir(),'writer-boundary-'));t.after(()=>rmSync(root,{recursive:true,force:true}));
 const work=read('games.json').works.find(w=>w.id==='g039'),put=(name,v)=>{const p=join(root,'data',name);mkdirSync(dirname(p),{recursive:true});writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
 for(const [name,value] of Object.entries({'main-adv-rpg-works-20261031.json':{works:[],identityReview:[]},'games.json':{works:[work]},'company-coverage.json':{companies:[]},'non-rpg-creator-supplement-20261030.json':{works:[]},'basic-catalogue-edits.json':emptyStore(),'work-edit-history.json':{schemaVersion:1,records:{}},'taxonomy.json':read('taxonomy.json'),'editorial-publications.json':{batches:[]},'trusted-save-policy.json':{schemaVersion:1,mode:'trusted'}}))put(name,value);
 for(const name of ['adv-rpg-minimal-index-20261031','adv-rpg-next-studio-review-20261031','adv-rpg-round3-review-20261031'])put(name+'.json',{records:[]});
 return {root,work};
}
test('a command receipt is sealed with its event and duplicate confirmation preserves later writes',async t=>{
 const {root,work}=fixture(t),cmd={schemaVersion:1,operationId:'writer-one',kind:'formal',actor:'tester',at:'2026-11-14T00:00:00Z',reason:'添加或调整剧作姓名',sources:[],expectedRevision:0,sourceLease:sourceLeaseSync(root),action:{type:'creators',workId:work.id,names:{writerNames:['First'],artistNames:[],musicianNames:[]}}};
 executeCommand(root,cmd,'tester');const first=await sealCatalogueWrite(root,{operationId:cmd.operationId,command:cmd}),bytes=readFileSync(join(root,first.path));assert.ok(first.receipt.auditRoot);
 const later={...cmd,operationId:'writer-two',at:'2026-11-14T00:01:00Z',expectedRevision:1,action:{...cmd.action,names:{...cmd.action.names,writerNames:['Later']}}};executeCommand(root,later,'tester');await sealCatalogueWrite(root,{operationId:later.operationId,command:later});
 assert.equal(executeCommand(root,cmd,'tester').alreadyApplied,true);await sealCatalogueWrite(root,{operationId:cmd.operationId,command:cmd});assert.deepEqual(readFileSync(join(root,first.path)),bytes);await verifyCatalogueWrite(root);
 const file=join(root,receiptPath(cmd.operationId)),receipt=JSON.parse(readFileSync(file));receipt.auditRoot.sha256='0'.repeat(64);writeFileSync(file,JSON.stringify(receipt));await assert.rejects(verifyCatalogueWrite(root),/代次链/);
});
test('reviewed formal writes use the same command receipt and seal it before the batch can be committed',async t=>{
 const {root,work}=fixture(t),p={schemaVersion:1,id:'10000000-0000-4000-8000-000000000001',kind:'work',reason:'核对正式作品补充说明',sources:['https://example.org/review'],change:{workId:work.id,expectedRevision:0,sourceLease:sourceLeaseSync(root),after:{...editableValues(work),notes:'隔离资料说明'}},preview:[{id:work.id}]},batch={id:'10000000-0000-4000-8000-000000000002',proposals:[p]};
 applyEditorialBatch(batch,root);const receipt=JSON.parse(readFileSync(join(root,receiptPath(p.id))));assert.equal(receipt.kind,'formal');assert.ok(receipt.auditRoot);await verifyCatalogueWrite(root);
 const snapshot=readFileSync(join(root,'data/work-edit-history.json'));assert.equal(applyEditorialBatch(batch,root).already,true);assert.deepEqual(readFileSync(join(root,'data/work-edit-history.json')),snapshot);
});
test('identity review and field assertion/selection receipts bind their exact commands to the same archive protocol',async t=>{
 const {root}=fixture(t),rows=['sa','sb'].map((id,i)=>({id,indexId:'index-'+id,title:'Twin',firstYear:1990,group:'Maker',gameplay:'ADV',source:'https://example.org/'+id,mainPlacement:'promoted-basic'}));
 writeFileSync(join(root,'data/main-adv-rpg-works-20261031.json'),JSON.stringify({works:rows,identityReview:[]}));
 const make=(kind,id,expectedRevision,action)=>({schemaVersion:1,operationId:id,kind,actor:'tester',at:'2026-11-14T00:00:00Z',reason:'逐项核对来源身份及字段证据',sources:['https://example.org/review'],expectedRevision,sourceLease:sourceLeaseSync(root),action});
 const commands=[
  ()=>make('identity','identity-distinct',0,{type:'resolve',caseId:'name-year:twin|1990',outcome:'distinct',links:rows.map(r=>({sourceId:r.id,workId:r.id}))}),
  ()=>make('field','field-assert',0,{type:'assert',assertion:{id:'claim',scope:{type:'work',workId:'sa',id:'sa'},field:'group',value:'Reviewed Maker',sources:['https://example.org/claim'],sourceIds:['sa'],status:'supported',subjects:[]}}),
  ()=>make('field','field-select',1,{type:'select',assertionId:'claim'})
 ];
 for(const build of commands){const command=build();executeCommand(root,command,'tester');await sealCatalogueWrite(root,{operationId:command.operationId,command});}
 await verifyCatalogueWrite(root);const field=JSON.parse(readFileSync(join(root,'data/field-evidence.json')));assert.equal(field.revision,2);assert.equal(Object.keys(field.choices).length,1);
});
