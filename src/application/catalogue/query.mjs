import {basicFilterRows, matchingBasicPositions} from './filters.mjs';
import {compileCombinedSearch} from './search.mjs';
import {createCatalogueView} from './view.mjs';

export function createCatalogueQuery(base, store) {
 const view = createCatalogueView(base, store);
 return {...view, filterRows:basicFilterRows(view.entries, view.childrenByMain)};
}

export function queryCatalogueRows(rows, filters, groups = [], advanced = null) {
 return matchingBasicPositions(rows, filters, groups.length ? compileCombinedSearch(groups) : null, advanced);
}
