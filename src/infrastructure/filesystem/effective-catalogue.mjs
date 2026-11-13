import {readFieldStore} from './field-evidence.mjs';
import {fieldProjection} from '../../domain/catalogue/field-evidence.mjs';
import {existsSync,readFileSync} from 'node:fs';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {buildEffectiveCatalogue} from '../../domain/catalogue/effective.mjs';
import {readBasicStoreSync} from './basic-store.mjs';
import {REGISTRY_PATH} from './registry.mjs';
import {readJsonFileSync} from './registry.mjs';
import {readIdentityStore} from './source-identities.mjs';

export const SOURCE_FILES=[REGISTRY_PATH,'data/adv-rpg-minimal-index-20261031.json','data/adv-rpg-next-studio-review-20261031.json','data/adv-rpg-round3-review-20261031.json','data/games.json','data/non-rpg-creator-supplement-20261030.json','data/work-edit-history.json','data/company-coverage.json','data/taxonomy.json','data/date-contract.json',
 'src/domain/catalogue/model.mjs','src/domain/catalogue/effective.mjs','src/domain/catalogue/dates.mjs','src/domain/catalogue/journal.mjs','src/domain/catalogue/journal-index.mjs','src/domain/catalogue/identity.mjs','src/domain/catalogue/order.mjs','src/domain/taxonomy/style-tags.mjs','src/application/catalogue/commands.mjs','work-edit-model.mjs','management-model.mjs',
 'data/field-evidence.json','data/entities.json','data/creator-credits.json','src/domain/catalogue/field-evidence.mjs','data/trusted-save-policy.json','data/source-identity-decisions.json','src/domain/catalogue/source-identities.mjs','src/domain/catalogue/formal-journal.mjs','src/application/catalogue/formal-commands.mjs',
 'src/application/commands/envelope.mjs','src/application/commands/execute.mjs','src/application/commands/policy.mjs'];
export function sourceLeaseSync(root){
 const files={};
 const header=JSON.parse(readFileSync(join(root,REGISTRY_PATH),'utf8'));
 const paths=[...SOURCE_FILES,...(header.storage?.shards||[]).map(ref=>'data/'+ref.path)];
 for(const path of paths){
  if(!existsSync(join(root,path)))continue;
  const raw=readFileSync(join(root,path));files[path]=createHash('sha1').update('blob '+raw.length+'\0').update(raw).digest('hex');
 }
 return {schemaVersion:1,files};
}
export function loadEffectiveInputsSync(root){
 const read=(name,fallback)=>existsSync(join(root,'data',name))?JSON.parse(readFileSync(join(root,'data',name),'utf8')):fallback;
 const registry=read('main-adv-rpg-works-20261031.json',{works:[]});
 const formalLinks={...(registry.storage?.formalLinks||Object.fromEntries((registry.works||[]).filter(w=>w.linkedRecordId).map(w=>[w.id,w.linkedRecordId])))};
 const main=read('games.json',{works:[]}),supplement=read('non-rpg-creator-supplement-20261030.json',{works:[]}),coverage=read('company-coverage.json',{companies:[]});
 const known=[...main.works,...supplement.works,...coverage.companies.flatMap(c=>[...(c.relatedGames||[]),...(c.dossierOnlyWorks||[])])],ids=new Set(known.map(w=>w.id)),identityStore=readIdentityStore(root);
 const profilesByCanonical=new Map(known.map(w=>[w.id,w.id]));
 if(known.some(w=>w.basicRegistryId)){
  const logical=registry.works?registry:readJsonFileSync(join(root,REGISTRY_PATH)),byIndex=new Map(logical.works.map(w=>[w.indexId,w]));
  for(const work of known)if(work.basicRegistryId&&byIndex.has(work.basicRegistryId)){
   const source=byIndex.get(work.basicRegistryId),decision=identityStore.links[source.id],canonical=decision?.status==='confirmed'?decision.workId:source.linkedRecordId||source.id;
   profilesByCanonical.set(canonical,work.id);if(!decision)formalLinks[source.id]=work.id;
  }
 }
 for(const [sourceId,decision] of Object.entries(identityStore.links))if(decision.status==='confirmed'&&profilesByCanonical.has(decision.workId))formalLinks[sourceId]=profilesByCanonical.get(decision.workId);
 const aliases=Object.fromEntries([...profilesByCanonical].filter(([id,profile])=>id!==profile).map(([id,profile])=>[profile,id]));
 for(const [sourceId,target] of Object.entries(formalLinks)){const canonical=identityStore.links[sourceId]?.workId||aliases[target]||target;if(sourceId!==canonical)aliases[sourceId]=canonical;}
 for(const [sourceId,link] of Object.entries(identityStore.links))if(sourceId!==link.workId)aliases[sourceId]=link.workId;
 const fieldEvidence=fieldProjection(readFieldStore(root),aliases);
 return {main,supplement,coverage,identityStore,fieldEvidence,history:read('work-edit-history.json',{records:{}}),
  basicStore:existsSync(join(root,'data/basic-catalogue-edits.json'))?readBasicStoreSync(root):{records:{}},formalLinks};
}
export const loadEffectiveCatalogueSync=root=>buildEffectiveCatalogue(loadEffectiveInputsSync(root));
