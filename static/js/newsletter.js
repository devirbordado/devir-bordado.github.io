/* Newsletter: envia o cadastro ao Worker (Cloudflare), que confere o Turnstile
   e pede ao Brevo o e-mail de confirmação. O Turnstile só é carregado quando a
   pessoa começa a usar o formulário. */
(function(){
var f=document.querySelector('form.nl'); if(!f) return;
var box=f.querySelector('.nl-ts'), inner=f.querySelector('.nl-ts-in'), ph=f.querySelector('.nl-ts-btn'), msg=f.querySelector('.nl-msg'), btn=f.querySelector('button[type=submit]'), email=f.elements.email;
var d=f.dataset, token='', wid=null, loading=false, ready=false;
var last='';
function say(k,cls){last=k;msg.textContent=d['m'+k.charAt(0).toUpperCase()+k.slice(1)]||'';msg.className='nl-msg fine '+(cls||'')}
function fit(){ // encolhe o retângulo de 300x65 quando a coluna é mais estreita
  var w=box.clientWidth||300, k=Math.min(1,w/300);
  inner.style.transform=k<1?'scale('+k+')':'';
  box.style.height=Math.round(65*k)+'px';
}
fit(); window.addEventListener('resize',fit);
function render(){
  if(ready||!window.turnstile) return; ready=true; inner.textContent='';
  wid=turnstile.render(inner,{sitekey:d.sitekey,language:d.lang==='en-us'?'en':'pt-br',theme:'light',size:'normal',
    callback:function(t){token=t;if(last==='verify')say('')},
    'expired-callback':function(){token=''},
    'error-callback':function(){token='';say('failed','erro')}});
}
function load(){
  if(loading) return; loading=true;
  if(window.turnstile){render();return}                      // outro formulário da página já carregou o Turnstile
  if(document.querySelector('script[src*="turnstile/v0/api.js"]')){var iv=setInterval(function(){if(window.turnstile){clearInterval(iv);render()}},100);return}
  var st=ph&&ph.querySelector('strong'), st0=st&&st.textContent; if(st&&d.mLoading) st.textContent=d.mLoading;
  window.__dbTs=render;
  var s=document.createElement('script');
  s.src='https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=__dbTs';
  s.async=true; s.defer=true; s.onerror=function(){loading=false;if(st&&st0)st.textContent=st0;say('network','erro')};
  document.head.appendChild(s);
}
email.addEventListener('focus',load,{once:true});
f.addEventListener('pointerdown',load,{once:true});
if(ph) ph.addEventListener('click',load,{once:true});
f.addEventListener('submit',function(ev){
  ev.preventDefault();
  if(btn.disabled) return;
  if(f.elements.website.value){return}                      // isca preenchida: ignora
  if(!email.value||!email.checkValidity()){say('invalid','erro');email.focus();return}
  if(!token){load();say('verify','erro');return}
  btn.disabled=true; say('sending');
  var ctl=new AbortController(), t=setTimeout(function(){ctl.abort()},15000);
  fetch(d.worker,{method:'POST',headers:{'Content-Type':'application/json'},signal:ctl.signal,
    body:JSON.stringify({email:email.value.trim(),'cf-turnstile-response':token,lang:d.lang,website:f.elements.website.value})})
  .then(function(r){return r.json().catch(function(){return{}}).then(function(j){return{s:r.status,j:j}})})
  .then(function(x){
    if(x.j&&x.j.ok){say('ok','ok');f.reset()}
    else{var e=x.j&&x.j.error;
      if(e==='invalid_email')say('invalid','erro');
      else if(e==='turnstile_failed'||e==='turnstile_missing')say('failed','erro');
      else say('error','erro')}
  })
  .catch(function(){say('network','erro')})
  .finally(function(){clearTimeout(t);btn.disabled=false;token='';if(wid!==null&&window.turnstile)turnstile.reset(wid)});
});
})();
