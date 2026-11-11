import {projectEntries} from '../../domain/catalogue/model.mjs';
import {buildIdentityMap} from '../../domain/catalogue/identity.mjs';
import {compareBasicOrder} from '../../domain/catalogue/order.mjs';

// Shared by editing, the browser, the search worker and build-time snapshots.
// Deleted identities stay available to relationship validation, never to search.
export function createCatalogueView(base, store, {strict = false, includeIdentities = false} = {}) {
 const projected = projectEntries(base, store, {includeChildren:true, includeDeleted:true});
 const known = new Map(projected.map(row => [row._key, row]));
 const all = projected.filter(row => !row._deleted), byId = new Map(all.map(row => [row._key, row]));
 const childrenByMain = new Map(), issues = [];
 for (const row of all) if (row.parentId) {
  const parent = known.get(row.parentId);
  if (!parent || parent._deleted || parent.parentId) {
   issues.push({type:'invalid-parent', id:row._key, parentId:row.parentId});
   continue;
  }
  if (!childrenByMain.has(row.parentId)) childrenByMain.set(row.parentId, []);
  childrenByMain.get(row.parentId).push(row);
 }
 for (const [id] of Object.entries(store.records)) if (!known.has(id)) issues.push({type:'missing-identity', id});
 if (strict && issues.length) throw Error('目录身份关系校验失败：' + JSON.stringify(issues.slice(0, 10)));
 const invalid = new Set(issues.filter(issue => issue.type === 'invalid-parent').map(issue => issue.id));
 // An unresolved parent must not make a source record disappear from browsing.
 const entries = all.filter(row => !row.parentId || invalid.has(row._key)).sort(compareBasicOrder);
 return {entries, all, byId, childrenByMain, issues,
  ...(includeIdentities?{identities:buildIdentityMap([...base,...store.additions,...projected])}:{})};
}
