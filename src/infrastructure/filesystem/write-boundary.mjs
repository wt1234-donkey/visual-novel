import {readFileSync,writeFileSync,mkdirSync,existsSync,readdirSync} from 'node:fs';
import {join,dirname} from 'node:path';
import {createHash} from 'node:crypto';
import {buildAuditLedger} from './audit-ledger.mjs';
import {createAuditReader} from '../storage/audit-reader.mjs';
import {journalKey} from '../../domain/catalogue/journal.mjs';
import {validateCommand} from '../../application/commands/envelope.mjs';

export const commandReceiptPath=id=>'data/command-receipts/'+createHash('sha256').update(id).digest('hex')+'.json';
const domains=new Set(['basic','formal','identity','field']);
const batchKinds=new Set(['editorial-batch','management','intake']);
const managed=['data/games.json','data/discovery-editorial.json','data/creator-credits.json','data/work-notes.json','data/management-history.json','data/narrative-cataloguing-20261030.json'];
const outputs={management:managed,intake:['data/main-adv-rpg-works-20261031.json'], 'editorial-batch':[...managed,'data/editorial-publications.json','data/basic-catalogue-edits.json','data/work-edit-history.json']};
function sourceHashes(root,kind){return Object.fromEntries((outputs[kind]||[]).filter(path=>existsSync(join(root,path))).map(path=>{const raw=readFileSync(join(root,path));return [path,createHash('sha1').update('blob '+raw.length+'\0').update(raw).digest('hex')];}));}
async function verifyDomainReceipt(reader,root,receipt){
 const command=validateCommand(JSON.parse(receipt.command)),event=await (await reader.open(root,{kind:receipt.kind})).findOperation(receipt.operationId);
 const {workId,...action}=command.action;
 const creators=receipt.kind==='formal'&&command.action.type==='creators',reason=creators?'添加或调整剧作、美术与音乐':receipt.kind==='basic'?command.reason:command.reason.trim();
 if(!event||event.actor!==receipt.actor||event.at!==receipt.at||event.revision!==receipt.revision||event.reason!==reason||receipt.kind!=='basic'&&journalKey(event.sources)!==journalKey(creators?[]:command.sources)||command.operationId!==receipt.operationId||command.kind!==receipt.kind||command.actor!==receipt.actor||command.at!==receipt.at||command.expectedRevision!==event.previousRevision||journalKey(receipt.kind==='formal'?action:command.action)!==journalKey(event.intent))throw Error('写入回执与追加事件不一致');
}
// All active writers stage in an isolated checkout. Only a sealed, validated
// candidate may become a Git commit; this function never promotes a branch.
export async function sealCatalogueWrite(root,descriptor){
 const {operationId}=descriptor;
 if(typeof operationId!=='string'||!operationId||operationId.length>500)throw Error('写入缺少稳定操作ID');
 const path=commandReceiptPath(operationId),file=join(root,path),prior=existsSync(file)?JSON.parse(readFileSync(file,'utf8')):null;
 let receipt=prior;
 if(!receipt){
  const {kind,actor,at,revision=1,command}=descriptor;
  if(!batchKinds.has(kind)||typeof actor!=='string'||!actor||!Number.isFinite(Date.parse(at))||!Number.isSafeInteger(revision)||revision<1||!command)throw Error('批次写入回执无效');
  receipt={schemaVersion:1,operationId,kind,actor,at,revision,command:journalKey(command)};
 }else if(receipt.schemaVersion!==1||receipt.operationId!==operationId||!domains.has(receipt.kind)&&!batchKinds.has(receipt.kind)||descriptor.command&&receipt.command!==journalKey(descriptor.command))throw Error('操作ID已用于不同写入');
 const children=descriptor.childOperationIds||[];
 if(!Array.isArray(children)||children.length>500||new Set(children).size!==children.length||children.some(id=>typeof id!=='string'||!id||id.length>500))throw Error('批次子操作无效');
 const records=[{receipt,file},...children.map(id=>{const file=join(root,commandReceiptPath(id)),receipt=JSON.parse(readFileSync(file,'utf8'));if(receipt.schemaVersion!==1||receipt.operationId!==id||!domains.has(receipt.kind))throw Error('子操作回执无效');return {receipt,file};})];
 const archive=await buildAuditLedger(root),reader=createAuditReader(ref=>readFileSync(join(root,ref.path),'utf8'));
 for(const {receipt} of records)if(domains.has(receipt.kind))await verifyDomainReceipt(reader,archive.pointer.root,receipt);
 // A confirmed duplicate never rewrites its earlier receipt or archive proof.
 for(const record of records)if(!record.receipt.auditRoot){record.receipt={...record.receipt,auditRoot:archive.pointer.root,...(batchKinds.has(record.receipt.kind)?{resultSources:sourceHashes(root,record.receipt.kind)}:{})};mkdirSync(dirname(record.file),{recursive:true});writeFileSync(record.file,JSON.stringify(record.receipt,null,2)+'\n');}
 receipt=records[0].receipt;
 await buildAuditLedger(root,{check:true});
 return {receipt,path,archive:archive.pointer};
}
export async function verifyCatalogueWrite(root){
 const archive=await buildAuditLedger(root,{check:true}),reader=createAuditReader(ref=>readFileSync(join(root,ref.path),'utf8')),generations=new Set();
 let ref=archive.pointer.root;while(ref){if(generations.has(ref.sha256))throw Error('归档代次循环');generations.add(ref.sha256);ref=(await reader.read(ref)).previous;}
 const directory=join(root,'data/command-receipts');
 for(const name of existsSync(directory)?readdirSync(directory):[]){
  const receipt=JSON.parse(readFileSync(join(directory,name),'utf8'));
  if(!receipt.auditRoot)continue; // Explicit pre-protocol receipts remain untouched.
  if(receipt.schemaVersion!==1||!domains.has(receipt.kind)&&!batchKinds.has(receipt.kind)||commandReceiptPath(receipt.operationId)!=='data/command-receipts/'+name||!generations.has(receipt.auditRoot.sha256))throw Error('写入回执引用不属于当前归档代次链');
  await reader.read(receipt.auditRoot);
  if(domains.has(receipt.kind))await verifyDomainReceipt(reader,receipt.auditRoot,receipt);
  else if(!receipt.resultSources||Object.entries(receipt.resultSources).some(([path,sha])=>!outputs[receipt.kind].includes(path)||!/^[a-f0-9]{40}$/.test(sha)))throw Error('批次结果来源摘要无效');
 }
 return archive;
}
