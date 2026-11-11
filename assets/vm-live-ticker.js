/* Bandeau défilant « En direct + à venir dans les 12 h ».
   Données : branche scores-live (aucun redéploiement du site), repli sur /scores.json. */
(function () {
  'use strict';
  var SOURCES = ['https://raw.githubusercontent.com/Velocemercato/velocemercato.fr/scores-live/scores.json', '/scores.json'];
  var LIVE = { IN_PLAY: 1, PAUSED: 1 };
  var SOON = { TIMED: 1, SCHEDULED: 1 };
  var host = document.getElementById('vm-live-ticker');
  if (!host) return;

  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function heure(iso) {
    try { return new Date(iso).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Paris' }); } catch (e) { return ''; }
  }
  function charger(i) {
    if (i >= SOURCES.length) return Promise.resolve(null);
    return fetch(SOURCES[i] + '?t=' + Math.floor(Date.now() / 60000), { cache: 'no-store' })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .catch(function () { return charger(i + 1); });
  }
  function rendre(data) {
    var rows = (data && Array.isArray(data.matchs)) ? data.matchs : [];
    var now = Date.now(), lim = now + 12 * 3600 * 1000;
    var direct = rows.filter(function (m) { return LIVE[m.statut]; });
    var avenir = rows.filter(function (m) {
      var t = Date.parse(m.date); return SOON[m.statut] && t >= now - 5 * 60000 && t <= lim;
    }).sort(function (a, b) { return Date.parse(a.date) - Date.parse(b.date); });
    host.replaceChildren();
    if (!direct.length && !avenir.length) { host.hidden = true; return; }
    host.hidden = false;
    var piste = el('div', 'vlt-track');
    function item(m, live) {
      var s = el('a', 'vlt-item' + (live ? ' vlt-live' : ''));
      s.href = '/scores/';
      s.appendChild(el('span', 'vlt-tag', live ? (m.statut === 'PAUSED' ? '⏸ MI-TEMPS' : '🔴 DIRECT') : '⏱ ' + heure(m.date)));
      var sc = Array.isArray(m.score) && m.score[0] != null ? ' ' + m.score[0] + '-' + m.score[1] + ' ' : ' – ';
      s.appendChild(el('span', 'vlt-match', String(m.dom || '?') + (live ? sc : ' – ') + String(m.ext || '?')));
      s.appendChild(el('span', 'vlt-comp', String(m.comp || '')));
      piste.appendChild(s);
    }
    direct.forEach(function (m) { item(m, true); });
    avenir.slice(0, 20).forEach(function (m) { item(m, false); });
    // Contenu doublé pour un défilement continu.
    var clone = piste.cloneNode(true); clone.setAttribute('aria-hidden', 'true');
    var rail = el('div', 'vlt-rail'); rail.appendChild(piste); rail.appendChild(clone);
    var titre = el('a', 'vlt-title', direct.length ? 'EN DIRECT' : 'À VENIR'); titre.href = '/scores/';
    var vue = el('div', 'vlt-view'); vue.appendChild(rail);
    host.appendChild(titre); host.appendChild(vue);
    var dur = Math.max(20, (direct.length + avenir.length) * 6);
    rail.style.animationDuration = dur + 's';
  }
  function tick() { charger(0).then(rendre); }
  tick();
  setInterval(tick, 120000);
})();
