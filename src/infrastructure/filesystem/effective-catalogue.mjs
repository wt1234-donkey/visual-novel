import {existsSync,readFileSync} from 'node:fs';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {buildEffectiveCatalogue} from '../../domain/catalogue/effective.mjs';
import {readBasicStoreSync} from './basic-store.mjs';
import {REGISTRY_PATH} from './registry.mjs';

export const SOURCE_FILES=[REGISTRY_PATH,'data/adv-rpg-minimal-index-20261031.json','data/adv-rpg-next-studio-review-20261031.json','data/adv-rpg-round3-review-20261031.json','data/games.json','data/non-rpg-creator-supplement-20261030.json','data/work-edit-history.json','data/company-coverage.json','data/taxonomy.json','data/date-contract.json',
 'src/domain/catalogue/model.mjs','src/domain/catalogue/effective.mjs','src/domain/catalogue/dates.mjs','src/domain/catalogue/journal.mjs','src/domain/catalogue/journal-index.mjs','src/domain/catalogue/identity.mjs','src/domain/catalogue/order.mjs','src/domain/taxonomy/style-tags.mjs','src/application/catalogue/commands.mjs','work-edit-model.mjs','management-model.mjs'];
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
 const formalLinks=registry.storage?.formalLinks||Object.fromEntries((registry.works||[]).filter(w=>w.linkedRecordId).map(w=>[w.id,w.linkedRecordId]));
 return {main:read('games.json',{works:[]}),supplement:read('non-rpg-creator-supplement-20261030.json',{works:[]}),
  coverage:read('company-coverage.json',{companies:[]}),history:read('work-edit-history.json',{records:{}}),
  basicStore:existsSync(join(root,'data/basic-catalogue-edits.json'))?readBasicStoreSync(root):{records:{}},formalLinks};
}
export const loadEffectiveCatalogueSync=root=>buildEffectiveCatalogue(loadEffectiveInputsSync(root));
