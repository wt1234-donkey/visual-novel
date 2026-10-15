import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import {filterCatalogue} from '../filter.mjs';
const data=JSON.parse(readFileSync(new URL('../data/games.json',import.meta.url),'utf8'));
const ids=filters=>new Set(filterCatalogue(data,filters).map(x=>x.work.id));

test('parser input and chosen action commands remain distinct',()=>{
  const typed=ids({interaction:'文字输入'}),menu=ids({interaction:'菜单指令'});
  assert.ok(typed.has('g015'));assert.ok(!menu.has('g015'));
  assert.ok(menu.has('g593'));assert.ok(!typed.has('g593'));
  assert.ok(typed.has('g991')&&menu.has('g991'));
});
test('reading and point investigation do not collapse into mouse clicks',()=>{
  assert.ok(ids({interaction:'阅读推进'}).has('g032'));
  assert.ok(!ids({interaction:'点击调查'}).has('g032'));
  assert.ok(ids({interaction:'点击调查'}).has('g055'));
  assert.ok(ids({interaction:'谜题操作'}).has('g055'));
});
test('work-level interaction filter composes with release filters without duplicating content',()=>{
  const matches=filterCatalogue(data,{interaction:'点击调查',query:'極限脱出 9時間9人9の扉',from:'2017',to:'2017'});
  assert.equal(matches.length,1);assert.equal(matches[0].platformReleases.length,3);
  assert.equal(matches[0].contentVersions.length,1);
  assert.equal(filterCatalogue(data,{interaction:'文字输入',query:'極限脱出 9時間9人9の扉'}).length,0);
  assert.deepEqual(ids({query:'节奏演奏'}),ids({interaction:'节奏演奏'}));
});
test('unknown operations are explicit and do not acquire speculative input tags',()=>{
  for(const {work} of filterCatalogue(data,{interaction:'待核实'}))assert.deepEqual(work.interactionModes,['待核实']);
  assert.ok(ids({interaction:'待核实'}).has('g534'));
  assert.ok(!ids({interaction:'文字输入'}).has('g534'));
  assert.equal(filterCatalogue(data,{interaction:''}).length,data.works.length);
});
