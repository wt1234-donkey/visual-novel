import {sourceLeaseSync} from './effective-catalogue.mjs';
import {readJsonFileSync} from './registry.mjs';
import {readFileSync,existsSync} from 'node:fs';
import {join} from 'node:path';
import {readBasicStoreSync} from './basic-store.mjs';
import {buildCatalogueSnapshot} from '../../application/catalogue/snapshot.mjs';
import {readIdentityStore,identityCatalogueForSnapshot,identityFormalLinks} from './source-identities.mjs';
import {projectRegistry} from '../../domain/catalogue/model.mjs';

export function loadCatalogueSnapshot(root,{allowMissingLegacy=false}={}) {
 const read = name => allowMissingLegacy&&!existsSync(join(root,'data',name))&&['adv-rpg-minimal-index-20261031.json','adv-rpg-next-studio-review-20261031.json','adv-rpg-round3-review-20261031.json','non-rpg-creator-supplement-20261030.json'].includes(name)?{records:[],works:[]}:readJsonFileSync(join(root, 'data', name));
 const inputs = {
  registry:read('main-adv-rpg-works-20261031.json'),
  initial:read('adv-rpg-minimal-index-20261031.json').records,
  batches:[['batch2', 'adv-rpg-next-studio-review-20261031.json'], ['batch3', 'adv-rpg-round3-review-20261031.json']].map(([id, file]) => [id, read(file).records]),
  store:readBasicStoreSync(root), main:read('games.json'),
  supplement:read('non-rpg-creator-supplement-20261030.json'), history:read('work-edit-history.json')
 };
 inputs.identityStore=readIdentityStore(root);
 const legacy=buildCatalogueSnapshot(inputs),coverage=existsSync(join(root,'data/company-coverage.json'))?read('company-coverage.json'):{companies:[]};
 const sourceIdentity=identityCatalogueForSnapshot(inputs,legacy,coverage);
 sourceIdentity.stats.bulkVisibleGroups=projectRegistry(inputs.registry,inputs.store).works.length;
 sourceIdentity.stats.legacySourceRowCount=legacy.sourceRows.length;
 inputs.identityLinks=identityFormalLinks(sourceIdentity);
 const snapshot=buildCatalogueSnapshot(inputs);
 sourceIdentity.stats.basicVisibleGroups=snapshot.entries.length;
 sourceIdentity.stats.discoveryBasicGroups=snapshot.home.rows.length;
 snapshot.sourceIdentity=sourceIdentity;
 return {inputs, sourceLease:sourceLeaseSync(root), snapshot};
}
