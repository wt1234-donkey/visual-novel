import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {applyChange,emptyStore,parseCSV,parseStyleUpdates,planStyleUpdates,projectEntries,undoLast,STYLE_UPDATE_HEADERS} from '../basic-catalogue-model.mjs';
import {STYLE_DIMENSIONS,styleState,styleLabels,validateStyleTags} from '../basic-style-tags.mjs';
import {buildStyleRequest,parseStyleReview,styleReviewRows,validateCandidates} from '../basic-style-review.mjs';
import {basicFilterRows,styleOptions} from '../basic-catalogue-filters.mjs';
import {compileCombinedSearch} from '../basic-combined-search.mjs';
import {styleInputs,readStyleInputs} from '../basic-style-workbench.mjs';

const first={id:'first',title:'同名作品',firstYear:1965,group:'历史厂商',gameplay:'ADV',source:'印刷目录',plotStyles:['悬疑','推理','疗愈']};
const second={id:'second',title:'同名作品',firstYear:1990,group:'另一厂商',gameplay:'ADV',source:'https://example.org/story',plotTags:{theme:'科幻'}};
const base=[first,second];
const apply=(store,action)=>applyChange(store,base,action,{actor:'reviewer',reason:'测试',expectedRevision:store.revision});

test('nine dimensions allow any combination of up to six tags',()=>{
 const tags={tone:'黑暗',perspective:['第一人称','多视角'],theme:['悬疑','科幻','历史']};
 assert.equal(Object.keys(STYLE_DIMENSIONS).length,9);
 assert.deepEqual(validateStyleTags(tags),tags);
 assert.throws(()=>validateStyleTags({...tags,setting:'校园'}),/最多选择6个/);
 assert.throws(()=>validateStyleTags({theme:['悬疑','悬疑']}),/不能重复/);
 assert.throws(()=>validateStyleTags({theme:['悬疑','群像']}),/故事题材/);
 assert.deepEqual(styleState(first),{tags:{emotion:'治愈'},legacy:['悬疑','推理']});
 const form=new FormData();
 for(const tag of ['第一人称','多视角'])form.append('style-perspective',tag);
 assert.deepEqual(readStyleInputs(form),{perspective:['第一人称','多视角']});
 assert.match(styleInputs(tags),/已选 6 \/ 6 个/);
 assert.match(styleInputs(tags),/name="style-perspective" value="第一人称" checked/);
});

test('CSV uses IDs, preserves untouched dimensions and updates legacy works atomically',()=>{
 const csv=STYLE_UPDATE_HEADERS.slice(0,8).join(',')+'\r\nfirst,同名作品,,清空,,,悬疑,\r\nsecond,,喜剧,,,,,\r\n';
 const rows=parseStyleUpdates('\uFEFF'+csv),store=emptyStore();
 const projected=projectEntries(base,store);
 const next=apply(store,{type:'style-update',rows});
 assert.equal(next.recent.length,1);
 const [one,two]=projectEntries(base,next);
 assert.deepEqual(styleState(one),{tags:{theme:'悬疑'},legacy:['推理']});
 assert.equal(one.firstYear,1965);
 assert.equal(one.source,'印刷目录');
 assert.deepEqual(two.plotTags,{theme:'科幻',tone:'喜剧'});
 assert.deepEqual(projectEntries(base,undoLast(next,next.revision)),projected);
 assert.throws(()=>apply(store,{type:'style-update',rows:[rows[0],rows[0]]}),/重复/);
 assert.throws(()=>apply(store,{type:'style-update',rows:[rows[0],{...rows[1],id:'missing'}]}),/不存在/);
 assert.throws(()=>planStyleUpdates(projected,[{...rows[0],title:'作品名已变'}]),/名称/);
 assert.throws(()=>parseStyleUpdates(STYLE_UPDATE_HEADERS.slice(0,8).join(',')+'\nfirst,,,,,,群像,\n'),/故事题材/);
 assert.deepEqual(store,emptyStore());
});

