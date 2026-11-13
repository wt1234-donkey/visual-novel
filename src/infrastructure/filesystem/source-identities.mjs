import {existsSync,readFileSync} from 'node:fs';
import {join} from 'node:path';
import {emptyIdentityStore,validateIdentityStore,buildSourceIdentityCatalogue,identityFormalLinks} from '../../domain/catalogue/source-identities.mjs';
export const IDENTITY_PATH='data/source-identity-decisions.json';
export function readIdentityStore(root){return validateIdentityStore(existsSync(join(root,IDENTITY_PATH))?JSON.parse(readFileSync(join(root,IDENTITY_PATH),'utf8')):emptyIdentityStore());}
export function identityCatalogueForSnapshot(inputs,snapshot,coverage){
 const formalWorks=[...new Map([...inputs.supplement.works,...inputs.main.works].map(w=>[w.id,w])).values()];
 const coverageWorks=(coverage.companies||[]).flatMap(c=>[...(c.relatedGames||[]),...(c.dossierOnlyWorks||[])]);
 return buildSourceIdentityCatalogue({registry:inputs.registry,legacyRows:snapshot.all,formalWorks,coverageWorks,decisions:inputs.identityStore||emptyIdentityStore(),
  visible:{basicVisibleGroups:snapshot.entries.length,discoveryBasicGroups:snapshot.home.rows.length}});
}
export {identityFormalLinks};
