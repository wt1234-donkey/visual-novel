// Stable, shared event identity. Names never stand in for work identities.
export const AUDIT_PATH='data/audit-ledger/manifest.json';
export const AUDIT_SOURCES={basic:'data/basic-catalogue-edits.json',formal:'data/work-edit-history.json',identity:'data/source-identity-decisions.json',field:'data/field-evidence.json'};
export const auditEvents=(kind,store)=>kind==='basic'||kind==='formal'?store.journal?.events||[]:store.events||[];
export const auditOrder=(kind,event)=>kind==='formal'?event.sequence:event.revision;
export function auditWorkIds(kind,event){
 const ids=new Set();const add=id=>{if(typeof id==='string'&&id)ids.add(id);};
 if(kind==='basic')for(const row of [...event.changes,...event.added,...event.removed])add(row.id);
 else if(kind==='formal')add(event.workId);
 else if(kind==='field')for(const change of event.changes){
  if(change.table==='assertions')add((change.after||change.before)?.scope.workId);
  else add(JSON.parse(change.id)[1]);
 }else{
  for(const link of event.intent?.links||[]){add(link.workId);add(link.sourceId);}
  for(const change of event.changes||[]){if(change.table==='links')add(change.id);add(change.before?.workId);add(change.after?.workId);}
 }
 return [...ids].sort();
}
export function replaceAuditEvents(kind,input,events){
 const store=structuredClone(input);
 if(kind==='basic'||kind==='formal'){if(store.journal)store.journal.events=events;else if(events.length)throw Error('日志缺少检查点');}
 else store.events=events;
 return store;
}
