import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterCatalogue} from '../filter.mjs';
const read=n=>JSON.parse(readFileSync(new URL('../data/'+n,import.meta.url),'utf8'));
const data=read('games.json'),co=read('company-coverage.json').companies.find(c=>c.id==='toho');
const table=read('gameplay-catalogues.json').companies.toho;
const fresh=data.works.filter(w=>['g1212','g1213','g1214'].includes(w.id));
const related=key=>co.relatedGames.find(w=>w.id==='toho-'+key);

test('TOHO admits documented menu narratives but retains mixed input as dossier bibliography',()=>{
 assert.equal(fresh.length,3);assert.equal(co.relatedGames.length,11);
 for(const w of [...fresh,...co.relatedGames]){
  assert.ok(!w.interactionModes.includes('文字输入'));
  assert.ok(!w.interactionModes.includes('待核实'));
 }
 for(const w of fresh){
  for(const query of [w.chineseTitle,w.originalTitle])assert.ok(filterCatalogue(data,{query}).some(x=>x.work.id===w.id));
 }
 assert.deepEqual(co.legacyCommandWorkIds,['g112']);
 assert.deepEqual(co.dossierOnlyWorks.map(w=>w.id),['toho-cinemascope-godzilla','toho-touch-pc']);
 for(const w of co.dossierOnlyWorks){
  assert.ok(w.interactionModes.includes('文字输入'));
  assert.ok(!data.works.some(x=>x.id===w.id));
  assert.ok(!('contentVersions' in w));assert.ok(!('platformReleases' in w));
 }
 assert.match(co.dossierOnlyWorks[1].interactionNote,/动词指令输入、名词选择/);
 assert.ok(fresh.find(w=>w.id==='g1212').interactionModes.includes('瞄准射击'));
 assert.ok(!fresh.find(w=>w.id==='g1212').interactionModes.includes('战斗指令'));
 assert.match(related('kaiju8').interactionNote,/预写会话/);
});

test('independent Lupin adaptations and actual joint-project publisher identities remain separate',()=>{
 assert.equal(fresh.find(w=>w.id==='g1212').firstYear,1985);
 assert.equal(related('cagliostro-msx').firstYear,1987);
 assert.equal(related('babylon-msx').firstYear,1988);
 assert.equal(fresh.find(w=>w.id==='g1214').firstYear,1989);
 assert.equal(related('times-of-lore').firstYear,1988);
 assert.equal(related('times-of-lore').platformReleases[0].publisher,'Origin Systems');
 assert.match(related('times-of-lore').notes,/1990\/12\/07/);
 assert.equal(related('phanpara').platformReleases[0].publisher,'Sumzap');
 assert.equal(related('kaiju8').platformReleases[0].publisher,'Akatsuki Games');
 assert.equal(related('sakuna-hinuka').platformReleases[0].publisher,'TOHO Games');
 assert.match(related('sakuna-hinuka').notes,/2026\/07\/27已停止服务/);
 for(const key of ['phanpara','kaiju8','sakuna-hinuka']){
  const w=related(key);assert.deepEqual(w.platformReleases.map(r=>r.platform),['iOS','Android']);
  assert.equal(new Set(w.platformReleases.map(r=>r.contentVersionId)).size,1);
 }
 for(const w of co.relatedGames){
  assert.equal(w.contentVersions.length,1);assert.equal(w.contentVersions[0].basis,'original');
  assert.deepEqual(w.contentVersions[0].evidenceReleaseIds,w.platformReleases.map(r=>r.id));
  assert.ok(w.platformReleases.every(r=>r.releaseRole==='contentDebut'));
 }
});

test('all TOHO cards and source decisions render once, with future and licensing references outside data',()=>{
 const page=readFileSync(new URL('../toho.html',import.meta.url),'utf8');
 const ids=[...co.workIds,...co.relatedGames.map(w=>w.id),...co.dossierOnlyWorks.map(w=>w.id)];
 assert.equal(ids.length,18);assert.equal(new Set(ids).size,18);
 for(const id of ids)assert.equal(page.split(`class="card" id="${id}"`).length-1,1,id);
 const rows=table.groups.flatMap(g=>g.rows),refs=rows.filter(r=>r.workId).map(r=>r.workId);
 assert.equal(rows.length,42);assert.equal(table.groups.length,6);
 assert.deepEqual([...refs].sort(),[...ids].sort());
 assert.equal(co.foundedAt,'1932-08-12');
 assert.match(co.publisherNote,/用户具名要求/);
 assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
 for(const title of ['薬屋のひとりごと ～偽りの皇弟～','ハイキュー!! ALL Challengers','GUNHED（PCE）／ガンヘッド 新たなる戦い（FC）']){
  assert.ok(rows.some(r=>r.title===title&&!r.workId));
  assert.ok(![...data.works,...co.relatedGames].some(w=>w.originalTitle===title));
 }
 assert.ok(readFileSync(new URL('../index.html',import.meta.url),'utf8').includes('href="toho.html"'));
});
