import {createBasicWebIndex,searchHomeSlots,slotPage,compareBasicOrder} from './basic-catalogue-index.mjs';
import {projectEntries} from './basic-catalogue-model.mjs';
import {basicFilterRows,matchingBasicPositions} from './basic-catalogue-filters.mjs';

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
async function basicPositions({revision,store,generation,filters}){
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
 return Uint32Array.from(matchingBasicPositions(filteredRows,filters));
}
self.onmessage=async({data})=>{
 const {id,kind}=data;
 try{
  const result=await (kind==='home'?homePage(data):basicPositions(data));
  self.postMessage({id,result},result instanceof Uint32Array?[result.buffer]:[]);
 }catch(error){self.postMessage({id,error:error.message});}
};
