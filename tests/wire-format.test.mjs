import test from 'node:test';
import assert from 'node:assert/strict';
import {gzipSync} from 'node:zlib';
import {decodePublishedText} from '../src/infrastructure/storage/wire-format.mjs';
import {readReleaseText} from '../src/infrastructure/storage/release-reader.mjs';
import {blobDigest} from '../src/infrastructure/storage/digests.mjs';
import {createBasicWebIndex} from '../basic-catalogue-index.mjs';
const wire=text=>JSON.stringify({atlasWire:'gzip-base64-v1',data:gzipSync(text).toString('base64')});

test('generated data decodes byte-for-byte with native streams and without them',async()=>{
 const text=JSON.stringify({title:'原始来源与版本',records:Array(300).fill('preserved source evidence')})+'\n';
 assert.equal(await decodePublishedText(text),text);
 assert.equal(await decodePublishedText(wire(text)),text);
 const saved=globalThis.DecompressionStream;
 try{globalThis.DecompressionStream=undefined;assert.equal(await decodePublishedText(wire(text)),text);}
 finally{globalThis.DecompressionStream=saved;}
});
test('release digest verifies decoded bytes, never the transport wrapper',async()=>{
 const revision='a'.repeat(40),text='{"original":"source"}\n',ref={path:'catalogue-web/'+revision+'/data.json',sha:await blobDigest(text)};
 const fetcher=async()=>new Response(wire(text));
 assert.equal(await readReleaseText(ref,{revision},fetcher),text);
 await assert.rejects(readReleaseText(ref,{revision},async()=>new Response(wire('{"changed":true}'))),/摘要不匹配/);
});
test('basic catalogue index and detail fallback work without native decompression',async()=>{
 const revision='b'.repeat(40),index=JSON.stringify({rows:[['i','w','作品',1965,0,0,0]],groups:['Maker'],gameplay:['ADV'],statuses:['promoted-basic']}),details='[{"source":"https://example.org/work"}]';
 const manifest={schema:1,revision,shardSize:250,home:{total:0},basic:{total:1},assets:{'basic-index.json':{sha:await blobDigest(index)},'basic-0.json':{sha:await blobDigest(details)}}};
 const saved=globalThis.DecompressionStream;
 try{globalThis.DecompressionStream=undefined;
  const reader=createBasicWebIndex(async url=>new Response(url.endsWith('manifest.json')?JSON.stringify(manifest):wire(url.endsWith('basic-index.json')?index:details)),{release:null});
  assert.equal((await reader.basicRows())[0].title,'作品');
  assert.equal((await reader.details('basic',[0])).get(0).source,'https://example.org/work');
 }finally{globalThis.DecompressionStream=saved;}
});
