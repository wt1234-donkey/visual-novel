import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterCatalogue} from '../filter.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../data/'+p,import.meta.url),'utf8'));
const data=read('games.json');
const co=read('company-coverage.json').companies.find(c=>c.id==='riverhill_soft');
const table=read('gameplay-catalogues.json').companies.riverhill_soft;
const related=id=>co.relatedGames.find(w=>w.id==='riverhill-'+id);

test('Riverhill menu narratives are searchable without admitting additional parser works',()=>{
 for(const query of ['阿格雷斯','AGGRES','ZODIAC 2']){
  const rows=filterCatalogue(data,{query,interaction:'菜单指令',company:'リバーヒルソフト'});
  assert.deepEqual(rows.map(x=>x.work.id),['g1177']);
  assert.equal(rows[0].contentVersions.length,1);
  assert.equal(rows[0].platformReleases[0].year,1986);
 }
 assert.deepEqual(filterCatalogue(data,{company:'リバーヒルソフト',interaction:'文字输入'}).map(x=>x.work.id).sort(),co.legacyCommandWorkIds.slice().sort());
 for(const w of data.works.filter(w=>/^g11(7[6-9]|8[0-9]|9[0-2])$/.test(w.id))) assert.ok(!w.interactionModes.includes('文字输入'));
 assert.equal(data.platformReleases.find(r=>r.workId==='g1176').publisher,'ユニオンプランニング');
});

test('Blue Chicago keeps LaserActive debut and foreign originals keep original publishers',()=>{
 const blue=data.works.find(w=>w.id==='g1187');
 assert.equal(blue.firstYear,1994);
 const r=data.platformReleases.filter(r=>r.workId===blue.id);
 assert.equal(r.length,1);assert.equal(r[0].platform,'LaserActive LD-ROM²');assert.equal(r[0].publisher,'パイオニアLDC');
 assert.equal(data.platformReleases.find(r=>r.workId==='g1188').publisher,'Simon & Schuster Interactive');
 assert.equal(data.platformReleases.find(r=>r.workId==='g1189').publisher,'Activision');
 assert.ok(co.workIds.includes('g967'));
 assert.equal(co.relatedGames.filter(w=>/Skullmonkeys/.test(w.originalTitle)).length,1);
 assert.ok(!co.relatedGames.some(w=>w.originalTitle==='The Neverhood'));
});

test('Ogre Saturn additions share original work identity and record actual first added content',()=>{
 for(const key of ['ogre','tactics']){
  const w=related(key);assert.equal(w.contentVersions.length,2);assert.equal(w.platformReleases.length,2);
  assert.equal(w.contentVersions[1].comparedTo,w.contentVersions[0].id);
  assert.equal(w.platformReleases[0].publisher,'クエスト');
  assert.equal(w.platformReleases[1].publisher,'リバーヒルソフト');
  assert.equal(w.platformReleases[1].contentRelation,'added');
  assert.ok(w.platformReleases.every(r=>r.releaseRole==='contentDebut'));
 }
 assert.match(related('ogre').contentVersions[1].addedContent[0].description,/五个可玩剧本/);
 assert.match(related('tactics').contentVersions[1].addedContent[0].description,/录音/);
 assert.equal(related('tactics').platformReleases[1].voice,'有（部分）');
 assert.equal(related('burai-lower').platformReleases[0].platform,'PC-9801');
 assert.equal(related('burai-lower').firstYear,1990);
 assert.equal(related('abe').firstYear,1998);
 assert.ok(!related('abe').interactionModes.includes('文字输入'));
 assert.ok(!related('kigen').interactionModes.includes('即时动作'));
 assert.equal(related('hauzer').platformReleases[0].publisher,'松下電器産業');
 assert.equal(related('dora').platformReleases[0].publisher,'小学館');
});

test('parser originals, life simulations and ambiguous affiliations remain outside new database admission',()=>{
 for(const w of co.dossierOnlyWorks){
  assert.ok(w.interactionModes.includes('文字输入'));
  assert.ok(!data.works.some(x=>x.id===w.id));
  assert.ok(!('contentVersions' in w)&&!('platformReleases' in w));
 }
 const rows=table.groups.flatMap(g=>g.rows);
 const body=[...co.workIds,...co.relatedGames.map(w=>w.id),...co.dossierOnlyWorks.map(w=>w.id)];
 assert.deepEqual(rows.filter(r=>r.workId).map(r=>r.workId).sort(),body.sort());
 for(const title of ['World Neverland ～オルルド','あどべんちゃーイン博多','Dragon（','Private eye dol','クレイマン ガンホッケー','ゼノビアの皇子']){
  assert.ok(rows.some(r=>r.title?.includes(title)&&!r.workId));
 }
 const page=readFileSync(new URL('../riverhill_soft.html',import.meta.url),'utf8');
 assert.equal(page.split('<article class="card"').length-1,body.length);
 assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
});
