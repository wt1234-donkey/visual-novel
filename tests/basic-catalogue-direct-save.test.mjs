import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {readLatestBasicStore} from '../basic-catalogue-live.mjs';

const editor=readFileSync(new URL('../basic-catalogue-editor.mjs',import.meta.url),'utf8');
const browse=readFileSync(new URL('../minimal-adv-rpg.mjs',import.meta.url),'utf8');
const html=readFileSync(new URL('../minimal-adv-rpg.html',import.meta.url),'utf8');

test('live repository revision overrides lagging published snapshot',async()=>{
 let called=false;
 const result=await readLatestBasicStore(async()=>({revision:9}),async()=>{called=true;return {revision:8};});
 assert.deepEqual(result,{store:{revision:9},source:'github'});
 assert.equal(called,false);
});
test('published snapshot is read-only fallback when live GET is unavailable',async()=>{
 const result=await readLatestBasicStore(async()=>{throw Error('rate limited');},async()=>({revision:8}));
 assert.deepEqual(result,{store:{revision:8},source:'pages'});
 await assert.rejects(readLatestBasicStore(async()=>{throw Error('network');},async()=>{throw Error('offline');}),/不可读取/);
});
test('basic editor does not generate editorial proposals and requires write authorization',()=>{
 assert.doesNotMatch(editor,/makeProposal|offerEditorialProposal|basicProposalPreview|EDITORIAL_URL|送审预览|预览并送审/);
 assert.match(editor,/if\(!actor\)\{[\s\S]*?连接 GitHub 写入权限/);
 assert.match(editor,/await service\.execute\(action,reason,\{undo\}\)/);
 assert.match(editor,/async function commit\(action,reason,undo=false\)/);
 assert.match(editor,/function merge\(ids\)/);
 assert.match(editor,/type:'merge'/);
});
test('clicking a catalogue title opens the editor, with merge and three tag tools preserved',()=>{
 assert.match(browse,/class="work-title" data-edit/);
 assert.match(browse,/editor\.edit\(button\.dataset\.edit\)/);
 assert.match(browse,/editor\.merge\(\[\.\.\.selection\]\)/);
 for(const id of ['basic-style-bulk','basic-style-csv','basic-style-review','basic-merge']){
  assert.ok(html.includes('id="'+id+'"'));
 }
 assert.doesNotMatch(html,/编目审核队列|发布审核入口/);
});
