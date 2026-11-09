/* Publicações: data de acesso da citação ABNT e botões "Copiar". */
(function () {
  'use strict';
  var meses = ['jan.', 'fev.', 'mar.', 'abr.', 'maio', 'jun.', 'jul.', 'ago.', 'set.', 'out.', 'nov.', 'dez.'];
  var hoje = new Date();
  var acesso = hoje.getDate() + ' ' + meses[hoje.getMonth()] + ' ' + hoje.getFullYear();
  document.querySelectorAll('[data-acesso]').forEach(function (el) { el.textContent = acesso; });

  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var alvo = document.querySelector(btn.getAttribute('data-copy'));
      if (!alvo) return;
      var texto = alvo.textContent.replace(/\s+/g, ' ').trim();
      var rotulo = btn.textContent;
      var ok = function () {
        btn.textContent = btn.getAttribute('data-done') || 'OK';
        setTimeout(function () { btn.textContent = rotulo; }, 1800);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(texto).then(ok, function () {});
      } else {
        var t = document.createElement('textarea');
        t.value = texto; document.body.appendChild(t); t.select();
        try { document.execCommand('copy'); ok(); } catch (e) {}
        document.body.removeChild(t);
      }
    });
  });
})();
