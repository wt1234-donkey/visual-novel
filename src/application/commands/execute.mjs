import {validateCommand,commandText} from './envelope.mjs';
import {applyChange,undoLast} from '../../domain/catalogue/model.mjs';
import {createCatalogueView} from '../catalogue/view.mjs';
import {projectWork,validateHistory} from '../../../work-edit-model.mjs';
import {applyFormalCommand} from '../catalogue/formal-commands.mjs';
import {applyIdentityReview} from '../../domain/catalogue/source-identities.mjs';
const reject=(message,code)=>{throw Object.assign(Error(message),{code});};
export function assertCommandSource(lease,current,kind){
 const required=Object.entries(current.files).filter(([path])=>!(kind==='formal'&&path==='data/work-edit-history.json')&&!(kind==='identity'&&path==='data/source-identity-decisions.json'));
 if(lease?.schemaVersion!==1||!required.length||required.some(([path,sha])=>lease?.files?.[path]!==sha))reject('来源或规则已变化，请保留输入并重新核对','SOURCE_CHANGED');
}
// Context is loaded by the executor from its trusted checkout, never from a browser snapshot.
export function planCommand(command,context,identity){
 validateCommand(command);
 if(!identity||identity!==command.actor)reject('操作人须与已认证派发人一致','ACTOR_MISMATCH');
 const previous=context.receipt;
 if(previous){if(previous.command!==commandText(command))reject('操作ID已经用于不同内容','OPERATION_CONFLICT');return {alreadyApplied:true,receipt:previous};}
 assertCommandSource(command.sourceLease,context.sourceLease,command.kind);
 const meta={id:command.operationId,at:command.at,actor:identity,reason:command.reason,sources:command.sources,expectedRevision:command.expectedRevision};
 let store,revision;
 if(command.kind==='basic'){
  if(command.action.type==='undo'&&context.basicStore.recent.at(-1)?.id!==command.action.targetId)reject('回撤目标已变化','CATALOGUE_CONFLICT');
  store=command.action.type==='undo'?undoLast(context.basicStore,command.expectedRevision,meta):applyChange(context.basicStore,context.basicRows,command.action,meta);
  createCatalogueView(context.basicRows,store,{strict:true});revision=store.revision;
 }else if(command.kind==='identity'){
  store=applyIdentityReview(context.identityStore,context.sourceIdentity,command.action,meta);revision=store.revision;
 }else{
  const base=context.formalWorks.find(work=>work.id===command.action.workId);if(!base)reject('正式作品不存在','TARGET_NOT_FOUND');
  const projected=context.reservedWorks.map(work=>projectWork(work,context.formalStore));
  store=applyFormalCommand(context.formalStore,base,command,context.taxonomy,projected);
  validateHistory(store,context.reservedWorks,context.taxonomy);revision=store.records[base.id].revision;
 }
 return {alreadyApplied:false,store,receipt:{schemaVersion:1,operationId:command.operationId,kind:command.kind,revision,actor:identity,at:command.at,command:commandText(command)}};
}
