// Read the live GitHub version so browser refreshes see direct edits before Pages finishes deploying.
// A cached published snapshot is only a fallback; authenticated saves still check the live SHA.
export async function readLatestBasicStore(readLive,readPublished){
 try{return {store:await readLive(),source:'github'};}
 catch(liveError){
  try{return {store:await readPublished(),source:'pages'};}
  catch(publishedError){throw Error('基础库最新数据和站点副本均不可读取：'+publishedError.message);}
 }
}
