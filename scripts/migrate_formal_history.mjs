import {readFileSync,writeFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {resolve,join} from 'node:path';
import {upgradeFormalHistory,formalState} from '../src/domain/catalogue/formal-journal.mjs';
import {journalKey} from '../src/domain/catalogue/journal.mjs';
import {validateHistory} from '../work-edit-model.mjs';

export function verifyFormalHistory(root){
 const read=path=>JSON.parse(readFileSync(join(root,path),'utf8'));
 const store=read('data/work-edit-history.json'),coverage=read('data/company-coverage.json');
 const works=[...new Map([...read('data/non-rpg-creator-supplement-20261030.json').works,...read('data/games.json').works,
  ...coverage.companies.flatMap(c=>[...(c.relatedGames||[]),...(c.dossierOnlyWorks||[])])].map(w=>[w.id,w])).values()];
 validateHistory(store,works,read('data/taxonomy.json'));
 if(store.schemaVersion!==2)throw Error('正式审计尚未迁移至完整日志格式');
 const expected=read('config/formal-audit-checkpoint.json');
 const digest=createHash('sha256').update(journalKey(store.journal.baseline)).digest('hex');
 if(expected.baselineSha256!==digest||expected.sourceCommit!==store.journal.checkpoint.sourceCommit||expected.at!==store.journal.checkpoint.at)
  throw Error('正式审计迁移检查点已变化');
 return {works:Object.keys(store.records).length,events:store.journal.events.length,checkpoint:expected};
}

if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const root=fileURLToPath(new URL('../',import.meta.url)),path=join(root,'data/work-edit-history.json');
 if(process.argv.includes('--apply')){
  const old=JSON.parse(readFileSync(path,'utf8'));
  if(old.schemaVersion===1){
   const sourceCommit=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),at=new Date().toISOString();
   validateHistory(old,[...JSON.parse(readFileSync(join(root,'data/games.json'))).works,...JSON.parse(readFileSync(join(root,'data/non-rpg-creator-supplement-20261030.json'))).works],JSON.parse(readFileSync(join(root,'data/taxonomy.json'))));
   const next=upgradeFormalHistory(old,{at,sourceCommit});
   if(journalKey(formalState(next))!==journalKey(old))throw Error('迁移改变了现行状态');
   writeFileSync(join(root,'config/formal-audit-checkpoint.json'),JSON.stringify({schemaVersion:1,sourceCommit,at,
    baselineSha256:createHash('sha256').update(journalKey(old)).digest('hex'),legacyHistory:'Retained as checkpoint evidence; older edits remain in Git history.'},null,2)+'\n');
   writeFileSync(path,JSON.stringify(next,null,2)+'\n');
  }
 }
 console.log(JSON.stringify(verifyFormalHistory(root)));
}
