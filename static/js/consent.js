/* Consentimento de cookies e Google Analytics (somente estatísticas).
   - Antes da escolha, nada é enviado ao Google e o gtag.js nem é baixado.
   - "Permitir": carrega o gtag.js e libera apenas analytics_storage; publicidade e remarketing ficam sempre negados.
   - "Recusar" (ou revogar depois): nada é carregado; cookies _ga* já existentes são apagados. */
(function () {
  'use strict';
  var root = document.getElementById('db-consent');
  if (!root) return;
  var cfg = {}; try { cfg = JSON.parse(root.getAttribute('data-cfg')); } catch (e) {}
  var ID = cfg.id, KEY = 'db_consent_v1', TTL = 365 * 864e5, carregado = false;

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  gtag('consent', 'default', { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'denied' });

  function ler() {
    try { var v = JSON.parse(localStorage.getItem(KEY)); if (v && typeof v.a === 'boolean' && Date.now() - v.t < TTL) return v; } catch (e) {}
    return null;
  }
  function gravar(a) { try { localStorage.setItem(KEY, JSON.stringify({ a: a, t: Date.now() })); } catch (e) {} }

  function permitir() {
    if (!ID) return;
    window['ga-disable-' + ID] = false;
    if (!carregado) {
      carregado = true;
      var s = document.createElement('script'); s.async = true;
      s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(ID);
      document.head.appendChild(s);
      gtag('js', new Date());
      gtag('consent', 'update', { analytics_storage: 'granted' });
      gtag('config', ID, { allow_google_signals: false, allow_ad_personalization_signals: false });
    } else {
      gtag('consent', 'update', { analytics_storage: 'granted' });
    }
  }
  function apagarCookies() {
    var host = location.hostname, partes = host.split('.'), apex = partes.length > 2 ? partes.slice(-2).join('.') : host;
    document.cookie.split(';').forEach(function (c) {
      var n = c.split('=')[0].trim();
      if (n.indexOf('_ga') !== 0) return;
      [host, '.' + host, '.' + apex].forEach(function (d) {
        document.cookie = n + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=' + d;
      });
      document.cookie = n + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
    });
  }
  function negar() {
    if (ID) window['ga-disable-' + ID] = true;
    gtag('consent', 'update', { analytics_storage: 'denied' });
    apagarCookies();
  }

  function mostrar(foco) {
    root.hidden = false;
    if (foco) { var h = root.querySelector('h2'); if (h) h.focus(); }
  }
  function esconder() { root.hidden = true; }

  root.querySelector('[data-accept]').addEventListener('click', function () { gravar(true); permitir(); esconder(); });
  root.querySelector('[data-reject]').addEventListener('click', function () { gravar(false); negar(); esconder(); });
  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('[data-cookies]');
    if (t) { e.preventDefault(); mostrar(true); }
  });
  window.dbConsent = { open: function () { mostrar(true); } };

  var v = ler();
  if (!v) { mostrar(false); } else if (v.a) { permitir(); } else { negar(); }
})();
