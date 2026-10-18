import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterCatalogue} from '../filter.mjs';
const read=n=>JSON.parse(readFileSync(new URL('../data/'+n,import.meta.url),'utf8'));
const data=read('games.json');
const coverage=read('company-coverage.json');
const co=coverage.companies.find(c=>c.id==='falcom');
const table=read('gameplay-catalogues.json').companies.falcom;
const work=k=>co.relatedGames.find(w=>w.id==='falcom-'+k);

test('Monster House admits mapped commands while existing Falcom parsers remain historical',()=>{
 for(const query of ['怪物之屋','モンスターハウス','Monster House']){
  const rows=filterCatalogue(data,{query,interaction:'菜单指令',company:'日本ファルコム'});
  assert.deepEqual(rows.map(x=>x.work.id),['g1193']);
  assert.equal(rows[0].work.firstYear,1983);
  assert.equal(rows[0].contentVersions.length,1);
 }
 assert.deepEqual(data.works.find(w=>w.id==='g1193').interactionModes,['菜单指令']);
 for(const id of co.legacyCommandWorkIds) assert.ok(data.works.find(w=>w.id===id).interactionModes.includes('文字输入'));
 for(const w of co.relatedGames) assert.ok(!w.interactionModes.includes('文字输入'));
 for(const w of co.dossierOnlyWorks){
  assert.ok(w.interactionModes.includes('文字输入'));
  assert.ok(!data.works.some(x=>x.id===w.id));
  assert.ok(!('contentVersions' in w)&&!('platformReleases' in w));
 }
});

test('remakes and expansions share work identities and only debut content is recorded',()=>{
 const ys3=work('ys3');
 assert.deepEqual(ys3.contentVersions.map(c=>c.firstYear),[1989,2005,2010,2023]);
 assert.equal(ys3.contentVersions[2].comparedTo,ys3.contentVersions[1].id);
 assert.equal(ys3.contentVersions[3].comparedTo,ys3.contentVersions[2].id);
 assert.match(ys3.contentVersions[3].addedContent[0].description,/亚特鲁.*语音/);
 assert.equal(work('brandish-vt').firstYear,1996);
 assert.ok(!co.relatedGames.some(w=>w.id==='falcom-brandish4'));
 assert.equal(work('sora-fc').contentVersions.at(-1).firstYear,2025);
 assert.equal(work('sora-sc').contentVersions.at(-1).firstYear,2026);
 assert.equal(work('kyoto').firstYear,2026);
 assert.ok(!co.relatedGames.some(w=>/the-(1st|2nd)/.test(w.id)));
 for(const key of ['sora-fc','sora-sc']){
  const w=work(key), c=w.contentVersions.at(-1);
  assert.deepEqual(w.platformReleases.filter(r=>r.contentVersionId===c.id).map(r=>r.platform).sort(),['Nintendo Switch','Nintendo Switch 2','PlayStation 5']);
 }
 const proud=work('ys10').contentVersions.at(-1);
 assert.equal(proud.firstYear,2025);
 assert.deepEqual(work('ys10').platformReleases.filter(r=>r.contentVersionId===proud.id).map(r=>r.platform),['Nintendo Switch 2']);
 assert.ok(co.relatedGames.every(w=>w.platformReleases.every(r=>r.releaseRole==='contentDebut')));
});

test('licensed versions retain actual publishers and shared works are not copied',()=>{
 assert.equal(work('wind1').platformReleases[0].publisher,'NECホームエレクトロニクス');
 assert.equal(work('ys4-mask').platformReleases[0].publisher,'トンキンハウス');
 assert.equal(work('ys-strategy').platformReleases[0].publisher,'マーベラスインタラクティブ');
 assert.equal(work('ys5').platformReleases.at(-1).publisher,'光栄');
 for(const key of ['zero','azure','sora-fc','sora-sc','sora-3rd']){
  const evo=work(key).platformReleases.find(r=>r.kind==='Evolution');
  assert.equal(evo.publisher,'角川ゲームス');
 }
 const shared=['ascii-dragon-slayer','sierra-on-line-sorcerian','hudson-faxanadu','hudson-ys4'];
 for(const id of shared){
  assert.equal(coverage.companies.flatMap(c=>c.relatedGames||[]).filter(w=>w.id===id).length,1);
  assert.match(co.publisherWorkText,new RegExp('#'+id));
 }
 assert.equal(work('ys-vs-sora').interactionModes.includes('选项分支'),false);
 assert.ok(!work('ys-strategy').characters.includes('アドル'));
});

test('reference table covers every body identity once and excluded types create no records',()=>{
 const rows=table.groups.flatMap(g=>g.rows);
 const body=[...co.workIds,...co.relatedGames.map(w=>w.id),...co.dossierOnlyWorks.map(w=>w.id)];
 assert.deepEqual(rows.filter(r=>r.workId).map(r=>r.workId).sort(),body.sort());
 for(const title of ['女子大生プライベート','Vantage Master（','Lord Monarch（','Sorcerian Online','梦之轨迹','晓之轨迹']) assert.ok(rows.some(r=>r.title?.includes(title)&&!r.workId));
 const page=readFileSync(new URL('../falcom.html',import.meta.url),'utf8');
 assert.equal(page.split('<article class="card"').length-1,body.length);
 assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
 assert.equal(co.relatedGames.length,54);
 assert.equal(co.relatedGames.reduce((n,w)=>n+w.contentVersions.length,0),82);
});
