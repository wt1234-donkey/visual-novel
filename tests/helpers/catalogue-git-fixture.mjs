import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {emptyStore,upgradeStore} from '../../basic-catalogue-model.mjs';
import {catalogueState,journalKey} from '../../src/domain/catalogue/journal.mjs';
import {planCatalogueFiles,finishCatalogueFiles,jsonText} from '../../src/infrastructure/storage/catalogue-files.mjs';
import {gitBlobHash} from '../../src/infrastructure/filesystem/basic-store.mjs';

export const STORE='data/basic-catalogue-edits.json';
export const stateHash=store=>createHash('sha256').update(journalKey(catalogueState(store))).digest('hex');
export function split(store,active=null){
 const plan=planCatalogueFiles(store,active),hashes=new Map(plan.files.map(file=>[file.path,gitBlobHash(file.content)]));
 return {...plan,store:finishCatalogueFiles(plan,hashes,stateHash(store))};
}

export function gitFixture(initial=upgradeStore(emptyStore())){
 const blobs=new Map(),trees=new Map(),commits=new Map(),calls=[];
 let serial=0,head,failAt=null,intercept=null;
 const sha=value=>createHash('sha1').update(JSON.stringify(value)).digest('hex');
 const putBlob=text=>{const id=gitBlobHash(text);blobs.set(id,text);return id;};
 const putTree=tree=>{const id=sha([...tree].sort());trees.set(id,new Map(tree));return id;};
 const commit=(tree,parents=[])=>{const id=sha({tree,parents,serial:++serial});commits.set(id,{tree:{sha:tree},parents});return id;};
 const currentTree=()=>trees.get(commits.get(head).tree.sha);
 const seed=split(initial),map=new Map(seed.files.map(file=>[file.path,putBlob(file.content)]));
 map.set(STORE,putBlob(jsonText(seed.store)));map.set('unrelated.txt',putBlob('original'));
 head=commit(putTree(map));
 const response=(data,status=200)=>({ok:status>=200&&status<300,status,headers:{get:()=>null},json:async()=>data,text:async()=>typeof data==='string'?data:JSON.stringify(data)});
 const store=()=>JSON.parse(blobs.get(currentTree().get(STORE)));
 const api={calls,blobs,
  get head(){return head;},get store(){return store();},
  lease(paths){return {schemaVersion:1,files:Object.fromEntries(paths.map(path=>[path,currentTree().get(path)]))};},
  file(path){return blobs.get(currentTree().get(path));},
  paths(){return [...currentTree().keys()].sort();},
  fail(stage){failAt=stage;},
  onRef(callback){intercept=callback;},
  changeFile(path,text){const next=new Map(currentTree());next.set(path,putBlob(text));head=commit(putTree(next),[head]);},
  publish(next){
   const last=next.journal.shards.at(-1),active=last?JSON.parse(blobs.get(last.sha)):null;
   const plan=split(next,active),tree=new Map(currentTree());
   for(const file of [...plan.files,{path:STORE,content:jsonText(plan.store)}])tree.set(file.path,putBlob(file.content));
   for(const path of plan.remove)tree.delete(path);
   head=commit(putTree(tree),[head]);return store();
  },
  async fetch(url,options={}){
   const method=options.method||'GET',body=options.body?JSON.parse(options.body):undefined;
   const parsed=new URL(url,'https://local.test/'),path=parsed.pathname.replace('/repos/wt1234-donkey/visual-novel','');
   calls.push({method,path,body});
   if(method==='GET'&&path==='/user')return response({login:'tester'});
   if(method==='GET'&&path==='')return response({permissions:{push:true}});
   if(method==='GET'&&path==='/git/ref/heads/main')return response({object:{sha:head,type:'commit'}});
   if(method==='GET'&&path.startsWith('/contents/')){
    const ref=parsed.searchParams.get('ref'),file=path.slice('/contents/'.length),tree=trees.get(commits.get(ref)?.tree.sha),id=tree?.get(file);
    return id?response({sha:id,content:Buffer.from(blobs.get(id)).toString('base64')}):response({message:'Not found'},404);
   }
   if(method==='GET'&&path.startsWith('/git/blobs/')){
    const id=path.split('/').at(-1),text=blobs.get(id);
    return text!==undefined?response({sha:id,content:Buffer.from(text).toString('base64')}):response({message:'Not found'},404);
   }
   if(method==='GET'&&path.startsWith('/git/commits/'))return response(commits.get(path.split('/').at(-1)));
   if(method==='GET'&&path.startsWith('/git/trees/')){const tree=trees.get(path.split('/').at(-1));return response({truncated:false,tree:[...tree].map(([path,sha])=>({path,sha,type:'blob'}))});}
   const stage=path==='/git/blobs'?'blob':path==='/git/trees'?'tree':path==='/git/commits'?'commit':method==='PATCH'?'ref':null;
   if(stage&&stage===failAt)return response({message:'Injected transaction failure'},500);
   if(method==='POST'&&path==='/git/blobs')return response({sha:putBlob(body.content)},201);
   if(method==='POST'&&path==='/git/trees'){
    assert.ok(trees.has(body.base_tree));const tree=new Map(trees.get(body.base_tree));
    for(const entry of body.tree){if(entry.sha===null){assert.ok(tree.has(entry.path));tree.delete(entry.path);}else{assert.ok(blobs.has(entry.sha));tree.set(entry.path,entry.sha);}}
    return response({sha:putTree(tree)},201);
   }
   if(method==='POST'&&path==='/git/commits')return response({sha:commit(body.tree,body.parents)},201);
   if(method==='PATCH'&&path==='/git/refs/heads/main'){
    assert.equal(body.force,false);
    if(intercept){const callback=intercept;intercept=null;await callback(api);}
    if(commits.get(body.sha).parents[0]!==head)return response({message:'Update is not a fast forward'},422);
    head=body.sha;return response({object:{sha:head}});
   }
   throw Error('Unexpected request '+method+' '+url);
  }
 };
 return api;
}
