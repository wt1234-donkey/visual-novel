import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=n=>JSON.parse(readFileSync(new URL('../data/'+n,import.meta.url),'utf8'));
const data=read('games.json'),co=read('company-coverage.json').companies.find(c=>c.id==='db_soft');
const table=read('gameplay-catalogues.json').companies.db_soft;
const related=key=>co.relatedGames.find(w=>w.id==='db-soft-'+key);

test('dB narrative admissions distinguish remembered menu words from parser input',()=>{
 assert.deepEqual(co.workIds,['g746','g747']);assert.equal(co.relatedGames.length,4);
 for(const w of co.relatedGames){
  assert.ok(!w.interactionModes.includes('文字输入'));assert.ok(!w.interactionModes.includes('待核实'));
  assert.ok(!data.works.some(x=>x.id===w.id));
  assert.equal(w.contentVersions.length,1);assert.equal(w.platformReleases.length,1);
  const c=w.contentVersions[0],r=w.platformReleases[0];
  assert.equal(c.basis,'original');assert.deepEqual(c.evidenceReleaseIds,[r.id]);
  assert.equal(r.contentVersionId,c.id);assert.equal(r.releaseRole,'contentDebut');
  assert.equal(r.publisher,'デービーソフト');assert.deepEqual(r.publisherCompanies,['dB-SOFT']);
 }
 assert.match(related('melroon').interactionNote,/从已记住的话语中选择/);
 assert.ok(!related('melroon').interactionModes.includes('战斗指令'));
 assert.match(related('produce').interactionNote,/不直接操纵/);
 assert.ok(related('produce').interactionModes.includes('战术策略'));
 assert.match(related('layla').notes,/固定密码不作为叙事文字输入/);
 assert.match(related('melroon').notes,/11\/30.*12月/);
});

test('two typed adventures remain bibliography, without database content or releases',()=>{
 assert.deepEqual(co.dossierOnlyWorks.map(w=>w.id),['db-soft-south-pacific','db-soft-don-juan']);
 for(const w of co.dossierOnlyWorks){
  assert.ok(w.interactionModes.includes('文字输入'));assert.ok(!('contentVersions' in w));
  assert.ok(!('platformReleases' in w));assert.ok(!data.works.some(x=>x.id===w.id));
 }
});

test('dB page reuses brand identities once and keeps sparse, pure and cancelled references outside cards',()=>{
 const page=readFileSync(new URL('../db_soft.html',import.meta.url),'utf8');
 const ids=[...co.workIds,...co.relatedGames.map(w=>w.id),...co.dossierOnlyWorks.map(w=>w.id)];
 assert.equal(ids.length,8);
 for(const id of ids)assert.equal(page.split(`class="card" id="${id}"`).length-1,1,id);
 const rows=table.groups.flatMap(g=>g.rows),refs=rows.filter(r=>r.workId).map(r=>r.workId);
 assert.equal(rows.length,75);assert.equal(table.groups.length,7);assert.deepEqual([...refs].sort(),[...ids].sort());
 assert.equal(co.foundedAt,'1980-05');
 assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
 for(const title of ['クロスブレイム／Cross Blaim（1986／MSX）','ブラックウィング／Black Wing','鉄道王II（GB计划）']){
  assert.ok(rows.some(r=>r.title===title&&!r.workId));
  assert.ok(!co.relatedGames.some(w=>w.originalTitle===title));
 }
 assert.ok(rows.filter(r=>r.type?.includes('具体玩法待核')).length>0);
 assert.match(rows.find(r=>r.title==='Flappy Special（1990／GB）').note,/Victor/);
 assert.ok(readFileSync(new URL('../index.html',import.meta.url),'utf8').includes('href="db_soft.html"'));
});
