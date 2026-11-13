import {operationReceipt,publicationState,PUBLICATION_LABELS} from '../application/publication/status.mjs';
import {withDeadline} from '../infrastructure/storage/async-read.mjs';
const ancestryCaches=new WeakMap();
const KEY='catalogue-operation-receipts-v1',REPO='https://api.github.com/repos/wt1234-donkey/visual-novel';
export function recordSavedOperation(values){
 const receipt=operationReceipt(values);
 if(typeof localStorage!=='undefined')try{const rows=JSON.parse(localStorage.getItem(KEY)||'[]');localStorage.setItem(KEY,JSON.stringify([receipt,...rows.filter(row=>row.operationId!==receipt.operationId)].slice(0,30)));}catch{}
 if(typeof window!=='undefined')window.dispatchEvent(new CustomEvent('catalogue-operation-saved',{detail:receipt}));
 return receipt;
}
export async function checkPublication(receipts,fetcher=fetch,{signal,timeout=12000,requestTimeout=8000}={}){
 receipts=receipts.slice(0,5);
 let deployment=null,runs=[],available=true;
 const check=async scope=>{
 const json=url=>withDeadline(async s=>{const response=await fetcher(url,{cache:'no-store',signal:s});if(!response.ok)throw Error('发布状态暂不可读取');return response.json();},{signal:scope,timeout:requestTimeout});
 try{deployment=await json('./deployment.json');}catch{}
 // Offline publication evidence is sufficient, including a later descendant release.
 if(receipts.every(receipt=>publicationState(receipt,deployment).state==='published'))return receipts.map(receipt=>({receipt,...publicationState(receipt,deployment)}));
 try{
  const data=await json(REPO+'/actions/runs?branch=main&per_page=20');runs=(data.workflow_runs||[]).filter(run=>['.github/workflows/pages.yml','.github/workflows/pages-deploy.yml'].includes(run.path)&&run.event!=='pull_request'&&/^[a-f0-9]{40}$/.test(run.head_sha)).slice(0,2);
  if(!ancestryCaches.has(fetcher))ancestryCaches.set(fetcher,new Map());
  const comparisons=ancestryCaches.get(fetcher);
  if(comparisons.size>100)comparisons.clear();
  for(const receipt of receipts)for(const run of runs){
   if(!receipt.commit)continue;
   if(run.head_sha===receipt.commit){run.contains??=new Set();run.contains.add(receipt.operationId);continue;}
   const key=receipt.commit+'...'+run.head_sha;
   if(!comparisons.has(key))comparisons.set(key,json(REPO+'/compare/'+key).then(value=>['identical','ahead'].includes(value.status)).catch(error=>{comparisons.delete(key);throw error;}));
   if(await comparisons.get(key)){run.contains??=new Set();run.contains.add(receipt.operationId);}
  }
 }catch{available=false;}
 return receipts.map(receipt=>({receipt,...publicationState(receipt,deployment,runs.map(run=>({...run,containsOperation:run.contains?.has(receipt.operationId)})),{available})}));
 };
 try{return await withDeadline(check,{signal,timeout});}catch{return receipts.map(receipt=>({receipt,...publicationState(receipt,deployment,[],{available:false})}));}
}
export function installPublicationStatus(){
 let receipts=[];try{receipts=JSON.parse(localStorage.getItem(KEY)||'[]').map(operationReceipt);}catch{}
 let host,pending=false,timer;
 function render(rows){
  if(!receipts.length)return;
  if(!host){host=document.createElement('details');host.id='publication-status';host.style.cssText='margin:12px;padding:12px;border:1px solid #d8d1e3;border-radius:8px;background:#faf8ff;color:#393043;font:13px/1.6 system-ui';(document.querySelector('main')||document.body).prepend(host);}
  host.replaceChildren();const title=document.createElement('summary');title.textContent='保存与发布状态 · '+PUBLICATION_LABELS[rows[0]?.state||'saved'];host.append(title);
  for(const row of rows.slice(0,5)){
   const p=document.createElement('p');p.textContent=({basic:'基础库',formal:'正式作品',identity:'身份核对',field:'字段证据'}[row.receipt.kind])+' r'+row.receipt.revision+' · '+PUBLICATION_LABELS[row.state]+' · '+row.receipt.at;
   if(row.url&&/^https:\/\/github\.com\/wt1234-donkey\/visual-novel\//.test(row.url)){const a=document.createElement('a');a.href=row.url;a.textContent=' 查看发布记录';a.target='_blank';a.rel='noopener noreferrer';p.append(a);}
   host.append(p);
  }
  const button=document.createElement('button');button.type='button';button.textContent='检查发布状态';button.addEventListener('click',refresh);host.append(button);
 }
 async function refresh(){
  if(pending||!receipts.length)return;pending=true;
  try{const rows=await checkPublication(receipts);render(rows);clearTimeout(timer);if(rows.some(row=>['waiting','publishing'].includes(row.state)))timer=setTimeout(refresh,30000);}
  catch{render(receipts.map(receipt=>({receipt,state:'unknown'})));}finally{pending=false;}
 }
 window.addEventListener('catalogue-operation-saved',event=>{receipts=[event.detail,...receipts.filter(row=>row.operationId!==event.detail.operationId)].slice(0,30);render(receipts.map(receipt=>({receipt,state:'saved'})));refresh();});
 if(receipts.length){render(receipts.map(receipt=>({receipt,state:'saved'})));refresh();}
}
