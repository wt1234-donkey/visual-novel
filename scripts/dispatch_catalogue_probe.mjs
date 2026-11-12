// Exercises the real blob/dispatch protocol without placing test data on main.
import {fileURLToPath} from 'node:url';
import {loadCatalogueSnapshot} from '../src/infrastructure/filesystem/catalogue-snapshot.mjs';
import {projectEntries,valuesOf} from '../src/domain/catalogue/model.mjs';
import {validateCommand,commandText} from '../src/application/commands/envelope.mjs';
import {gitBlobHash} from '../src/infrastructure/filesystem/basic-store.mjs';
const root=fileURLToPath(new URL('../',import.meta.url));
if(process.env.GITHUB_REPOSITORY!=='wt1234-donkey/visual-novel'||process.env.GITHUB_REF!=='refs/heads/main')throw Error('隔离派发只能从本仓库 main 启动');
const {snapshot,inputs,sourceLease}=loadCatalogueSnapshot(root);
const row=projectEntries(snapshot.sourceRows,inputs.store).find(row=>row.title.length<430);
const command=validateCommand({schemaVersion:1,operationId:'gate-probe-'+process.env.GITHUB_RUN_ID,kind:'basic',actor:'github-actions[bot]',at:new Date().toISOString(),reason:'隔离验证可信保存通道',sources:[],expectedRevision:inputs.store.revision,sourceLease,action:{type:'edit',id:row._key,values:{...valuesOf(row),title:row.title+' [isolated gate probe]'}}});
const request=async(path,body)=>{
 const response=await fetch('https://api.github.com/repos/wt1234-donkey/visual-novel'+path,{method:'POST',headers:{Authorization:'Bearer '+process.env.GH_TOKEN,Accept:'application/vnd.github+json','Content-Type':'application/json'},body:JSON.stringify(body)});
 if(!response.ok)throw Error('隔离派发失败（HTTP '+response.status+'）');return response.status===204?{}:response.json();
};
const text=commandText(command),blob=await request('/git/blobs',{encoding:'utf-8',content:text});
if(blob.sha!==gitBlobHash(text))throw Error('命令 blob 摘要不一致');
await request('/dispatches',{event_type:'catalogue-command-probe-v1',client_payload:{schemaVersion:1,operationId:command.operationId,commandSha:blob.sha}});
console.log(JSON.stringify({operationId:command.operationId,commandSha:blob.sha}));
