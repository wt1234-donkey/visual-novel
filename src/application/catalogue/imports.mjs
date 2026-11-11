import {validateValues} from '../../domain/catalogue/model.mjs';
import {STYLE_KEYS,STYLE_DIMENSIONS,styleName,styleValue,validateStyleTags} from '../../domain/taxonomy/style-tags.mjs';

export const LEGACY_CSV_HEADERS=['名称','年份','厂商','主要玩法','剧情风格1','剧情风格2','剧情风格3','来源'];
const dimensionHeaders=STYLE_KEYS.map(key=>STYLE_DIMENSIONS[key].label);
const legacyDimensionHeaders=dimensionHeaders.slice(0,6);
export const CSV_HEADERS=['名称','年份','厂商','主要玩法',...dimensionHeaders,'来源'];
const SIX_DIMENSION_CSV_HEADERS=['名称','年份','厂商','主要玩法',...legacyDimensionHeaders,'来源'];
export const STYLE_UPDATE_HEADERS=['作品ID','作品名称',...dimensionHeaders];
const SIX_DIMENSION_UPDATE_HEADERS=['作品ID','作品名称',...legacyDimensionHeaders];
function dimensionValues(cells,{allowClear=false}={}){
 const tags=Object.fromEntries(cells.flatMap((cell,i)=>{
  const text=cell.trim();
  if(!text)return [];
  const list=text.split(/[、|；;]+/).map(styleName).filter(Boolean);
  return [[STYLE_KEYS[i],allowClear&&text==='清空'?null:styleValue(list)]];
 }));
 return validateStyleTags(tags,{allowClear});
}
export function parseStyleUpdates(text){
 const [header,...rows]=parseCSV(text);
 if(![STYLE_UPDATE_HEADERS,SIX_DIMENSION_UPDATE_HEADERS].some(valid=>JSON.stringify(header)===JSON.stringify(valid)))
  throw Error('CSV表头须与标签更新模板一致');
 if(!rows.length||rows.length>500)throw Error('每次更新1至500部作品');
 return rows.map((row,i)=>{
  try{
   if(row.length!==header.length)throw Error('列数须为'+header.length);
   const tags=dimensionValues(row.slice(2),{allowClear:true});
   return {id:row[0].trim(),title:row[1].trim(),mode:'set',tags};
  }catch(error){throw Error('第'+(i+2)+'行：'+error.message);}
 });
}

export function parseCSV(text){
 const rows=[];let row=[],value='',quoted=false;const t=text.replace(/^\uFEFF/,'');
 for(let i=0;i<t.length;i++){const c=t[i];if(c==='"'){if(quoted&&t[i+1]==='"'){value+='"';i++;}else if(quoted)quoted=false;else if(!value)quoted=true;else throw Error('CSV引号格式无效');}else if(!quoted&&(c===','||c==='\n'||c==='\r')){row.push(value);value='';if(c!==','){if(c==='\r'&&t[i+1]==='\n')i++;rows.push(row);row=[];}}else value+=c;}
 if(quoted)throw Error('CSV引号未闭合');if(value||row.length){row.push(value);rows.push(row);}return rows.filter(r=>r.some(v=>v.trim()));
}
export function parseImport(text,format){
 let input;if(format==='json'){input=JSON.parse(text);if(!Array.isArray(input))throw Error('JSON须为作品数组');}
 else{
  const [header,...rows]=parseCSV(text);
  const legacy=JSON.stringify(header)===JSON.stringify(LEGACY_CSV_HEADERS);
  if(!legacy&&![CSV_HEADERS,SIX_DIMENSION_CSV_HEADERS].some(valid=>JSON.stringify(header)===JSON.stringify(valid)))throw Error('CSV表头须与下载模板完全一致');
  input=rows.map((r,i)=>{
   if(r.length!==header.length)throw Error('第'+(i+2)+'行列数须为'+header.length);
   return {title:r[0].trim(),firstYear:r[1].trim()?Number(r[1]):null,group:r[2].trim(),gameplay:r[3].trim(),
    ...(legacy?{plotStyles:[...new Set(r.slice(4,7).map(s=>s.trim()).filter(Boolean))]}:{plotStyles:[],plotTags:dimensionValues(r.slice(4,-1))}),source:r.at(-1).trim()};
  });
 }
 if(!input.length||input.length>500)throw Error('每次导入1至500部作品');return input.map((w,i)=>{try{return validateValues(w);}catch(e){throw Error('第'+(i+1)+'部：'+e.message);}});
}
