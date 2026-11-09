(function(){
var h=document.getElementById('hdr');
function s(){h.classList.toggle('solid',window.scrollY>10)}
s();window.addEventListener('scroll',s,{passive:true});
var pairs=[['bm','mais'],['bl','pl'],['br','pr']];
function closeAll(){pairs.forEach(function(p){var b=document.getElementById(p[0]),t=document.getElementById(p[1]);t.classList.remove('open');b.setAttribute('aria-expanded','false')})}
pairs.forEach(function(p){var b=document.getElementById(p[0]),t=document.getElementById(p[1]);
b.addEventListener('click',function(e){e.stopPropagation();var o=!t.classList.contains('open');closeAll();if(o){t.classList.add('open');b.setAttribute('aria-expanded','true')}})});
document.addEventListener('click',closeAll);
document.addEventListener('keydown',function(e){if(e.key==='Escape')closeAll()});
})();

(function(){
document.querySelectorAll('[data-more]').forEach(function(b){
var n=+b.dataset.step||9,g=document.querySelector(b.dataset.more);
b.addEventListener('click',function(){var h=g.querySelectorAll('.bcard[hidden]');for(var i=0;i<n&&i<h.length;i++)h[i].hidden=false;if(!g.querySelector('.bcard[hidden]'))b.hidden=true})})
})();
