import {createPublishedAuditAccess,assertSmallLegacyHistory} from '../infrastructure/storage/audit-access.mjs';
import {formalHistoryPage} from '../domain/catalogue/formal-journal.mjs';
import {fieldHistory} from '../domain/catalogue/field-evidence.mjs';
import {identityHistory} from '../domain/catalogue/source-identities.mjs';
const published=createPublishedAuditAccess();
export async function auditHistory(kind,store,options={},access=null){
 const indexed=access?await access():await published.open(kind,{store});
 if(indexed){const page=await indexed.history(options);
  if(kind==='formal'){const baseline=store.projectionVersion?store.baselineRecords:store.journal?.baseline.records||store.records;page.baselineRevision=baseline?.[options.workId]?.revision||0;page.legacyRecent=structuredClone(baseline?.[options.workId]?.recent||[]);}
  return page;
 }
 assertSmallLegacyHistory(kind,store);
 return ({formal:formalHistoryPage,field:fieldHistory,identity:identityHistory})[kind](store,options);
}