test('AI request uses linked existing synopsis, skips placeholders and approval appends to occupied dimensions',()=>{
 const synopsis='未来社会中的舰队依靠星际技术探索行星，并开始艰苦的太空航行。';
 const works=projectEntries(base,emptyStore());
 const archive=[{id:'full-first',synopsis,source:'https://example.org/full'},{id:'second',synopsis:'作品剧情简介待依据官方原文细编。',source:second.source}];
 const request=buildStyleRequest([{...works[0],linkedRecordId:'full-first'},works[1]],archive,{});
 assert.deepEqual(request.items.map(item=>item.id),['first']);
 assert.deepEqual(request.issues.map(item=>item.id),['second']);
 assert.ok(request.items[0].dimensions.includes('emotion'));
 assert.equal(request.items[0].maxTags,5);
 const item={...request.items[0],candidates:[{dimension:'theme',tag:'科幻',quote:'舰队依靠星际技术探索行星',source:'https://example.org/full'}]};
 const payload={schemaVersion:1,model:'test-model',items:[item],issues:request.issues};
 assert.deepEqual(parseStyleReview(JSON.stringify(payload)),payload);
 assert.throws(()=>validateCandidates(item,[{...item.candidates[0],quote:'编造的内容'}]),/摘录/);
 assert.throws(()=>validateCandidates(item,[{...item.candidates[0],source:'https://example.org/unrelated'}]),/来源/);
 const rows=styleReviewRows([{...item,model:'test-model'}],new Map([['first',new Set(['科幻'])]]));
 const updated=apply(emptyStore(),{type:'style-update',rows});
 assert.equal(updated.records.first.style.plotTagEvidence.theme.quote,item.candidates[0].quote);
 assert.equal(projectEntries(base,updated)[0].plotTags.theme,'科幻');
 assert.equal(planStyleUpdates(projectEntries(base,updated),rows).unchanged.length,1);
 const replaced=apply(updated,{type:'style-update',rows:[{id:'first',mode:'set',tags:{theme:'战争'}}]});
 assert.deepEqual(replaced.records.first.style.plotTagEvidence,{});
});


test('downloadable style templates match the CSV and AI review import formats',()=>{
 const template=name=>readFileSync(new URL('../templates/'+name,import.meta.url),'utf8');
 assert.deepEqual(parseCSV(template('basic-style-update.csv')),[STYLE_UPDATE_HEADERS]);
 const [update]=parseStyleUpdates(template('basic-style-update-example.csv'));
 assert.deepEqual(update.tags,{emotion:null,theme:['科幻','悬疑'],perspective:'第一人称'});
 const example=parseStyleReview(template('basic-style-candidates-example.json'));
 assert.equal(example.items.length,1);
 assert.equal(example.items[0].candidates[0].dimension,'theme');
});


test('appending and removing individual labels preserves per-tag evidence and enforces the cap on final totals',()=>{
 const evidence={quote:'记录了可核对的剧情内容',source:'https://example.org/story',model:'test'};
 const init=apply(emptyStore(),{type:'style-update',rows:[{id:'second',mode:'set',tags:{theme:'历史'},evidence:{theme:evidence}}]});
 const next=apply(init,{type:'style-update',rows:[{id:'second',mode:'append',tags:{theme:'悬疑',perspective:'第一人称'},evidence:{'悬疑':evidence}}]});
 const work=projectEntries(base,next)[1];
 assert.deepEqual(styleLabels(work.plotTags),['历史','悬疑','第一人称']);
 assert.deepEqual(work.plotTagEvidence,{'历史':evidence,'悬疑':evidence});
 const row=basicFilterRows([work],new Map())[0];
 assert.deepEqual(row.themes,['历史','悬疑']);
 assert.equal(compileCombinedSearch([[{field:'style',mode:'all',values:['第一人称','悬疑']} ]])(row),true);
 assert.equal(styleOptions([work]).find(group=>group.label==='叙事视角').options[0].count,1);
 const removed=apply(next,{type:'style-update',rows:[{id:'second',mode:'remove',tags:{theme:'悬疑'}}]});
 assert.deepEqual(removed.records.second.style.plotTagEvidence,{theme:evidence});
 assert.throws(()=>apply(next,{type:'style-update',rows:[{id:'second',mode:'append',tags:{theme:['科幻','推理','战争','奇幻']}}]}),/最多选择6个/);
 assert.deepEqual(projectEntries(base,undoLast(removed,removed.revision))[1],work);
});

test('AI can approve two independent tags in one dimension',()=>{
 const synopsis='这一叙事以第一人称展开，并逐步切换至多视角。';
 const item={id:'second',title:second.title,model:'test',synopsis,sources:[second.source],candidates:[
  {dimension:'perspective',tag:'第一人称',quote:'以第一人称展开',source:second.source},
  {dimension:'perspective',tag:'多视角',quote:'逐步切换至多视角',source:second.source}
 ]};
 assert.equal(validateCandidates(item,item.candidates).length,2);
 assert.throws(()=>validateCandidates(item,[item.candidates[0],item.candidates[0]]),/重复/);
 const rows=styleReviewRows([item],new Map([[item.id,new Set(['第一人称','多视角'])]]));
 const next=apply(emptyStore(),{type:'style-update',rows});
 assert.deepEqual(next.records.second.style.plotTags.perspective,['第一人称','多视角']);
 assert.equal(next.records.second.style.plotTagEvidence['多视角'].quote,'逐步切换至多视角');
});
