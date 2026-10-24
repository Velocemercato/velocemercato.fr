/* Bouton « 📲 Installer l'app » pour les pages VM qui n'ont pas la barre VM (vmbar.py).
   Usage dans le <head> : <script src="/assets/vm-install.js" data-nom="VM Recettes" defer></script>
   Le manifeste de la page (<link rel="manifest">) donne le nom, l'icône et le dossier de l'appli. */
(function () {
  var me = document.currentScript, nom = (me && me.getAttribute('data-nom')) || 'l’appli VM';
  if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(function () {});
  if (document.getElementById('vmInst')) return; // barre VM déjà présente : son bouton suffit
  var mf = document.querySelector('link[rel="manifest"]'), href = (mf && mf.getAttribute('href')) || '';
  var app = (href.match(/app[/]([a-z]+)[.]webmanifest/) || [, 'vm'])[1], key = 'vm-app-non-' + app, no = false;
  try { no = localStorage.getItem(key) === '1'; } catch (e) {}
  var standalone = matchMedia('(display-mode: standalone)').matches || navigator.standalone;
  var ios = /iphone|ipad|ipod/i.test(navigator.userAgent), dp = null, ib = null;
  function button() {
    if (ib) return ib;
    var st = document.createElement('style');
    st.textContent = '.vminst{display:none;position:fixed;left:14px;bottom:calc(14px + env(safe-area-inset-bottom,0px));z-index:75;align-items:center;gap:6px;font:800 14px/1 system-ui,sans-serif;padding:12px 16px;border-radius:999px;border:2px solid #000;background:#1d3fb8;color:#fff;box-shadow:3px 3px 0 #000;cursor:pointer}.vminst.show{display:flex}@media print{.vminst{display:none!important}}';
    document.head.appendChild(st);
    ib = document.createElement('button');
    ib.type = 'button'; ib.className = 'vminst'; ib.id = 'vmInst'; ib.textContent = '📲 Installer ' + nom;
    ib.onclick = function () {
      if (dp) { dp.prompt(); dp.userChoice.then(function () { ib.classList.remove('show'); }); dp = null; return; }
      if (ios) alert('Pour installer ' + nom + ' sur iPhone : — 1. Ouvre cette page dans Safari — 2. Bouton Partager ↑ en bas — 3. « Sur l’écran d’accueil » — 4. « Ajouter »');
      try { localStorage.setItem(key, '1'); } catch (e) {}
      ib.classList.remove('show');
    };
    (document.body || document.documentElement).appendChild(ib);
    return ib;
  }
  function show() { if (no) return; function go() { button().classList.add('show'); }
    if (document.body) go(); else document.addEventListener('DOMContentLoaded', go); }
  if (!standalone) {
    addEventListener('beforeinstallprompt', function (e) { e.preventDefault(); dp = e; show(); });
    if (ios) show();
  }
  addEventListener('appinstalled', function () { if (ib) ib.classList.remove('show'); });
})();
