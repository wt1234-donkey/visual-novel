import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {unfinishedRows,filterUnfinished,unfinishedPage} from '../organization-unfinished.mjs';
const read=name=>JSON.parse(readFileSync(new URL('../data/'+name,import.meta.url),'utf8'));
const data=read('organizations.json'),credits=read('credits.json'),rows=unfinishedRows(data);
test('unfinished categories exactly preserve explicit unresolved identities and dossier duties',()=>{
  assert.deepEqual(data.unfinished.counts,{identity:32,duty:600,creation:809,evidence:480,chronology:47,relation:1});
  assert.equal(rows.length,1969);assert.equal(new Set(rows.map(r=>r.id)).size,rows.length);
  assert.deepEqual(new Set(rows.filter(r=>r.kind==='identity').map(r=>r.entityIds[0])),new Set(data.nodes.filter(n=>!n.previewOnly&&n.verification==='unresolved').map(n=>n.id)));
  const expected=new Set(credits.dossierMemberships.filter(m=>m.status==='pendingRole'||m.group==='unresolved').map(m=>'duty:'+m.dossierId+':'+m.workId));
  assert.deepEqual(new Set(rows.filter(r=>r.kind==='duty').map(r=>r.id)),expected);
  const yuzu=rows.find(r=>r.id==='duty:yuzusoft:g232');assert.ok(yuzu.recordIds.includes('duty-589'));assert.equal(data.verificationLedger.records['duty-589'].status,'证据充分');
  assert.equal(yuzu.status,'正式职责待核');assert.ok(yuzu.detail.includes('台账已有'));
});
test('missing creation means no registered direct creation, never no known publisher or no creator',()=>{
  const created=new Set(data.nodes.flatMap(n=>n.groups?.creation||[]).map(r=>r.workId));
  const missing=Object.values(data.works).filter(w=>w.placement==='main'&&!created.has(w.id));
  assert.deepEqual(new Set(rows.filter(r=>r.kind==='creation').map(r=>r.workId)),new Set(missing.map(w=>w.id)));
  assert.ok(rows.filter(r=>r.kind==='creation').every(r=>r.detail.includes('不表示没有创作者')));
});
test('pending, conflict, partial and version-limited evidence stay distinct and overlap formal duty queues',()=>{
  const expected=Object.values(data.verificationLedger.records).filter(r=>r.status!=='证据充分'&&r.status!=='归属纠正');
  assert.deepEqual(new Set(rows.filter(r=>r.kind==='evidence').map(r=>r.recordId)),new Set(expected.map(r=>r.recordId)));
  const pending=filterUnfinished(rows,{kind:'evidence',status:'仍待核',query:'Sinclair'});assert.deepEqual(pending,[]);
  assert.equal(filterUnfinished(rows,{kind:'evidence',status:'限版确认'}).length,391);
  assert.ok(rows.some(a=>a.kind==='duty'&&rows.some(b=>b.kind==='evidence'&&a.workId===b.workId)));
});
test('pending relation is not duplicated as a date gap, and missing rename dates are explicitly listed',()=>{
  const spin=rows.filter(r=>r.edgeId==='preview-silkys-origin');assert.equal(spin.length,1);assert.equal(spin[0].kind,'relation');
  assert.ok(rows.some(r=>r.historyId==='novect-name'&&r.kind==='chronology'));
  assert.ok(rows.filter(r=>r.kind==='chronology').every(r=>r.detail.includes('未核')||r.detail.includes('待核')));
});
test('search, status and category combine, and pagination is bounded and nonmutating',()=>{
  const found=filterUnfinished(rows,{kind:'identity',query:'Addison-Wesley Productions'});assert.equal(found.length,1);
  assert.equal(filterUnfinished(rows,{kind:'identity',status:'限版确认'}).length,0);
  const first=unfinishedPage(rows,1),second=unfinishedPage(rows,2);assert.equal(first.rows.length,20);assert.equal(second.rows.length,20);assert.notEqual(first.rows[0].id,second.rows[0].id);
  assert.equal(unfinishedPage([],99).page,1);assert.equal(unfinishedPage(rows,99999).page,Math.ceil(rows.length/20));
  assert.deepEqual(unfinishedPage(rows,1).rows,first.rows);
});
