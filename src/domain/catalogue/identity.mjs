// Existing IDs remain stable throughout the incremental migration. A source ID
// is an alias only when an explicit registry mapping exists; names are not IDs.
export const workKey = work => work.matchedWorkId || work.registryId || work.id;
export const nameKey = value => String(value || '').normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');

export function buildIdentityMap(rows) {
 const sourceToWork = new Map(), sourcesByWork = new Map();
 for (const row of rows) {
  const id = workKey(row);
  if (typeof id !== 'string' || !id) throw Error('作品缺少稳定身份');
  if (!sourcesByWork.has(id)) sourcesByWork.set(id, new Set());
  for (const sourceId of [row.id, row.indexId, row.registryId, row.matchedWorkId, ...(row.sourceRecordIds || [])].filter(Boolean)) {
   const previous = sourceToWork.get(sourceId);
   if (previous && previous !== id) throw Error('来源身份映射冲突：' + sourceId);
   sourceToWork.set(sourceId, id);
   sourcesByWork.get(id).add(sourceId);
  }
 }
 return {sourceToWork, sourcesByWork};
}
