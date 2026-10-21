const query=document.getElementById('directory-search'),kind=document.getElementById('directory-kind');
const items=[...document.querySelectorAll('[data-directory-kind]')];
const norm=v=>v.normalize('NFKC').toLocaleLowerCase().replace(/\s+/g,'');
function render(){let n=0;const q=norm(query.value);for(const item of items){item.hidden=!!(kind.value&&kind.value!==item.dataset.directoryKind||q&&!norm(item.dataset.search).includes(q));if(!item.hidden)n++;}document.getElementById('directory-count').textContent=`显示${n}项`;
}
query.addEventListener('input',render);kind.addEventListener('change',render);
function showHash(){if(location.hash){const item=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(item?.matches('[data-directory-kind]')){query.value='';kind.value='';render();item.scrollIntoView({block:'start'});}}}
render();showHash();window.addEventListener('hashchange',showHash);
