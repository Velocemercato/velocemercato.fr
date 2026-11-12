/* Bandeau défilant « En direct + à venir dans les 12 h ».
   Données : branche scores-live (aucun redéploiement du site), repli sur /scores.json. */
(function () {
  'use strict';
  var SOURCES = ['https://raw.githubusercontent.com/Velocemercato/velocemercato.fr/scores-live/scores.json', '/scores.json'];
  var LIVE = { IN_PLAY: 1, PAUSED: 1 };
  var SOON = { TIMED: 1, SCHEDULED: 1 };
  var host = document.getElementById('vm-live-ticker');
  if (!host) return;
  // Choix du visiteur (mémorisé sur cet appareil) : quels sports défilent dans le bandeau.
  var SPORTS = { foot: '⚽ Foot', basket: '🏀 NBA', nfl: '🏈 NFL', hockey: '🏒 NHL' };
  var PREF = 'vm-bandeau-sports';
  function choix() {
    try { var v = JSON.parse(localStorage.getItem(PREF) || 'null'); if (v && typeof v === 'object') return v; } catch (e) {}
    return { foot: true, basket: true, nfl: true, hockey: true };
  }
  var dernier = null;
  function panneau() {
    var old = document.getElementById('vlt-panel'); if (old) { old.remove(); return; }
    var c = choix(), p = el('div'); p.id = 'vlt-panel'; p.setAttribute('role', 'dialog'); p.setAttribute('aria-label', 'Choisir les sports du bandeau');
    p.appendChild(el('b', null, 'Mon bandeau :'));
    Object.keys(SPORTS).forEach(function (k) {
      var l = el('label'), i = el('input'); i.type = 'checkbox'; i.checked = c[k] !== false;
      i.onchange = function () { var x = choix(); x[k] = i.checked; try { localStorage.setItem(PREF, JSON.stringify(x)); } catch (e) {} rendre(dernier); };
      l.appendChild(i); l.appendChild(document.createTextNode(SPORTS[k])); p.appendChild(l);
    });
    var ok = el('button', null, 'OK'); ok.type = 'button'; ok.onclick = function () { p.remove(); }; p.appendChild(ok);
    document.body.appendChild(p);
  }

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
    dernier = data;
    var c = choix();
    var tous = (data && Array.isArray(data.matchs)) ? data.matchs : [];
    var rows = tous.filter(function (m) { return c[m.sport || 'foot'] !== false; });
    var now = Date.now(), lim = now + 12 * 3600 * 1000;
    var direct = rows.filter(function (m) { return LIVE[m.statut]; });
    var avenir = rows.filter(function (m) {
      var t = Date.parse(m.date); return SOON[m.statut] && t >= now - 5 * 60000 && t <= lim;
    }).sort(function (a, b) { return Date.parse(a.date) - Date.parse(b.date); });
    host.replaceChildren();
    if (!direct.length && !avenir.length) {
      // Des matchs existent mais pas dans les sports choisis : on garde le bouton pour changer d'avis.
      var dispo = tous.some(function (m) { return LIVE[m.statut] || (SOON[m.statut] && Date.parse(m.date) <= lim && Date.parse(m.date) >= now - 5 * 60000); });
      if (!dispo) { host.hidden = true; return; }
      host.hidden = false;
      var b = el('button', 'vlt-cfg', '⚙ Sports'); b.type = 'button'; b.onclick = panneau;
      host.appendChild(el('span', 'vlt-comp', 'Aucun match pour tes sports choisis.')); host.appendChild(b); return;
    }
    host.hidden = false;
    var piste = el('div', 'vlt-track');
    function item(m, live) {
      var s = el('a', 'vlt-item' + (live ? ' vlt-live' : ''));
      s.href = '/scores/';
      s.appendChild(el('span', 'vlt-tag', live ? (m.statut === 'PAUSED' ? '⏸ MI-TEMPS' : '🔴 DIRECT') : '⏱ ' + heure(m.date)));
      var sc = Array.isArray(m.score) && m.score[0] != null ? ' ' + m.score[0] + '-' + m.score[1] + ' ' : ' – ';
      s.appendChild(el('span', 'vlt-match', String(m.dom || '?') + (live ? sc : ' – ') + String(m.ext || '?')));
      s.appendChild(el('span', 'vlt-comp', (SPORTS[m.sport || 'foot'] || '').split(' ')[0] + ' ' + String(m.comp || '')));
      piste.appendChild(s);
    }
    direct.forEach(function (m) { item(m, true); });
    avenir.slice(0, 20).forEach(function (m) { item(m, false); });
    // Contenu doublé pour un défilement continu.
    var clone = piste.cloneNode(true); clone.setAttribute('aria-hidden', 'true');
    var rail = el('div', 'vlt-rail'); rail.appendChild(piste); rail.appendChild(clone);
    var titre = el('a', 'vlt-title', direct.length ? 'EN DIRECT' : 'À VENIR'); titre.href = '/scores/';
    var vue = el('div', 'vlt-view'); vue.appendChild(rail);
    var cfg = el('button', 'vlt-cfg', '⚙ Sports'); cfg.type = 'button'; cfg.setAttribute('aria-label', 'Choisir les sports du bandeau'); cfg.onclick = panneau;
    host.appendChild(titre); host.appendChild(vue); host.appendChild(cfg);
    var dur = Math.max(20, (direct.length + avenir.length) * 6);
    rail.style.animationDuration = dur + 's';
  }
  function tick() { charger(0).then(rendre); }
  tick();
  setInterval(tick, 120000);
})();
