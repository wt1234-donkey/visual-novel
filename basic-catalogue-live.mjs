// Read the live GitHub version so browser refreshes see direct edits before Pages finishes deploying.
// A cached published snapshot is only a fallback; authenticated saves still check the live SHA.
export async function readLatestBasicStore(readLive,readPublished){
 const snapshot=value=>value?.store?value:{store:value};
 try{return {...snapshot(await readLive()),source:'github'};}
 catch(liveError){
  try{return {...snapshot(await readPublished()),source:'pages'};}
  catch(publishedError){throw Error('基础库最新数据和站点副本均不可读取：'+publishedError.message);}
 }
}
