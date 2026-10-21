import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterCatalogue} from '../filter.mjs';

const data=JSON.parse(readFileSync(new URL('../data/games.json',import.meta.url)));
const company=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url))).companies.find(c=>c.id==='addison_wesley');
const appendix=JSON.parse(readFileSync(new URL('../data/gameplay-catalogues.json',import.meta.url))).companies.addison_wesley;

test('Addison-Wesley reuses four Tolkien identities and adds two parser adventures',()=>{
  assert.deepEqual(company.workIds,['g113','g1021','g1026','g1028','g1272','g1273']);
  assert.deepEqual(company.authorizedCommandWorkIds,['g1272','g1273']);
  for(const id of company.authorizedCommandWorkIds){
    const work=data.works.find(w=>w.id===id);
    assert.deepEqual(work.interactionModes,['文字输入']);
    assert.ok(filterCatalogue(data,{query:work.originalTitle}).some(x=>x.work.id===id));
    assert.equal(data.contentVersions.filter(v=>v.workId===id).length,1);
    assert.equal(data.platformReleases.filter(v=>v.workId===id).length,1);
  }
  const page=readFileSync(new URL('../addison_wesley.html',import.meta.url),'utf8');
  for(const id of company.workIds)assert.equal(page.split(`class="card" id="${id}"`).length-1,1,id);
  assert.equal(appendix.groups.flatMap(g=>g.rows).length,15);
  assert.equal(appendix.groups.flatMap(g=>g.rows).filter(r=>r.workId).length,6);
  assert.ok(!data.works.some(w=>w.originalTitle==='Jenny of the Prairie'));
});
