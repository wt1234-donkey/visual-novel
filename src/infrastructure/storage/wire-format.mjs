// Generated-resource transport only. Digests always describe the decoded text.
const prefix='{"atlasWire":"gzip-base64-v1","data":"';
export async function decodePublishedText(text){
 if(!text.startsWith(prefix))return text;
 const value=JSON.parse(text);
 if(value.atlasWire!=='gzip-base64-v1'||typeof value.data!=='string'||Object.keys(value).length!==2)throw Error('目录压缩格式无效');
 const bytes=Uint8Array.from(atob(value.data),char=>char.charCodeAt(0));
 if(typeof DecompressionStream!=='undefined')return new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
 const {gunzipSync}=await import('./gzip-fallback.mjs');
 return new TextDecoder('utf-8',{fatal:true}).decode(gunzipSync(bytes));
}
