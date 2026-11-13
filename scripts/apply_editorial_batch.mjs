import {readJsonFileSync} from '../src/infrastructure/filesystem/registry.mjs';
import {readFileSync,writeFileSync, mkdtempSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {execFileSync} from 'node:child_process';
import {isDeepStrictEqual} from 'node:util';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {EDITORIAL_LIMIT,EDITORIAL_BATCH_LIMIT,editorialId,validateProposal} from '../editorial-proposal.mjs';
import {applyChange,undoLast,validateStore} from '../basic-catalogue-model.mjs';
import {saveEdit,undoEdit,projectWork,validateHistory} from '../work-edit-model.mjs';
import {readBasicStoreSync,saveBasicStoreSync} from '../src/infrastructure/filesystem/basic-store.mjs';
import {assembleBasicRows} from './build_basic_web_index.mjs';
import {createHash} from 'node:crypto';
import {validateBasicAction} from '../src/application/commands/envelope.mjs';
import {assertCommandSource} from '../src/application/commands/execute.mjs';
import {sourceLeaseSync} from '../src/infrastructure/filesystem/effective-catalogue.mjs';
import {journalKey} from '../src/domain/catalogue/journal.mjs';

const root=fileURLToPath(new URL('../',import.meta.url));
const read=(dir,file)=>readJsonFileSync(join(dir,'data',file));
const save=(dir,file,data)=>writeFileSync(join(dir,'data',file),JSON.stringify(data,null,2)+'\n');
const fail=message=>{throw Error(message);};
const baseFile='basic-catalogue-edits.json',workFile='work-edit-history.json',ledgerFile='editorial-publications.json';

const baseInputs=['main-adv-rpg-works-20261031.json','adv-rpg-minimal-index-20261031.json',
 'adv-rpg-next-studio-review-20261031.json','adv-rpg-round3-review-20261031.json'];
function catalogueRows(dir){
 const [registry,index,second,third]=baseInputs.map(file=>read(dir,file));
 return assembleBasicRows(registry,index.records,[['batch2',second.records],['batch3',third.records]]);
}

function checkStaleBasicEdit(dir,proposal,action,current,history){
 const {expectedRevision}=proposal.change;
 const suffix=' 请重新核对后送审。提案 '+proposal.id+'（送审版本 '+expectedRevision+'，当前版本 '+current.revision+'）';
 if(expectedRevision>=current.revision||!['edit','style-update'].includes(action.type))
  fail('基础身份库版本已变化，无法自动校验此操作。'+suffix);
 if(!history.has(expectedRevision)){
  const git=args=>execFileSync('git',args,{cwd:dir,encoding:'utf8',stdio:['ignore','pipe','pipe']});
  const file='data/'+baseFile;
  let original;
  // Use the committed baseline even when the proposal supplies a client-side preview.
  try{
   const commits=git(['log','--first-parent','-n','64','--format=%H','HEAD','--',file]).trim().split(/\s+/).filter(Boolean);
   for(const commit of commits){
    const snapshot=JSON.parse(git(['show',commit+':'+file]));
    if(snapshot.revision!==expectedRevision)continue;
    git(['diff','--quiet',commit,'--',...baseInputs.map(name=>'data/'+name)]);
    original=validateStore(snapshot);
    break;
   }
  }catch{/* Missing history or changed source data requires a fresh review. */}
  history.set(expectedRevision,original);
 }
 const original=history.get(expectedRevision);
 if(!original)fail('基础身份库原始版本无法核对，或基础资料已更新。'+suffix);
 const targets=action.type==='edit'?[action.id]:action.rows.map(row=>row.id);
 for(const id of targets){
  if(!isDeepStrictEqual(original.records[id],current.records[id])||
     !isDeepStrictEqual(original.additions.find(w=>w.id===id),current.additions.find(w=>w.id===id)))
   fail('目标基础作品已变化（'+id+'）。'+suffix);
 }
}

function fullWorks(dir){
 const games=read(dir,'games.json').works;
 const supplement=read(dir,'non-rpg-creator-supplement-20261030.json').works;
 const dossiers=read(dir,'company-coverage.json').companies.flatMap(c=>[...(c.relatedGames||[]),...(c.dossierOnlyWorks||[])]);
 const full=[...new Map([...supplement,...games].map(w=>[w.id,w])).values()];
 return {full,reserved:[...full,...dossiers]};
}
function strictBasic(action){
 validateBasicAction(action.type==='undo'?{...action,targetId:action.targetId||'legacy-reviewed-undo'}:action);
 const validKey=id=>typeof id==='string'&&/^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,199}$/.test(id)&&!['constructor','prototype'].includes(id);
 if(action.type==='add'){
  const allowed=new Set(['id','title','firstYear','group','gameplay','plotStyles','plotTags','plotTagEvidence','source']);
  if(!Array.isArray(action.works)||action.works.some(w=>!w||Object.keys(w).some(k=>!allowed.has(k))))fail('新增提案含无效作品字段');
 }
 if(action.type==='merge'&&(!validKey(action.mainId)||!Array.isArray(action.ids)||action.ids.length>500||action.ids.some(id=>!validKey(id))||
   !action.relation||Object.keys(action.relation).some(k=>!['type','label','note','source'].includes(k))))fail('合并提案格式无效');
 if(['edit','delete','detach'].includes(action.type)&&!validKey(action.id))fail('基础作品 ID 无效');
 if(action.type==='style-update'&&(!Array.isArray(action.rows)||action.rows.some(r=>!r||!validKey(r.id))))fail('风格提案格式无效');
 return action;
}
export function applyEditorialBatch(batch,dir=root){
 if(!batch||!editorialId(batch.id)||!Array.isArray(batch.proposals)||
   !batch.proposals.length||batch.proposals.length>EDITORIAL_BATCH_LIMIT)fail('发布批次无效');
 const proposals=batch.proposals.map(validateProposal),ids=proposals.map(p=>p.id);
 if(new Set(ids).size!==ids.length)fail('发布批次含重复提案');
 const ledger=read(dir,ledgerFile);
 const fingerprints=Object.fromEntries(proposals.map(p=>[p.id,createHash('sha256').update(journalKey(p)).digest('hex')]));
 const sameBatch=ledger.batches.find(row=>row.id===batch.id);
 if(sameBatch){
  if(journalKey(sameBatch.proposals)!==journalKey(ids)||journalKey(sameBatch.fingerprints)!==journalKey(fingerprints))fail('批次ID已用于其他内容，或旧批次缺少可核对摘要；已保存资料保留');
  return {already:true,management:false};
 }
 if(ledger.batches.some(row=>row.id===batch.id||row.proposals.some(id=>ids.includes(id))))fail('该提案已经入库，请同步状态');
 const time=new Date().toISOString();
 const policy=(()=>{try{return read(dir,'trusted-save-policy.json').mode;}catch{return 'legacy';}})();
 for(const p of proposals.filter(p=>['basic','work'].includes(p.kind))){
  if(p.change.sourceLease||policy==='trusted')assertCommandSource(p.change.sourceLease,sourceLeaseSync(dir),p.kind==='work'?'formal':'basic');
 }
 const basic=proposals.filter(p=>p.kind==='basic'),formal=proposals.filter(p=>p.kind==='work');
 let basicResult,workResult;
 if(basic.length){
  basicResult=readBasicStoreSync(dir);
  const current=basicResult,revision=current.revision;
  const base=catalogueRows(dir),touched=new Set(),history=new Map();
  for(const p of basic){
   const action=strictBasic(p.change.action);
   if(p.change.expectedRevision!==revision)checkStaleBasicEdit(dir,p,action,current,history);
   if(action.type==='undo'){
    if(basic.length>1)fail('基础库回撤须单独发布');
    basicResult=undoLast(basicResult,revision,{id:p.id,at:time,actor:'编目审核台',reason:p.reason});continue;
   }
   const next=applyChange(basicResult,base,action,{expectedRevision:basicResult.revision,id:p.id,at:time,actor:'编目审核台',reason:p.reason});
   const event=next.recent.at(-1);
   for(const key of [...event.added,...event.changes.map(row=>row.id)]){
    if(touched.has(key))fail('所选提案修改了相同基础作品，请拆分并核对 '+key);
    touched.add(key);
   }
   basicResult=next;
  }
 }
 if(formal.length){
  const taxonomy=read(dir,'taxonomy.json'),{full,reserved}=fullWorks(dir);
  workResult=read(dir,workFile);
  for(const p of formal){
   const c=p.change,base=full.find(w=>w.id===c.workId);
   if(!base)fail('正式作品已变化，请重新读取 '+c.workId);
   const projected=reserved.map(w=>projectWork(w,workResult));
   workResult=c.undo?undoEdit(workResult,base,c.undo,c.expectedRevision,taxonomy,projected,{id:p.id,at:time,actor:'编目审核台',reason:p.reason,sources:p.sources}):
    saveEdit(workResult,base,c.after,{id:p.id,at:time,actor:'编目审核台',expectedRevision:c.expectedRevision,reason:p.reason,sources:p.sources},taxonomy,projected);
  }
  validateHistory(workResult,reserved,taxonomy);
 }
 const management=proposals.filter(p=>p.kind==='management');
 if(management.length){
  const scratch=mkdtempSync(join(tmpdir(),'editorial-batch-'));
  try{
   for(const p of management){
    const file=join(scratch,p.id+'.json');
    writeFileSync(file,JSON.stringify(p.change.package));
    execFileSync('python3',['scripts/manage_catalogue.py',file],{cwd:dir,stdio:'inherit'});
   }
  }finally{rmSync(scratch,{recursive:true,force:true});}
 }
 if(basicResult)saveBasicStoreSync(dir,basicResult);
 if(workResult)save(dir,workFile,workResult);
 ledger.batches.push({id:batch.id,proposals:ids,fingerprints,at:time});
 save(dir,ledgerFile,ledger);
 return {already:false,management:!!management.length};
}

if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 const raw=readFileSync(process.argv[2]);
 if(raw.length>EDITORIAL_LIMIT)fail('发布批次超出 55 KB');
 const result=applyEditorialBatch(JSON.parse(raw));
 console.log(result.already?'该批次已入库，继续核对 Pages 发布。':'编目批次已在工作区通过数据校验。');
 if(process.env.GITHUB_OUTPUT)writeFileSync(process.env.GITHUB_OUTPUT,
  'already='+result.already+'\nmanagement='+result.management+'\n',{flag:'a'});
}
