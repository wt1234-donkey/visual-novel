import test from 'node:test';
import assert from 'node:assert/strict';
import {createResourceLoader} from '../src/application/catalogue/resource-loader.mjs';
const tick=()=>new Promise(setImmediate);
test('cancelled optional work cannot publish over a new selection or remove its newer resource',async()=>{
 const cache=new Map(),calls=[];let resolveOld;
 const ensure=createResourceLoader(cache,{ready:()=>calls.push('ready'),failed:()=>calls.push('failed')});
 const signal=new AbortController();ensure('notes',()=>new Promise(r=>resolveOld=r),v=>calls.push(v),signal.signal);
 await tick();signal.abort();cache.delete('notes');ensure('notes',async()=> 'new',v=>calls.push(v));await tick();
 resolveOld('old');await tick();assert.deepEqual(calls,['new','ready']);assert.equal(cache.get('notes').status,'ready');
});
test('one optional rejection keeps other resources usable and an explicit retry can recover',async()=>{
 const cache=new Map(),calls=[];const ensure=createResourceLoader(cache,{ready:()=>calls.push('ready'),failed:()=>calls.push('failed')});
 ensure('notes',()=>{throw Error('temporary failure');},()=>calls.push('invalid'));
 ensure('formal',async()=> 'work',v=>calls.push(v));await tick();
 assert.equal(cache.get('notes').status,'failed');assert.equal(cache.get('formal').status,'ready');
 cache.delete('notes');ensure('notes',async()=> 'notes',v=>calls.push(v));await tick();assert.equal(cache.get('notes').status,'ready');assert.ok(!calls.includes('invalid'));
});
