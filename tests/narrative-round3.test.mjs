import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
import * as basicFilters from '../basic-catalogue-filters.mjs';
import {needsAdvancedIndex} from '../basic-combined-search.mjs';
import {compareBasicOrder,withBasicDetails} from '../basic-catalogue-index.mjs';
import {assembleBasicRows} from '../scripts/build_basic_web_index.mjs';
import {workKey,validateStore,projectEntries,emptyStore} from '../basic-catalogue-model.mjs';
import {readLatestBasicStore} from '../basic-catalogue-live.mjs';

test('basic catalogue loads round three with canonical identities, aliases and deferred decisions', async()=>{
  const elements=new Map();
  function element(id){
    if(!elements.has(id))elements.set(id,{
      value:'',innerHTML:'<option value="">全部</option>',textContent:'',
      get options(){return [...this.innerHTML.matchAll(/<option[^>]*value="([^"]*)"[^>]*>.*?<\/option>/g)].map(m=>({value:m[1],outerHTML:m[0]}))},
      addEventListener(){},
    });
    return elements.get(id);
  }
  const read=async path=>JSON.parse(await readFile(new URL('../'+path,import.meta.url),'utf8'));
  const [registry,initial,batch2,review]=await Promise.all([
    'main-adv-rpg-works-20261031.json','adv-rpg-minimal-index-20261031.json',
    'adv-rpg-next-studio-review-20261031.json','adv-rpg-round3-review-20261031.json'
  ].map(path=>read('data/'+path)));
  const rows=assembleBasicRows(registry,initial.records,[['batch2',batch2.records],['batch3',review.records]]);
  const source={meta:async()=>({basic:registry.summary}),basicRows:async()=>rows,details:async()=>new Map()};
  const setupCombinedControls=()=>({options(){},groups:()=>[]});
  const context=vm.createContext({...basicFilters,setupCombinedControls,needsAdvancedIndex,location:{hash:''},document:{getElementById:element},console,workKey,validateStore,compareBasicOrder,withBasicDetails,
    createBasicWebIndex:()=>source,createCatalogueWorker:()=>async()=>null,
    readLatestBasicStore,createEditClient:()=>({read:async()=>({store:emptyStore()})}),
    createBasicEditor:(base,store,onChange)=>{onChange(projectEntries(base,store),projectEntries(base,store,{includeChildren:true}),store);return {};},
    fetch:async path=>({ok:true,json:async()=>read(path)})});
  await vm.runInContext((await readFile(new URL('../minimal-adv-rpg.mjs',import.meta.url),'utf8')).replace(/^import .*;$/gm,''),context);
  const entries=JSON.parse(vm.runInContext('JSON.stringify(entries)',context));
  for(const row of review.records){
    if(row.registryId){
      const matches=entries.filter(e=>e.matchedWorkId===row.registryId);
      assert.equal(matches.length,1,row.title+' must display once by canonical ID');
      assert.ok([matches[0].title,...(matches[0].aliases||[])].includes(row.title));
    }else{
      const held=entries.find(e=>e.title===row.title);
      assert.equal(held.status,row.status);
      assert.ok(held.reason);
    }
  }
  assert.ok(entries.some(e=>e.gameplayNote?.includes('情感能力')));
  element('q').value='アナザーコード 2つの記憶';
  await vm.runInContext('filterAndDraw()',context);
  assert.ok(element('rows').innerHTML.includes('Another Code'));
  element('q').value='';element('status').value='eligibility-review';
  await vm.runInContext('filterAndDraw()',context);
  assert.ok(element('rows').innerHTML.includes('ステディ'));
});
