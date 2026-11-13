import {readFileSync,writeFileSync,mkdirSync,readdirSync,existsSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {gzipSync} from 'node:zlib';
import {loadCatalogueSnapshot} from '../src/infrastructure/filesystem/catalogue-snapshot.mjs';
import {FIELD_DEFINITIONS,scopeKey,choiceBase,evidenceCsv,fieldCounts} from '../src/domain/catalogue/field-evidence.mjs';
import {journalKey} from '../src/domain/catalogue/journal.mjs';
export function verifyFieldReceipts(root,store){
 const dir=join(root,'data/command-receipts'),found=new Map();
 if(existsSync(dir))for(const name of readdirSync(dir).filter(n=>n.endsWith('.json'))){const r=JSON.parse(readFileSync(join(dir,name),'utf8'));if(r.kind!=='field')continue;const c=JSON.parse(r.command),e=store.events.find(e=>e.id===r.operationId);
  if(!e||name!==createHash('sha256').update(r.operationId).digest('hex')+'.json'||r.revision!==e.revision||c.kind!=='field'||c.operationId!==e.id||c.actor!==e.actor||c.at!==e.at||c.expectedRevision!==e.previousRevision||c.reason.trim()!==e.reason||journalKey(c.action)!==journalKey(e.intent)||journalKey(c.sources)!==journalKey(e.sources))throw Error('字段证据回执与审计事件不一致');found.set(e.id,r);}
 if(store.events.some(e=>!found.has(e.id)))throw Error('字段证据事件缺少原命令回执；禁止删除历史或只修改当前快照');
 return found.size;
}
const bucket=id=>createHash('sha256').update(id).digest()[0]%64;
export const evidenceStats=fieldCounts;
export function buildFieldEvidenceDirectory(output,revision,{snapshot,sourceLease},effective,save){
 const {context,store}=snapshot.fieldCatalogue,groups=new Map();
 for(const [key,row] of context.targets){const [type,workId,id]=JSON.parse(key),scope={type,workId,id};if(!groups.has(workId))groups.set(workId,[]);groups.get(workId).push({scope,values:Object.fromEntries(Object.keys(FIELD_DEFINITIONS[type]).map(f=>[f,f==='title'?row.displayTitle||row.title||id:f==='firstYear'?row.firstYear??row.year??null:row[f]??(f.endsWith('Names')?[]:'')])),source:row.source||''});}
 function overlay(id,row){const canonical=context.aliases[id]||id,target=groups.get(canonical)?.find(t=>t.scope.type==='work');if(!target)return;const base=choiceBase(row);for(const f of Object.keys(FIELD_DEFINITIONS.work)){const value=f==='title'?base.displayTitle||base.title:f==='firstYear'?(base._key?base.year:base.firstYear??base.year):base[f];if(value!==undefined)target.values[f]=value;}if(base.source)target.source=base.source;}
 for(const row of snapshot.all)overlay(row._key,row);
 for(const w of [...effective.supplement.works,...effective.main.works,...effective.coverage.companies.flatMap(c=>[...(c.relatedGames||[]),...(c.dossierOnlyWorks||[])])])overlay(w.id,w);
 const parts=Array.from({length:64},()=>({}));for(const [id,targets] of groups)parts[bucket(id)][id]=targets;
 const lookups=parts.map((part,n)=>save('field-targets-'+n,part));
 return Promise.all(lookups).then(refs=>save('field-evidence-directory',{schemaVersion:1,revision,sourceLease,stats:evidenceStats(store),aliases:context.aliases,fields:FIELD_DEFINITIONS,lookups:refs,
  subjects:{entity:[...context.subjects.entity.values()].map(({id,name,type})=>({id,name,type})),person:[...context.subjects.person.values()].map(({id,name,alias})=>({id,name,alias,type:'person'}))}}));
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const root=fileURLToPath(new URL('../',import.meta.url)),{snapshot}=loadCatalogueSnapshot(root);
 verifyFieldReceipts(root,snapshot.fieldCatalogue.store);
 if(process.argv.includes('--export'))writeFileSync(join(root,'data/field-evidence.csv'),evidenceCsv(snapshot.fieldCatalogue.store));
 console.log(JSON.stringify(evidenceStats(snapshot.fieldCatalogue.store)));
}
