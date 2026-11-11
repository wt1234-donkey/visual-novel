import {catalogueState,journalKey} from '../../domain/catalogue/journal.mjs';
import {utf8Bytes} from './catalogue-files.mjs';

const hex=bytes=>Array.from(new Uint8Array(bytes),byte=>byte.toString(16).padStart(2,'0')).join('');
export const digestText=async(text,algorithm='SHA-256')=>hex(await crypto.subtle.digest(algorithm,utf8Bytes(text)));
export const blobDigest=async text=>digestText('blob '+utf8Bytes(text).length+'\0'+text,'SHA-1');
export const stateDigest=async store=>digestText(journalKey(catalogueState(store)));
export async function verifySnapshot(store){
 if(store.schemaVersion===3&&(store.transaction||await stateDigest(store)!==store.journal.stateHash))throw Error('基础库快照摘要校验失败');
 return store;
}
