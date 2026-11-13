/* Rubrique « pure » : sur une page d'univers (Foot, Multisport, Actus, Gaming, Mangas…), on ne garde
   que le contenu de cet univers. Les menus et vignettes vers les AUTRES univers sont masqués,
   et un bouton « ← Retour » est ajouté. Le contenu des articles n'est jamais touché. */
(function () {
  'use strict';
  var s = document.currentScript, ici = (s && s.getAttribute('data-univers')) || '';
  var UNIVERS = {
    foot: [/^\/foot(\/|$)/, /^\/foot-amateur(\/|$)/, /^\/a\//, /^\/scores(\/|$)/, /^\/$/],
    multisport: [/^\/multisport(\/|$)/],
    actus: [/^\/actus(\/|$)/, /^\/region(\/|$)/, /^\/belfort(\/|$)/],
    gaming: [/^\/vm-gaming(\/|$)/, /^\/gaming\.html/],
    mangas: [/^\/mangas(\/|$)/, /^\/series(\/|$)/]
  };
  // Racines des univers VM : un lien vers l'une d'elles qui n'est pas l'univers courant est « hors rubrique ».
  var RACINES = [/^\/foot(\/|$)/, /^\/foot-amateur(\/|$)/, /^\/multisport(\/|$)/, /^\/actus(\/|$)/, /^\/vm-gaming(\/|$)/,
    /^\/gaming\.html/, /^\/mangas(\/|$)/, /^\/series(\/|$)/, /^\/web-studio\.html/, /^\/studio\.html/, /^\/region(\/|$)/,
    /^\/belfort(\/|$)/, /^\/cinema(\/|$)/, /^\/pronos(\/|$)/, /^\/services(\/|$)/, /^\/decouvrir\.html/];
  function chemin(a) {
    try { var u = new URL(a.getAttribute('href'), location.href); } catch (e) { return null; }
    if (/(^|\.)vmunivers\.fr$/.test(u.hostname)) return '/vmunivers';
    if (!/(^|\.)velocemercato\.fr$/.test(u.hostname) && u.hostname !== location.hostname) return null;
    return u.pathname;
  }
  function horsRubrique(a) {
    var p = chemin(a); if (!p) return false;
    if (p === '/vmunivers') return true;
    var mien = UNIVERS[ici] || [];
    if (mien.some(function (r) { return r.test(p); })) return false;
    return RACINES.some(function (r) { return r.test(p); });
  }
  function nettoyer() {
    if (!UNIVERS[ici]) return;
    // 1) Groupes de navigation majoritairement tournés vers d'autres univers.
    document.querySelectorAll('nav, header nav, section, aside, .vu-strip, [class*="portal"], [class*="ribbon"]').forEach(function (g) {
      if (g.closest('article,[data-vm-garder],#vm-live-ticker') || g.querySelector('article')) return;
      var liens = [].slice.call(g.querySelectorAll('a[href]'));
      if (liens.length < 2) return;
      var dehors = liens.filter(horsRubrique).length;
      if (dehors >= 2 && dehors / liens.length >= 0.5) g.hidden = true, g.style.display = 'none';
    });
    // 2) Boutons isolés vers un autre univers (hors texte d'article).
    document.querySelectorAll('a[href]').forEach(function (a) {
      if (a.closest('article, p, [data-vm-garder], #vm-live-ticker') || !horsRubrique(a)) return;
      a.style.display = 'none';
    });
  }
  function retour() {
    if (document.getElementById('vm-retour')) return;
    var b = document.createElement('a');
    b.id = 'vm-retour'; b.href = '/'; b.textContent = '← Retour';
    b.setAttribute('aria-label', 'Retour à l’accueil Véloce Mercato');
    b.style.cssText = 'position:fixed;left:10px;bottom:14px;z-index:9998;background:#e52643;color:#fff;font:800 15px system-ui,sans-serif;padding:11px 16px;border-radius:999px;text-decoration:none;box-shadow:0 6px 20px #0009';
    b.onclick = function (e) {
      try { if (document.referrer && new URL(document.referrer).hostname === location.hostname && history.length > 1) { e.preventDefault(); history.back(); } } catch (x) {}
    };
    document.body.appendChild(b);
  }
  function go() { nettoyer(); retour(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
  // Certains blocs sont ajoutés après coup par d'autres scripts.
  setTimeout(nettoyer, 1500); setTimeout(nettoyer, 4000);
})();
