import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterCatalogue} from '../filter.mjs';
const read=n=>JSON.parse(readFileSync(new URL('../data/'+n,import.meta.url),'utf8'));
const data=read('games.json'),co=read('company-coverage.json').companies.find(c=>c.id==='konami');
const related=id=>co.relatedGames.find(w=>w.id==='konami-'+id);
const fresh=data.works.filter(w=>Number(w.id.slice(1))>=1216&&Number(w.id.slice(1))<=1228);

test('Konami reuses existing typed narrative and admits independent story spin-offs into main search',()=>{
 assert.equal(co.workIds.length,24);assert.equal(fresh.length,13);assert.equal(co.relatedGames.length,22);
 const sn=data.works.find(w=>w.id==='g040');assert.ok(sn.interactionModes.includes('文字输入'));assert.ok(sn.interactionModes.includes('菜单指令'));
 assert.match(sn.interactionNote,/后续版/);assert.ok(!co.dossierOnlyWorks?.some(w=>w.id==='g040'));
 for(const w of fresh){
  assert.ok(co.workIds.includes(w.id));
  for(const query of [w.chineseTitle,w.originalTitle])assert.ok(filterCatalogue(data,{query}).some(x=>x.work.id===w.id),query);
  const cv=data.contentVersions.filter(c=>c.workId===w.id),rs=data.platformReleases.filter(r=>r.workId===w.id);
  assert.equal(cv.length,1);assert.equal(cv[0].basis,'original');
  assert.deepEqual(cv[0].evidenceReleaseIds,rs.map(r=>r.id));assert.ok(rs.every(r=>r.releaseRole==='contentDebut'));
 }
 for(const id of ['g1217','g1218','g1219']){
  const rs=data.platformReleases.filter(r=>r.workId===id);assert.deepEqual(rs.map(r=>r.platform),['PlayStation','Saturn']);
  assert.equal(new Set(rs.map(r=>r.contentVersionId)).size,1);
 }
});

test('documented minigames and input boundaries are not copied across the whole romance series',()=>{
 const w=id=>data.works.find(w=>w.id===id);
 assert.ok(w('g1218').interactionModes.includes('节奏演奏'));
 assert.ok(w('g1220').interactionModes.includes('节奏演奏'));
 assert.ok(!w('g1221').interactionModes.includes('菜单指令'));
 assert.match(w('g1222').interactionNote,/EVS起名/);
 assert.ok(w('g1227').interactionModes.includes('谜题操作'));
 assert.ok(!w('g1227').interactionModes.includes('文字输入'));
 assert.ok(w('g1216').interactionModes.includes('即时动作'));
});

test('RPG and stealth stories preserve actual gameplay and do not enter main visual-novel categories',()=>{
 for(const w of co.relatedGames){assert.ok(!data.works.some(x=>x.id===w.id));assert.ok(w.contentVersions.some(c=>c.basis==='original'));}
 assert.deepEqual(related('acid2').interactionModes,['卡牌棋盘','战术策略']);
 assert.ok(!related('acid2').interactionModes.includes('即时动作'));
 assert.ok(related('suikoden3').interactionModes.includes('视角切换'));
 assert.ok(related('rhapsodia').interactionModes.includes('战术策略'));
 assert.ok(related('cardstories').interactionModes.includes('卡牌棋盘'));
 const star=related('starleap');assert.equal(star.firstYear,2026);
 assert.deepEqual(star.platformReleases.map(r=>r.platform),['iOS','Android']);
 assert.equal(new Set(star.platformReleases.map(r=>r.contentVersionId)).size,1);
 assert.equal(related('mgs').firstYear,1998);assert.equal(related('mgs3').firstYear,2004);
 assert.ok(!related('gz').platformReleases.some(r=>r.platform==='Windows'));
});

test('new material, platform variants and ordinary ports remain separate',()=>{
 const hd=related('suikoden1');assert.equal(hd.contentVersions.length,2);
 assert.match(hd.contentVersions[1].evidence,/重新绘制/);
 assert.equal(hd.platformReleases.filter(r=>r.year===2025).length,6);
 assert.ok(!hd.platformReleases.some(r=>r.platform==='Nintendo Switch 2'));
 assert.equal(related('suikoden2').contentVersions.length,1);
 const delta=related('mgs3');assert.equal(delta.contentVersions.length,3);
 const ps=delta.platformReleases.find(r=>r.platform==='PlayStation 5'),pc=delta.platformReleases.find(r=>r.platform==='Windows'),xb=delta.platformReleases.find(r=>r.platform==='Xbox Series X|S');
 assert.equal(ps.contentVersionId,pc.contentVersionId);assert.notEqual(ps.contentVersionId,xb.contentVersionId);
 for(const c of delta.contentVersions.filter(c=>c.basis==='added')){assert.equal(c.comparedTo,'konami-mgs3-c-original');assert.ok(c.addedContent.length);}
 assert.equal(co.relatedGames.reduce((n,w)=>n+w.contentVersions.length,0),25);
 assert.equal(co.relatedGames.reduce((n,w)=>n+w.platformReleases.length,0),39);
});

test('all Konami identities render once and pending series remain explicit reference rows',()=>{
 const page=readFileSync(new URL('../konami.html',import.meta.url),'utf8');
 const ids=[...co.workIds,...co.relatedGames.map(w=>w.id)];assert.equal(ids.length,46);
 for(const id of ids)assert.equal(page.split(`class="card" id="${id}"`).length-1,1,id);
 const table=read('gameplay-catalogues.json').companies.konami,rows=table.groups.flatMap(g=>g.rows);
 assert.equal(table.groups.length,9);assert.equal(rows.length,62);
 assert.deepEqual(rows.filter(r=>r.workId).map(r=>r.workId).sort(),ids.sort());
 assert.ok(rows.some(r=>r.title==='Silent Hill系列'&&!r.workId));
 assert.ok(rows.some(r=>r.title==='天与地／天と地と（PC-88 1990）'&&!r.workId));
 assert.match(co.scope,/原聊天完整清单未恢复/);
 assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
});
