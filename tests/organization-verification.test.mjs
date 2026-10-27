import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {verificationRecords,worksFor,familyEdges} from '../relationships-preview.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../data/'+p,import.meta.url),'utf8'));
const data=read('organizations.json'),source=read('organization-verification-20261027.json');
test('round ten preserves all statuses, sources, work identities and unique record references',()=>{
  assert.equal(source.records.length,637);
  assert.deepEqual(data.verificationLedger.counts,{'仍待核':218,'限版确认':267,'证据充分':104,'部分证据':38,'证据冲突':10});
  const attached=data.nodes.flatMap(n=>(n.groups?.verification||[]).flatMap(r=>r.recordIds));
  assert.equal(attached.length,637);assert.equal(new Set(attached).size,637);
  for(const r of source.records){
    assert.deepEqual(data.verificationLedger.records[r.recordId],r);
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
