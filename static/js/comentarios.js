/* Comentários do blog.
   - "Ver comentários" busca a lista só quando a pessoa clica.
   - O formulário abre ao clicar; o Turnstile só é carregado quando ela começa a usá-lo.
   - Tudo que vem do servidor é inserido como TEXTO (textContent), nunca como HTML. */
(function(){
var root=document.getElementById('comentarios'); if(!root) return;
var d=root.dataset, base=d.worker.replace(/\/+$/,''), max=parseInt(d.max,10)||1200;
var bList=root.querySelector('[data-act=list]'), bForm=root.querySelector('[data-act=form]');
var list=root.querySelector('.cmt-list'), f=root.querySelector('form.cmt-form'), msg=root.querySelector('.cmt-msg');
var box=f.querySelector('.cmt-ts'), inner=f.querySelector('.cmt-ts-in'), ph=f.querySelector('.cmt-ts-btn');
var send=f.querySelector('button[type=submit]'), ta=f.elements.comment, cnt=f.querySelector('.cmt-n'), cntp=f.querySelector('.cmt-count');
var token='', wid=null, loading=false, ready=false, loaded=false, last='';

function m(k){return d['m'+k.charAt(0).toUpperCase()+k.slice(1)]||''}
function say(k,cls){last=k;msg.textContent=k?m(k):'';msg.className='cmt-msg fine '+(cls||'')}

/* ---- lista ---- */
function fmt(s){try{var p=s.split('-');return new Intl.DateTimeFormat(d.lang,{dateStyle:'long',timeZone:'UTC'}).format(new Date(Date.UTC(+p[0],+p[1]-1,+p[2])))}catch(e){return s||''}}
function head(name,date,badge){
  var h=document.createElement('p'); h.className='cmt-head';
  var w=document.createElement('span'); w.className='cmt-who'; w.textContent=name; h.appendChild(w);
  if(badge){var b=document.createElement('span'); b.className='cmt-badge'; b.textContent=badge; h.appendChild(b)}
  var t=document.createElement('span'); t.className='cmt-date'; t.textContent=fmt(date); h.appendChild(t);
  return h;
}
function render(items){
  list.textContent='';
  if(!items.length){var p=document.createElement('p'); p.className='fine'; p.textContent=m('none'); list.appendChild(p); return}
  var ul=document.createElement('ol'); ul.className='cmt-ul';
  items.forEach(function(c){
    var li=document.createElement('li'); li.className='cmt-item';
    li.appendChild(head(c.n||m('anon'),c.d));
    var p=document.createElement('p'); p.className='cmt-txt'; p.textContent=c.t; li.appendChild(p);
    if(c.r&&c.r.length){
      var rs=document.createElement('ol'); rs.className='cmt-replies';
      c.r.forEach(function(r){
        var ri=document.createElement('li'); ri.className='cmt-reply';
        ri.appendChild(head(d.author,r.d,m('author')));
        var rp=document.createElement('p'); rp.className='cmt-txt'; rp.textContent=r.t; ri.appendChild(rp);
        rs.appendChild(ri);
      });
      li.appendChild(rs);
    }
    ul.appendChild(li);
  });
  list.appendChild(ul);
}
function loadList(){
  say('loading'); bList.disabled=true;
  fetch(base+'/list?page='+encodeURIComponent(d.page))
  .then(function(r){return r.json()})
  .then(function(j){if(!j||!j.ok)throw 0; loaded=true; say(''); render(j.comments||[])})
  .catch(function(){say('loaderr','erro'); list.hidden=true; bList.setAttribute('aria-expanded','false'); bList.textContent=m('view')})
  .finally(function(){bList.disabled=false});
}
bList.addEventListener('click',function(){
  var open=bList.getAttribute('aria-expanded')==='true';
  if(open){list.hidden=true; bList.setAttribute('aria-expanded','false'); bList.textContent=m('view'); return}
  list.hidden=false; bList.setAttribute('aria-expanded','true'); bList.textContent=m('hide');
  if(!loaded) loadList();
});

/* ---- formulário ---- */
bForm.addEventListener('click',function(){
  var open=bForm.getAttribute('aria-expanded')==='true';
  f.hidden=open; bForm.setAttribute('aria-expanded',open?'false':'true'); bForm.textContent=open?m('write'):m('close');
  if(!open){fit(); ta.focus()}
});
function updCount(){var n=[...ta.value].length; cnt.textContent=n; cntp.className='cmt-count fine'+(n>max-100?' warn':'')}
ta.addEventListener('input',updCount);

function fit(){var w=box.clientWidth||300,k=Math.min(1,w/300); inner.style.transform=k<1?'scale('+k+')':''; box.style.height=Math.round(65*k)+'px'}
window.addEventListener('resize',fit);
function renderTs(){
  if(ready||!window.turnstile) return; ready=true; inner.textContent='';
  wid=turnstile.render(inner,{sitekey:d.sitekey,language:d.lang==='en-us'?'en':'pt-br',theme:'light',size:'normal',
    callback:function(t){token=t; if(last==='verify')say('')},
    'expired-callback':function(){token=''},
    'error-callback':function(){token=''; say('failed','erro')}});
}
function loadTs(){
  if(loading) return; loading=true;
  var st=ph&&ph.querySelector('strong'), st0=st&&st.textContent; if(st&&d.mTsload) st.textContent=d.mTsload;
  if(window.turnstile){renderTs();return}
  if(document.querySelector('script[src*="turnstile/v0/api.js"]')){ // a newsletter do rodapé já pediu o script
    var iv=setInterval(function(){if(window.turnstile){clearInterval(iv);renderTs()}},100); return;
  }
  window.__dbTsC=renderTs;
  var s=document.createElement('script');
  s.src='https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=__dbTsC';
  s.async=true; s.defer=true;
  s.onerror=function(){loading=false; if(st&&st0)st.textContent=st0; say('network','erro')};
  document.head.appendChild(s);
}
f.addEventListener('focusin',loadTs,{once:true});
f.addEventListener('pointerdown',loadTs,{once:true});
if(ph) ph.addEventListener('click',loadTs,{once:true});

f.addEventListener('submit',function(ev){
  ev.preventDefault();
  if(send.disabled) return;
  if(f.elements.website.value) return;                       // isca preenchida: ignora
  var text=ta.value.trim(), em=f.elements.email.value.trim();
  if(!text){say('empty','erro'); ta.focus(); return}
  if([...text].length>max){say('long','erro'); return}
  if((text.match(/https?:\/\//gi)||[]).length>2){say('links','erro'); return}
  if(em&&!f.elements.email.checkValidity()){say('email','erro'); f.elements.email.focus(); return}
  if(!token){loadTs(); say('verify','erro'); return}
  send.disabled=true; say('sending');
  var ctl=new AbortController(), t=setTimeout(function(){ctl.abort()},15000);
  fetch(base+'/submit',{method:'POST',headers:{'Content-Type':'application/json'},signal:ctl.signal,
    body:JSON.stringify({page:d.page,comment:text,name:f.elements.name.value.trim(),surname:f.elements.surname.value.trim(),email:em,website:f.elements.website.value,'cf-turnstile-response':token})})
  .then(function(r){return r.json().catch(function(){return{}}).then(function(j){return{s:r.status,j:j}})})
  .then(function(x){
    var j=x.j||{};
    if(j.ok){say('ok','ok'); f.reset(); updCount(); f.hidden=true; bForm.setAttribute('aria-expanded','false'); bForm.textContent=m('write')}
    else{var e=j.error;
      if(e==='empty')say('empty','erro');
      else if(e==='too_long')say('long','erro');
      else if(e==='links')say('links','erro');
      else if(e==='invalid_email')say('email','erro');
      else if(e==='turnstile_failed'||e==='turnstile_missing')say('failed','erro');
      else if(e==='rate_limited')say('rate','erro');
      else if(e==='daily_limit')say('daily','erro');
      else say('error','erro')}
  })
  .catch(function(){say('network','erro')})
  .finally(function(){clearTimeout(t); send.disabled=false; token=''; if(wid!==null&&window.turnstile)turnstile.reset(wid)});
});
})();
