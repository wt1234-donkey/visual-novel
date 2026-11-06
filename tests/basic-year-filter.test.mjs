import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
import * as basicFilters from '../basic-catalogue-filters.mjs';
import {workKey,validateStore,projectEntries,emptyStore} from '../basic-catalogue-model.mjs';

test('basic catalogue year filter combines with search and resets pagination', async () => {
  const elements = new Map();
  function element(id) {
    if (!elements.has(id)) elements.set(id, {
      value:'', innerHTML:'<option value="">全部</option>', textContent:'', handlers:{},
      get options() { return [...this.innerHTML.matchAll(/<option[^>]*value="([^"]*)"[^>]*>.*?<\/option>/g)].map(m=>({value:m[1],outerHTML:m[0]})); },
      addEventListener(type, fn) { this.handlers[type]=fn; }
    });
    return elements.get(id);
  }
  const works = Array.from({length:30}, (_,i)=>({id:'id'+i,indexId:'i'+i,title:'Ninety '+i,aliases:[],firstYear:1990,gameplay:'ADV',group:'Group',mainPlacement:'promoted-basic'}));
  works.push({id:'other',indexId:'other',title:'Other',aliases:['Hidden alias'],firstYear:2001,gameplay:'RPG',group:'Group',mainPlacement:'promoted-basic'});
  works.push({id:'unknown',indexId:'unknown',title:'Unknown',aliases:[],firstYear:null,gameplay:'ADV',group:'Group',mainPlacement:'promoted-basic'});
  const registry={works,identityReview:[],summary:{promotedBasic:32,existingComplete:0,promotedDossier:0}};
  const index={records:[],summary:{alreadyMain:0,alreadyDossier:0,identityReview:0}};
  const context=vm.createContext({...basicFilters,document:{getElementById:element},console,workKey,validateStore,createBasicEditor:(base,store,onChange)=>{onChange(projectEntries(base,store),projectEntries(base,store,{includeChildren:true}),store);return {};},fetch:async path=>({ok:true,json:async()=>path.includes('main-adv-rpg-works')?registry:path.includes('minimal-index')?index:path.includes('basic-catalogue-edits')?emptyStore():path.includes('manufacturer-regions')?{schemaVersion:1,entries:[]}:{records:[]}})});
  await vm.runInContext((await readFile(new URL('../minimal-adv-rpg.mjs',import.meta.url),'utf8')).replace(/^import .*;$/gm,''),context);
  assert.match(element('year').innerHTML,/value="1990"/);
  assert.match(element('year').innerHTML,/value="2001"/);
  assert.doesNotMatch(element('year').innerHTML,/value="null"/);
  element('next').handlers.click();
  assert.match(element('pagination').textContent,/第 2/);
  element('page-number').value='1';element('page-jump').handlers.submit({preventDefault(){}});
  assert.match(element('pagination').textContent,/第 1/);
  element('page-number-bottom').value='2';element('page-jump-bottom').handlers.submit({preventDefault(){}});
  assert.match(element('pagination').textContent,/第 2/);assert.equal(element('page-number').value,2);
  element('page-number').value='3';element('page-jump').handlers.submit({preventDefault(){}});
  assert.match(element('page-error').textContent,/整数页码/);assert.match(element('pagination').textContent,/第 2/);
  element('year').value='2001'; element('year').handlers.change();
  assert.match(element('pagination').textContent,/第 1/);
  assert.match(element('count').textContent,/找到 1 条/);
  assert.match(element('rows').innerHTML,/Other/);
  element('q').value='Hidden alias'; element('q').handlers.input();
  assert.match(element('count').textContent,/找到 1 条/);
  element('year').value='1990'; element('year').handlers.change();
  assert.match(element('count').textContent,/找到 0 条/);
  assert.equal(element('page-number').disabled,true);assert.equal(element('page-go-bottom').disabled,true);
  element('q').value=''; element('q').handlers.input();
  assert.match(element('count').textContent,/找到 30 条/);
  element('year').value='unknown'; element('year').handlers.change();
  assert.match(element('rows').innerHTML,/Unknown/);
  assert.match(element('count').textContent,/找到 1 条/);
  element('year').value=''; element('year').handlers.change();
  assert.match(element('count').textContent,/找到 32 条/);
  element('gameplay').value='adventure';element('gameplay').handlers.change();assert.match(element('count').textContent,/找到 31 条/);
  element('gameplay').value='rpg';element('gameplay').handlers.change();assert.match(element('rows').innerHTML,/Other/);assert.match(element('count').textContent,/找到 1 条/);
  element('group-query').value='gRoUp';element('group-query').handlers.input();assert.match(element('count').textContent,/找到 1 条/);
  element('group-query').value='not-present';element('group-query').handlers.input();assert.match(element('count').textContent,/找到 0 条/);
  element('filter-reset').handlers.click();assert.match(element('count').textContent,/找到 32 条/);assert.equal(element('gameplay').value,'');
  element('group-region').value='japan';element('group-region').handlers.change();assert.match(element('count').textContent,/找到 0 条/);
  element('filter-reset').handlers.click();assert.match(element('count').textContent,/找到 32 条/);
});
