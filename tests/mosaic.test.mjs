import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterCatalogue} from '../filter.mjs';
const read=n=>JSON.parse(readFileSync(new URL('../data/'+n,import.meta.url),'utf8'));
const data=read('games.json');
const co=read('company-coverage.json').companies.find(c=>c.id==='mosaic');
const table=read('gameplay-catalogues.json').companies.mosaic;
const added=data.works.filter(w=>co.workIds.includes(w.id)&&w.id!=='g131');

test('Mosaic admits four selectable narratives while retaining only the existing Erik parser identity',()=>{
 assert.equal(added.length,4);
 for(const w of added){
  for(const query of [w.chineseTitle,w.originalTitle]) assert.ok(filterCatalogue(data,{query}).some(x=>x.work.id===w.id));
  assert.ok(!w.interactionModes.includes('文字输入'));
  assert.ok(w.interactionModes.includes('选项分支'));
  assert.equal(data.contentVersions.filter(c=>c.workId===w.id).length,1);
  assert.equal(data.platformReleases.filter(r=>r.workId===w.id).length,1);
 }
 assert.deepEqual(co.legacyCommandWorkIds,['g131']);
 assert.ok(data.works.find(w=>w.id==='g131').interactionModes.includes('文字输入'));
 const asciiQuery=filterCatalogue(data,{query:'The Secret Diary of Adrian Mole Aged 13 3/4'});
 assert.ok(asciiQuery.some(x=>x.work.id==='g1200'));
});

test('numeric story choices, system storage commands and office hotspots remain distinct',()=>{
 for(const id of ['g1200','g1201','g1203']){
  const w=added.find(w=>w.id===id);
  assert.deepEqual(w.interactionModes,['阅读推进','选项分支']);
  assert.match(w.interactionNote,/SAVE.*LOAD/);
  assert.match(w.interactionNote,/系统/);
  assert.match(w.interactionSources[0],/-manual\.pdf$/);
 }
 const y=added.find(w=>w.id==='g1202');
 assert.deepEqual(y.interactionModes,['阅读推进','选项分支','点击调查','菜单指令']);
 assert.ok(!y.interactionModes.includes('直接移动'));
 assert.ok(!added.find(w=>w.id==='g1201').interactionModes.includes('视角切换'));
 assert.match(y.interactionNote,/Hackergram/);
});

test('all six new parser bibliographies stay outside works, contents and releases even with mixed controls',()=>{
 assert.equal(co.dossierOnlyWorks.length,6);
 for(const w of co.dossierOnlyWorks){
  assert.ok(w.interactionModes.includes('文字输入'));
  assert.ok(!('contentVersions' in w)&&!('platformReleases' in w)&&!('versions' in w));
  assert.ok(!data.works.some(x=>x.id===w.id));
  assert.ok(!data.contentVersions.some(x=>x.workId===w.id));
  assert.ok(!data.platformReleases.some(x=>x.workId===w.id));
 }
 const n=co.dossierOnlyWorks.find(w=>w.id==='mosaic-nomad');
 assert.ok(n.interactionModes.includes('菜单指令'));
 assert.ok(n.interactionModes.includes('文字输入'));
 assert.equal(co.dossierOnlyWorks.find(w=>w.id==='mosaic-snow-queen').firstYear,1986);
 assert.match(co.dossierOnlyWorks.find(w=>w.id==='mosaic-steel-rat').interactionSources[0],/steelrat\.pdf$/);
});

test('original publishers, segmented stories and plans preserve independent identities',()=>{
 assert.equal(data.platformReleases.find(r=>r.workId==='g1203').publisher,'Virgin Games Ltd');
 for(const id of ['g1200','g1201','g1202']) assert.equal(data.platformReleases.find(r=>r.workId===id).publisher,'Mosaic Publishing Ltd');
 for(const w of added) assert.ok(data.platformReleases.filter(r=>r.workId===w.id).every(r=>r.releaseRole==='contentDebut'&&r.voice==='未核实'));
 const rows=table.groups.flatMap(g=>g.rows);
 assert.equal(rows.length,34);
 const refs=rows.filter(r=>r.workId).map(r=>r.workId);
 assert.deepEqual([...refs].sort(),[...co.workIds,...co.dossierOnlyWorks.map(w=>w.id)].sort());
 assert.equal(refs.length,new Set(refs).size);
 assert.equal(co.relatedGames.length,0);
 for(const title of ['Raffles','Alice','The Story of the Amulet／The Amulet','My Secret File','The Stainless Steel Rat：Spectrum条目']){
  const r=rows.find(r=>r.title===title);assert.ok(r&&r.type&&r.relation&&!('workId' in r));
 }
 assert.match(co.scope,/原聊天.*未完整/);
});
