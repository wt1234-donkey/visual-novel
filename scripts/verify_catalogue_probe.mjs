// Read the isolated GitHub receipt through the same verifier used by the browser.
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {join} from 'node:path';
import {receiptPath} from '../src/infrastructure/filesystem/command-executor.mjs';
import {submitCommand} from '../src/infrastructure/github/command-transport.mjs';
const root=fileURLToPath(new URL('../',import.meta.url));
const runId=process.env.GITHUB_RUN_ID;
if(process.env.GITHUB_REPOSITORY!=='wt1234-donkey/visual-novel'||process.env.GITHUB_REF!=='refs/heads/main'||!/^\d+$/.test(runId??''))throw Error('Receipt rehearsal requires this repository main workflow');
const event=JSON.parse(readFileSync(process.env.GITHUB_EVENT_PATH,'utf8'));
if(event.action!=='catalogue-command-probe-v1')throw Error('Receipt rehearsal requires the isolated event');
const receipt=JSON.parse(readFileSync(join(root,receiptPath(event.client_payload.operationId)),'utf8'));
const command=JSON.parse(receipt.command);
const request=async(path,method='GET')=>{
 if(method!=='GET')throw Error('Receipt verification must never write to GitHub');
 const isolated=path.replace('/git/ref/heads/main','/git/ref/heads/validation/trusted-save-gate-'+runId);
 const response=await fetch('https://api.github.com'+isolated,{headers:{Authorization:'Bearer '+process.env.GH_TOKEN,Accept:'application/vnd.github+json'}});
 if(!response.ok)throw Object.assign(Error('Cannot verify isolated receipt (HTTP '+response.status+')'),{status:response.status});
 return response.json();
};
const proof=await submitCommand(request,command,{timeout:0});
console.log(JSON.stringify({receiptVerified:true,...proof}));
