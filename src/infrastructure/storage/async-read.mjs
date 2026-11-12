// Bound both connection and response-body waits. The race also handles a broken
// adapter that ignores AbortSignal; late responses can never complete the caller.
export function withDeadline(task,{signal,timeout=8000}={}){
 if(signal?.aborted)return Promise.reject(signal.reason||new DOMException('读取已取消','AbortError'));
 const controller=new AbortController();let timer,onAbort;
 const stopped=new Promise((_,reject)=>{
  const stop=error=>{controller.abort(error);reject(error);};
  onAbort=()=>stop(signal.reason||new DOMException('读取已取消','AbortError'));
  signal?.addEventListener('abort',onAbort,{once:true});
  timer=setTimeout(()=>stop(new DOMException('读取超时，请重试','TimeoutError')),timeout);
 });
 return Promise.race([Promise.resolve().then(()=>task(controller.signal)),stopped]).finally(()=>{clearTimeout(timer);signal?.removeEventListener('abort',onAbort);});
}
export const interrupted=error=>['AbortError','TimeoutError'].includes(error?.name);
export function requestScope(){let current,serial=0;return {start(){current?.abort();const controller=new AbortController();current=controller;const id=++serial;return {signal:controller.signal,current:()=>id===serial&&!controller.signal.aborted};},cancel(){serial++;current?.abort();}};}
