import {readFileSync,existsSync} from 'node:fs';
import {join} from 'node:path';
import {emptyFieldStore,validateFieldStore,validateFieldReferences,fieldProjection,scopeKey} from '../../domain/catalogue/field-evidence.mjs';
export const FIELD_PATH='data/field-evidence.json';
export const readFieldStore=root=>validateFieldStore(existsSync(join(root,FIELD_PATH))?JSON.parse(readFileSync(join(root,FIELD_PATH),'utf8')):emptyFieldStore());
export function createFieldContext({identity,main,supplement={works:[]},coverage={companies:[]},entities=[],people=[],basicRows=[]}){
 const works=new Map(identity.works),sources=identity.sources,aliases={};
 for(const w of works.values())for(const id of w.profileIds||[])if(id!==w.id)aliases[id]=w.id;
 for(const l of identity.links.values())if(l.sourceId!==l.workId)aliases[l.sourceId]=l.workId;
 const targets=new Map();
 for(const w of works.values())targets.set(scopeKey({type:'work',workId:w.id,id:w.id}),w);
 const visit=data=>{for(const w of data.works||[]){const canonical=aliases[w.id]||w.id;targets.set(scopeKey({type:'work',workId:canonical,id:canonical}),w);for(const type of ['content','release'])for(const r of w[type==='content'?'contentVersions':'platformReleases']||[])add(type,r,canonical);}
  for(const type of ['content','release'])for(const r of data[type==='content'?'contentVersions':'platformReleases']||[])add(type,r,aliases[r.workId]||r.workId);};
 const add=(type,r,workId)=>targets.set(scopeKey({type,workId,id:r.id}),r);
 visit(supplement);visit(main);for(const c of coverage.companies||[])visit({works:[...(c.relatedGames||[]),...(c.dossierOnlyWorks||[])]});
 for(const w of basicRows){const canonical=aliases[w._key]||w._key;if(!targets.has(scopeKey({type:'work',workId:canonical,id:canonical})))targets.set(scopeKey({type:'work',workId:canonical,id:canonical}),w);}
 return {works,sources,aliases,targets,subjects:{entity:new Map(entities.map(e=>[e.id,e])),person:new Map(people.map(p=>[p.id,p]))},target(scope){const row=targets.get(scopeKey(scope));if(!row)throw Error('字段证据：范围ID不存在或不属于所选作品');return row;}};
}
export function fieldContextForSnapshot(inputs,snapshot,coverage,entities=[],people=[]){return createFieldContext({identity:snapshot.sourceIdentity,main:inputs.main,supplement:inputs.supplement,coverage,entities,people,basicRows:snapshot.all});}
export function loadFieldCatalogue(root,inputs,snapshot,coverage){
 const read=(name,fallback)=>existsSync(join(root,'data',name))?JSON.parse(readFileSync(join(root,'data',name),'utf8')):fallback;
 const store=readFieldStore(root),context=fieldContextForSnapshot(inputs,snapshot,coverage,read('entities.json',{entities:[]}).entities,read('creator-credits.json',{people:[]}).people);
 validateFieldReferences(store,context);return {store,context,projection:fieldProjection(store,context.aliases)};
}
