export const compareBasicOrder=(a,b)=>{
 const ay=Number.isInteger(a.year)?a.year:Infinity;
 const by=Number.isInteger(b.year)?b.year:Infinity;
 return ay-by||nameOrder.compare(a.title,b.title)||nameOrder.compare(a.id||'',b.id||'');
};
const nameOrder=new Intl.Collator('zh-Hans-CN',{numeric:true,sensitivity:'base'});
export const normalizeBasicQuery=text=>String(text??'').trim().normalize('NFKC').toLowerCase();
