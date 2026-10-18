import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterCatalogue} from '../filter.mjs';
const read=n=>JSON.parse(readFileSync(new URL('../data/'+n,import.meta.url),'utf8'));
const data=read('games.json');
const co=read('company-coverage.json').companies.find(c=>c.id==='taito');
const table=read('gameplay-catalogues.json').companies.taito;
const main=data.works.filter(w=>['g1204','g1205','g1206'].includes(w.id));
const related=co.relatedGames.filter(w=>w.id!=='taito-uq');
const get=id=>related.find(w=>w.id===id);

test('TAITO menu narratives can be found by Chinese and original titles without admitting parser play',()=>{
 assert.equal(main.length,3);assert.equal(related.length,12);
 for(const w of [...main,...related]){
  assert.ok(!w.interactionModes.includes('文字输入'));
  assert.ok(!w.interactionModes.includes('待核实'));
  assert.ok(w.interactionSources.length);
 }
 for(const w of main){
  for(const query of [w.chineseTitle,w.originalTitle])assert.ok(filterCatalogue(data,{query}).some(x=>x.work.id===w.id));
  assert.equal(data.contentVersions.filter(c=>c.workId===w.id).length,1);
  assert.equal(data.platformReleases.filter(r=>r.workId===w.id).length,1);
 }
 assert.deepEqual(main.find(w=>w.id==='g1205').interactionModes,['阅读推进','菜单指令','点击调查','瞄准射击','即时动作']);
 for(const id of ['g1204','g1206'])assert.match(main.find(w=>w.id===id).interactionNote,/续关密码/);
});

test('symbol spellcraft, selected keywords and the mobile quiz are not free-form text commands',()=>{
 assert.match(get('taito-dungeon-magic').interactionNote,/固定符号/);
 assert.match(get('taito-energy-breaker').interactionNote,/关键词列表选择/);
 assert.match(get('taito-takeshi').interactionNote,/二选一／四选一/);
 assert.ok(get('taito-takeshi').interactionModes.includes('设备互动'));
 assert.ok(get('taito-takeshi').interactionModes.includes('知识问答'));
 assert.ok(get('taito-jarvas').interactionModes.includes('即时动作'));
 assert.ok(!get('taito-minelvaton').interactionModes.includes('战斗指令'));
});

test('first content additions retain comparison targets and same-batch mobile releases share one content',()=>{
 const additions=related.flatMap(w=>w.contentVersions.filter(c=>c.basis==='added').map(c=>({w,c})));
 assert.equal(additions.length,3);
 for(const {w,c} of additions){
  assert.equal(c.comparedTo,w.id+'-c-original');
  assert.ok(c.addedContent.length);
  const batch=w.platformReleases.filter(r=>r.contentVersionId===c.id);
  assert.deepEqual(batch.map(r=>r.id),c.evidenceReleaseIds);
  assert.ok(batch.every(r=>r.releaseRole==='contentDebut'&&r.contentRelation==='added'));
 }
 const m=get('taito-takeshi');const mobile=m.platformReleases.filter(r=>r.year===2017);
 assert.deepEqual(mobile.map(r=>r.platform),['iOS','Android']);
 assert.equal(new Set(mobile.map(r=>r.contentVersionId)).size,1);
 assert.match(mobile[0].differences,/あめりか/);
 assert.equal(get('taito-estpolis2').platformReleases.find(r=>r.year===2010).publisher,'Square Enix');
 assert.equal(get('taito-dungeon-magic').platformReleases[0].publisher,'Natsume');
 assert.equal(get('taito-dungeon-magic').firstYear,1989);
 assert.equal(get('taito-estpolis-returns').firstYear,2001);
});

test('ordinary ports, other publishers, prototypes and future compilations stay as references',()=>{
 assert.equal(co.workIds.length+co.relatedGames.length,22);
 const rows=table.groups.flatMap(g=>g.rows),refs=rows.filter(r=>r.workId).map(r=>r.workId);
 assert.equal(rows.length,156);assert.equal(table.groups.length,10);
 assert.deepEqual([...refs].sort(),[...co.workIds,...co.relatedGames.map(w=>w.id)].sort());
 assert.equal(refs.length,new Set(refs).size);
 for(const title of ['エストポリス伝記 I＆II（2027预定）','Lufia III: Ruins Chaser','京都財テク殺人事件（1990）','Light Bringer（官方初出1993）','クレオパトラの魔宝（1987）']){
  const row=rows.find(r=>r.title===title);assert.ok(row&&row.type&&row.relation&&!row.workId);
 }
 assert.ok(related.flatMap(w=>w.platformReleases).every(r=>r.year<=2026));
 assert.equal(related.flatMap(w=>w.contentVersions).length,15);
 assert.equal(related.flatMap(w=>w.platformReleases).length,16);
});
