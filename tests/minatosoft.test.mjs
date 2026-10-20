import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterCatalogue} from '../filter.mjs';
const read=n=>JSON.parse(readFileSync(new URL('../data/'+n,import.meta.url),'utf8'));
const db=read('games.json'),co=read('company-coverage.json').companies.find(c=>c.id==='minatosoft');
const review=read('minatosoft-source-review.json');
const row=k=>review.rows.find(r=>r.key===k);
const work=k=>db.works.find(w=>w.id===row(k).workIds[0]);
const contents=k=>db.contentVersions.filter(c=>c.workId===work(k).id);

test('Minato independent chapters are searchable and all 32 supplied rows resolve',()=>{
 assert.equal(co.workIds.length,24);assert.equal(co.relatedGames.length,3);
 assert.equal(review.rows.length,32);assert.equal(new Set(review.rows.map(r=>r.key)).size,32);
 const all=new Set([...co.workIds,...co.relatedGames.map(w=>w.id)]);
 for(const r of review.rows){assert.ok(r.note&&r.source);assert.ok(r.workIds.every(id=>all.has(id)));}
 for(const id of co.workIds){
  const w=db.works.find(w=>w.id===id);
  for(const query of [w.chineseTitle,w.originalTitle])assert.ok(filterCatalogue(db,{query}).some(x=>x.work.id===id),query);
  assert.equal(db.contentVersions.filter(c=>c.workId===id&&c.basis==='original').length,1);
 }
 const chapters=['a1','a2','a3','a4','a5'].map(k=>work(k).id);
 assert.equal(new Set(chapters).size,5);assert.deepEqual(row('a-package').workIds,chapters);
 assert.ok(!chapters.includes(work('plus').id));assert.match(work('plus').bundledWith,/初回特典/);
 assert.notEqual(work('majikoi').id,work('majikoi-s').id);
 assert.equal(row('mahjong').workIds.length,0);
});

test('ports reuse identities and only concrete first content additions create versions',()=>{
 assert.deepEqual(row('kimi-ps2').workIds,[work('kimi').id]);
 assert.deepEqual(row('majikoi-r').workIds,[work('majikoi').id]);
 assert.deepEqual(row('kenran').workIds,[work('kurogane').id]);
 assert.equal(contents('kimi').length,3);assert.equal(contents('majikoi').length,2);assert.equal(contents('kurogane').length,2);
 const psp=contents('kimi').find(c=>c.id.endsWith('psp-extra'));
 assert.ok(psp.comparedTo.endsWith('ps2-story'));assert.match(psp.evidence,/新增.*CG.*脱出/);
 for(const id of co.workIds){for(const c of db.contentVersions.filter(c=>c.workId===id)){
  const rs=db.platformReleases.filter(r=>r.contentVersionId===c.id);
  assert.deepEqual(c.evidenceReleaseIds,rs.map(r=>r.id));assert.ok(rs.every(r=>r.releaseRole==='contentDebut'&&r.year===c.firstYear));
  if(c.basis==='added'){assert.ok(c.comparedTo&&c.addedContent.length);}
 }}
 assert.equal(db.contentVersions.filter(c=>co.workIds.includes(c.workId)).length,28);
 assert.equal(db.platformReleases.filter(r=>co.workIds.includes(r.workId)).length,28);
 assert.match(work('ichigo').notes,/独立运行/);
 assert.equal(db.platformReleases.find(r=>r.workId===work('ichigo').id).publisher,'RED FLAG SHIP');
});

test('bonus games keep actual publication and linear controls; battle themes do not infer combat',()=>{
 for(const k of ['yuyuyu','yuyuyu-s','yuyuyu-a']){
  const w=work(k);assert.equal(w.releaseContext,'bundledSample');assert.ok(w.bundledWith);
  assert.deepEqual(w.interactionModes,['阅读推进']);assert.equal(w.subcategory,'单线视觉小说');
  assert.equal(db.platformReleases.find(r=>r.workId===w.id).publisher,'ポニーキャニオン');
 }
 assert.deepEqual(['yuyuyu','yuyuyu-s','yuyuyu-a'].map(k=>work(k).firstYear),[2014,2015,2018]);
 for(const k of ['kurogane','wagahime','majikoi','waka']){
  assert.ok(!work(k).interactionModes.includes('即时动作'));assert.ok(!work(k).interactionModes.includes('战斗指令'));
 }
 assert.ok(work('majikoi').interactionModes.includes('规则对战'));assert.match(work('majikoi').interactionNote,/仅PS3/);
 assert.ok(work('carnivalfd').interactionModes.includes('规则对战'));
 assert.match(co.publisherNote,/株式会社ホークアイ/);
 assert.ok(!co.publisherWorkIds); // shared dossier scope is not a single publisher alias
 const climax=co.relatedGames.find(w=>w.id==='minatosoft-climax');
 assert.deepEqual(climax.platformReleases.map(r=>r.platform),['Web']);assert.match(climax.notes,/2024-10-03停服/);
 for(const w of co.relatedGames){assert.ok(!db.works.some(x=>x.id===w.id));assert.equal(w.contentVersions.length,1);}
});

test('the dossier renders each shared identity once and links the complete reference table',()=>{
 const page=readFileSync(new URL('../minatosoft.html',import.meta.url),'utf8');
 const ids=[...co.workIds,...co.relatedGames.map(w=>w.id)];
 for(const id of ids)assert.equal(page.split(`class="card" id="${id}"`).length-1,1,id);
 const rows=read('gameplay-catalogues.json').companies.minatosoft.groups.flatMap(g=>g.rows);
 assert.equal(rows.length,33);assert.deepEqual(rows.filter(r=>r.workId).map(r=>r.workId).sort(),ids.sort());
 assert.ok(rows.some(r=>r.title?.startsWith('クロガネ回姫雀')&&!r.workId));
 assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
 const home=readFileSync(new URL('../index.html',import.meta.url),'utf8');
 assert.match(home,/data-company="minatosoft" data-first-year="2007"/);
});
