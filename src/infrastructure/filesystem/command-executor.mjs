import {readFileSync,existsSync,mkdirSync,writeFileSync} from 'node:fs';
import {join,dirname} from 'node:path';
import {createHash} from 'node:crypto';
import {loadCatalogueSnapshot} from './catalogue-snapshot.mjs';
import {readBasicStoreSync,saveBasicStoreSync} from './basic-store.mjs';
import {planCommand} from '../../application/commands/execute.mjs';
export const receiptPath=operationId=>'data/command-receipts/'+createHash('sha256').update(operationId).digest('hex')+'.json';
export function executeCommand(root,command,identity){
 const path=receiptPath(command.operationId),receiptFile=join(root,path);
 const receipt=existsSync(receiptFile)?JSON.parse(readFileSync(receiptFile,'utf8')):null;
 // Duplicates are confirmed before checking today's source/revision; later edits are retained.
 let context={receipt};
 if(!receipt){
  const {snapshot,inputs,sourceLease}=loadCatalogueSnapshot(root),coverage=JSON.parse(readFileSync(join(root,'data/company-coverage.json'),'utf8'));
  const formalWorks=[...new Map([...inputs.supplement.works,...inputs.main.works].map(work=>[work.id,work])).values()];
  context={sourceLease,basicRows:snapshot.sourceRows,basicStore:inputs.store,formalStore:inputs.history,formalWorks,
   reservedWorks:[...formalWorks,...coverage.companies.flatMap(company=>[...(company.relatedGames||[]),...(company.dossierOnlyWorks||[])])],taxonomy:JSON.parse(readFileSync(join(root,'data/taxonomy.json'),'utf8'))};
 }
 const result=planCommand(command,context,identity);
 if(result.alreadyApplied)return {...result,paths:[path]};
 if(command.kind==='basic')saveBasicStoreSync(root,result.store);
 else writeFileSync(join(root,'data/work-edit-history.json'),JSON.stringify(result.store,null,2)+'\n');
 mkdirSync(dirname(receiptFile),{recursive:true});writeFileSync(receiptFile,JSON.stringify(result.receipt,null,2)+'\n');
 if(command.kind==='basic')readBasicStoreSync(root);
 return {...result,paths:command.kind==='basic'?['data/basic-catalogue-edits.json','data/basic-catalogue-journal',path]:['data/work-edit-history.json',path]};
}
