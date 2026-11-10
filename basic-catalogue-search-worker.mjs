import {createBasicWebIndex,searchHomeSlots,slotPage,compareBasicOrder} from './basic-catalogue-index.mjs?v=20261110-flex-tags';
import {projectEntries} from './basic-catalogue-model.mjs?v=20261110-version-groups';
import {basicFilterRows,matchingBasicPositions} from './basic-catalogue-filters.mjs?v=20261110-version-groups';
import {compileCombinedSearch,needsAdvancedIndex} from './basic-combined-search.mjs?v=20261110-flex-tags';

const index=createBasicWebIndex();
let homeRows,homeQuery,homeSlots,baseRows,basicGeneration,filteredRows;
async function homePage({query,page,size,revision}){
 homeRows??=index.homeSearch(revision).catch(error=>{homeRows=null;throw error;});
 const list=await homeRows;
 if(homeQuery!==query){
  homeSlots=searchHomeSlots(list,query);
  homeQuery=query;
 }
 return slotPage(homeSlots.length,page,size,homeSlots);
}
async function basicPositions({revision,store,generation,filters,groups=[]}){
 if(basicGeneration!==generation){
  baseRows??=index.basicRows(revision).catch(error=>{baseRows=null;throw error;});
  const all=projectEntries(await baseRows,store,{includeChildren:true});
  const children=new Map();
  for(const row of all)if(row.parentId){
   if(!children.has(row.parentId))children.set(row.parentId,[]);
   children.get(row.parentId).push(row);
  }
  filteredRows=basicFilterRows(all.filter(row=>!row.parentId).sort(compareBasicOrder),children);
  basicGeneration=generation;
 }
 const rows=filteredRows;
 const advanced=needsAdvancedIndex(groups)?await index.advancedRows(revision):null;
 return Uint32Array.from(matchingBasicPositions(rows,filters,groups.length?compileCombinedSearch(groups):null,advanced));
}
self.onmessage=async({data})=>{
 const {id,kind}=data;
 try{
  const result=await (kind==='home'?homePage(data):basicPositions(data));
  self.postMessage({id,result},result instanceof Uint32Array?[result.buffer]:[]);
 }catch(error){self.postMessage({id,error:error.message});}
};
