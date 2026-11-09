document.querySelectorAll('[data-gal]').forEach(function(g){
var s=g.querySelectorAll('.slide'),i=0;
function show(n){i=(n+s.length)%s.length;s.forEach(function(x,k){x.hidden=k!==i})}
g.querySelector('.prev').addEventListener('click',function(){show(i-1)});
g.querySelector('.next').addEventListener('click',function(){show(i+1)});
g.addEventListener('keydown',function(e){if(e.key==='ArrowLeft')show(i-1);if(e.key==='ArrowRight')show(i+1)});
if(s.length<2)g.querySelectorAll('.nav').forEach(function(b){b.hidden=true});
});
