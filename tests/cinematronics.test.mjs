import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const read=n=>JSON.parse(fs.readFileSync(new URL('../data/'+n,import.meta.url)));
const db=read('games.json');const co=read('company-coverage.json').companies.find(c=>c.id==='cinematronics');
const appendix=read('gameplay-catalogues.json').companies.cinematronics;
const rows=appendix.groups.flatMap(g=>g.rows);
test('Cinematronics reuses three existing non-parser narratives and preserves publisher identity',()=>{
 assert.deepEqual(co.workIds,['g010','g044','g045']);
 for(const id of co.workIds){const w=db.works.find(w=>w.id===id);assert.ok(w.interactionModes.includes('限时反应'));assert.ok(!w.interactionModes.includes('文字输入'));}
 assert.deepEqual(co.publisherWorkIds,['g010','g044']);
 assert.equal(db.platformReleases.find(v=>v.workId==='g045').publisher,'Leland');
});
test('gameplay appendix covers every body identity exactly once',()=>{
 assert.equal(appendix.groups.length,9);assert.equal(rows.length,80);
 assert.deepEqual(rows.filter(r=>r.workId).map(r=>r.workId),co.workIds);
 for(const r of rows.filter(r=>!r.workId)){assert.ok(r.type&&r.relation&&r.note);assert.ok(!r.contentVersions&&!r.platformReleases);}
});
test('aliases, prototypes, same-name company and RDI remain reference-only',()=>{
 for(const title of ['Zzyzzyxx','Brix','Up Your Alley','Hovercraft','Express Delivery','Crucible','Full Tilt! Pinball','Thayer’s Quest'])assert.ok(rows.some(r=>r.title===title&&!r.workId));
 const tq=rows.find(r=>r.title==='Thayer’s Quest');assert.ok(tq.note.includes('RDI'));assert.ok(tq.note.includes('不能仅因有键盘'));
 const llc=appendix.groups.find(g=>g.title.includes('1994'));assert.ok(llc.note.includes('不同法人'));assert.ok(!llc.rows.some(r=>r.workId));
});
test('ordinary re-releases do not create additional content records',()=>{
 assert.equal(db.contentVersions.filter(c=>co.workIds.includes(c.workId)).length,4);
 assert.equal(db.platformReleases.filter(v=>co.workIds.includes(v.workId)).length,4);
 const extras=db.contentVersions.filter(c=>co.workIds.includes(c.workId)&&c.basis==='added');assert.equal(extras.length,1);assert.equal(extras[0].firstYear,2002);
});
