import {requestScope} from '../src/infrastructure/storage/async-read.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import * as model from '../management-model.mjs';
import {buildManagementView} from '../src/application/management/view.mjs';
import {buildEffectiveCatalogue,displayTitle} from '../src/domain/catalogue/effective.mjs';

const original={id:'g800',title:'Source title',chineseTitle:'原始中文名',originalTitle:'Original name',firstYear:1965,category:'视觉小说',subcategory:'单线视觉小说',genre:'原始题材',characters:['原始角色'],synopsis:'原始简介',interactionModes:['阅读推进'],interactionNote:'原始操作依据',notes:'原始备注',source:'https://example.org/original'};
function fixture(){
 const raw={main:{works:[structuredClone(original)],contentVersions:[{id:'content-original',workId:'g800',firstYear:1965}],platformReleases:[{id:'release-original',workId:'g800',year:1965,publisher:'Historical credit'}]},supplement:{works:[],contentVersions:[],platformReleases:[]},
  history:{records:{g800:{overrides:{title:'当前有效名称',chineseTitle:'当前中文检索名',synopsis:'已更正简介 <script>',characters:['当前角色'],category:'冒险游戏',subcategory:'图形冒险',genre:'当前题材',interactionModes:['点击调查'],interactionNote:'当前操作依据',notes:'当前备注',source:'https://example.org/current',writerNames:['手动剧作']}}}},
  basicStore:{records:{identity:{identity:{title:original.title,firstYear:1965},values:{title:original.title,firstYear:1967,yearStatus:'unverified'}}}},formalLinks:{identity:'g800'}};
 const resources={editorial:{works:{}},creators:{people:[],credits:[]},notes:{works:{}},catalogue:{model:{dossiers:[]}},taxonomy:{subcategories:{'视觉小说':['单线视觉小说'],'冒险游戏':['图形冒险']},interactionModes:{'阅读推进':{},'点击调查':{}}},coverage:{companies:[]},baseline:{works:{}}};
 return {raw,resources};
}
async function harness({raw,resources,saved,loadError,hash='#g800'}={}){
 const f=fixture();raw??=f.raw;resources??=f.resources;
 const nodes=new Map(),storage=new Map(saved?[['narrative-management-v1',JSON.stringify(saved)]]:[]),calls=[];
 const element=selector=>{
  if(!nodes.has(selector))nodes.set(selector,{innerHTML:'',textContent:'',className:'',value:'',hidden:false,disabled:['#search','#new-work','#export-draft'].includes(selector),checked:false,elements:[],listeners:{},addEventListener(type,fn){(this.listeners[type]??=[]).push(fn);},querySelectorAll:()=>[],focus(){},select(){}});
  return nodes.get(selector);
 };
 const files=Object.fromEntries(Object.entries({editorial:'discovery-editorial.json',creators:'creator-credits.json',notes:'work-notes.json',catalogue:'entity-catalogue.json',baseline:'narrative-editorial-baseline-20261029.json'}).map(([key,file])=>['./data/'+file,resources[key]]));
 const context=vm.createContext({requestScope,createOnDemandReader:()=>({directory:async()=>{if(loadError)throw loadError;return {raw:structuredClone(raw),editorial:structuredClone(resources.editorial),catalogue:resources.catalogue,coverage:resources.coverage};},formal:async(id,family)=>family==='formal'?{source:raw.main.works.find(w=>w.id===id),contentVersions:raw.main.contentVersions.filter(w=>w.workId===id),platformReleases:raw.main.platformReleases.filter(w=>w.workId===id)}:resources[family].works[id]??null,optional:async name=>structuredClone(resources[name])}),registerPageRecovery:()=>{},restoreReleaseState:async()=>{},readReleaseJson:async path=>structuredClone(path.includes('taxonomy')?resources.taxonomy:files['./'+path]),...model,buildManagementView,displayTitle,structuredClone,console,
  document:{querySelector:element},location:{hash},history:{replaceState(){}},window:{addEventListener(){}},
  localStorage:{getItem:key=>storage.get(key)??null,setItem:(key,value)=>storage.set(key,value)},
  fetch:async url=>{calls.push(url);if(!(url in files))throw Error('Unexpected fetch '+url);return {ok:true,json:async()=>structuredClone(files[url])};},
  loadEffectiveCatalogue:async()=>{if(loadError)throw loadError;return {...buildEffectiveCatalogue(raw),raw:structuredClone(raw),sourceLease:{schemaVersion:1}};},
  readPublishedSource:async path=>structuredClone(path.includes('taxonomy')?resources.taxonomy:resources.coverage),
  managementProposal:()=>{},offerEditorialProposal:()=>{}});
 const source=readFileSync(new URL('../manage.mjs',import.meta.url),'utf8').replace(/^import .*;$/gm,'').replace('\nload();','\nglobalThis.managementLoaded=load();');
 vm.runInContext(source,context);await context.managementLoaded;await new Promise(setImmediate);
 return {context,element,storage,calls,run:source=>vm.runInContext(source,context),plain:source=>JSON.parse(JSON.stringify(vm.runInContext(source,context)))};
}

