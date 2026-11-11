import {pathToFileURL} from 'node:url';
import {readBasicStoreSync,saveBasicStoreSync} from '../src/infrastructure/filesystem/basic-store.mjs';
import {journalSummary} from '../src/domain/catalogue/journal-index.mjs';

export function migrateBasicStorage(root,{write=false,check=false}={}){
 let store=readBasicStoreSync(root);const changed=store.schemaVersion!==3;
 if(check&&changed)throw Error('基础库尚未迁移至分片存储');
 if(write&&changed)store=saveBasicStoreSync(root,store,{migrate:true});
 return {schemaVersion:store.schemaVersion,revision:store.revision,...journalSummary(store),shards:store.journal?.shards?.length??0,changed:write&&changed};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)
 console.log(JSON.stringify(migrateBasicStorage(process.cwd(),{write:process.argv.includes('--write'),check:process.argv.includes('--check')})));
