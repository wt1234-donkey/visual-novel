import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=p=>JSON.parse(readFileSync(new URL('../data/'+p,import.meta.url),'utf8'));
const data=read('games.json');
const co=read('company-coverage.json').companies.find(c=>c.id==='te_soft');
const table=read('gameplay-catalogues.json').companies.te_soft;
const related=id=>co.relatedGames.find(w=>w.id==='te-soft-'+id);

test('T&E is Japanese; two nonparser adventures join the main catalogue and old identities are reused',()=>{
 assert.equal(co.foundedAt,'1982-10');
 assert.match(co.publisherNote,/日本/);
 assert.deepEqual(co.workIds,['g1173','g1174','g073','g087','g088','g010']);
 for(const id of ['g1173','g1174'])assert.ok(!data.works.find(w=>w.id===id).interactionModes.includes('文字输入'));
 for(const id of ['g073','g087','g088'])assert.ok(data.works.find(w=>w.id===id).interactionModes.includes('文字输入'));
 assert.equal(data.works.find(w=>w.id==='g087').firstYear,1983);
 assert.ok(!co.relatedGames.some(w=>/Star Arthur|Dragon.s Lair/.test(w.originalTitle)));
 assert.ok(!co.dossierOnlyWorks?.length);
});

test('remakes and SFC scenarios are sourced additions under the original work identity',()=>{
 assert.equal(co.relatedGames.length,20);
 assert.equal(co.relatedGames.flatMap(w=>w.contentVersions).length,27);
 assert.equal(co.relatedGames.flatMap(w=>w.platformReleases).length,27);
 assert.equal(related('hydlide').contentVersions.length,5);
 assert.equal(related('hydlide-3').contentVersions.length,3);
 assert.equal(related('sword-world').contentVersions.length,2);
 for(const w of co.relatedGames){
  assert.ok(!w.interactionModes.includes('文字输入'));
  assert.ok(!data.works.some(x=>x.id===w.id));
  assert.equal(w.contentVersions.filter(c=>c.basis==='original').length,1);
  assert.ok(w.platformReleases.every(r=>r.releaseRole==='contentDebut'));
  for(const c of w.contentVersions.filter(c=>c.basis==='added')){
   assert.equal(c.comparedTo,w.id+'-c-original');assert.ok(c.addedContent[0].source);
  }
 }
 assert.ok(!co.relatedGames.some(w=>/^Virtual Hydlide$/.test(w.originalTitle)));
 assert.match(related('hydlide').platformReleases.find(r=>r.year===1995).publisher,/世嘉/);
 assert.equal(related('hydlide').platformReleases.find(r=>r.year===1986).publisher,'東芝EMI');
 assert.match(related('bushi').notes,/Game Freak开发/);
 assert.match(related('ashguine-2').platformReleases[0].publisher,/Panasoft/);
});

test('DAIVA stories differ by protagonist and the strategy finale has no copied action modes',()=>{
 const stories=co.relatedGames.filter(w=>w.id.startsWith('te-soft-daiva-'));
 assert.equal(stories.length,7);
 assert.equal(new Set(stories.map(w=>w.characters[0])).size,7);
 assert.deepEqual(stories.map(w=>w.firstYear),[1987,1987,1987,1987,1987,1986,1988]);
 for(const w of stories.slice(0,6))assert.ok(w.interactionModes.includes('瞄准射击'));
 assert.deepEqual(stories[6].interactionModes,['菜单指令','资源经营','战术策略']);
 assert.equal(stories[5].platformReleases[0].publisher,'東芝EMI');
});

test('gameplay reference preserves excluded genres and uncertain controls without fabricating releases',()=>{
 const rows=table.groups.flatMap(g=>g.rows);
 assert.equal(rows.length,99);assert.equal(table.groups.length,9);
 assert.equal(rows.filter(r=>r.workId).length,26);
 for(const part of ['Slayer','Blade Chronicle','Shiren','Real Golf Game','Chronicle RE:']){
  const row=rows.find(r=>r.title?.includes(part));assert.ok(row&&!row.workId);
  assert.ok(!row.platformReleases&&!row.contentVersions);
 }
 const page=readFileSync(new URL('../te_soft.html',import.meta.url),'utf8');
 assert.equal(page.split('<article class="card"').length-1,26);
 assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
 assert.match(readFileSync(new URL('../index.html',import.meta.url),'utf8'),/href="te_soft.html">T&amp;E SOFT（日本）社/);
});
