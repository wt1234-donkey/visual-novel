import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {verificationRecords,worksFor,familyEdges} from '../relationships-preview.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../data/'+p,import.meta.url),'utf8'));
const data=read('organizations.json'),source=read('organization-verification-20261027.json'),delta=read('organization-verification-round16-20261027.json'),revision=read('organization-verification-round20-20261027.json'),followup=read('organization-verification-five-followup-20261028.json');
test('versioned ledger preserves original records and attaches scoped updates without duplicate identities',()=>{
  assert.equal(source.records.length,637);
  assert.deepEqual(data.verificationLedger.counts,{'仍待核':1,'限版确认':388,'证据充分':156,'部分证据':82,'证据冲突':10});
  const attached=data.nodes.flatMap(n=>(n.groups?.verification||[]).flatMap(r=>r.recordIds));
  assert.equal(attached.length,637);assert.equal(new Set(attached).size,637);
  for(const r of source.records){
    const update16=delta.records.find(item=>item.recordId===r.recordId),update=followup.records.find(item=>item.recordId===r.recordId)||revision.records.find(item=>item.recordId===r.recordId)||update16;
    assert.deepEqual(data.verificationLedger.records[r.recordId],update||r);
    if(update16){const history=data.verificationLedger.recordHistories[r.recordId].find(h=>h.round===10);assert.equal(history.status,r.status);assert.equal(history.detail,r.detail);}
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
  assert.equal(verificationRecords(data,kadokawa,{status:'限版确认',query:'g900'})[0].workId,'g900');
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

test('five follow-up updates are individually filterable and historical conflicts do not resolve legal identities',()=>{
  assert.equal(delta.records.length,195);assert.equal(revision.records.length,37);
  assert.equal(data.verificationLedger.changedCount,5);
  assert.deepEqual(data.verificationLedger.changedRecordIds,['identity-1','identity-2','identity-40','identity-41','identity-42']);
  assert.equal(data.verificationLedger.source.round,29);
  assert.deepEqual(data.verificationLedger.previousSource,revision.source);
  const addison=data.nodes.find(n=>n.id==='entity-name-6ed2a96c53cd');
  const rows=['main','related','bibliography'].flatMap(placement=>verificationRecords(data,addison,{changedOnly:true,placement}));assert.equal(rows.length,2);
  assert.ok(rows.every(r=>followup.records.some(item=>item.recordId===r.recordId)));
  const nana=data.nodes.find(n=>n.id==='entity-nanawind');assert.equal(verificationRecords(data,nana,{changedOnly:true}).length,0);
  const unresolved=data.nodes.find(n=>n.id==='entity-name-de3ed19ac095');assert.equal(unresolved.type,'unknown');
  const conflicts=verificationRecords(data,unresolved,{status:'证据冲突'});
  assert.ok(conflicts.length);assert.ok(conflicts.every(r=>r.sources.length));
  const champion=data.nodes.find(n=>n.id==='entity-name-a978e18d1d4b');
  assert.deepEqual(verificationRecords(data,champion,{changedOnly:true,placement:'related'}).map(r=>r.recordId),['identity-40','identity-41','identity-42']);
  const protectedKeys=['category','id','topic','game','placement','need','oldUrl','recordId','entityId','workId'];
  for(const row of delta.records){const prior=source.records.find(r=>r.recordId===row.recordId);assert.equal(prior.status,'仍待核');for(const key of protectedKeys)assert.deepEqual(row[key],prior[key]);}
  for(const row of followup.records){const prior=revision.records.find(r=>r.recordId===row.recordId)||delta.records.find(r=>r.recordId===row.recordId)||source.records.find(r=>r.recordId===row.recordId);for(const key of protectedKeys)assert.deepEqual(row[key],prior[key]);assert.equal(row.status,prior.status);assert.ok(data.verificationLedger.recordHistories[row.recordId].some(h=>h.round===20));}
  assert.equal(followup.records.find(r=>r.recordId==='identity-2').oldUrl,revision.records.find(r=>r.recordId==='identity-2').oldUrl);
});

test('round twenty keeps the unresolved Sinclair claim and stores multiple historical snapshots',()=>{
  assert.equal(revision.records.length,37);
  assert.deepEqual(Object.values(data.verificationLedger.records).filter(r=>r.status==='仍待核').map(r=>r.recordId),['duty-558']);
  const pending=data.verificationLedger.records['duty-558'];assert.ok(pending.sources.length);assert.ok(pending.detail.includes('Sinclair Research'));
  assert.ok(data.verificationLedger.recordHistories['duty-150'].some(h=>h.round===10));
  assert.ok(data.verificationLedger.recordHistories['duty-150'].some(h=>h.round===16));
  assert.equal(data.verificationLedger.records['identity-19'].status,'限版确认');
  assert.ok(data.verificationLedger.recordHistories['identity-19'].some(h=>h.status==='证据冲突'));
  const sinclair=data.nodes.find(n=>n.id==='entity-sinclair');
  assert.deepEqual(verificationRecords(data,sinclair,{changedOnly:true,status:'仍待核'}).map(r=>r.recordId),[]);
});
