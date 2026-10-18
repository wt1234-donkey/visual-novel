import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterCatalogue} from '../filter.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../data/'+p,import.meta.url),'utf8'));
const data=read('games.json');
const co=read('company-coverage.json').companies.find(c=>c.id==='hummingbird_soft');
const table=read('gameplay-catalogues.json').companies.hummingbird_soft;
const related=id=>co.relatedGames.find(w=>w.id==='hummingbird-'+id);

test('Agni is searchable through title, original name, publisher and menu controls without admitting parser books',()=>{
 for(const query of ['阿格尼之石','アグニの石','The Stone of Agni']){
  const results=filterCatalogue(data,{query,interaction:'菜单指令',company:'ハミングバードソフト'});
  assert.deepEqual(results.map(x=>x.work.id),['g1175']);
  assert.equal(results[0].contentVersions.length,1);
  assert.equal(results[0].platformReleases[0].year,1988);
 }
 assert.deepEqual(filterCatalogue(data,{company:'ハミングバードソフト',interaction:'文字输入'}).map(x=>x.work.id),['g101','g102','g105','g109']);
 for(const w of co.dossierOnlyWorks){
  assert.ok(w.interactionModes.includes('文字输入'));
  assert.ok(!data.works.some(x=>x.id===w.id));
  assert.ok(!('contentVersions' in w)&&!('platformReleases' in w));
 }
 assert.equal(data.platformReleases.find(r=>r.id==='g105-v2').contentVersionId,null);
 assert.equal(data.platformReleases.find(r=>r.id==='g105-v2').contentRelation,'unverified');
});

test('RPG identities keep first publisher, exclude ordinary ports and separate fixed film scenes from movie branching',()=>{
 assert.equal(co.relatedGames.length,12);
 for(const w of co.relatedGames){
  assert.ok(!w.interactionModes.includes('文字输入'));
  assert.ok(!data.works.some(x=>x.id===w.id));
  assert.equal(w.contentVersions.filter(c=>c.basis==='original').length,1);
  assert.ok(w.platformReleases.every(r=>r.releaseRole==='contentDebut'&&r.year===w.firstYear));
 }
 assert.equal(related('deep-dungeon').platformReleases[0].publisher,'スクウェア');
 assert.equal(related('deep-dungeon-4').platformReleases[0].publisher,'アスミック');
 assert.equal(related('black-death-mask').platformReleases[0].publisher,'松下電器産業');
 assert.ok(related('black-death-mask').interactionModes.includes('点击调查'));
 assert.notEqual(related('black-death-mask').category,'互动动画');
 assert.ok(!related('lodoss-sfc').interactionModes.includes('视角切换'));
 assert.equal(related('lodoss-sfc').platformReleases[0].publisher,'角川書店');
 assert.equal(related('garzey').platformReleases[0].platform,'Windows 95');
 assert.ok(related('garzey').interactionModes.includes('选项分支'));
 assert.ok(!co.relatedGames.some(w=>/英雄戦争|ソード・ワールド/.test(w.originalTitle)));
});

test('the appendix covers every body identity once while pure gameplay, tools and unshipped releases stay reference-only',()=>{
 const rows=table.groups.flatMap(g=>g.rows);
 const body=[...co.workIds,...co.relatedGames.map(w=>w.id),...co.dossierOnlyWorks.map(w=>w.id)];
 assert.deepEqual(rows.filter(r=>r.workId).map(r=>r.workId).sort(),body.sort());
 for(const part of ['福神漬（','福神漬3（','ファイアボール','DISK FRIEND','ロードス島戦記III']){
  const row=rows.find(r=>r.title?.includes(part));
  assert.ok(row&&!row.workId&&!row.contentVersions&&!row.platformReleases);
 }
 const page=readFileSync(new URL('../hummingbird_soft.html',import.meta.url),'utf8');
 assert.equal(page.split('<article class="card"').length-1,body.length);
 assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
});
