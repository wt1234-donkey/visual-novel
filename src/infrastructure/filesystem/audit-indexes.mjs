import {createHash} from 'node:crypto';
import {journalKey} from '../../domain/catalogue/journal.mjs';
const hash = id => createHash('sha256').update(id).digest('hex');
const size = value => Buffer.byteLength(JSON.stringify(value)+'\n');
const compare = ([a],[b]) => a < b ? -1 : a > b ? 1 : 0;

// Append only the right edge. Already referenced leaves and event locations
// remain immutable, including an unfilled event segment from an earlier save.
export async function appendAuditRange(ref, entries, reader, writer, limits) {
 const leaf = rows => ({...writer.put({schemaVersion:1,type:'range-leaf',entries:rows}),min:rows[0].order,max:rows.at(-1).order,count:rows.length});
 const branch = children => ({...writer.put({schemaVersion:1,type:'range-branch',children}),min:children[0].min,max:children.at(-1).max,count:children.reduce((n,r)=>n+r.count,0)});
 const chunks = (rows, fn) => Array.from({length:Math.ceil(rows.length/limits.indexEntries)},(_,i)=>fn(rows.slice(i*limits.indexEntries,(i+1)*limits.indexEntries)));
 async function append(pointer, rows) {
  const node = await reader.read(pointer);
  if (node.type === 'range-leaf') {
   if (node.entries.length === limits.indexEntries) return [pointer,...chunks(rows,leaf)];
   return chunks([...node.entries,...rows],leaf);
  }
  if (node.type !== 'range-branch' || !node.children.length) throw Error('审计分页索引格式无效');
  const tail = await append(node.children.at(-1),rows);
  return chunks([...node.children.slice(0,-1),...tail],branch);
 }
 if (!entries.length) return ref;
 let level = ref ? await append(ref,entries) : chunks(entries,leaf);
 while (level.length > 1) level = chunks(level,branch);
 return level[0];
}

// Copy only branches reached by changed keys; group a batch before writing so
// transient, unreachable index versions are never persisted per individual row.
export async function setAuditMap(ref, updates, reader, writer, limits, depth=0) {
 if (!updates.length) return ref;
 const node = ref ? await reader.read(ref) : {type:'map',entries:{}};
 if (node.type === 'map') {
  const entries = Object.fromEntries([...new Map([...Object.entries(node.entries),...updates])].sort(compare));
  const value = {schemaVersion:1,type:'map',entries};
  if (Object.keys(entries).length <= limits.indexEntries && size(value) <= limits.indexBytes) return writer.put(value);
  if(depth>=64)throw Error('审计索引键碰撞超出容量');
  const buckets=new Map(),children={};
  for(const row of Object.entries(entries)){const key=hash(row[0]).slice(depth,depth+2);if(!buckets.has(key))buckets.set(key,[]);buckets.get(key).push(row);}
  for(const [key,rows] of buckets)children[key]=await setAuditMap(null,rows,reader,writer,limits,depth+2);
  return writer.put({schemaVersion:1,type:'branch',depth,children:Object.fromEntries(Object.entries(children).sort(compare))});
 }
 if (node.type !== 'branch' || node.depth !== depth) throw Error('审计索引层级无效');
 const children = {...node.children}, buckets = new Map();
 for (const row of updates) {const key=hash(row[0]).slice(depth,depth+2);if(!buckets.has(key))buckets.set(key,[]);buckets.get(key).push(row);}
 for (const [key,rows] of buckets) children[key]=await setAuditMap(children[key]||null,rows,reader,writer,limits,depth+2);
 return writer.put({schemaVersion:1,type:'branch',depth,children:Object.fromEntries(Object.entries(children).sort(compare))});
}

export async function auditMapEntries(reader,pointer,prefix='') {
  const node=await reader.read(pointer);
  if(node.type==='map') {
   const rows=Object.entries(node.entries);
   if(rows.some(([id])=>!hash(id).startsWith(prefix)))throw Error('审计索引键位置不一致');
   return rows;
  }
  if(node.type!=='branch'||node.depth!==prefix.length||prefix.length>=64)throw Error('审计索引层级无效');
  const result=[];
  for(const [key,ref] of Object.entries(node.children)) {
   if(!/^[a-f0-9]{2}$/.test(key))throw Error('审计索引桶无效');
   result.push(...await auditMapEntries(reader,ref,prefix+key));
  }
  return result;
}
export async function verifyAuditIndexes(reader, descriptor, postings) {
 const expected=new Map(postings.map(({workIds,...p})=>[p.id,p]));
 const operations=await auditMapEntries(reader,descriptor.operations);
 if(expected.size!==postings.length||operations.length!==expected.size||operations.some(([id,p])=>journalKey(p)!==journalKey(expected.get(id))))throw Error('归档操作索引与事件全集不一致');
 const byWork=new Map();
 for(const posting of postings)for(const id of posting.workIds){if(!byWork.has(id))byWork.set(id,[]);const {workIds,...row}=posting;byWork.get(id).push(row);}
 const works=await auditMapEntries(reader,descriptor.works);
 if(works.length!==byWork.size)throw Error('归档作品索引与事件全集不一致');
 for(const [id,target] of works) {
  const rows=await reader.postings(target.root,{limit:Number.MAX_SAFE_INTEGER}), wanted=byWork.get(id);
  if(!wanted||target.count!==wanted.length||journalKey(rows)!==journalKey(wanted))throw Error('归档作品索引与事件全集不一致');
 }
}
