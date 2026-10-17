import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const read=n=>JSON.parse(fs.readFileSync(new URL('../data/'+n,import.meta.url)));
const db=read('games.json');const co=read('company-coverage.json').companies.find(c=>c.id==='dataeast');
const added=db.works.filter(w=>/^g11(5[1-9]|6[01])$/.test(w.id));
const rows=read('gameplay-catalogues.json').companies.dataeast.groups.flatMap(g=>g.rows);
test('Data East adds eleven non-parser narratives and preserves old laserdisc IDs',()=>{
 assert.equal(added.length,11);assert.equal(co.workIds.length,14);
 assert.ok(['g082','g083','g085'].every(id=>co.workIds.includes(id)));
 for(const w of added)assert.ok(!w.interactionModes.includes('文字输入'));
 assert.equal(co.relatedGames.length,9);assert.equal(co.publisherWorkIds.length,13);
});
test('Dangerous Duo second disk is dependent content of the same case',()=>{
 const w=db.works.find(w=>w.id==='g1153');assert.equal(w.firstYear,1988);
 const cs=db.contentVersions.filter(c=>c.workId===w.id);assert.equal(cs.length,2);
 const c=cs.find(c=>c.basis==='added');assert.equal(c.firstYear,1989);assert.equal(c.comparedTo,'g1153-c-original');assert.ok(c.evidence.includes('已通关前篇'));
 assert.ok(!added.some(w=>w.originalTitle.endsWith('後編')));
});
test('shared original and remaster batches use one content identity per batch',()=>{
 for(const [cid,platforms] of [['g1155-c-original',['PlayStation','Sega Saturn']],['g1160-c-remaster',['PlayStation 4','PlayStation Vita']]]){
  const vs=db.platformReleases.filter(v=>v.contentVersionId===cid);assert.deepEqual(new Set(vs.map(v=>v.platform)),new Set(platforms));
  assert.ok(vs.every(v=>v.releaseRole==='contentDebut'));assert.equal(new Set(vs.map(v=>v.year)).size,1);
 }
 assert.equal(db.contentVersions.filter(c=>added.some(w=>w.id===c.workId)).length,13);
 assert.equal(db.platformReleases.filter(v=>added.some(w=>w.id===v.workId)).length,15);
 assert.equal(db.platformReleases.find(v=>v.workId==='g1159').publisher,'セガ');
 assert.ok(db.platformReleases.filter(v=>v.contentVersionId==='g1160-c-remaster').every(v=>v.publisher==='El Dia'));
});
test('automatic character changes and passwords are not free input or selectable perspective',()=>{
 const w=db.works.find(w=>w.id==='g1154');assert.ok(!w.interactionModes.includes('视角切换'));assert.ok(w.interactionNote.includes('自动'));
 assert.ok(db.works.find(w=>w.id==='g1156').interactionNote.includes('资料解锁码'));
});
test('Returns is sourced new area content within Metal Max, not another RPG identity',()=>{
 const w=co.relatedGames.find(w=>w.id==='dataeast-metalmax');assert.equal(w.contentVersions.length,2);
 const c=w.contentVersions.find(c=>c.basis==='added');assert.equal(c.comparedTo,w.id+'-c-original');assert.ok(c.evidence.includes('Devil’s Tower'));
 assert.ok(!co.relatedGames.some(w=>w.id.includes('returns')));
 assert.ok(!co.relatedGames.some(w=>w.originalTitle==='Shadowrun'));
});
test('reference appendix covers body once without admitting gameplay-only titles',()=>{
 assert.equal(rows.length,238);
 const linked=rows.filter(r=>r.workId).map(r=>r.workId);assert.equal(linked.length,23);
 assert.deepEqual(new Set(linked),new Set([...co.workIds,...co.relatedGames.map(w=>w.id)]));
 for(const t of ['Switch / Panic!','Cobra Command（1988）','Creature Shock','Voice Idol Maniacs / Voice Idol Collection: Pool Bar Story','Magical Drop III','Tattoo Assassins','Shadowrun（SFC）'])assert.ok(rows.some(r=>r.title===t&&!r.workId));
});
