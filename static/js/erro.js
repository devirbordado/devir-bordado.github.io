/* Página 404: escolhe idioma pelo endereço e o tipo de mensagem conforme o caminho (?e= força um tipo). */
(function () {
  'use strict';
  var el = document.getElementById('erro-dados');
  var cena = document.querySelector('[data-fio]');
  if (!el || !cena) return;
  var dados; try { dados = JSON.parse(el.textContent); } catch (e) { return; }

  var caminho = location.pathname.toLowerCase();
  var en = /^\/en-us(\/|$)/.test(caminho) || (!/^\/pt-br(\/|$)/.test(caminho) && /^en/i.test(navigator.language || ''));
  var lang = en ? 'en-us' : 'pt-br', t = dados[lang];
  document.documentElement.lang = en ? 'en-US' : 'pt-BR';

  // existe a seção, mas não a página dentro dela?
  var secoes = en ? ['blog', 'herbarium', 'collection', 'publications', 'research-lines', 'about-db', 'playlists', 'digital', 'downloads']
                  : ['blog', 'herbario', 'acervo', 'publicacoes', 'linhas-de-pesquisa', 'sobre-db', 'playlists', 'digital', 'downloads'];
  var partes = caminho.split('/').filter(Boolean);
  if (partes[0] === (en ? 'en-us' : 'pt-br')) partes.shift();
  var tipo = new URLSearchParams(location.search).get('e');
  if (!tipo || !t.msgs[tipo]) tipo = (partes.length > 1 && secoes.indexOf(partes[0]) > -1) ? 'secao' : 'nao-encontrada';

  var set = function (sel, txt) { var n = cena.querySelector(sel); if (n) n.textContent = txt; };
  set('[data-fio-main]', t.main);
  set('[data-fio-msg]', t.msgs[tipo]);
  set('[data-fio-home]', t.home);
  set('[data-fio-search]', t.search);
  var base = '/' + lang + '/';
  var h = cena.querySelector('[data-fio-home]'); if (h) h.href = base;
  var s = cena.querySelector('[data-fio-search]'); if (s) s.href = base + (en ? 'search/' : 'busca/');
  document.title = t.main;
})();