test('list, heading and profile display the same effective fields, with original facts in a labelled foldout',async()=>{
 const h=await harness(),list=h.element('#work-list').innerHTML,heading=h.element('#work-heading').innerHTML,panel=h.element('#panel').innerHTML;
 assert.match(list,/当前中文检索名/);assert.match(list,/1967（待核）/);assert.match(heading,/1967（待核）/);assert.match(heading,/冒险游戏/);
 const [current,source]=panel.split('<details><summary>查看原始资料</summary>');
 for(const value of ['当前中文检索名','1967（待核）','已更正简介 &lt;script&gt;','当前角色','当前题材','点击调查','当前操作依据','当前备注','手动剧作','https://example.org/current'])assert.ok(current.includes(value),value);
 assert.ok(!current.includes('<script>'));assert.match(source,/Source title/);assert.match(source,/1965/);assert.match(source,/原始简介/);assert.match(source,/https:\/\/example.org\/original/);
 assert.deepEqual(h.plain('data.games.works[0]'),original);assert.deepEqual(h.plain('working.games.works[0]'),original);
 assert.equal(h.plain('getPackage().operations').length,0);
 assert.ok(!h.calls.some(url=>/games\.json|supplement/.test(url)),'source records come from the same published input snapshot');
});

test('search uses corrected years and characters while retaining original names and aliases',async()=>{
 const h=await harness();
 for(const query of ['1967','当前角色','当前中文检索名','当前有效名称','Source title','原始中文名','Original name']){
  h.element('#search').value=query;h.run('renderList()');assert.match(h.element('#work-list').innerHTML,/data-work="g800"/,query);
 }
 for(const query of ['1965','原始角色']){h.element('#search').value=query;h.run('renderList()');assert.ok(!h.element('#work-list').innerHTML.includes('data-work="g800"'),query);}
});

test('display projection preserves source identities and follows correction removal',()=>{
 const {raw,resources}=fixture(),working={...resources,games:raw.main,supplement:raw.supplement},before=JSON.stringify(working);
 const current=buildManagementView(working,raw);
 assert.equal(current.byId.get('g800').firstYear,1967);assert.deepEqual(current.main.contentVersions,raw.main.contentVersions);assert.deepEqual(current.main.platformReleases,raw.main.platformReleases);
 const restored=buildManagementView(working,{...raw,history:{records:{}},basicStore:{records:{}}});
 assert.equal(restored.byId.get('g800').displayTitle,'原始中文名');assert.equal(restored.byId.get('g800').firstYear,1965);assert.equal(restored.byId.get('g800').synopsis,'原始简介');assert.equal(JSON.stringify(working),before);
 const supplement={works:[{...original,id:'g802'}]},withSupplement=buildManagementView({...working,supplement},{...raw,history:{records:{g802:{overrides:{title:'补充库当前名称'}}}}});
 assert.equal(withSupplement.byId.get('g802').displayTitle,'补充库当前名称');assert.equal(withSupplement.main.works.length,1);
});

test('note edits and new-work drafts export and reload against original baselines without display fields',async()=>{
 const h=await harness();
 h.run("saveNote({confirmed:true,title:'资料核对',text:'这是一条有来源和适用范围的测试说明。',source:'https://example.org/note',dossier:'example',anchor:'g800'});reason='资料核对测试';");
 const bundle={work:{...original,id:'g801',title:'本机新作草稿',chineseTitle:'',firstYear:2026},contentVersions:[{id:'g801-original',workId:'g801'}],platformReleases:[{id:'g801-release',workId:'g801'}]};
 h.context.newBundle=structuredClone(bundle);h.run("setResource(working,'newWork','g801',newBundle);selected='g801';render();saveDraft();");
 assert.match(h.element('#work-heading').innerHTML,/本机新作草稿/);assert.match(h.element('#panel').innerHTML,/尚未提交的新作草稿/);assert.ok(!h.element('#panel').innerHTML.includes('查看原始资料'));
 const saved=JSON.parse(h.storage.get('narrative-management-v1')),operations=saved.package.operations;
 assert.deepEqual(operations.find(op=>op.resource==='newWork').after,bundle);assert.equal(operations.find(op=>op.resource==='notes').before,null);assert.deepEqual(h.plain('data.games.works[0]'),original);
 assert.ok(!JSON.stringify(operations).includes('sourceFirstYear'));assert.ok(!JSON.stringify(operations).includes('displayTitle'));
 const reopened=await harness({saved,hash:''});assert.deepEqual(reopened.plain('getPackage().operations'),operations);assert.match(reopened.element('#work-heading').innerHTML,/本机新作草稿/);
 reopened.run("selected='g800';render()");assert.match(reopened.element('#work-heading').innerHTML,/1967（待核）/);assert.equal(reopened.plain('working.notes.works.g800').length,1);
});

test('an unavailable effective snapshot fails visibly without enabling edits or discarding a saved draft',async()=>{
 const saved={schemaVersion:1,package:{operations:[],reason:'待恢复草稿'},formCache:{},selected:'',tab:'profile'};
 const h=await harness({saved,loadError:Error('当前作品快照摘要不匹配')});
 assert.match(h.element('#notice').textContent,/当前作品快照摘要不匹配/);assert.equal(h.element('#new-work').disabled,true);assert.equal(h.element('#search').disabled,true);assert.deepEqual(JSON.parse(h.storage.get('narrative-management-v1')),saved);
});
