import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {buildCatalogueSnapshot} from '../../application/catalogue/snapshot.mjs';

export function loadCatalogueSnapshot(root) {
 const read = name => JSON.parse(readFileSync(join(root, 'data', name), 'utf8'));
 const inputs = {
  registry:read('main-adv-rpg-works-20261031.json'),
  initial:read('adv-rpg-minimal-index-20261031.json').records,
  batches:[['batch2', 'adv-rpg-next-studio-review-20261031.json'], ['batch3', 'adv-rpg-round3-review-20261031.json']].map(([id, file]) => [id, read(file).records]),
  store:read('basic-catalogue-edits.json'), main:read('games.json'),
  supplement:read('non-rpg-creator-supplement-20261030.json'), history:read('work-edit-history.json')
 };
 return {inputs, snapshot:buildCatalogueSnapshot(inputs)};
}
