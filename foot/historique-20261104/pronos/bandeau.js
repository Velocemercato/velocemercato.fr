/* Bandeau « Les pronos du jour sont en ligne » pour velocemercato.fr et vmunivers.fr.
   N'affiche RIEN d'autre qu'un lien vers VM Actus & Pronos, et seulement si une sélection est active. */
(function () {
  var BASE = 'https://velocemercato.fr/pronos/';
  function active(d, humain) {
    if (!d || typeof d !== 'object') return false;
    if (humain ? !(d.valide === true && String(d.valide_par || '').trim()) : d.publie_sans_validation !== true) return false;
    var now = Date.now(), a = Date.parse(d.debut), b = Date.parse(d.expire);
    return a <= now && now < b;
  }
  function get(f) {
    return fetch(BASE + f + '?v=' + Math.floor(Date.now() / 300000), { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; });
  }
  Promise.all([get('selection.json'), get('analyse-claude.json'), get('acces.json')]).then(function (r) {
    var owner = active(r[0], true), ia = active(r[1], false), vip = r[2] && r[2].actif === true;
    if (!owner && !ia && !vip) return;
    var a = document.createElement('a');
    a.href = BASE + (owner ? '#pronos-du-jour' : ia ? '#analyse-claude' : '#acces-vip');
    a.setAttribute('aria-label', 'Les pronos du jour sont en ligne sur VM Actus et Pronos, réservé aux 18 ans et plus');
    a.style.cssText = 'display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:8px;margin:0;padding:10px 14px;' +
      'background:linear-gradient(90deg,#c4081f,#ff1f3d);color:#fff;font:800 15px/1.3 system-ui,sans-serif;text-decoration:none;' +
      'text-align:center;border-bottom:3px solid #ffc21a';
    a.innerHTML = '<span>' + (owner || ia ? '👑 Pronos du jour : exclusivement sur velocemercato.fr' : '🔒 Pronos VIP : accès gratuit par email') + '</span>' +
      '<span style="background:#ffc21a;color:#111;border-radius:999px;padding:3px 10px">' + (owner || ia ? 'Voir les pronos →' : 'Demander l’accès →') + '</span>' +
      '<span style="font-weight:700;font-size:12px;opacity:.9">🔞 18+</span>';
    document.body.insertBefore(a, document.body.firstChild);
  });
})();
