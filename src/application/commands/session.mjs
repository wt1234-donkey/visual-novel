import {journalKey} from '../../domain/catalogue/journal.mjs';
import {validateCommand} from './envelope.mjs';
const copy=value=>structuredClone(value);
const defaultStorage=()=>{try{return globalThis.sessionStorage||null;}catch{return null;}};
const signatureOf=command=>journalKey({actor:command.actor,action:command.action,reason:command.reason,sources:command.sources});
const validatePending=(command,kind)=>{
 if(command.kind!==kind)throw Error('命令类型与当前会话不匹配');
 validateCommand({...command,sourceLease:command.sourceLease||{schemaVersion:1,files:{}}});
};
export function createCommandSession({kind,storage=defaultStorage()}={}){
 const PENDING_KEY='catalogue-'+kind+'-pending-v1';
 const pending=new Map();let active=false;
 try{for(const command of JSON.parse(storage?.getItem(PENDING_KEY)||'[]')){validatePending(command,kind);pending.set(signatureOf(command),copy(command));}}catch{pending.clear();}
 const persist=()=>{try{if(pending.size)storage?.setItem(PENDING_KEY,JSON.stringify([...pending.values()]));else storage?.removeItem(PENDING_KEY);}catch{/* The same in-memory operation remains available if storage is unavailable. */}};
 return {
  pending(workId){return [...pending.values()].filter(command=>workId===undefined||command.action.workId===workId).map(copy);},
  async execute(command,executor){
   if(active)throw Error('上一次操作尚未结束');
   validatePending(command,kind);const signature=signatureOf(command);
   if(!pending.has(signature))pending.set(signature,copy(command));
   persist();active=true;
   try{const result=await executor(copy(pending.get(signature)));pending.delete(signature);persist();return result;}
   catch(error){
    // These pre-write conflicts are definite. Ambiguous transport failures keep
    // their command for subsequent clicks, reconnects and explicit retries.
    if(error.formalWriteNotAttempted||error.commandNotApplied){pending.delete(signature);persist();}
    throw error;
   }finally{active=false;}
  }
 };
}

