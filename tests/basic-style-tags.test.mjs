import test from 'node:test';
import assert from 'node:assert/strict';
import {applyChange,emptyStore,parseStyleUpdates,planStyleUpdates,projectEntries,undoLast,STYLE_UPDATE_HEADERS} from '../basic-catalogue-model.mjs';
import {STYLE_DIMENSIONS,styleState,validateStyleTags} from '../basic-style-tags.mjs';
import {buildStyleRequest,parseStyleReview,styleReviewRows,validateCandidates} from '../basic-style-review.mjs';

const first={id:'first',title:'同名作品',firstYear:1965,group:'历史厂商',gameplay:'ADV',source:'印刷目录',plotStyles:['悬疑','推理','疗愈']};
const second={id:'second',title:'同名作品',firstYear:1990,group:'另一厂商',gameplay:'ADV',source:'https://example.org/story',plotTags:{theme:'科幻'}};
const base=[first,second];
const apply=(store,action)=>applyChange(store,base,action,{actor:'reviewer',reason:'测试',expectedRevision:store.revision});

test('six axes accept one controlled tag each and preserve ambiguous legacy tags',()=>{
 const tags={tone:'喜剧',emotion:'压抑',expression:'群像',relationship:'百合',theme:'悬疑',content:'NTR'};
 assert.equal(Object.keys(STYLE_DIMENSIONS).length,6);
 assert.deepEqual(validateStyleTags(tags),tags);
 assert.throws(()=>validateStyleTags({...tags,theme:['悬疑','推理']}),/故事题材/);
 assert.throws(()=>validateStyleTags({...tags,theme:'群像'}),/故事题材/);
 assert.deepEqual(styleState(first),{tags:{emotion:'治愈'},legacy:['悬疑','推理']});
});

test('CSV uses IDs, preserves untouched dimensions and updates legacy works atomically',()=>{
 const csv=STYLE_UPDATE_HEADERS.join(',')+'\r\nfirst,同名作品,,清空,,,悬疑,\r\nsecond,,喜剧,,,,,\r\n';
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
 assert.throws(()=>parseStyleUpdates(STYLE_UPDATE_HEADERS.join(',')+'\nfirst,,,,,,群像,\n'),/故事题材/);
 assert.deepEqual(store,emptyStore());
});

test('AI request uses linked existing synopsis, skips placeholders and approval fills empty dimensions',()=>{
 const synopsis='未来社会中的舰队依靠星际技术探索行星，并开始艰苦的太空航行。';
 const works=projectEntries(base,emptyStore());
 const archive=[{id:'full-first',synopsis,source:'https://example.org/full'},{id:'second',synopsis:'作品剧情简介待依据官方原文细编。',source:second.source}];
 const request=buildStyleRequest([{...works[0],linkedRecordId:'full-first'},works[1]],archive,{});
 assert.deepEqual(request.items.map(item=>item.id),['first']);
 assert.deepEqual(request.issues.map(item=>item.id),['second']);
 assert.ok(!request.items[0].dimensions.includes('emotion'));
 const item={...request.items[0],candidates:[{dimension:'theme',tag:'科幻',quote:'舰队依靠星际技术探索行星',source:'https://example.org/full'}]};
 const payload={schemaVersion:1,model:'test-model',items:[item],issues:request.issues};
 assert.deepEqual(parseStyleReview(JSON.stringify(payload)),payload);
 assert.throws(()=>validateCandidates(item,[{...item.candidates[0],quote:'编造的内容'}]),/摘录/);
 assert.throws(()=>validateCandidates(item,[{...item.candidates[0],source:'https://example.org/unrelated'}]),/来源/);
 const rows=styleReviewRows([{...item,model:'test-model'}],new Map([['first',new Set(['theme'])]]));
 const updated=apply(emptyStore(),{type:'style-update',rows});
 assert.equal(updated.records.first.style.plotTagEvidence.theme.quote,item.candidates[0].quote);
 assert.equal(projectEntries(base,updated)[0].plotTags.theme,'科幻');
 assert.equal(planStyleUpdates(projectEntries(base,updated),rows).unchanged.length,1);
 const replaced=apply(updated,{type:'style-update',rows:[{id:'first',mode:'set',tags:{theme:'战争'}}]});
 assert.deepEqual(replaced.records.first.style.plotTagEvidence,{});
});
