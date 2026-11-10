import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {compileCombinedSearch,needsAdvancedIndex,normalizeLanguage} from '../basic-combined-search.mjs';
import {basicFilterRows,matchingBasicPositions} from '../basic-catalogue-filters.mjs';

const any=(field,...values)=>({field,mode:'any',values});
const all=(field,...values)=>({field,mode:'all',values});
const none=(field,...values)=>({field,mode:'none',values});
const rows=basicFilterRows([
 {_key:'a',slot:2,title:'图文冒险甲',year:1980,gameplay:'ADV',gameplayTags:['graphic-adventure','text-input'],plotTags:{theme:'悬疑'}},
 {_key:'b',slot:3,title:'普通 RPG',year:1999,gameplay:'RPG',plotTags:{theme:'科幻'}},
 {_key:'c',slot:4,title:'剧情 RPG',year:1999,gameplay:'剧情RPG'},
 {_key:'d',slot:5,title:'时间未知',year:null,gameplay:'纯文字冒险'},
],new Map());
const advanced={
 2:{productionRegion:['japan'],creator:['alice','bob'],language:['zh-hans','en'],duration:120,contentCount:2,
  releases:[{platform:['windows'],releaseRegion:['japan'],releaseYear:1999},{platform:['playstation'],releaseRegion:['europe'],releaseYear:2000}]},
 3:{theme:['科幻'],productionRegion:['japan']},
 4:{theme:['历史'],productionRegion:['japan'],duration:240},
};
const match=groups=>matchingBasicPositions(rows,{},compileCombinedSearch(groups),advanced);

test('visual filter groups compose OR across groups, AND within groups, and preserve documented non-pure RPG',()=>{
 assert.deepEqual(match([[any('year','1980..1999'),any('theme','悬疑','科幻','历史'),any('productionRegion','日本'),none('gameplay','纯RPG')]]),[0,2]);
 assert.deepEqual(match([[any('year','1980'),all('gameplay','图形冒险','文字输入')],[any('year','1999'),any('gameplay','纯RPG')]]),[0,1]);
 assert.deepEqual(match([[none('gameplay','RPG')]]),[0,3]);
 assert.deepEqual(match([[any('style','历史')]]),[2]);
 assert.equal(needsAdvancedIndex([[any('style','历史')]]),true);
 assert.equal(needsAdvancedIndex([[any('gameplay','图形冒险'),any('style','喜剧')]]),false);
});

test('creator conjunction, language aliases, numeric bounds, and unavailable fields behave consistently',()=>{
 assert.equal(normalizeLanguage('zh-CN'),'zh-hans');
 assert.deepEqual(match([[all('creator','Alice','Bob'),all('language','中文','英语'),any('duration','120..240'),any('contentCount','>= 2')]]),[0]);
 assert.deepEqual(match([[any('duration','<= 240')]]),[0,2]);
 assert.deepEqual(match([[any('contentCount','0')]]),[]);
 assert.deepEqual(match([[none('contentCount','>= 1')]]),[1,2,3]);
 assert.throws(()=>compileCombinedSearch([[any('year','1999..1980')]]),/数字条件/);
});

test('positive release filters use the same record and negative release filters exclude any documented match',()=>{
 assert.deepEqual(match([[any('platform','Windows'),any('releaseRegion','欧洲')]]),[]);
 assert.deepEqual(match([[any('platform','Windows'),any('releaseRegion','日本'),any('releaseYear','1999')]]),[0]);
 assert.deepEqual(match([[any('platform','Windows'),none('releaseRegion','欧洲')]]),[]);
});

test('region overrides point to real release IDs, and current labels have migrated with conflicts archived',()=>{
 const read=name=>JSON.parse(readFileSync(new URL('../data/'+name,import.meta.url),'utf8'));
 const releaseById=new Map(read('games.json').platformReleases.map(r=>[r.id,r]));
 for(const [id,regions] of Object.entries(read('basic-release-regions.json'))){
  assert.ok(releaseById.get(id)?.source,id);
  assert.ok(regions.length&&regions.every(region=>['japan','northAmerica','europe','oceania'].includes(region)),id);
 }
 const records=read('basic-catalogue-edits.json').records;
 assert.deepEqual(records['nextmoe-4567'].values.plotTags,{tone:'喜剧',relationship:'恋爱',theme:'日常'});
 assert.deepEqual(records['nextmoe-10729'].values.plotStyles,[]);
 assert.deepEqual(records['nextmoe-10729'].legacyPlotStyles,['色情','NTR','乱伦']);
});
