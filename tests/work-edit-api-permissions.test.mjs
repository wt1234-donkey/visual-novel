import test from 'node:test';
import assert from 'node:assert/strict';
import {createEditClient,TOKEN_SETUP_URL} from '../work-edit-api.mjs';
const store={schemaVersion:1,records:{}};
const response=(status,payload={},headers={})=>({ok:status>=200&&status<300,status,headers:new Headers(headers),json:async()=>payload});
const denied=(status,message,headers={})=>createEditClient('test-only',async()=>response(status,{message},headers));

test('a connection checks account write access with reads only and does not claim token write permission',async()=>{
 const calls=[];const client=createEditClient('test-only',async(url,options)=>{calls.push(options.method);return response(200,url.endsWith('/user')?{login:'wt1234-donkey'}:{permissions:{push:true}});});
 assert.equal(await client.connect(),'wt1234-donkey');assert.deepEqual(calls,['GET','GET']);
 for(const permissions of [undefined,{push:false}])await assert.rejects(()=>createEditClient('test-only',async url=>response(200,url.endsWith('/user')?{login:'other-user'}:{permissions})).connect(),/other-user.*wt1234-donkey\/visual-novel.*写入权限/);
});
test('classic credentials with read-only public access fail before editing; scoped public write credentials connect',async()=>{
 const client=scopes=>createEditClient('ghp_test_only',async url=>response(200,url.endsWith('/user')?{login:'wt1234-donkey'}:{permissions:{push:true}},{'x-oauth-scopes':scopes}));
 await assert.rejects(()=>client('').connect(),/缺少公开仓库内容写入权限/);
 await assert.rejects(()=>client('read:user, repo:status').connect(),/缺少公开仓库内容写入权限/);
 assert.equal(await client('public_repo').connect(),'wt1234-donkey');
 const fineGrained=createEditClient('github_pat_test_only',async url=>response(200,url.endsWith('/user')?{login:'wt1234-donkey'}:{permissions:{push:true}},{'x-oauth-scopes':''}));
 assert.equal(await fineGrained.connect(),'wt1234-donkey');
});
test('fine-grained permission failures identify the write, owner, selected repo and contents permission',async()=>{
 await assert.rejects(()=>denied(403,'Resource not accessible by personal access token').write(store,'sha','合并作品'),e=>{
  assert.equal(e.status,403);assert.equal(e.code,'PERMISSION_DENIED');assert.match(e.message,/保存网站修改失败（HTTP 403）/);assert.match(e.message,/Resource owner 为 wt1234-donkey/);assert.match(e.message,/Only select repositories → visual-novel/);assert.match(e.message,/Contents 为 Read and write/);assert.match(e.message,/Public repositories.*读取权限/);assert.match(e.message,/GitHub 返回：Resource not accessible/);return true;
 });
});
test('rate limits, protected branches, expired credentials and conflicts have distinct diagnoses',async()=>{
 const scenarios=[[403,'API rate limit exceeded','RATE_LIMIT'],[403,'Forbidden','RATE_LIMIT',{'x-ratelimit-remaining':'0'}],[429,'Too many requests','RATE_LIMIT'],[403,'GH013: Repository rule violations found','BRANCH_RULE'],[422,'protected branch update failed','BRANCH_RULE'],[401,'Bad credentials','INVALID_TOKEN'],[409,'Conflict','CONFLICT'],[422,'sha does not match','CONFLICT'],[422,'Invalid request','VALIDATION']];
 for(const [status,message,code,headers] of scenarios)await assert.rejects(()=>denied(status,message,headers).write(store,'sha','test'),e=>{assert.equal(e.code,code);if(code==='RATE_LIMIT')assert.doesNotMatch(e.message,/Contents 为/);return true;});
});
test('a missing history file is reported as a read failure with the actual history path',async()=>{
 const client=createEditClient('test-only',async()=>response(404,{message:'Not Found'}),{historyPath:'data/basic-catalogue-edits.json'});
 await assert.rejects(()=>client.read(),e=>{assert.equal(e.code,'NOT_FOUND');assert.match(e.message,/读取网站修改记录失败（HTTP 404）/);assert.match(e.message,/data\/basic-catalogue-edits.json/);return true;});
});
test('GitHub diagnostics never reflect the supplied credential and network failures preserve context',async()=>{
 const token='github_pat_test_secret';await assert.rejects(()=>createEditClient(token,async()=>response(403,{message:'Rejected '+token})).write(store,'sha','test'),e=>{assert.ok(!e.message.includes(token));assert.match(e.message,/凭证已隐藏/);return true;});
 await assert.rejects(()=>createEditClient('test-only',async()=>{throw TypeError('Failed to fetch');}).write(store,'sha','test'),/保存网站修改失败.*无法连接 GitHub API.*当前填写保留/);
});
test('the credential link pre-fills only the intended resource owner and content permission',()=>{
 const url=new URL(TOKEN_SETUP_URL);assert.equal(url.origin,'https://github.com');assert.equal(url.searchParams.get('target_name'),'wt1234-donkey');assert.equal(url.searchParams.get('contents'),'write');assert.equal(url.searchParams.get('administration'),null);
});
