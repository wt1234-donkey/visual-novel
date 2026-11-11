import {createEditClient} from './contents-repository.mjs';
import {validateStore} from '../../domain/catalogue/model.mjs';
export {TOKEN_SETUP_URL} from './contents-repository.mjs';

export function createBasicRepository(token = '', fetcher = fetch) {
 return createEditClient(token, fetcher, {historyPath:'data/basic-catalogue-edits.json', validate:validateStore});
}
