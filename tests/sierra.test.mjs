import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import {filterCatalogue} from '../filter.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const data=read('data/games.json');
const co=read('data/company-coverage.json').companies.find(c=>c.id==='sierra');
const page=readFileSync(new URL('../sierra.html',import.meta.url),'utf8');

test('Sierra menu composition is searchable without admitting parser bibliography',()=>{
  for(const id of ['g1092','g1093','g1094']){
    const w=data.works.find(w=>w.id===id);
    assert.ok(w.interactionModes.includes('菜单指令'));
    assert.ok(!w.interactionModes.includes('文字输入'));
    assert.deepEqual(filterCatalogue(data,{query:w.originalTitle,interaction:'菜单指令'}).map(r=>r.work.id),[id]);
    assert.equal(filterCatalogue(data,{query:w.originalTitle,interaction:'文字输入'}).length,0);
    assert.equal(data.contentVersions.filter(c=>c.workId===id).length,1);
    const releases=data.platformReleases.filter(r=>r.workId===id);
    assert.equal(releases.length,1);
    assert.equal(releases[0].releaseRole,'contentDebut');
  }
  for(const w of co.dossierOnlyWorks){
    assert.ok(w.interactionModes.includes('文字输入'));
    assert.ok(!data.works.some(x=>x.id===w.id));
    assert.ok(!data.contentVersions.some(x=>x.workId===w.id));
    assert.ok(!data.platformReleases.some(x=>x.workId===w.id));
  }
});

test('Gelfling reuses Dark Crystal and first publishers survive the brand grouping',()=>{
  assert.deepEqual(co.entries.find(e=>e.title==='Gelfling Adventure').workIds,['g099']);
  assert.equal(co.workIds.filter(id=>id==='g099').length,1);
  assert.ok(!data.works.some(w=>w.id!=='g099' && /Gelfling Adventure/.test(w.originalTitle)));
  const oldRelease=data.platformReleases.find(r=>r.id==='g099-v2');
  assert.equal(oldRelease.contentVersionId,null);
  assert.equal(oldRelease.contentRelation,'unverified');
  assert.equal(data.platformReleases.find(r=>r.id==='g060-v1').publisher,'IBM');
  for(const id of ['g1092','g1093'])assert.equal(data.platformReleases.find(r=>r.workId===id).publisher,'Sunnyside Soft');
  assert.ok(co.workContexts.g099.includes('空格／回车'));
});

test('Sierra groups cover each identity once and excluded genres produce no cards',()=>{
  const ids=[...co.workIds,...co.dossierOnlyWorks.map(w=>w.id)];
  const grouped=co.dossierGroups.flatMap(g=>g.workIds);
  assert.equal(ids.length,13);
  assert.equal(new Set(grouped).size,grouped.length);
  assert.deepEqual(new Set(grouped),new Set(ids));
  assert.equal((page.match(/<article class="card"/g)||[]).length,13);
  const excluded=co.entries.filter(e=>e.status.startsWith('排除'));
  assert.equal(excluded.length,21);
  for(const e of excluded){
    assert.deepEqual(e.workIds,[]);
    assert.ok(!e.relatedIds?.length && !e.dossierIds?.length);
  }
  const ultima=co.dossierOnlyWorks.find(w=>w.id==='sierra-ultima2');
  assert.ok(ultima.interactionNote.includes('不影响游戏结果'));
  assert.ok(ultima.interactionNote.includes('并非自由话题解析器'));
});
