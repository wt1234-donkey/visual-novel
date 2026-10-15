import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import {filterCatalogue} from '../filter.mjs';
const data=JSON.parse(readFileSync(new URL('../data/games.json',import.meta.url),'utf8'));

test('platform filtering retains release year and one shared content identity',()=>{
  const result=filterCatalogue(data,{from:'2017',to:'2017'}).find(x=>x.work.id==='g055');
  assert.equal(result.platformReleases.length,3);
  assert.equal(result.contentVersions.length,1);
  const ps4=filterCatalogue(data,{platform:'PlayStation 4',from:'2017'}).find(x=>x.work.id==='g055');
  assert.equal(ps4.platformReleases.length,1);
  assert.equal(ps4.contentVersions[0].id,result.contentVersions[0].id);
  assert.equal(ps4.work.firstYear,2009);
  assert.equal(ps4.contentVersions[0].firstYear,2017);
});

test('unverified historical releases stay visible without content version inflation',()=>{
  const result=filterCatalogue(data,{contentStatus:'unverified'});
  assert.equal(result.reduce((sum,x)=>sum+x.platformReleases.length,0),964);
  assert.ok(result.every(x=>x.contentVersions.length===0));
  assert.ok(result.every(x=>x.platformReleases.every(r=>r.contentVersionId===null)));
  const linked=filterCatalogue(data,{contentStatus:'linked'});
  assert.ok(linked.every(x=>x.platformReleases.every(r=>r.contentVersionId)));
});

test('clearing filters returns all preserved releases and distinct content identities',()=>{
  const result=filterCatalogue(data);
  assert.equal(result.length,data.works.length);
  assert.deepEqual(result.flatMap(x=>x.platformReleases.map(r=>r.id)).sort(),
    data.platformReleases.map(r=>r.id).sort());
  assert.deepEqual(result.flatMap(x=>x.contentVersions.map(c=>c.id)).sort(),
    data.contentVersions.map(c=>c.id).sort());
});
