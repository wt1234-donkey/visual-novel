import {journalKey} from '../../domain/catalogue/journal.mjs';
import {formalOperation,confirmFormalOperation} from '../../domain/catalogue/formal-journal.mjs';
import {saveEdit,saveCreatorNames,undoEdit} from '../../../work-edit-model.mjs';
import {createCommandSession} from '../commands/session.mjs';

const copy=value=>structuredClone(value);
export function formalCommandMeta(command){
 return {id:command.operationId,at:command.at,actor:command.actor,expectedRevision:command.expectedRevision,
  reason:command.action.type==='creators'?'添加或调整剧作、美术与音乐':command.reason,
  sources:command.action.type==='creators'?[]:command.sources};
}
const intentOf=command=>{const {workId,...intent}=command.action;return intent;};
export function applyFormalCommand(store,base,command,taxonomy,works){
 const meta=formalCommandMeta(command),action=command.action;
 return action.type==='undo'?undoEdit(store,base,action.targetId,command.expectedRevision,taxonomy,works,meta):
  action.type==='creators'?saveCreatorNames(store,base,action.names,meta,taxonomy,works):saveEdit(store,base,action.values,meta,taxonomy,works);
}

// Failed responses retain the exact ID, timestamp, revision and source lease.
// A retry is confirmation of that command, not a new edit against today's state.
export const createFormalCommandSession=options=>createCommandSession({kind:'formal',...options});

export async function commitFormalCommand({repository,opened,command,base,taxonomy,works,validate=()=>{}}){
 if(repository.commandMode==='trusted')return repository.executeCommand(command);
 const confirm=live=>{
  const meta=formalCommandMeta(command),event=formalOperation(live.store,command.operationId);
  if(!event)return null;
  confirmFormalOperation(live.store,base.id,meta,command.action.type,intentOf(command));
  return {...live,operationId:event.id,kind:'formal',actor:event.actor,at:event.at,workId:base.id,revision:event.revision,commit:live.head,alreadyApplied:true};
 };
 // Receipt lookup deliberately precedes the current source/revision guard.
 const actual=await repository.read({verifySource:false}),previous=confirm(actual);if(previous)return previous;
 let live,next;
 try{
  live=await repository.read();await validate(live);
  if(journalKey(live.store.records[base.id]||null)!==journalKey(opened.store.records[base.id]||null))
   throw Object.assign(Error('此作品已在其他页面修改，请重新读取并核对；当前输入保留'),{code:'CATALOGUE_CONFLICT'});
  next=applyFormalCommand(live.store,base,command,taxonomy,works);
 }catch(error){error.formalWriteNotAttempted=true;throw error;}
 try{
  const result=await repository.write(next,live.sha,'Formal '+command.action.type+' '+base.id+': '+command.reason);
  return {...result,store:next,operationId:command.operationId,kind:'formal',actor:command.actor,at:command.at,workId:base.id,revision:next.records[base.id].revision};
 }catch(error){
  try{const found=confirm(await repository.read({verifySource:false}));if(found)return {...found,verifiedAfterError:true};}catch(reconciliation){if(reconciliation.code==='OPERATION_CONFLICT')throw reconciliation;}
  throw error;
 }
}
