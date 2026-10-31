import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

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
  const context=vm.createContext({document:{getElementById:element},console,
    fetch:async path=>({ok:true,json:async()=>JSON.parse(await readFile(new URL('../'+path,import.meta.url),'utf8'))})});
  await vm.runInContext(await readFile(new URL('../minimal-adv-rpg.mjs',import.meta.url),'utf8'),context);
  const entries=JSON.parse(vm.runInContext('JSON.stringify(entries)',context));
  const review=JSON.parse(await readFile(new URL('../data/adv-rpg-round3-review-20261031.json',import.meta.url),'utf8'));
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
  vm.runInContext('filterAndDraw()',context);
  assert.ok(element('rows').innerHTML.includes('Another Code'));
  element('q').value='';element('status').value='eligibility-review';
  vm.runInContext('filterAndDraw()',context);
  assert.ok(element('rows').innerHTML.includes('ステディ'));
});
