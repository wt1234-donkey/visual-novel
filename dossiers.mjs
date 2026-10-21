// Static dossiers remain usable without JavaScript; filters only hide existing cards.
const kindButtons=document.querySelectorAll('[data-dossier-kind]');
for(const button of kindButtons)button.addEventListener('click',()=>{
  const kind=button.dataset.dossierKind;let total=0;
  for(const item of document.querySelectorAll('.dossier-item')){item.hidden=!!kind&&item.dataset.kind!==kind;if(!item.hidden)total++;}
  for(const period of document.querySelectorAll('.dossier-periods>.dossier-period')){
    const visible=[...period.querySelectorAll('.dossier-item')].filter(x=>!x.hidden).length;period.hidden=!visible;
    const count=period.querySelector('h4>span');if(count)count.textContent=`${visible}个专题`;
  }
  for(const b of kindButtons)b.setAttribute('aria-pressed',String(b===button));
  document.getElementById('dossier-filter-count').textContent=`${total}个专题`;
});
const controls=[...document.querySelectorAll('[data-dossier-filter]')];
function filterDossier(){
  const filters=Object.fromEntries(controls.map(c=>[c.dataset.dossierFilter,c.value]));let count=0;
  for(const wrapper of document.querySelectorAll('.dossier-card-wrapper')){
    wrapper.hidden=!!(filters.placement&&wrapper.dataset.placement!==filters.placement||filters.relation&&wrapper.dataset.relation!==filters.relation||filters.mode&&!wrapper.dataset.modes.split('|').includes(filters.mode));
    if(!wrapper.hidden)count++;
  }
  for(const group of document.querySelectorAll('[data-participation-group]')){
    const visible=[...group.querySelectorAll('.dossier-card-wrapper')].filter(w=>!w.hidden).length;group.hidden=!visible;
    group.querySelector('.group-count').textContent=`${visible}部`;
  }
  const result=document.getElementById('dossier-result-count');if(result)result.textContent=`显示${count}部作品 · 同一作品在本专题只计一次`;
}
for(const control of controls)control.addEventListener('change',filterDossier);
if(controls.length)filterDossier();
