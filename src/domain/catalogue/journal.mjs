const clone = value => structuredClone(value);
const own = (object, key) => Object.hasOwn(object, key);
const safeId = id => typeof id === 'string' && id.length > 0 && !['__proto__','constructor','prototype'].includes(id);
const normalize = value => Array.isArray(value) ? value.map(normalize) : value && typeof value === 'object' ?
 Object.fromEntries(Object.keys(value).sort().filter(key => value[key] !== undefined).map(key => [key, normalize(value[key])])) : value;
export const journalKey = value => JSON.stringify(normalize(value));
const same = (left, right) => journalKey(left) === journalKey(right);
export const catalogueState = store => clone({schemaVersion:1,revision:store.revision,additions:store.additions,records:store.records,recent:store.recent});

// State and its logical journal share one atomic file until a multi-file
// repository transaction is introduced. The checkpoint marks exact coverage.
export function withJournal(store) {
 if (store.schemaVersion === 2 || store.schemaVersion === 3) return clone(store);
 return {...clone(store),schemaVersion:2,journal:{schemaVersion:1,baseline:catalogueState(store),events:[]}};
}

export function appendJournal(before, after, meta, commandType, intent) {
 if (![2,3].includes(before.schemaVersion)) return after;
 const regular = commandType !== 'undo', entry = regular ? after.recent.at(-1) : before.recent.at(-1);
 const changes = regular ? entry.changes : entry.changes.map(change => ({id:change.id,before:clone(change.after),after:clone(change.before)}));
 const ids = new Set(entry.added);
 const event = {
  schemaVersion:1,id:meta.id,at:meta.at,actor:meta.actor,reason:meta.reason,
  previousRevision:before.revision,revision:after.revision,commandType,intent:clone(intent),
  changes:clone(changes),added:regular?after.additions.filter(work=>ids.has(work.id)).map(clone):[],
  removed:regular?[]:before.additions.filter(work=>ids.has(work.id)).map(clone),
  ...(regular?{}:{undoOf:entry.id})
 };
 if(before.schemaVersion===3){
  after.transaction=after.transaction||{baseline:catalogueState(before),events:[]};
  after.transaction.events.push(event);
 }else after.journal.events.push(event);
 return after;
}

export function replayJournal(journal, validateState = () => {}) {
 if (!journal || journal.schemaVersion !== 1 || journal.baseline?.schemaVersion !== 1 ||
  !Array.isArray(journal.events) || own(journal.baseline,'journal')) throw Error('基础库变更日志格式无效');
 const state = clone(journal.baseline), seen = new Set();
 validateState(state);
 for (const event of journal.events) {
  if (!event || event.schemaVersion !== 1 || !safeId(event.id) || seen.has(event.id) ||
   typeof event.actor !== 'string' || !event.actor.trim() || typeof event.reason !== 'string' || !event.reason.trim() ||
   typeof event.at !== 'string' || !Number.isFinite(Date.parse(event.at)) ||
   !Number.isSafeInteger(event.revision) || event.previousRevision !== state.revision || event.revision !== state.revision+1 ||
   !['edit','style-update','add','merge','delete','detach','undo'].includes(event.commandType) ||
   !event.intent || typeof event.intent !== 'object' || Array.isArray(event.intent) ||
   !Array.isArray(event.changes) || !Array.isArray(event.added) || !Array.isArray(event.removed)) throw Error('基础库变更日志不连续或操作身份无效');
  seen.add(event.id);
  const touched = new Set();
  for (const change of event.changes) {
   if (!change || !safeId(change.id) || touched.has(change.id) || !own(change,'before') || !own(change,'after') ||
    !same(own(state.records,change.id)?state.records[change.id]:null,change.before)) throw Error('变更日志的修改前值不匹配');
   touched.add(change.id);
   if (change.after === null) delete state.records[change.id];
   else Object.defineProperty(state.records,change.id,{value:clone(change.after),enumerable:true,writable:true,configurable:true});
  }
  const removed = new Set();
  for (const work of event.removed) {
   if (!work || removed.has(work.id) || !same(state.additions.find(row=>row.id===work.id),work)) throw Error('变更日志的移除作品不匹配');
   removed.add(work.id);
  }
  state.additions = state.additions.filter(work=>!removed.has(work.id));
  for (const work of event.added) {
   if (!work || state.additions.some(row=>row.id===work.id)) throw Error('变更日志重复新增作品');
   state.additions.push(clone(work));
  }
  if (event.commandType === 'undo') {
   const last = state.recent.pop();
   if (!last || last.id !== event.undoOf || event.intent.type !== 'undo' || event.intent.targetId !== event.undoOf ||
    event.added.length || !same(event.changes,last.changes.map(change=>({id:change.id,before:change.after,after:change.before}))) ||
    !same([...removed].sort(),[...last.added].sort())) throw Error('变更日志撤销目标不匹配');
  } else {
   if (event.removed.length || event.intent.type !== event.commandType) throw Error('变更日志的操作类型不匹配');
   state.recent.push({id:event.id,at:event.at,actor:event.actor,reason:event.reason,changes:clone(event.changes),added:event.added.map(work=>work.id)});
   state.recent = state.recent.slice(-3);
  }
  state.revision = event.revision;
  validateState(state);
 }
 return state;
}

export function validateJournal(store, validateState) {
 const replayed = replayJournal(store.journal, validateState);
 if (!same(replayed,catalogueState(store))) throw Error('基础库快照与变更日志不一致');
 return replayed;
}

export function journalHistory(store, {before = Infinity, limit = 20, workId = null} = {}) {
 if(store.schemaVersion===3)throw Error('分片历史须由仓储按需读取');
 if (!Number.isSafeInteger(limit) || limit < 1 || limit > 100) throw Error('每页历史须为1至100条');
 const events = (store.journal?.events || []).filter(event=>event.revision < before && (!workId ||
  event.changes.some(change=>change.id===workId) || [...event.added,...event.removed].some(work=>work.id===workId)));
 const page = events.slice(-limit).reverse();
 return {events:clone(page),nextBefore:events.length>limit?page.at(-1).revision:null,
  baselineRevision:store.journal?.baseline.revision ?? store.revision,total:events.length};
}
