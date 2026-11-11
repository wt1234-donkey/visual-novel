import {applyChange, undoLast, projectEntries, valuesOf, reconcileBasicEdit, validateStore, upgradeStore} from '../../domain/catalogue/model.mjs';
import {journalKey} from '../../domain/catalogue/journal.mjs';
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
 const intent = undo ? {type:'undo',targetId:opened.recent.at(-1)?.id} : original;
 const applied = async snapshot => {
  const store=snapshot.store;
  if(store.schemaVersion===3&&typeof repository.findOperation!=='function')throw Error('事务仓储不支持操作核验');
  const event=store.schemaVersion===3?await repository.findOperation(snapshot,operation.id):store.journal?.events.find(event=>event.id===operation.id);
  if(!event)return false;
  if(event.actor!==operation.actor||event.reason!==operation.reason||journalKey(event.intent)!==journalKey(intent))throw conflict('操作ID已用于其他修改');
  return true;
 };
 // At most one CAS retry, always planned from the original form and baseline.
 // A transport error is verified remotely, never blindly sent twice.
 for (let attempt = 0; attempt < 2; attempt++) {
  const live = await repository.read();
  validateStore(live.store);
  if (!live.sha) throw Error('请先读取最新修改记录后保存');
  if(await applied(live))return {...live,result:{sha:live.sha,commit:live.head,alreadyApplied:true}};
  const command = rebaseBasicCommand(base, opened, live.store, original, undo);
  const current=upgradeStore(live.store), metadata={...operation,intent,expectedRevision:current.revision};
  const next = undo ? undoLast(current, current.revision, metadata) : applyChange(current, base, command, metadata);
  createCatalogueView(base, next, {strict:true});
  let result;
  try {
   result = await repository.write(next, live.sha, 'Basic catalogue: ' + operation.reason.slice(0, 100));
  } catch (error) {
   if (error.code === 'CONFLICT' && attempt === 0) continue;
   if (error.status && error.status < 500) throw error;
   try {
    const actual = await repository.read();
    validateStore(actual.store);
    if (!await applied(actual)) throw error;
    result = {sha:actual.sha,commit:actual.head,verifiedAfterError:true};
    return {...actual,result};
   } catch { throw error; }
  }
  const {store:written,...receipt}=result;
  return {store:written||next, sha:receipt.sha, result:receipt};
 }
}
