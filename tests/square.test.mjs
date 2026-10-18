import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterCatalogue} from '../filter.mjs';
const read=n=>JSON.parse(readFileSync(new URL('../data/'+n,import.meta.url),'utf8'));
const data=read('games.json');
const co=read('company-coverage.json').companies.find(c=>c.id==='square');
const table=read('gameplay-catalogues.json').companies.square;
const fresh=data.works.filter(w=>['g1207','g1208','g1209','g1210','g1211'].includes(w.id));
const related=id=>co.relatedGames.find(w=>w.id==='square-'+id);

test('Square menu, sound-novel and filmed narratives are searchable without parser admission',()=>{
 assert.equal(fresh.length,5);assert.equal(co.relatedGames.length,62);
 for(const w of [...fresh,...co.relatedGames]){
  assert.ok(!w.interactionModes.includes('文字输入'));
  assert.ok(!w.interactionModes.includes('待核实'));
  assert.ok(w.interactionSources.length);
 }
 for(const w of fresh){
  for(const query of [w.chineseTitle,w.originalTitle])assert.ok(filterCatalogue(data,{query}).some(x=>x.work.id===w.id));
  assert.equal(data.contentVersions.filter(c=>c.workId===w.id).length,1);
  assert.equal(data.platformReleases.filter(r=>r.workId===w.id).length,1);
 }
 assert.match(fresh.find(w=>w.id==='g1211').interactionNote,/预设列表/);
 assert.match(related('ff2').interactionNote,/关键词列表选择/);
 assert.ok(!related('dynami').interactionModes.includes('战斗指令'));
 assert.ok(related('treasure-conflix').interactionModes.includes('驾驶操控'));
});

test('free spell creation, parser commands and online chat remain only in the dossier',()=>{
 assert.deepEqual(co.legacyCommandWorkIds,['g076','g081']);
 assert.deepEqual(co.dossierOnlyWorks.map(w=>w.id),['square-alpha','square-rudra','square-ff11']);
 for(const w of co.dossierOnlyWorks){
  assert.ok(w.interactionModes.includes('文字输入'));
  assert.ok(!data.works.some(x=>x.id===w.id));
  assert.ok(!('contentVersions' in w));assert.ok(!('platformReleases' in w));
 }
 assert.match(co.dossierOnlyWorks.find(w=>w.id==='square-rudra').interactionNote,/决定魔法效果/);
 assert.match(co.dossierOnlyWorks.find(w=>w.id==='square-ff11').interactionNote,/斜杠命令/);
});

test('original and later content credits do not collapse into the successor publisher',()=>{
 const additions=co.relatedGames.flatMap(w=>w.contentVersions.filter(c=>c.basis==='added').map(c=>({w,c})));
 assert.equal(additions.length,8);
 for(const {w,c} of additions){
  assert.equal(c.comparedTo,w.id+'-c-original');assert.ok(c.addedContent.length);
  const batch=w.platformReleases.filter(r=>r.contentVersionId===c.id);
  assert.deepEqual(batch.map(r=>r.id),c.evidenceReleaseIds);
  assert.ok(batch.every(r=>r.releaseRole==='contentDebut'&&r.contentRelation==='added'));
 }
 assert.equal(related('bof').firstYear,1993);
 assert.equal(related('bof').platformReleases[0].publisher,'Capcom');
 assert.equal(related('ffusa').firstYear,1992);
 assert.equal(related('mario-rpg').platformReleases[0].publisher,'任天堂');
 assert.equal(data.platformReleases.find(r=>r.workId==='g1209').publisher,'任天堂');
 const sf=related('sf').platformReleases.filter(r=>r.year===2021);
 assert.equal(sf.length,4);assert.equal(new Set(sf.map(r=>r.contentVersionId)).size,1);
 assert.ok(sf.every(r=>r.publisher==='Square Enix'));
 assert.equal(related('seiken3').platformReleases.filter(r=>r.year===2020).length,2);
 assert.equal(co.relatedGames.flatMap(w=>w.contentVersions).length,70);
 assert.equal(co.relatedGames.flatMap(w=>w.platformReleases).length,74);
});

test('all cards render once, reused collaborations link to original identities, and references stay last',()=>{
 const page=readFileSync(new URL('../square.html',import.meta.url),'utf8');
 const ids=[...co.workIds,...co.relatedGames.map(w=>w.id),...co.dossierOnlyWorks.map(w=>w.id)];
 assert.equal(ids.length,72);assert.equal(new Set(ids).size,72);
 for(const id of ids)assert.equal(page.split(`class="card" id="${id}"`).length-1,1,id);
 const rows=table.groups.flatMap(g=>g.rows),refs=rows.filter(r=>r.workId).map(r=>r.workId);
 assert.equal(rows.length,138);assert.equal(table.groups.length,6);
 assert.deepEqual([...refs].sort(),[...ids].sort());
 for(const id of ['carry-lab-hao','hummingbird-deep-dungeon','hummingbird-deep-dungeon-2','hummingbird-deep-dungeon-3']){
  assert.ok(!ids.includes(id));assert.ok(rows.some(r=>r.source?.endsWith('#'+id)));
 }
 for(const title of ['Apple Town Story（1987）','恋はバランス（1996）','牌神2（1998）','Final Fantasy III WonderSwan Color计划']){
  assert.ok(rows.some(r=>r.title===title&&!r.workId));
 }
 assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
 assert.ok(co.relatedGames.flatMap(w=>w.platformReleases).every(r=>r.year<=2026));
});
