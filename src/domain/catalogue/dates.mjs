// Keep this small browser contract identical to data/date-contract.json; CI checks parity.
export const DATE_CONTRACT={schemaVersion:1,minimumYear:1900,maximumYear:2200,unknownValue:null,statuses:['unknown','unverified','published','planned'],formalAdmission:'published'};
export const isRecordedYear=year=>year===null||Number.isInteger(year)&&year>=DATE_CONTRACT.minimumYear&&year<=DATE_CONTRACT.maximumYear;
export const isPublishedYear=(year,currentYear=new Date().getFullYear())=>year!==null&&isRecordedYear(year)&&year<=currentYear;
export function recordedDate(year,status=year===null?'unknown':'unverified'){
 if(!isRecordedYear(year)||!DATE_CONTRACT.statuses.includes(status)||status==='unknown'&&year!==null||status!=='unknown'&&year===null||status==='published'&&!isPublishedYear(year))throw Error('年份或日期状态无效');
 return {year,status};
}
