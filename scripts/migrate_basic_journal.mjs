import {readFileSync,writeFileSync,renameSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {validateStore,upgradeStore} from '../src/domain/catalogue/model.mjs';

export function migrateBasicJournal(root,{write=false,check=false}={}){
 const file=join(root,'data','basic-catalogue-edits.json'),store=validateStore(JSON.parse(readFileSync(file,'utf8')));
 if(check&&store.schemaVersion!==2)throw Error('基础库尚未迁移至变更日志格式');
 const next=upgradeStore(store);
 if(write&&store.schemaVersion!==2){
  const temp=file+'.journal-tmp';writeFileSync(temp,JSON.stringify(next,null,2)+'\n');renameSync(temp,file);
 }
 return {schemaVersion:next.schemaVersion,revision:next.revision,baselineRevision:next.journal.baseline.revision,
  events:next.journal.events.length,records:Object.keys(next.records).length,changed:store.schemaVersion!==2&&write};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)
 console.log(JSON.stringify(migrateBasicJournal(process.cwd(),{write:process.argv.includes('--write'),check:process.argv.includes('--check')})));
