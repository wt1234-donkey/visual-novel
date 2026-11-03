import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
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
  const context=vm.createContext({document:{getElementById:element},console,workKey,validateStore,createBasicEditor:(base,store,onChange)=>{onChange(projectEntries(base,store),projectEntries(base,store,{includeChildren:true}),store);return {};},fetch:async path=>({ok:true,json:async()=>path.includes('main-adv-rpg-works')?registry:path.includes('minimal-index')?index:path.includes('basic-catalogue-edits')?emptyStore():{records:[]}})});
  await vm.runInContext((await readFile(new URL('../minimal-adv-rpg.mjs',import.meta.url),'utf8')).replace(/^import .*;$/gm,''),context);
  assert.match(element('year').innerHTML,/value="1990"/);
  assert.match(element('year').innerHTML,/value="2001"/);
  assert.doesNotMatch(element('year').innerHTML,/value="null"/);
  element('next').handlers.click();
  assert.match(element('pagination').textContent,/第 2/);
  element('year').value='2001'; element('year').handlers.change();
  assert.match(element('pagination').textContent,/第 1/);
  assert.match(element('count').textContent,/找到 1 条/);
  assert.match(element('rows').innerHTML,/Other/);
  element('q').value='Hidden alias'; element('q').handlers.input();
  assert.match(element('count').textContent,/找到 1 条/);
  element('year').value='1990'; element('year').handlers.change();
  assert.match(element('count').textContent,/找到 0 条/);
  element('q').value=''; element('q').handlers.input();
  assert.match(element('count').textContent,/找到 30 条/);
  element('year').value='unknown'; element('year').handlers.change();
  assert.match(element('rows').innerHTML,/Unknown/);
  assert.match(element('count').textContent,/找到 1 条/);
  element('year').value=''; element('year').handlers.change();
  assert.match(element('count').textContent,/找到 32 条/);
});
