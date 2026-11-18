import {validateCommand,commandText} from '../../application/commands/envelope.mjs';
import {blobDigest,digestText} from '../storage/digests.mjs';
import {withDeadline,interrupted} from '../storage/async-read.mjs';

// Retry only read requests and content-addressed blob uploads. A dispatch may
// already have been accepted when its response is lost: never auto-repeat it.
const transient=error=>error?.code==='NETWORK_ERROR'||interrupted(error)||[500,502,503,504].includes(error?.status);
export async function submitCommand(request,command,{timeout=240000,requestTimeout=8000,signal,interval=2000,pause=ms=>new Promise(resolve=>setTimeout(resolve,ms)),fetchPublic=fetch,resume=false,onProgress=()=>{}}={}){
 validateCommand(command);const repo='/repos/wt1234-donkey/visual-novel',text=commandText(command),digest=await blobDigest(text);
 const path='data/command-receipts/'+await digestText(command.operationId,'SHA-256')+'.json';
 const progress=stage=>onProgress({stage,operationId:command.operationId});
 const call=(path,method='GET',body,scope=signal)=>withDeadline(s=>request(path,method,body,{signal:s,timeout:requestTimeout}),{signal:scope,timeout:requestTimeout});
 const stableCall=async(path,method='GET',body,scope=signal)=>{
  const repeat=method==='GET'||method==='POST'&&path===repo+'/git/blobs';
  for(let attempt=0;;attempt++){
   try{return await call(path,method,body,scope);}
   catch(error){
    if(!repeat||attempt>=2||scope?.aborted||!transient(error))throw error;
    progress('retrying');
    await withDeadline(()=>pause(200*(attempt+1)),{signal:scope,timeout:requestTimeout});
   }
  }
 };
 const read=async(scope=signal)=>{
  const head=(await stableCall(repo+'/git/ref/heads/main','GET',undefined,scope)).object.sha;
  let file;try{file=await stableCall(repo+'/contents/'+path+'?ref='+head,'GET',undefined,scope);}catch(error){if(error.status===404)return null;throw error;}
  const blob=file.content?file:await stableCall(repo+'/git/blobs/'+file.sha,'GET',undefined,scope);
  const raw=new TextDecoder().decode(Uint8Array.from(atob(blob.content.replace(/\s/g,'')),c=>c.charCodeAt(0)));
  if(await blobDigest(raw)!==file.sha)throw Error('命令回执摘要不符');
  const receipt=JSON.parse(raw);if(receipt.command!==text)throw Object.assign(Error('操作ID已用于不同内容'),{code:'OPERATION_CONFLICT'});
  if(receipt.schemaVersion!==1||receipt.operationId!==command.operationId||receipt.kind!==command.kind||receipt.actor!==command.actor||!Number.isSafeInteger(receipt.revision)||receipt.revision<1)throw Error('命令回执身份或修订无效');
  return {operationId:command.operationId,kind:receipt.kind,actor:receipt.actor,at:receipt.at||command.at,
   revision:receipt.revision,commit:head,...(command.kind==='formal'?{workId:command.action.workId}:{})};
 };
 const matchingRuns=async scope=>{
  const data=await withDeadline(async s=>{
   const response=await fetchPublic('https://api.github.com'+repo+'/actions/runs?event=repository_dispatch&branch=main&per_page=30',{cache:'no-store',signal:s});
   if(!response.ok)throw Error('无法读取可信保存工作流状态（HTTP '+response.status+'）');
   return response.json();
  },{signal:scope,timeout:requestTimeout});
  return (data.workflow_runs||[]).filter(run=>run.path==='.github/workflows/catalogue-command.yml'&&run.display_title==='保存 '+command.operationId);
 };
 progress('checking');
 const existing=await read();if(existing){progress('confirmed');return {...existing,alreadyApplied:true};}
 let shouldDispatch=true;
 if(resume){
  progress('reconciling');
  let runs;
  try{runs=await matchingRuns(signal);}
  catch(error){
   if(signal?.aborted)throw error;
   throw Object.assign(Error('暂无法确认先前命令是否仍在运行，未重复派发；请稍后以同一操作重试。'),{code:'COMMAND_PENDING',operationId:command.operationId,cause:error});
  }
  // Reconcile a still-running or completed-successful dispatch instead of
  // creating an unnecessary second workflow run.
  if(runs.some(run=>run.status!=='completed'||run.conclusion==='success'))shouldDispatch=false;
 }
 let dispatchError;
 if(shouldDispatch){
  progress('uploading');
  const blob=await stableCall(repo+'/git/blobs','POST',{content:text,encoding:'utf-8'});if(blob.sha!==digest)throw Error('命令对象摘要不符');
  progress('dispatching');
  try{await call(repo+'/dispatches','POST',{event_type:'catalogue-command-v1',client_payload:{schemaVersion:1,operationId:command.operationId,commandSha:digest}});}
  catch(error){dispatchError=error;if(error.status&&error.status<500)throw Object.assign(error,{commandNotApplied:true});if(signal?.aborted)throw error;}
 }
 progress('waiting');
 const wait=async scope=>{
  let polls=0;
  do{
   let receipt;
   try{receipt=await read(scope);}catch(error){
    if(!transient(error)||scope?.aborted)throw error;
    // Exhausted the bounded safe reads. Do not leave the form waiting for
    // the entire workflow budget while GitHub's receipt endpoint stays down.
    // The dispatch may have succeeded; retain its operation ID for later
    // reconciliation and surface the underlying HTTP/network diagnosis.
    throw Object.assign(Error('命令 '+command.operationId+' 的回执暂无法读取：'+error.message+'。当前输入与原操作ID已保留，稍后可继续核对。'),{
     code:'COMMAND_PENDING',operationId:command.operationId,cause:error
    });
   }
   if(receipt){progress('confirmed');return receipt;}
   if(timeout===0)return null;
   if(++polls%5===0){
    let runs=[];try{runs=await matchingRuns(scope);}catch(error){if(scope?.aborted)throw error;}
    if(runs.length&&runs.every(run=>run.status==='completed'&&run.conclusion!=='success')){
     // A terminal run can fail after promotion. Re-read the atomic receipt
     // before classifying this operation as definitely not applied.
     const confirmed=await read(scope);if(confirmed){progress('confirmed');return confirmed;}
     throw Object.assign(Error('命令校验或提交失败，当前输入保留。请同步后重新核对：'+runs[0].html_url),{code:'COMMAND_REJECTED',commandNotApplied:true,operationId:command.operationId});
    }
   }
   await withDeadline(()=>pause(interval),{signal:scope,timeout:Math.max(requestTimeout,interval+100)});
  }while(true);
 };
 try{const receipt=timeout===0?await wait(signal):await withDeadline(wait,{signal,timeout});if(receipt)return receipt;}
 catch(error){if(!interrupted(error)||signal?.aborted)throw error;dispatchError=error;}
 throw Object.assign(Error('命令 '+command.operationId+' 的执行结果暂无法确认。当前输入已保留；重试会核对同一操作，请查看可信保存工作流。'),{code:'COMMAND_PENDING',operationId:command.operationId,cause:dispatchError});
}
