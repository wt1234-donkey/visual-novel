import {validateCommand,commandText} from '../../application/commands/envelope.mjs';
import {blobDigest,digestText} from '../storage/digests.mjs';
export async function submitCommand(request,command,{timeout=240000,interval=2000,pause=ms=>new Promise(resolve=>setTimeout(resolve,ms)),fetchPublic=fetch}={}){
 validateCommand(command);const repo='/repos/wt1234-donkey/visual-novel',text=commandText(command),digest=await blobDigest(text);
 const path='data/command-receipts/'+await digestText(command.operationId,'SHA-256')+'.json';
 const read=async()=>{
  const head=(await request(repo+'/git/ref/heads/main')).object.sha;
  let file;try{file=await request(repo+'/contents/'+path+'?ref='+head);}catch(error){if(error.status===404)return null;throw error;}
  const blob=file.content?file:await request(repo+'/git/blobs/'+file.sha);
  const raw=new TextDecoder().decode(Uint8Array.from(atob(blob.content.replace(/\s/g,'')),c=>c.charCodeAt(0)));
  if(await blobDigest(raw)!==file.sha)throw Error('命令回执摘要不符');
  const receipt=JSON.parse(raw);if(receipt.command!==text)throw Object.assign(Error('操作ID已用于不同内容'),{code:'OPERATION_CONFLICT'});
  if(receipt.schemaVersion!==1||receipt.operationId!==command.operationId||receipt.kind!==command.kind||receipt.actor!==command.actor||!Number.isSafeInteger(receipt.revision)||receipt.revision<1)throw Error('命令回执身份或修订无效');
  return {operationId:command.operationId,revision:receipt.revision,commit:head};
 };
 const existing=await read();if(existing)return existing;
 const blob=await request(repo+'/git/blobs','POST',{content:text,encoding:'utf-8'});if(blob.sha!==digest)throw Error('命令对象摘要不符');
 // A lost dispatch response can mean acceptance. Reconcile the same immutable operation, never invent a replacement ID.
 let dispatchError;
 try{await request(repo+'/dispatches','POST',{event_type:'catalogue-command-v1',client_payload:{schemaVersion:1,operationId:command.operationId,commandSha:digest}});}catch(error){dispatchError=error;if(error.status&&error.status<500)throw error;}
 const started=Date.now();let polls=0;
 do{
  const receipt=await read();if(receipt)return receipt;if(Date.now()-started>=timeout)break;
  if(++polls%5===0){
   let run;try{const response=await fetchPublic('https://api.github.com'+repo+'/actions/runs?event=repository_dispatch&branch=main&per_page=30',{cache:'no-store'});if(response.ok)run=(await response.json()).workflow_runs?.find(value=>value.path==='.github/workflows/catalogue-command.yml'&&value.display_title==='保存 '+command.operationId);}catch{}
   if(run?.status==='completed'&&run.conclusion!=='success')throw Object.assign(Error('命令校验或提交失败，当前输入保留。请查看执行记录：'+run.html_url),{code:'COMMAND_REJECTED',operationId:command.operationId});
  }
  await pause(interval);
 }while(true);
 throw Object.assign(Error('命令 '+command.operationId+' 的执行结果暂无法确认。当前输入已保留；重试会核对同一操作，请查看可信保存工作流。'),{code:'COMMAND_PENDING',operationId:command.operationId,cause:dispatchError});
}
