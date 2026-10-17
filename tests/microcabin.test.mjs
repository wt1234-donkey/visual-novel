import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const read=n=>JSON.parse(fs.readFileSync(new URL('../data/'+n,import.meta.url)));
const db=read('games.json');
const co=read('company-coverage.json').companies.find(c=>c.id==='microcabin');
const newly=db.works.filter(w=>/^g11(4[2-9]|50)$/.test(w.id));
test('Micro Cabin adds nine menu narratives without duplicating old identities',()=>{
 assert.equal(newly.length,9);assert.equal(co.workIds.length,14);
 for(const w of newly)assert.ok(!w.interactionModes.includes('文字输入'));
 assert.deepEqual(co.legacyCommandWorkIds,['g097','g098','g133']);
 assert.ok(co.workIds.includes('g942')&&co.workIds.includes('g1060'));
 assert.ok(!co.workIds.includes('g001')&&!co.workIds.includes('g946'));
});
test('parser-only bibliography never acquires main contents or releases',()=>{
 assert.equal(co.dossierOnlyWorks.length,7);
 for(const w of co.dossierOnlyWorks){assert.ok(w.interactionModes.includes('文字输入'));assert.ok(!db.works.some(x=>x.id===w.id));assert.ok(!w.contentVersions&&!w.platformReleases);}
});
test('JX artwork increment is compared and ordinary ports do not expand new works',()=>{
 const c=db.contentVersions.filter(x=>newly.some(w=>w.id===x.workId));assert.equal(c.length,10);
 const added=c.filter(x=>x.basis==='added');assert.equal(added.length,1);assert.equal(added[0].comparedTo,'g1142-c-original');assert.ok(added[0].addedContent[0].description.includes('110'));
 assert.equal(db.platformReleases.filter(x=>newly.some(w=>w.id===x.workId)).length,10);
});
test('RPG development and publishing credits remain distinct',()=>{
 assert.equal(co.relatedGames.length,13);
 assert.equal(co.relatedGames.find(w=>w.id==='microcabin-riglord').platformReleases[0].publisher,'セガ');
 assert.equal(co.relatedGames.find(w=>w.id==='microcabin-nirgends').platformReleases[0].publisher,'NECホームエレクトロニクス');
 assert.ok(co.relatedGames.find(w=>w.id==='microcabin-dragonhalf').notes.includes('另一身份'));
});
test('raising, board, action and control-pending rows remain reference only',()=>{
 const rows=read('gameplay-catalogues.json').companies.microcabin.groups.flatMap(x=>x.rows);
 assert.equal(rows.length,115);
 for(const t of ['マリオネットカンパニー','プリンセスメーカー','ファイナリスト','宝ビルアドベンチャー','ギャルッぽクラブ','ドラゴンハーフ（PC Engine，1994）'])assert.ok(rows.some(r=>r.title===t&&!r.workId));
 const all=[...co.workIds,...co.relatedGames.map(w=>w.id),...co.dossierOnlyWorks.map(w=>w.id)];
 assert.deepEqual(new Set(rows.filter(r=>r.workId).map(r=>r.workId)),new Set(all));
});
