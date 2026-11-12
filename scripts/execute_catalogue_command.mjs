import {readFileSync,writeFileSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {join} from 'node:path';
import {COMMAND_LIMIT,validateCommand} from '../src/application/commands/envelope.mjs';
import {gitBlobHash} from '../src/infrastructure/filesystem/basic-store.mjs';
import {executeCommand} from '../src/infrastructure/filesystem/command-executor.mjs';
const root=fileURLToPath(new URL('../',import.meta.url));
export function dispatchReference(event){
 const ref=event.client_payload;
 if(event.repository?.full_name!=='wt1234-donkey/visual-novel'||event.action!=='catalogue-command-v1'||!event.sender?.login||!ref||Object.keys(ref).some(key=>!['schemaVersion','operationId','commandSha'].includes(key))||ref.schemaVersion!==1||typeof ref.operationId!=='string'||!ref.operationId||ref.operationId.length>500||!/^[a-f0-9]{40}$/.test(ref.commandSha))throw Error('命令派发身份或对象引用无效');
 return {...ref,actor:event.sender.login};
}
async function main(){
 const policy=JSON.parse(readFileSync(join(root,'data/trusted-save-policy.json'),'utf8'));
 if(policy.mode!=='trusted')throw Error('可信保存尚未切换；请先完成规则与直存联调，不接受生产命令');
 const event=JSON.parse(readFileSync(process.env.GITHUB_EVENT_PATH,'utf8')),reference=dispatchReference(event);
 const response=await fetch('https://api.github.com/repos/wt1234-donkey/visual-novel/git/blobs/'+reference.commandSha,{headers:{Authorization:'Bearer '+process.env.GH_TOKEN,Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}});
 if(!response.ok)throw Error('无法读取命令对象');
 const blob=await response.json();if(blob.size>COMMAND_LIMIT||blob.encoding!=='base64')throw Error('命令对象超过大小限制或编码无效');
 const bytes=Buffer.from(blob.content.replace(/\s/g,''),'base64');if(bytes.length>COMMAND_LIMIT||gitBlobHash(bytes)!==reference.commandSha)throw Error('命令对象摘要不符');
 const command=validateCommand(JSON.parse(bytes.toString('utf8')));if(command.operationId!==reference.operationId)throw Error('派发操作ID不一致');
 const result=executeCommand(root,command,reference.actor);
 if(process.env.GITHUB_OUTPUT)writeFileSync(process.env.GITHUB_OUTPUT,'already='+result.alreadyApplied+'\nkind='+command.kind+'\n',{flag:'a'});
 console.log(JSON.stringify({operationId:command.operationId,revision:result.receipt.revision,alreadyApplied:result.alreadyApplied}));
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)await main();
