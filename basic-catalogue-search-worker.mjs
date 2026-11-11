import {createBasicWebIndex,searchHomeSlots,slotPage} from './basic-catalogue-index.mjs?v=20261111-architecture';
import {createCatalogueQuery,queryCatalogueRows} from './src/application/catalogue/query.mjs';
import {needsAdvancedIndex} from './basic-combined-search.mjs?v=20261111-architecture';

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
  filteredRows=createCatalogueQuery(await baseRows,store).filterRows;
  basicGeneration=generation;
 }
 const rows=filteredRows;
 const advanced=needsAdvancedIndex(groups)?await index.advancedRows(revision):null;
 return Uint32Array.from(queryCatalogueRows(rows,filters,groups,advanced));
}
self.onmessage=async({data})=>{
 const {id,kind}=data;
 try{
  const result=await (kind==='home'?homePage(data):basicPositions(data));
  self.postMessage({id,result},result instanceof Uint32Array?[result.buffer]:[]);
 }catch(error){self.postMessage({id,error:error.message});}
};
