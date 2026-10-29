import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {verificationRecords,worksFor,familyEdges} from '../relationships-preview.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../data/'+p,import.meta.url),'utf8'));
const data=read('organizations.json'),source=read('organization-verification-20261027.json'),delta=read('organization-verification-round16-20261027.json'),revision=read('organization-verification-round20-20261027.json'),followup=read('organization-verification-five-followup-20261028.json'),closure=read('organization-round28-closure-20261028.json');
test('versioned ledger preserves original records and attaches scoped updates without duplicate identities',()=>{
  assert.equal(source.records.length,637);
  assert.deepEqual(data.verificationLedger.counts,{'限版确认':391,'证据充分':156,'部分证据':79,'证据冲突':10,'归属纠正':1});
  const attached=data.nodes.flatMap(n=>(n.groups?.verification||[]).flatMap(r=>r.recordIds));
  assert.equal(attached.length,637);assert.equal(new Set(attached).size,637);
  for(const r of source.records){
    const update16=delta.records.find(item=>item.recordId===r.recordId),update=closure.records.find(item=>item.recordId===r.recordId)||followup.records.find(item=>item.recordId===r.recordId)||revision.records.find(item=>item.recordId===r.recordId)||update16;
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

test('five follow-up history remains intact after four scoped corrections',()=>{
  assert.equal(delta.records.length,195);assert.equal(revision.records.length,37);
  assert.equal(data.verificationLedger.changedCount,4);
  assert.deepEqual(data.verificationLedger.changedRecordIds,['identity-36','identity-37','duty-120','duty-558']);
  assert.equal(data.verificationLedger.source.round,30);
  assert.deepEqual(data.verificationLedger.previousSource,followup.source);
  const addison=data.nodes.find(n=>n.id==='entity-name-6ed2a96c53cd');
  const rows=['main','related','bibliography'].flatMap(placement=>verificationRecords(data,addison,{changedOnly:true,placement}));assert.equal(rows.length,0);
  assert.ok(followup.records.every(r=>data.verificationLedger.recordHistories[r.recordId].some(h=>h.round===20)));
  const nana=data.nodes.find(n=>n.id==='entity-nanawind');assert.equal(verificationRecords(data,nana,{changedOnly:true}).length,0);
  const unresolved=data.nodes.find(n=>n.id==='entity-name-de3ed19ac095');assert.equal(unresolved.type,'unknown');
  const conflicts=verificationRecords(data,unresolved,{status:'证据冲突'});
  assert.ok(conflicts.length);assert.ok(conflicts.every(r=>r.sources.length));
  const champion=data.nodes.find(n=>n.id==='entity-name-a978e18d1d4b');
  assert.deepEqual(verificationRecords(data,champion,{changedOnly:true,placement:'related'}).map(r=>r.recordId),[]);
  const protectedKeys=['category','id','topic','game','placement','need','oldUrl','recordId','entityId','workId'];
  for(const row of delta.records){const prior=source.records.find(r=>r.recordId===row.recordId);assert.equal(prior.status,'仍待核');for(const key of protectedKeys)assert.deepEqual(row[key],prior[key]);}
  for(const row of followup.records){const prior=revision.records.find(r=>r.recordId===row.recordId)||delta.records.find(r=>r.recordId===row.recordId)||source.records.find(r=>r.recordId===row.recordId);for(const key of protectedKeys)assert.deepEqual(row[key],prior[key]);assert.equal(row.status,prior.status);assert.ok(data.verificationLedger.recordHistories[row.recordId].some(h=>h.round===20));}
  assert.equal(followup.records.find(r=>r.recordId==='identity-2').oldUrl,revision.records.find(r=>r.recordId==='identity-2').oldUrl);
});

test('Sinclair claim is limited to QL edition and its pending history is retained',()=>{
  assert.equal(revision.records.length,37);
  assert.deepEqual(Object.values(data.verificationLedger.records).filter(r=>r.status==='仍待核').map(r=>r.recordId),[]);
  const pending=revision.records.find(r=>r.recordId==='duty-558');assert.equal(pending.status,'仍待核');
  assert.equal(data.verificationLedger.records['duty-558'].status,'限版确认');
  assert.ok(data.verificationLedger.recordHistories['duty-558'].some(h=>h.status==='仍待核'));
  assert.ok(data.verificationLedger.recordHistories['duty-150'].some(h=>h.round===10));
  assert.ok(data.verificationLedger.recordHistories['duty-150'].some(h=>h.round===16));
  assert.equal(data.verificationLedger.records['identity-19'].status,'限版确认');
  assert.ok(data.verificationLedger.recordHistories['identity-19'].some(h=>h.status==='证据冲突'));
  const sinclair=data.nodes.find(n=>n.id==='entity-sinclair');
  assert.deepEqual(verificationRecords(data,sinclair,{changedOnly:true,status:'限版确认'}).map(r=>r.recordId),['duty-558']);
});

test('round 28 results map only the reviewed mobile channels, QL edition, and Saturn correction',()=>{
  assert.equal(closure.records.length,4);
  const credits=read('credits.json'),games=read('games.json');
  const scoped=credits.credits.filter(c=>['identity-36','identity-37','duty-558'].includes(c.reviewId));
  assert.deepEqual(scoped.map(c=>[c.reviewId,c.targetType,c.targetId,c.role]),[
    ['identity-37','release','g209-v2','serviceProvider'],
    ['identity-36','release','g209-v3','serviceProvider'],
    ['duty-558','edition','g089-ql-classic-adventures-1985','publisher']]);
  assert.ok(scoped.every(c=>c.status==='sourceReviewed'&&c.source&&c.reviewRecord));
  assert.deepEqual(credits.scopedEditions.find(e=>e.id===closure.scopedEdition.id),closure.scopedEdition);
  assert.equal(games.platformReleases.some(r=>r.id==='g089-ql-classic-adventures-1985'),false);
  assert.equal(scoped.some(c=>['g089-v1','g089-v2','g089-v3','g089-v4'].includes(c.targetId)),false);
  const ascii=credits.dossierMemberships.find(m=>m.dossierId==='ascii'&&m.workId==='ascii-anearth');
  assert.deepEqual([ascii.group,ascii.status,ascii.roles],['reference','sourceReviewedCorrection',[]]);
  assert.equal(credits.credits.some(c=>c.entityId==='entity-ascii'&&c.workId==='ascii-anearth'),false);
  assert.equal(data.verificationLedger.records['duty-120'].status,'归属纠正');
  assert.ok(readFileSync(new URL('../ascii.html',import.meta.url),'utf8').includes('メディアワークス'));
});
