import {applyChange, undoLast, projectEntries, valuesOf, reconcileBasicEdit, validateStore} from '../../domain/catalogue/model.mjs';
import {createCatalogueView} from './view.mjs';

const same = (a, b) => JSON.stringify(a ?? null) === JSON.stringify(b ?? null);
const conflict = message => Object.assign(Error(message + '；当前表单内容已保留，请同步后核对。'), {code:'CATALOGUE_CONFLICT'});
const relation = row => row && {parentId:row.parentId, relation:row.relation, deleted:row._deleted};

// Commands know catalogue rules. Repositories provide read/write and know only
// how to persist bytes. No DOM, credentials, GitHub URLs or network globals here.
export function rebaseBasicCommand(base, opened, latest, action, undo = false) {
 if (same(opened, latest)) return action;
 if (undo) throw conflict('基础库已变化，撤销须基于最新记录');
 const before = new Map(projectEntries(base, opened, {includeChildren:true}).map(row => [row._key, row]));
 const after = new Map(projectEntries(base, latest, {includeChildren:true}).map(row => [row._key, row]));
 if (action.type === 'edit') {
  const old = before.get(action.id), current = after.get(action.id);
  if (!old || !current || !same(relation(old), relation(current))) throw conflict('目标作品的删除或版本关系已变化');
  return {...action, values:reconcileBasicEdit(valuesOf(old), action.values, valuesOf(current))};
 }
 // Non-destructive additions are revalidated against all latest identities.
 if (action.type === 'add') return action;
 const ids = action.type === 'style-update' ? action.rows.map(row => row.id) : [];
 if (!ids.length) throw conflict('版本合并、删除或解除操作需要重新核对最新目录');
 for (const id of ids) if (!same(before.get(id), after.get(id))) throw conflict('目标基础作品已变化（' + id + '）');
 return action;
}

export async function commitBasicCommand({repository, snapshot, base, action, meta, undo = false}) {
 const opened = structuredClone(validateStore(snapshot.store));
 const original = structuredClone(action), operation = structuredClone(meta);
 // At most one CAS retry, always planned from the original form and baseline.
 // A transport error is verified remotely, never blindly sent twice.
 for (let attempt = 0; attempt < 2; attempt++) {
  const live = await repository.read();
  validateStore(live.store);
  if (!live.sha) throw Error('请先读取最新修改记录后保存');
  const command = rebaseBasicCommand(base, opened, live.store, original, undo);
  const next = undo ? undoLast(live.store, live.store.revision) : applyChange(live.store, base, command, {...operation, expectedRevision:live.store.revision});
  createCatalogueView(base, next, {strict:true});
  let result;
  try {
   result = await repository.write(next, live.sha, 'Basic catalogue: ' + operation.reason.slice(0, 100));
  } catch (error) {
   if (error.code === 'CONFLICT' && attempt === 0) continue;
   if (error.status) throw error;
   try {
    const actual = await repository.read();
    if (!same(actual.store, next)) throw error;
    result = {sha:actual.sha, verifiedAfterError:true};
   } catch { throw error; }
  }
  return {store:next, sha:result.sha, result};
 }
}
