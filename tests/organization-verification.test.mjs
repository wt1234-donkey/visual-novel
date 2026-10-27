import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {verificationRecords,worksFor,familyEdges} from '../relationships-preview.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../data/'+p,import.meta.url),'utf8'));
const data=read('organizations.json'),source=read('organization-verification-20261027.json'),delta=read('organization-verification-round16-20261027.json');
test('versioned ledger preserves original records and attaches scoped updates without duplicate identities',()=>{
  assert.equal(source.records.length,637);
  assert.deepEqual(data.verificationLedger.counts,{'仍待核':23,'限版确认':366,'证据充分':146,'部分证据':83,'证据冲突':19});
  const attached=data.nodes.flatMap(n=>(n.groups?.verification||[]).flatMap(r=>r.recordIds));
  assert.equal(attached.length,637);assert.equal(new Set(attached).size,637);
  for(const r of source.records){
    const update=delta.records.find(item=>item.recordId===r.recordId);
    assert.deepEqual(data.verificationLedger.records[r.recordId],update||r);
    if(update){assert.equal(data.verificationLedger.recordHistory[r.recordId].status,r.status);assert.equal(data.verificationLedger.recordHistory[r.recordId].detail,r.detail);}
    assert.ok(data.works[r.workId]);
    const node=data.nodes.find(n=>n.id===r.entityId);
    assert.ok(node.groups.verification.some(row=>row.workId===r.workId&&row.recordIds.includes(r.recordId)));
  }
});
test('verification filters retain version limits and separate evidence from original-production credits',()=>{
  const node=data.nodes.find(n=>n.id==='entity-nanawind');
  const rows=verificationRecords(data,node,{status:'限版确认',query:'LunaSystem'});
  assert.equal(rows.length,4);assert.ok(rows.every(r=>r.detail.includes('共同品牌')));
  for(const r of rows)assert.ok(!worksFor(data,node,'creation').some(w=>w.workId===r.workId));
  assert.equal(verificationRecords(data,node,{category:'身份'}).length,0);
  const kadokawa=data.nodes.find(n=>n.id==='entity-name-82fc3d1bfdaa');
  assert.equal(verificationRecords(data,kadokawa,{status:'证据冲突'})[0].workId,'g900');
  assert.equal(verificationRecords(data,kadokawa,{query:'不存在的核查作品'}).length,0);
});
test('project collaboration adds no ownership edge and CoreMoreco correction preserves sales scope',()=>{
  const collaboration=data.cooperations[0];assert.equal(collaboration.recordIds.length,4);
  assert.ok(!data.edges.some(e=>collaboration.entityIds.includes(e.parent)&&collaboration.entityIds.includes(e.child)));
  const core=read('entities.json').entities.find(n=>n.id==='entity-name-21dcd9c9c1e7');
  assert.equal(core.type,'brand');assert.ok(core.historyNote.includes('销售公司'));
  const hulotte=data.families.find(f=>f.entityIds.includes('entity-hulotte'));
  const roi=familyEdges(data,hulotte).find(e=>e.child==='entity-hulotte_roi');
  assert.equal(roi.status,'sourceReviewed');assert.ok(roi.dateLabel.includes('起止未核'));
});

test('branch updates are individually filterable and historical conflicts do not resolve legal identities',()=>{
  assert.equal(delta.records.length,195);assert.equal(data.verificationLedger.changedCount,195);
  assert.equal(new Set(data.verificationLedger.changedRecordIds).size,195);
  assert.equal(data.verificationLedger.source.round,16);
  const alice=data.nodes.find(n=>n.id==='entity-alicesoft');
  const rows=verificationRecords(data,alice,{changedOnly:true});assert.ok(rows.length>0);
  assert.ok(rows.every(r=>r.newRound>=11&&r.newRound<=16));
  const nana=data.nodes.find(n=>n.id==='entity-nanawind');assert.equal(verificationRecords(data,nana,{changedOnly:true}).length,0);
  const unresolved=data.nodes.find(n=>n.id==='entity-name-de3ed19ac095');assert.equal(unresolved.type,'unknown');
  const conflicts=verificationRecords(data,unresolved,{changedOnly:true,status:'证据冲突'});
  assert.ok(conflicts.length);assert.ok(conflicts.every(r=>r.sources.length));
  const protectedKeys=['category','id','topic','game','placement','need','oldUrl','recordId','entityId','workId'];
  for(const row of delta.records){const prior=source.records.find(r=>r.recordId===row.recordId);assert.equal(prior.status,'仍待核');for(const key of protectedKeys)assert.deepEqual(row[key],prior[key]);}
});
