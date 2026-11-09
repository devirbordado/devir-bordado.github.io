/* Busca global: lê o índice embutido na página (#busca-dados), mescla resultados de todas as seções. */
(function () {
  'use strict';
  var raiz = document.querySelector('.pg-busca');
  if (!raiz) return;
  var $ = function (s) { return raiz.querySelector(s); };
  var ler = function (id) {
    try { return JSON.parse(document.getElementById(id).textContent); } catch (e) { return null; }
  };
  var dados = ler('busca-dados'), cores = ler('busca-cores') || {}, msgs = ler('busca-msgs') || {};
  var input = $('#busca-q'), grid = $('[data-resultados]'), status = $('.busca-status');
  var cena = $('[data-fio]'), mais = $('.busca-mais'), btnMais = $('[data-mais]');
  var PASSO = 24, lista = [], mostrados = 0, termos = [];

  // remove acentos preservando o comprimento do texto (permite achar o trecho no original)
  function norm(s) {
    return String(s || '').replace(/[^\u0000-\u007f]/g, function (c) { return c.normalize('NFD').charAt(0); }).toLowerCase();
  }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function marcar(texto, ts) {
    var n = norm(texto), faixas = [];
    ts.forEach(function (t) { var i = 0; while ((i = n.indexOf(t, i)) > -1) { faixas.push([i, i + t.length]); i += t.length; } });
    faixas.sort(function (a, b) { return a[0] - b[0]; });
    var out = '', pos = 0;
    faixas.forEach(function (f) {
      if (f[1] <= pos) return;
      var ini = Math.max(f[0], pos);
      out += esc(texto.slice(pos, ini)) + '<mark>' + esc(texto.slice(ini, f[1])) + '</mark>';
      pos = f[1];
    });
    return out + esc(texto.slice(pos));
  }
  function trecho(texto, ts) {
    var n = norm(texto), p = -1;
    for (var i = 0; i < ts.length; i++) { var k = n.indexOf(ts[i]); if (k > -1 && (p < 0 || k < p)) p = k; }
    if (p < 0) return texto.slice(0, 180) + (texto.length > 180 ? '…' : '');
    var a = Math.max(0, p - 80), b = Math.min(texto.length, p + 120);
    return (a > 0 ? '…' : '') + texto.slice(a, b) + (b < texto.length ? '…' : '');
  }

  if (!dados) { mostrarErro('indisponivel', ''); return; }
  dados.forEach(function (d) {
    d._t = norm(d.t); d._st = norm(d.st); d._g = norm(d.g); d._d = norm(d.d); d._m = norm(d.m); d._x = norm(d.x);
  });

  function buscar(q) {
    termos = norm(q).split(/\s+/).filter(Boolean);
    var r = [];
    dados.forEach(function (d) {
      var pts = 0;
      for (var i = 0; i < termos.length; i++) {
        var t = termos[i], s = 0;
        if (d._t.indexOf(t) > -1) s += 8;
        if (d._st.indexOf(t) > -1) s += 4;
        if (d._g.indexOf(t) > -1) s += 5;
        if (d._m.indexOf(t) > -1) s += 3;
        if (d._d.indexOf(t) > -1) s += 3;
        if (d._x.indexOf(t) > -1) s += 1;
        if (!s) return;            // todos os termos precisam aparecer
        pts += s;
      }
      r.push({ d: d, s: pts });
    });
    r.sort(function (a, b) { return b.s - a.s || (b.d.dt > a.d.dt ? 1 : -1); });
    return r.map(function (x) { return x.d; });
  }

  function card(d) {
    var cor = cores[d.k] || '#5A4B3E';
    var base = d.d || d.x || '';
    return '<article class="rcard" style="--c:' + cor + '"><p class="rcard-sec">' + esc(d.s) + '</p>' +
      '<h2><a href="' + esc(d.u) + '">' + marcar(d.t, termos) + '</a></h2>' +
      (d.st ? '<p class="rcard-sub">' + marcar(d.st, termos) + '</p>' : '') +
      '<p class="rcard-txt">' + marcar(trecho(base, termos), termos) + '</p></article>';
  }
  function desenhar() {
    var fim = Math.min(lista.length, mostrados + PASSO), html = '';
    for (var i = mostrados; i < fim; i++) html += card(lista[i]);
    grid.insertAdjacentHTML('beforeend', html);
    mostrados = fim;
    mais.hidden = mostrados >= lista.length;
  }
  function mostrarErro(tipo, q) {
    grid.innerHTML = ''; mais.hidden = true;
    var m = (msgs[tipo] || '').replace('{q}', q);
    var alvo = cena.querySelector('[data-fio-msg]'); if (alvo) alvo.textContent = m;
    cena.hidden = false;
  }
  function executar(q) {
    grid.innerHTML = ''; mostrados = 0; cena.hidden = true; mais.hidden = true;
    q = q.trim();
    if (!q) { status.textContent = raiz.getAttribute('data-hint'); return; }
    lista = buscar(q);
    if (!lista.length) { status.textContent = ''; mostrarErro('sem-resultado', q); return; }
    status.textContent = lista.length === 1 ? raiz.getAttribute('data-um') + ' “' + q + '”' : lista.length + ' ' + raiz.getAttribute('data-many') + ' “' + q + '”';
    desenhar();
  }
  btnMais.addEventListener('click', desenhar);

  var q = new URLSearchParams(location.search).get('q') || '';
  input.value = q;
  executar(q);
})();
