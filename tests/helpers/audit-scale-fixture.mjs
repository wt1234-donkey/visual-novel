import {emptyStore,applyChange,valuesOf,validateStore} from '../../basic-catalogue-model.mjs';
import {catalogueState} from '../../src/domain/catalogue/journal.mjs';
import {saveCreatorNames,validateHistory} from '../../work-edit-model.mjs';
import {emptyIdentityStore,buildSourceIdentityCatalogue,applyIdentityReview,validateIdentityStore} from '../../src/domain/catalogue/source-identities.mjs';
import {emptyFieldStore,validateFieldStore} from '../../src/domain/catalogue/field-evidence.mjs';
import {readFileSync} from 'node:fs';
export const scaleMeta=(id,revision)=>({id,actor:'capacity-test',at:'2026-11-14T03:00:00Z',reason:'容量样本核对并保留完整历史',sources:['https://example.org/scale'],expectedRevision:revision});
export function appendBasicScale(store,base,i){
 const before={...catalogueState(store),schemaVersion:2,journal:{schemaVersion:1,baseline:catalogueState(store),events:[]}};
 const next=applyChange(before,base,{type:'edit',id:'hot',values:{...valuesOf(base[0]),group:'Maker '+i}},scaleMeta('scale-'+i,store.revision));
 return {...next,journal:{...store.journal,events:[...store.journal.events,next.journal.events[0]]}};
}
export function basicScale(count){
 const base=[{id:'hot',title:'Hot',year:1980,group:'Maker',gameplay:'ADV'},{id:'cold',title:'Cold',year:1980,group:'Maker',gameplay:'ADV'}],initial=emptyStore();let current=initial;const events=[];
 for(let i=1;i<=count;i++){const before={...catalogueState(current),schemaVersion:2,journal:{schemaVersion:1,baseline:catalogueState(current),events:[]}},target=base[i%200===0?1:0];current=applyChange(before,base,{type:'edit',id:target.id,values:{...valuesOf(target),group:'Maker '+i}},scaleMeta('scale-'+i,current.revision));events.push(current.journal.events[0]);}
 const store={...catalogueState(current),schemaVersion:2,journal:{schemaVersion:1,baseline:initial,events}};validateStore(store);return {store,base};
}
export function formalScale(count){
 const base=JSON.parse(readFileSync(new URL('../../data/games.json',import.meta.url))).works.find(w=>w.id==='g039'),taxonomy=JSON.parse(readFileSync(new URL('../../data/taxonomy.json',import.meta.url)));
 const works=[{...base,id:'hot'},{...base,id:'cold'}],events=[];let current={schemaVersion:1,records:{}},checkpoint;
 for(let i=1;i<=count;i++){const target=works[i%200===0?1:0],before={schemaVersion:1,records:current.records},next=saveCreatorNames(before,target,{writerNames:['Writer '+i],artistNames:[],musicianNames:[]},scaleMeta('formal-'+i,current.records[target.id]?.revision||0),taxonomy,works);checkpoint??=next.journal.checkpoint;const event=next.journal.events[0];event.sequence=i;events.push(event);current=next;}
 const store={schemaVersion:2,records:current.records,journal:{schemaVersion:1,checkpoint,baseline:{schemaVersion:1,records:{}},events}};validateHistory(store,works,taxonomy);return {store,works,taxonomy};
}
export function identityScale(count){
 const registry={works:['hot','cold'].map(id=>({id,title:id,firstYear:1980,source:'https://example.org/'+id})),identityReview:[]},catalogue=buildSourceIdentityCatalogue({registry}),store=emptyIdentityStore();
 const templates=Object.fromEntries(['hot','cold'].map(id=>[id,applyIdentityReview(emptyIdentityStore(),catalogue,{type:'resolve',caseId:'source:'+id,outcome:'link',links:[{sourceId:id,workId:id}]},scaleMeta('template-'+id,0)).events[0]]));
 for(let i=1;i<=count;i++){const id=i%200===0?'cold':'hot',event=structuredClone(templates[id]);Object.assign(event,{id:'identity-'+i,previousRevision:i-1,revision:i});for(const change of event.changes){change.before=structuredClone(store[change.table][change.id]||null);change.after.operationId=event.id;store[change.table][change.id]=structuredClone(change.after);}store.events.push(event);store.revision=i;}
 validateIdentityStore(store);return {store,registry};
}
export function fieldScale(count){
 const store=emptyFieldStore();
 for(const id of ['hot','cold']){const assertion={id:'claim-'+id,scope:{type:'work',workId:id,id},field:'firstYear',value:1981,sources:['https://example.org/claim'],sourceIds:[],status:'supported',subjects:[]},revision=store.revision+1;store.events.push({schemaVersion:1,id:'assert-'+id,type:'assert',intent:{type:'assert',assertion},...scaleMeta('assert-'+id,store.revision),previousRevision:store.revision,revision,changes:[{table:'assertions',id:assertion.id,before:null,after:assertion}]});delete store.events.at(-1).expectedRevision;store.assertions[assertion.id]=assertion;store.revision=revision;}
 for(let i=3;i<=count;i++){const id=i%200===0?'cold':'hot',key=JSON.stringify(['work',id,id,'firstYear']),meta=scaleMeta('field-'+i,i-1),after={assertionId:'claim-'+id,operationId:meta.id,actor:meta.actor,at:meta.at,reason:meta.reason};const event={schemaVersion:1,id:meta.id,type:'select',intent:{type:'select',assertionId:'claim-'+id},actor:meta.actor,at:meta.at,reason:meta.reason,sources:meta.sources,previousRevision:i-1,revision:i,changes:[{table:'choices',id:key,before:structuredClone(store.choices[key]||null),after}]};store.choices[key]=after;store.events.push(event);store.revision=i;}
 validateFieldStore(store);return {store};
}
