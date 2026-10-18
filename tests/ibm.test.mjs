import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterCatalogue} from '../filter.mjs';
const read=n=>JSON.parse(readFileSync(new URL('../data/'+n,import.meta.url),'utf8'));
const data=read('games.json');
const co=read('company-coverage.json').companies.find(c=>c.id==='ibm');
const table=read('gameplay-catalogues.json').companies.ibm;
const added=data.works.filter(w=>co.workIds.includes(w.id)&&!co.legacyCommandWorkIds.includes(w.id));
const related=id=>co.relatedGames.find(w=>w.id==='ibm-'+id);

test('new IBM narrative works are searchable and exclude parser interaction',()=>{
 assert.equal(added.length,6);
 for(const w of added){
  for(const query of [w.chineseTitle,w.originalTitle])
   assert.ok(filterCatalogue(data,{query}).some(x=>x.work.id===w.id));
  assert.ok(!w.interactionModes.includes('文字输入'));
  assert.equal(data.contentVersions.filter(c=>c.workId===w.id).length,1);
  assert.equal(data.platformReleases.filter(r=>r.workId===w.id).length,1);
 }
 for(const id of co.legacyCommandWorkIds)
  assert.ok(data.works.find(w=>w.id===id).interactionModes.includes('文字输入'));
 assert.deepEqual([...co.legacyCommandWorkIds].sort(),['g057','g060','g089']);
 assert.deepEqual(co.dossierOnlyWorks,[]);
});

test('mapped Zyll commands and microphone events are not free typed parser commands',()=>{
 const z=related('zyll');
 assert.deepEqual(z.interactionModes,['菜单指令','战斗指令']);
 assert.ok(!z.interactionModes.includes('直接移动'));
 assert.match(z.interactionSources[0],/zyll-manual\.pdf$/);
 for(const id of ['g1196','g1197']){
  const w=added.find(w=>w.id===id);
  assert.ok(w.interactionModes.includes('设备互动'));
  assert.match(w.interactionNote,/麦克风/);
  assert.ok(!w.interactionModes.includes('文字输入'));
 }
 assert.ok(added.find(w=>w.id==='g1196').interactionModes.includes('限时反应'));
 assert.ok(!added.find(w=>w.id==='g1195').interactionModes.includes('节奏演奏'));
});

test('IBM association preserves actual original publishers and shared hybrid content',()=>{
 for(const id of ['g1198','g1199']){
  const r=data.platformReleases.find(r=>r.workId===id);
  assert.equal(r.publisher,'American Laser Games');
  assert.match(r.platform,/街机/);
  assert.ok(!filterCatalogue(data,{query:data.works.find(w=>w.id===id).originalTitle,company:'IBM'}).some(x=>x.work.id===id));
 }
 const y=related('yellow-brick-road');
 assert.equal(y.firstYear,1995);
 assert.equal(y.contentVersions.length,1);
 assert.equal(y.platformReleases.length,2);
 assert.deepEqual(y.platformReleases.map(r=>r.platform).sort(),['Macintosh','Windows 3.x']);
 for(const r of y.platformReleases){
  assert.equal(r.publisher,'Synergy Inc.');
  assert.equal(r.contentVersionId,y.contentVersions[0].id);
  assert.equal(r.releaseRole,'contentDebut');
 }
 assert.equal(y.contentVersions[0].evidenceReleaseIds.length,2);
 assert.ok(!data.works.some(w=>w.id==='ibm-yellow-brick-road'));
});

test('reference table accounts for every body identity without turning packages or drills into games',()=>{
 const rows=table.groups.flatMap(g=>g.rows);
 assert.equal(rows.length,49);
 const refs=rows.filter(r=>r.workId).map(r=>r.workId);
 const all=[...co.workIds,...co.relatedGames.map(w=>w.id)];
 assert.equal(refs.length,new Set(refs).size);
 assert.deepEqual([...refs].sort(),all.sort());
 assert.equal(co.foundedAt,'1911-06-16');
 assert.match(added.find(w=>w.id==='g1195').notes,/7th Level.*1994年Chuck Jones/);
 for(const title of ['Adventures in Math','Quest for Fame（1995）','Mad Dog McCree and Mad Dog II（1996合辑）','The Forbidden City: Beyond Space & Time（2008）']){
  const row=rows.find(r=>r.title===title);
  assert.ok(row&&row.type&&row.relation);
  assert.ok(!('workId' in row)&&!('contentVersions' in row)&&!('platformReleases' in row));
 }
});
