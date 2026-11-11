import {buildEffectiveCatalogue} from '../../domain/catalogue/effective.mjs';

// Display projection only. Draft comparisons and update packages retain their
// original source objects in `data` / `working`.
export function buildManagementView(working, inputs) {
 const effective=buildEffectiveCatalogue({...inputs,main:working.games,supplement:working.supplement,coverage:working.coverage});
 return {...effective,byId:new Map([...effective.supplement.works,...effective.main.works].map(work=>[work.id,work]))};
}
