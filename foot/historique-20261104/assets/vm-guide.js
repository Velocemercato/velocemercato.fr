/* Guide « 📲 Installer l'appli » : s'ouvre quand on arrive depuis l'annuaire vmunivers.fr (lien avec ?installer=1).
   Montre le bon geste selon le téléphone (iPhone : bouton Partager puis « Sur l'écran d'accueil » ; Android : bouton Installer ou menu ⋮).
   Usage dans le <head> : <script src="/assets/vm-guide.js" defer></script> */
(function () {
  if (!/[?&]installer=1\b/.test(location.search)) return;
  if (matchMedia('(display-mode: standalone)').matches || navigator.standalone) return;
  var ua = navigator.userAgent, ios = /iphone|ipad|ipod/i.test(ua) || (/macintosh/i.test(ua) && navigator.maxTouchPoints > 1);
  var safari = ios && !/crios|fxios|edgios|instagram|fban|fbav|snapchat|tiktok/i.test(ua), dp = null, box = null, nom = '';
  addEventListener('beforeinstallprompt', function (e) { e.preventDefault(); dp = e; if (box) draw(); });
  addEventListener('appinstalled', function () { if (box) box.remove(); });
  // Retire ?installer=1 de l'adresse : un lien partagé ensuite n'ouvrira pas le guide.
  try { var u = new URL(location.href); u.searchParams.delete('installer'); history.replaceState(history.state, '', u); } catch (e) {}

  var SHARE = '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" style="vertical-align:-5px"><path d="M12 3v12M7.5 7.5 12 3l4.5 4.5" fill="none" stroke="#1d7cf2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M8 10H6a1 1 0 0 0-1 1v9a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-9a1 1 0 0 0-1-1h-2" fill="none" stroke="#1d7cf2" stroke-width="2" stroke-linecap="round"/></svg>';
  var ADD = '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" style="vertical-align:-5px"><rect x="4" y="4" width="16" height="16" rx="4" fill="none" stroke="#0b1533" stroke-width="2"/><path d="M12 8v8M8 12h8" stroke="#0b1533" stroke-width="2" stroke-linecap="round"/></svg>';
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }

  function draw() {
    var n = esc(nom || 'l’appli'), body;
    if (dp) body = '<p>Un seul geste : l’appli <b>' + n + '</b> arrive sur ton écran d’accueil, avec sa propre icône.</p><button type="button" class="vmg-go" id="vmgGo">📲 Installer ' + n + '</button>';
    else if (ios && !safari) body = '<ol><li>Ouvre cette page dans <b>Safari</b> (menu ⋯ puis « Ouvrir dans Safari »).</li><li>Touche le bouton <b>Partager</b> ' + SHARE + ' en bas de l’écran.</li><li>Choisis <b>« Sur l’écran d’accueil »</b> ' + ADD + ' puis <b>« Ajouter »</b>.</li></ol>';
    else if (ios) body = '<ol><li>Touche le bouton <b>Partager</b> ' + SHARE + ' en bas de l’écran<br><small>(le carré avec la flèche vers le haut)</small>.</li><li>Fais défiler et choisis <b>« Sur l’écran d’accueil »</b> ' + ADD + '.</li><li>Touche <b>« Ajouter »</b> en haut à droite.</li></ol>';
    else body = '<ol><li>Ouvre le menu <b>⋮</b> en haut à droite du navigateur.</li><li>Choisis <b>« Installer l’application »</b> ou <b>« Ajouter à l’écran d’accueil »</b> ' + ADD + '.</li><li>Confirme avec <b>« Installer »</b>.</li></ol>';
    box.querySelector('.vmg-b').innerHTML = body;
    var go = document.getElementById('vmgGo');
    if (go) go.onclick = function () { var p = dp; dp = null; p.prompt(); p.userChoice.then(function () { box.remove(); }); };
  }

  function open() {
    var st = document.createElement('style');
    st.textContent = '.vmg{position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:96;max-width:440px;margin:0 auto;background:#fff;color:#0b1533;border:3px solid #000;border-radius:18px;padding:16px 16px 14px;box-shadow:6px 6px 0 #f4cf55;font:15px/1.45 system-ui,-apple-system,sans-serif}'
      + '.vmg h2{margin:0 34px 8px 0;font:900 1.12rem/1.2 system-ui,sans-serif}.vmg ol{margin:0;padding-left:1.3em;display:grid;gap:8px}.vmg p{margin:0 0 10px}.vmg small{color:#55607a}'
      + '.vmg-x{position:absolute;top:8px;right:8px;width:34px;height:34px;border-radius:50%;border:2px solid #000;background:#fff;font:900 16px/1 system-ui;cursor:pointer;color:#0b1533}'
      + '.vmg-go{width:100%;font:900 1rem/1 system-ui,sans-serif;padding:14px;border-radius:999px;border:2px solid #000;background:#1d3fb8;color:#fff;box-shadow:3px 3px 0 #000;cursor:pointer}'
      + '.vmg-arrow{display:block;text-align:center;font-size:1.6rem;line-height:1;margin-top:8px;color:#1d7cf2}'
      + '@media(prefers-reduced-motion:no-preference){.vmg-arrow{animation:vmgB 1s ease-in-out infinite alternate}@keyframes vmgB{to{transform:translateY(6px)}}}@media print{.vmg{display:none}}';
    document.head.appendChild(st);
    box = document.createElement('div');
    box.className = 'vmg'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-labelledby', 'vmgT');
    box.innerHTML = '<button type="button" class="vmg-x" aria-label="Fermer">✕</button><h2 id="vmgT">📲 Installer ' + esc(nom || 'l’appli') + '</h2><div class="vmg-b"></div>' + (ios && safari ? '<span class="vmg-arrow" aria-hidden="true">⬇</span>' : '');
    box.querySelector('.vmg-x').onclick = function () { box.remove(); };
    document.body.appendChild(box);
    draw();
  }

  function start() {
    var mf = document.querySelector('link[rel="manifest"]');
    if (!mf) return open();
    fetch(mf.href).then(function (r) { return r.json(); }).then(function (m) { nom = m.short_name || m.name || ''; })
      .catch(function () {}).then(open);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
