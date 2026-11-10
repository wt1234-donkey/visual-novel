import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createManufacturerIndex,manufacturerKey,matchingManufacturers,manufacturerOptions,gameplayKeys,gameplayOptions,gameplayDisplay,styleOptions,styleName,pageIndex} from '../basic-catalogue-filters.mjs';
import {STYLE_OPTIONS,validateValues,valuesOf} from '../basic-catalogue-model.mjs';

const metadata={entries:[{region:'japan',names:['Key','ELF']},{region:'other',names:['inkle']}]};
test('manufacturer choices merge case and width variants, count each work once and preserve source identities',()=>{
 const works=[{group:'Key',groups:['key','ＫＥＹ']},{group:'KEY'},{group:'Key Plus'},{group:'inkle'},{group:'日本語の未知チーム'}],before=structuredClone(works);
 const index=createManufacturerIndex(works,metadata),key=index.find(row=>row.key==='key');
 assert.equal(key.count,2);assert.equal(key.region,'japan');assert.equal(key.variants.length,4);assert.equal(index.length,4);assert.deepEqual(works,before);
 assert.equal(index.find(row=>row.key===manufacturerKey('日本語の未知チーム')).region,'unknown');
 assert.deepEqual(matchingManufacturers(index,{region:'other'}).map(row=>row.label),['inkle']);
 assert.equal(matchingManufacturers(index,{query:'kEy'}).length,2);assert.equal(matchingManufacturers(index,{query:'missing'}).length,0);
});
test('every manufacturer remains reachable by search, options stay bounded and a selected rare name remains visible',()=>{
 const works=Array.from({length:450},(_,i)=>({group:'Studio '+i}));const index=createManufacturerIndex(works);
 const options=manufacturerOptions(index,{},'studio 449');assert.equal(options.total,450);assert.equal(options.visible.length,200);assert.ok(options.visible.some(row=>row.key==='studio 449'));
 assert.deepEqual(manufacturerOptions(index,{query:'studio 449'}).visible.map(row=>row.key),['studio 449']);
 assert.equal(manufacturerOptions(index,{region:'japan'},'studio 449').visible.length,0);
 const conflicting=createManufacturerIndex([{group:'Key'}],{entries:[...metadata.entries,{region:'other',names:['KEY']}]});assert.equal(conflicting[0].region,'unknown');
});
test('gameplay browsing combines equivalent labels and matches all parts of mixed gameplay without changing raw facts',()=>{
 assert.deepEqual(gameplayKeys('ADV'),gameplayKeys('Adventure'));assert.deepEqual(gameplayKeys('RPG'),gameplayKeys('Role-playing (RPG)'));
 assert.deepEqual(gameplayKeys('ARPG'),['rpg','action']);assert.deepEqual(gameplayKeys('ADV／策略RPG'),['adventure','rpg','strategy']);
 assert.deepEqual(gameplayKeys('点击调查冒险\n点击调查；文字输入'),['point-click','text-input']);
 assert.deepEqual(gameplayKeys('Simulation, Strategy / tactics'),['simulation','strategy']);
 assert.deepEqual(gameplayKeys('迷宫RPG'),['rpg']);assert.deepEqual(gameplayKeys('角色扮演／战略模拟'),['rpg','strategy']);
 assert.deepEqual(gameplayKeys('剧情动作RPG'),['rpg','action']);assert.deepEqual(gameplayKeys('文字输入／仅专题'),['text-input']);
 assert.deepEqual(gameplayKeys('反RPG探索冒险'),['adventure']);assert.deepEqual(gameplayKeys('音乐恋爱育成'),['simulation']);
 assert.notDeepEqual(gameplayKeys('选项式冒险'),gameplayKeys('Menu-Driven'));assert.notDeepEqual(gameplayKeys('互动小说（玩法待核）'),gameplayKeys('文字输入'));
 const works=[{gameplay:'ARPG'},{gameplay:'Role-playing (RPG)'},{gameplay:'自定义玩法'}],before=structuredClone(works),options=gameplayOptions(works);
 assert.equal(options.find(row=>row.key==='rpg').count,2);assert.equal(options.find(row=>row.key==='custom:自定义玩法').label,'自定义玩法');assert.deepEqual(works,before);
 assert.equal(gameplayDisplay('自定义玩法'),'自定义玩法');assert.match(gameplayDisplay('ARPG'),/RPG.*动作/);
});
test('style suggestions use only the nine active dimensions',()=>{
 assert.equal(STYLE_OPTIONS.length,new Set(STYLE_OPTIONS).size);assert.ok(STYLE_OPTIONS.length>=50);
 for(const style of ['纯爱','致郁','科幻','成人向','NTR','乱伦'])assert.ok(STYLE_OPTIONS.includes(style));
 const options=styleOptions([{plotStyles:['治愈','疗愈','地方悬疑']},{plotStyles:['ntr']}]);
 assert.equal(options.flatMap(row=>row.options).find(row=>row.key==='治愈').count,1);assert.equal(styleName('ntr'),'NTR');
 assert.equal(options.length,9);assert.ok(!options.flatMap(row=>row.options).some(row=>row.label==='地方悬疑'));assert.ok(options.flatMap(row=>row.options).some(row=>row.key==='史诗'&&row.count===0));
 assert.throws(()=>validateValues({...valuesOf({title:'Example',group:'Studio',gameplay:'ADV'}),plotStyles:['a','b','c','d']}),/最多3个/);
});
test('page jumps accept valid first, last and intermediate pages and reject invalid requests',()=>{
 assert.equal(pageIndex('1',100),0);assert.equal(pageIndex('100',100),99);assert.equal(pageIndex(' 42 ',100),41);
 for(const input of ['','0','-1','101','1.5','abc','1e2','Infinity','9007199254740992'])assert.throws(()=>pageIndex(input,100),/整数页码/);
});
test('the shipped region index has explicit provenance and preserves Japanese and overseas historical brands',()=>{
 const data=JSON.parse(readFileSync(new URL('../data/basic-manufacturer-regions.json',import.meta.url),'utf8'));
 assert.equal(data.schemaVersion,1);for(const row of data.entries){assert.ok(['japan','other'].includes(row.region));assert.ok(row.names.length&&row.names.every(name=>typeof name==='string'&&name.trim()));assert.ok(row.basis&&row.sources.length);}
 const names=['Key','Konami','Infocom','Ultra Games','PROTOTYPE','JAST（日本）','inkle','Frontwing','Red Candle Games','Unlisted English Company'];
 const index=createManufacturerIndex(names.map(group=>({group})),data),regions=Object.fromEntries(index.map(row=>[row.key,row.region]));
 assert.equal(regions.key,'japan');assert.equal(regions.konami,'japan');assert.equal(regions.infocom,'other');assert.equal(regions['ultra games'],'other');assert.equal(regions.prototype,'japan');assert.equal(regions.inkle,'other');assert.equal(regions.frontwing,'japan');assert.equal(regions['red candle games'],'other');assert.equal(regions['unlisted english company'],'unknown');
});
