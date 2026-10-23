/* Kit commun des sites de démonstration Véloce Web Studio.
   Tout fonctionne dans le navigateur : rien n'est envoyé à un serveur.
   Les réservations et commandes de démonstration restent dans ce téléphone (localStorage). */
(function () {
  'use strict';
  var D = window.DEMO || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]; }); };
  // Rappel affiché dans chaque parcours : les démos n'envoient rien de réel.
  var SIM = '<p class="vd-sim">🧪 Simulation : aucun SMS ni e-mail réel n’est envoyé, rien n’est payé.</p>';
  var euro = function (n) { var r = Math.round(n * 100) / 100; return r.toLocaleString('fr-FR', {minimumFractionDigits: r % 1 ? 2 : 0, maximumFractionDigits: 2}).replace(/\u202f|\u00a0/g, ' ') + ' €'; };
  var pad = function (n) { return (n < 10 ? '0' : '') + n; };
  var JOURS = ['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'];
  var MOIS = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.'];
  var PHONE = /^(?:\+33\s?|0)[1-9](?:[\s.-]?\d{2}){4}$/;
  var MAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  var store = {
    get: function (k, d) { try { var v = localStorage.getItem('vd-' + D.id + '-' + k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem('vd-' + D.id + '-' + k, JSON.stringify(v)); } catch (e) { /* Stockage facultatif. */ } }
  };
  function toast(t) {
    var d = document.createElement('div'); d.className = 'vd-toast'; d.setAttribute('role', 'status'); d.textContent = t;
    document.body.appendChild(d); setTimeout(function () { d.remove(); }, 2600);
  }
  function ref(prefix) { return prefix + '-' + Math.random().toString(36).slice(2, 6).toUpperCase(); }
  function mins(hm) { var p = hm.split(':'); return +p[0] * 60 + +p[1]; }
  // Une plage qui finit après minuit (ex. 18:00 – 01:00) court jusqu'à minuit pour la journée.
  function endMin(r) { var e = mins(r[1]); return e <= mins(r[0]) ? 1440 : e; }
  function hm(m) { return pad(Math.floor(m / 60)) + ':' + pad(m % 60); }
  function hmFr(m) { return Math.floor(m / 60) + ' h ' + pad(m % 60); }
  function dayKey(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function dateFr(d) { return JOURS[d.getDay()] + ' ' + d.getDate() + ' ' + MOIS[d.getMonth()]; }
  function fromKey(k) { var p = k.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  // Créneaux déjà « pris » : pseudo-aléatoire mais stable, pour que la démo paraisse vivante.
  function busy(s, rate) { var h = 0; for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0; return (h % 100) < rate; }
  function smsHref(num, body) { return 'sms:' + String(num || '').replace(/[^\d+]/g, '') + '?&body=' + encodeURIComponent(body); }
  function mailHref(to, subject, body) { return 'mailto:' + (to || '') + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body); }
  function ics(title, start, durMin, place) {
    var f = function (d) { return d.getFullYear() + pad(d.getMonth() + 1) + pad(d.getDate()) + 'T' + pad(d.getHours()) + pad(d.getMinutes()) + '00'; };
    var end = new Date(start.getTime() + durMin * 60000);
    var txt = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Veloce Web Studio//Demo//FR', 'BEGIN:VEVENT', 'UID:' + Date.now() + '@velocemercato.fr',
      'DTSTAMP:' + f(new Date()), 'DTSTART:' + f(start), 'DTEND:' + f(end), 'SUMMARY:' + title.replace(/[,;]/g, ' '), 'LOCATION:' + String(place || '').replace(/[,;]/g, ' '),
      'BEGIN:VALARM', 'TRIGGER:-PT2H', 'ACTION:DISPLAY', 'DESCRIPTION:Rappel', 'END:VALARM', 'END:VEVENT', 'END:VCALENDAR'].join('\r\n');
    return URL.createObjectURL(new Blob([txt], {type: 'text/calendar'}));
  }

  /* ---------- Médias : photo ou vidéo, avec un repli soigné tant que le fichier n'existe pas ---------- */
  function placeholder(el) {
    if (el.querySelector('.vd-ph')) return;
    var ph = document.createElement('div'); ph.className = 'vd-ph';
    ph.innerHTML = '<div><span class="e" aria-hidden="true">' + esc(el.dataset.e || '📸') + '</span><b>' + esc(el.dataset.l || '') + '</b>' +
      (el.dataset.video || el.hasAttribute('data-video-pending') ? '<small>Vidéo à venir</small>' : el.hasAttribute('data-icon-media') || !el.dataset.img ? '' : '<small>Photo à venir</small>') + '</div>';
    el.appendChild(ph);
  }
  function media(root) {
    $$('.vd-media', root).forEach(function (el) {
      if (el.closest('details:not([open])')) return;
      if (el.dataset.ready) return; el.dataset.ready = '1';
      if (el.dataset.video) {
        var v = document.createElement('video');
        v.preload = 'none'; v.playsInline = true; v.muted = el.hasAttribute('data-muted'); v.loop = el.hasAttribute('data-loop');
        if (el.dataset.img) v.poster = el.dataset.img;
        v.setAttribute('aria-label', el.dataset.l || 'Vidéo');
        var src = document.createElement('source'); src.src = el.dataset.video; src.type = 'video/mp4';
        v.appendChild(src); el.appendChild(v);
        var play = document.createElement('button'); play.type = 'button'; play.className = 'vd-play'; play.setAttribute('aria-label', 'Lire la vidéo : ' + (el.dataset.l || '')); play.textContent = '▶';
        el.appendChild(play);
        var fail = function () { v.remove(); play.remove(); placeholder(el); };
        src.addEventListener('error', fail);
        play.addEventListener('click', function () { v.controls = true; play.remove(); var p = v.play(); if (p && p.catch) p.catch(fail); });
        // Sans poster ni vidéo publiée, on affiche tout de suite le repli.
        fetch(el.dataset.video, {method: 'HEAD'}).then(function (r) { if (!r.ok) fail(); }).catch(function () { /* Hors ligne : on laisse le lecteur. */ });
      } else if (el.dataset.img) {
        var i = new Image(); i.alt = el.dataset.l || ''; i.decoding = 'async';
        var hero = !!el.closest('.vd-hero-art');
        i.loading = hero ? 'eager' : 'lazy';
        if (hero) { i.fetchPriority = 'high'; i.width = 1122; i.height = 1402; }
        else if (el.closest('.vd-gal')) { i.width = 1254; i.height = 1254; }
        i.onerror = function () { i.remove(); placeholder(el); };
        i.src = el.dataset.img; el.appendChild(i);
        if (el.closest('.vd-gal')) {
          el.tabIndex = 0; el.setAttribute('role', 'button');
          el.setAttribute('aria-label', 'Agrandir : ' + (el.dataset.l || 'photo'));
          if (el.dataset.l) { var c = document.createElement('span'); c.className = 'vd-caption'; c.textContent = el.dataset.l; c.setAttribute('aria-hidden', 'true'); el.appendChild(c); }
        }
      } else placeholder(el);
    });
  }
  function m(img, e, l, extra) {
    return '<div class="vd-media" data-img="' + esc(img || '') + '" data-e="' + esc(e || '') + '" data-l="' + esc(l || '') + '"' + (extra || '') + '></div>';
  }

  /* ---------- Horaires ---------- */
  function openNow(hours, now) {
    now = now || new Date();
    var t = now.getHours() * 60 + now.getMinutes();
    return (hours[now.getDay()] || []).some(function (r) { return t >= mins(r[0]) && t < endMin(r); });
  }
  function hoursTable(el) {
    var H = D.hours || {}, today = new Date().getDay(), order = [1, 2, 3, 4, 5, 6, 0];
    el.innerHTML = '<p><span class="vd-open ' + (openNow(H) ? 'y">Ouvert maintenant' : 'n">Fermé pour le moment') + '</span></p><table class="vd-hours">' +
      order.map(function (d) {
        var r = H[d] || [];
        return '<tr' + (d === today ? ' class="today"' : '') + '><td>' + JOURS[d].charAt(0).toUpperCase() + JOURS[d].slice(1) + '</td><td>' +
          (r.length ? r.map(function (x) { return x[0].replace(':', ' h ') + ' – ' + x[1].replace(':', ' h '); }).join(' · ') : 'Fermé') + '</td></tr>';
      }).join('') + '</table>';
  }

  /* ---------- Choix d'un jour et d'un créneau (réutilisé partout) ---------- */
  function slotPicker(box, opt) {
    // opt: hours, days, step, dur, lead (minutes avant le 1er créneau du jour), rate (% occupé), key(day,time) -> bool déjà réservé, onPick
    var H = opt.hours, days = [], d = new Date(); d.setHours(0, 0, 0, 0);
    for (var i = 0; days.length < (opt.days || 14) && i < 60; i++) { var x = new Date(d); x.setDate(d.getDate() + i); days.push(x); }
    var selDay = null, selTime = null;
    box.innerHTML = '<div class="vd-days" role="group" aria-label="Choisir le jour"></div><div class="vd-slots" role="group" aria-label="Choisir l’heure" aria-live="polite"></div>';
    var dz = box.firstChild, sz = box.lastChild;
    function slotsFor(day) {
      var out = [], now = new Date(), isToday = dayKey(day) === dayKey(now), nowMin = now.getHours() * 60 + now.getMinutes() + (opt.lead || 60);
      (H[day.getDay()] || []).forEach(function (r) {
        for (var t = mins(r[0]); t + (opt.dur || 30) <= endMin(r); t += opt.step || 30) {
          if (isToday && t < nowMin) continue;
          var k = dayKey(day) + ' ' + hm(t);
          out.push({t: t, taken: busy(k + (opt.salt || ''), opt.rate == null ? 30 : opt.rate) || (opt.key && opt.key(dayKey(day), hm(t)))});
        }
      });
      return out;
    }
    days.forEach(function (day) {
      var free = slotsFor(day).some(function (s) { return !s.taken; });
      var b = document.createElement('button'); b.type = 'button'; b.className = 'vd-day'; b.disabled = !free;
      b.setAttribute('aria-pressed', 'false');
      b.innerHTML = '<small>' + JOURS[day.getDay()].slice(0, 3) + '</small><b>' + day.getDate() + '</b><small>' + MOIS[day.getMonth()] + '</small>';
      b.setAttribute('aria-label', dateFr(day) + (free ? '' : ', complet ou fermé'));
      b.onclick = function () {
        $$('.vd-day', dz).forEach(function (o) { o.setAttribute('aria-pressed', 'false'); });
        b.setAttribute('aria-pressed', 'true'); selDay = day; selTime = null; draw(); opt.onPick(null);
      };
      dz.appendChild(b);
    });
    function draw() {
      var list = slotsFor(selDay);
      sz.innerHTML = list.length ? '' : '<p class="vd-empty">Plus de créneau ce jour-là.</p>';
      list.forEach(function (s) {
        var b = document.createElement('button'); b.type = 'button'; b.className = 'vd-slot'; b.disabled = s.taken; b.textContent = hm(s.t).replace(':', 'h');
        b.setAttribute('aria-pressed', 'false'); if (s.taken) b.setAttribute('aria-label', hm(s.t) + ' déjà réservé');
        b.onclick = function () {
          $$('.vd-slot', sz).forEach(function (o) { o.setAttribute('aria-pressed', 'false'); });
          b.setAttribute('aria-pressed', 'true'); selTime = s.t; opt.onPick({day: selDay, t: s.t});
        };
        sz.appendChild(b);
      });
    }
    var first = $('.vd-day:not([disabled])', dz); if (first) first.click(); else sz.innerHTML = '<p class="vd-empty">Aucun créneau disponible pour le moment.</p>';
  }

  /* ---------- Coordonnées du client ---------- */
  function contactFields(o) {
    o = o || {};
    return '<div class="vd-2"><label class="vd-field">Prénom et nom *<input name="nom" required maxlength="80" autocomplete="name"></label>' +
      '<label class="vd-field">Téléphone mobile *<input name="tel" required type="tel" inputmode="tel" autocomplete="tel" placeholder="06 12 34 56 78"></label></div>' +
      '<label class="vd-field">E-mail' + (o.mailRequired ? ' *' : '') + '<input name="mail" type="email" autocomplete="email" ' + (o.mailRequired ? 'required ' : '') + 'placeholder="vous@exemple.fr"></label>' +
      (o.address ? '<label class="vd-field">Adresse de livraison *<input name="adresse" maxlength="160" autocomplete="street-address" placeholder="N°, rue, ville"></label>' : '') +
      '<label class="vd-field">' + esc(o.noteLabel || 'Une précision ?') + '<textarea name="note" maxlength="500" placeholder="' + esc(o.notePh || 'Facultatif') + '"></textarea></label>' +
      '<label class="vd-check"><input type="checkbox" name="ok" required> <span>J’accepte d’être contacté au sujet de ma demande. Démo : aucune donnée n’est envoyée, tout reste sur ce téléphone.</span></label>';
  }
  function readContact(form, o) {
    o = o || {};
    var v = function (n) { return form.elements[n] ? form.elements[n].value.trim() : ''; };
    var c = {nom: v('nom'), tel: v('tel'), mail: v('mail'), adresse: v('adresse'), note: v('note')};
    if (c.nom.length < 2) return [null, 'Indiquez votre prénom et votre nom.', 'nom'];
    if (!PHONE.test(c.tel)) return [null, 'Numéro de mobile invalide (ex. 06 12 34 56 78).', 'tel'];
    if ((o.mailRequired || c.mail) && !MAIL.test(c.mail)) return [null, 'Adresse e-mail invalide.', 'mail'];
    if (o.address && c.adresse.length < 6) return [null, 'Indiquez l’adresse de livraison complète.', 'adresse'];
    if (!form.elements.ok.checked) return [null, 'Cochez la case pour confirmer votre demande.', 'ok'];
    return [c];
  }

  /* ---------- Ticket : ce que reçoivent le client et le pro ---------- */
  function ticket(box, t) {
    // t: emoji,title,ref,lines[],smsClient,smsPro,mailSubject,mailBody,client,ics{title,start,dur},extra
    var c = t.client;
    box.innerHTML = '<div class="vd-ticket"><div class="vd-ticket-h"><span class="e" aria-hidden="true">' + esc(t.emoji || '✅') + '</span><div><h3>' + esc(t.title) +
      '</h3><div>Référence <span class="vd-ref">' + esc(t.ref) + '</span></div></div></div><div class="vd-ticket-b">' +
      '<div class="vd-sum">' + t.lines.map(function (l) { return '<div>' + l + '</div>'; }).join('') + '</div>' + (t.extra || '') +
      '<div class="vd-msgs"><div class="vd-phone"><h4>📱 SMS reçu par le client</h4><div class="vd-bubble me"></div></div>' +
      '<div class="vd-phone"><h4>🔔 SMS reçu par ' + esc(D.name) + '</h4><div class="vd-bubble"></div></div>' +
      '<div class="vd-phone"><h4>✉️ E-mail de confirmation</h4><div class="vd-bubble mail"></div></div></div>' +
      '<p class="vd-auto">⚡ <b>Sur votre vrai site</b>, ces SMS et e-mails partent <b>automatiquement</b> au client et au professionnel, avec un rappel la veille. Ici, en démo, vous pouvez vous les envoyer vous-même :</p>' +
      '<div class="vd-actions"><a class="vd-btn sm" data-a="sms">📱 M’envoyer le SMS</a>' + (c.mail ? '<a class="vd-btn sm alt" data-a="mail">✉️ M’envoyer l’e-mail</a>' : '') +
      (t.ics ? '<a class="vd-btn sm alt" data-a="ics" download="rendez-vous.ics">📅 Ajouter à mon agenda</a>' : '') +
      '<button type="button" class="vd-btn sm dark" data-a="new">↺ Nouvelle demande</button></div></div></div>';
    var b = $$('.vd-bubble', box);
    b[0].textContent = t.smsClient; b[1].textContent = t.smsPro; b[2].textContent = 'Objet : ' + t.mailSubject + '\n\n' + t.mailBody;
    $('[data-a=sms]', box).href = smsHref(c.tel, t.smsClient);
    if (c.mail) $('[data-a=mail]', box).href = mailHref(c.mail, t.mailSubject, t.mailBody);
    if (t.ics) $('[data-a=ics]', box).href = ics(t.ics.title, t.ics.start, t.ics.dur, D.address);
    $('[data-a=new]', box).onclick = t.onNew;
    box.scrollIntoView({behavior: 'smooth', block: 'start'});
    var h = $('h3', box); h.tabIndex = -1; h.focus({preventScroll: true});
  }

  /* ---------- Réservation (salon, institut, restaurant) ---------- */
  function booking(root) {
    var B = D.booking, isTable = B.kind === 'table', state = {};
    var steps = isTable ? ['Couverts', 'Date & heure', 'Coordonnées'] : ['Prestation', B.staff ? 'Avec qui' : null, 'Date & heure', 'Coordonnées'].filter(Boolean);
    var mine = function () { return store.get('bookings', []); };
    function head(i) { return SIM + '<ol class="vd-steps">' + steps.map(function (s, j) { return '<li class="' + (j === i ? 'on' : j < i ? 'done' : '') + '">' + esc(s) + '</li>'; }).join('') + '</ol>'; }
    function summary() {
      var s = [];
      if (state.svc) s.push('<b>' + esc(state.svc.name) + '</b> · ' + euro(state.svc.price) + ' · ' + state.svc.dur + ' min');
      if (state.covers) s.push('<b>' + state.covers + ' personne' + (state.covers > 1 ? 's' : '') + '</b>' + (state.zone ? ' · ' + esc(state.zone) : ''));
      if (state.staff) s.push('Avec <b>' + esc(state.staff) + '</b>');
      if (state.when) s.push('Le <b>' + dateFr(state.when.day) + ' à ' + hmFr(state.when.t) + '</b>');
      return s.length ? '<div class="vd-sum">' + s.join('<br>') + '</div>' : '';
    }
    function step(i) {
      var name = steps[i], html = head(i) + summary();
      if (name === 'Prestation') {
        var cats = []; B.services.forEach(function (s) { if (cats.indexOf(s.cat) < 0) cats.push(s.cat); });
        html += '<div class="vd-strip" role="group" aria-label="Catégories">' + cats.map(function (c, j) { return '<button type="button" class="vd-chip" aria-pressed="' + (j === 0) + '" data-c="' + esc(c) + '">' + esc(c) + '</button>'; }).join('') + '</div><div class="vd-pick" data-list></div>';
      } else if (name === 'Avec qui') {
        html += '<div class="vd-pick">' + ['Peu importe'].concat(B.staff.map(function (s) { return s.name; })).map(function (n, j) {
          var s = B.staff[j - 1];
          return '<button type="button" class="vd-opt" aria-pressed="false" data-n="' + esc(n) + '"><span class="e" aria-hidden="true">' + (s ? esc(s.e) : '✨') + '</span>' + esc(n) + '<small>' + (s ? esc(s.role) : 'Le premier disponible') + '</small></button>';
        }).join('') + '</div>';
      } else if (name === 'Couverts') {
        html += '<p style="margin:0 0 8px;font-weight:800">Combien serez-vous ?</p><div class="vd-strip">' + [1, 2, 3, 4, 5, 6, 7, 8].map(function (n) { return '<button type="button" class="vd-chip" aria-pressed="false" data-n="' + n + '">' + n + (n === 8 ? '+' : '') + '</button>'; }).join('') + '</div>' +
          (B.zones ? '<p style="margin:10px 0 8px;font-weight:800">Où souhaitez-vous être installé ?</p><div class="vd-strip" data-z>' + B.zones.map(function (z, j) { return '<button type="button" class="vd-chip" aria-pressed="' + (j === 0) + '">' + esc(z) + '</button>'; }).join('') + '</div>' : '');
      } else if (name === 'Date & heure') {
        html += '<div data-slots></div>';
      } else {
        html += '<form novalidate>' + contactFields({noteLabel: isTable ? 'Une occasion, une allergie, une chaise bébé ?' : 'Une précision pour ' + D.name + ' ?'}) + '<p class="vd-err" role="alert"></p></form>';
      }
      var last = i === steps.length - 1;
      html += '<div class="vd-nav-steps">' + (i ? '<button type="button" class="vd-btn sm alt" data-back>← Retour</button>' : '<span></span>') +
        '<button type="button" class="vd-btn ' + (last ? 'b' : '') + '" data-next disabled>' + (last ? '✅ Confirmer ma réservation' : 'Continuer →') + '</button></div>';
      root.innerHTML = html;
      var next = $('[data-next]', root), back = $('[data-back]', root);
      if (back) back.onclick = function () { step(i - 1); };
      if (name === 'Prestation') {
        var list = $('[data-list]', root);
        var drawCat = function (c) {
          list.innerHTML = B.services.filter(function (s) { return s.cat === c; }).map(function (s) {
            var k = B.services.indexOf(s);
            return '<button type="button" class="vd-opt" aria-pressed="' + (state.svc === s) + '" data-k="' + k + '">' + esc(s.name) + '<small>' + s.dur + ' min · ' + euro(s.price) + '</small></button>';
          }).join('');
          $$('.vd-opt', list).forEach(function (b) {
            b.onclick = function () { $$('.vd-opt', list).forEach(function (o) { o.setAttribute('aria-pressed', 'false'); }); b.setAttribute('aria-pressed', 'true'); state.svc = B.services[+b.dataset.k]; next.disabled = false; };
          });
        };
        $$('.vd-chip', root).forEach(function (c) { c.onclick = function () { $$('.vd-chip', root).forEach(function (o) { o.setAttribute('aria-pressed', 'false'); }); c.setAttribute('aria-pressed', 'true'); drawCat(c.dataset.c); }; });
        var pre = state.svc ? state.svc.cat : null, chip = pre && $$('.vd-chip', root).filter(function (c) { return c.dataset.c === pre; })[0];
        (chip || $('.vd-chip', root)).click(); next.disabled = !state.svc;
      }
      if (name === 'Avec qui') $$('.vd-opt', root).forEach(function (b) {
        if ((state.staff || 'Peu importe') === b.dataset.n) { b.setAttribute('aria-pressed', 'true'); next.disabled = false; }
        b.onclick = function () { $$('.vd-opt', root).forEach(function (o) { o.setAttribute('aria-pressed', 'false'); }); b.setAttribute('aria-pressed', 'true'); state.staff = b.dataset.n === 'Peu importe' ? null : b.dataset.n; state.when = null; next.disabled = false; };
      });
      if (name === 'Couverts') {
        $$('[data-n]', root).forEach(function (b) {
          if (+b.dataset.n === state.covers) { b.setAttribute('aria-pressed', 'true'); next.disabled = false; }
          b.onclick = function () { $$('[data-n]', root).forEach(function (o) { o.setAttribute('aria-pressed', 'false'); }); b.setAttribute('aria-pressed', 'true'); state.covers = +b.dataset.n; next.disabled = false; };
        });
        if (B.zones) { state.zone = state.zone || B.zones[0]; $$('[data-z] .vd-chip', root).forEach(function (b) {
          b.setAttribute('aria-pressed', String(b.textContent === state.zone));
          b.onclick = function () { $$('[data-z] .vd-chip', root).forEach(function (o) { o.setAttribute('aria-pressed', 'false'); }); b.setAttribute('aria-pressed', 'true'); state.zone = b.textContent; };
        }); }
      }
      if (name === 'Date & heure') {
        var dur = state.svc ? state.svc.dur : (B.dur || 90);
        slotPicker($('[data-slots]', root), {
          hours: B.hours || D.hours, step: B.step || 30, dur: isTable ? 15 : dur, lead: B.lead || 60, rate: B.rate, salt: (state.staff || '') + (state.covers > 5 ? 'big' : ''),
          key: function (day, time) { return mine().some(function (r) { return r.day === day && r.time === time && (!state.staff || r.staff === state.staff); }); },
          onPick: function (w) { state.when = w; next.disabled = !w; }
        });
      }
      if (last) {
        var form = $('form', root), err = $('.vd-err', root);
        next.disabled = false;
        next.onclick = function () {
          var r = readContact(form);
          if (!r[0]) { err.textContent = r[1]; if (form.elements[r[2]]) form.elements[r[2]].focus(); return; }
          confirm(r[0]);
        };
      } else next.onclick = function () { step(i + 1); };
    }
    function confirm(c) {
      var w = state.when, code = ref(D.refPrefix || 'RDV'), when = dateFr(w.day) + ' à ' + hmFr(w.t);
      var what = isTable ? 'Table pour ' + state.covers + (state.zone ? ' (' + state.zone + ')' : '') : state.svc.name;
      var rec = {ref: code, day: dayKey(w.day), time: hm(w.t), what: what, staff: state.staff || '', nom: c.nom, tel: c.tel, price: state.svc ? state.svc.price : 0, covers: state.covers || 0, at: Date.now()};
      var all = mine(); all.push(rec); store.set('bookings', all.slice(-60));
      var start = new Date(w.day); start.setHours(Math.floor(w.t / 60), w.t % 60);
      ticket(root, {
        emoji: isTable ? '🍽️' : '🎉', title: isTable ? 'Table réservée !' : 'Rendez-vous confirmé !', ref: code, client: c,
        lines: ['<b>' + esc(what) + '</b>' + (state.staff ? ' avec ' + esc(state.staff) : ''), '📅 ' + esc(when.charAt(0).toUpperCase() + when.slice(1)), '📍 ' + esc(D.address), state.svc ? '💶 ' + euro(state.svc.price) + ' · à régler sur place' : '👥 ' + state.covers + ' personne(s)'],
        smsClient: D.name + ' : c’est confirmé ' + c.nom.split(' ')[0] + ' ! ' + what + ' le ' + when + '. Réf ' + code + '. Pour annuler ou décaler, répondez à ce SMS. À bientôt !',
        smsPro: '🔔 Nouvelle réservation ' + code + ' : ' + what + ' le ' + when + (state.staff ? ' avec ' + state.staff : '') + '. Client : ' + c.nom + ' ' + c.tel + (c.note ? '. Note : ' + c.note : ''),
        mailSubject: 'Confirmation ' + code + ' — ' + D.name,
        mailBody: 'Bonjour ' + c.nom + ',\n\nVotre réservation est confirmée.\n\n' + what + '\nLe ' + when + '\n' + D.address + '\nRéférence : ' + code + '\n\nUn rappel vous sera envoyé la veille.\n\nÀ très vite,\n' + D.name,
        ics: {title: what + ' — ' + D.name, start: start, dur: state.svc ? state.svc.dur : 90},
        onNew: function () { state = {}; step(0); }
      });
      pro();
    }
    // Lien direct depuis une carte de prestation : « Réserver » présélectionne la prestation.
    window.vdBook = function (k) { state = {svc: B.services[k]}; step(steps.indexOf('Prestation') + 1); root.scrollIntoView({behavior: 'smooth'}); };
    step(0);
  }

  /* ---------- Commande (snack, drive) ---------- */
  function order(root) {
    var O = D.order, cart = store.get('cart', []), mode = O.modes[0].id;
    var bar = document.createElement('div'); bar.className = 'vd-cartbar'; bar.hidden = true;
    bar.innerHTML = '<div class="t"><span data-c></span><small data-m></small></div><button type="button" class="vd-btn sm">Voir le panier →</button>';
    document.body.appendChild(bar);
    var sheet = document.createElement('div'); sheet.className = 'vd-sheet'; sheet.hidden = true; sheet.setAttribute('role', 'dialog'); sheet.setAttribute('aria-modal', 'true');
    sheet.innerHTML = '<div class="vd-sheet-box"></div>'; document.body.appendChild(sheet);
    var box = sheet.firstChild;
    sheet.addEventListener('click', function (e) { if (e.target === sheet) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !sheet.hidden) close(); });
    function close() { sheet.hidden = true; }
    function itemPrice(l) { return l.price * l.q; }
    function sub() { return cart.reduce(function (s, l) { return s + itemPrice(l); }, 0); }
    function modeObj() { return O.modes.filter(function (x) { return x.id === mode; })[0]; }
    function fee() { var x = modeObj(); return x.fee && !(x.free && sub() >= x.free) ? x.fee : 0; }
    function save() { store.set('cart', cart); refresh(); }
    function refresh() {
      var n = cart.reduce(function (s, l) { return s + l.q; }, 0);
      bar.hidden = !n; document.body.classList.toggle('has-cart', !!n);
      $('[data-c]', bar).textContent = n + ' article' + (n > 1 ? 's' : '') + ' · ' + euro(sub());
      var x = O.modes.filter(function (o) { return o.free; })[0];
      $('[data-m]', bar).textContent = x ? (sub() >= x.free ? x.l + ' offerte ✓' : 'Plus que ' + euro(x.free - sub()) + ' pour la ' + x.l.toLowerCase() + ' offerte') : (O.prep ? 'Prêt en ~' + O.prep + ' min' : '');
      $$('[data-qty]').forEach(function (q) { var l = cart.filter(function (c) { return c.key === q.dataset.qty; })[0]; $('span', q).textContent = l ? l.q : 0; });
    }
    function add(item, choice, extra, label) {
      var key = item.id + (label ? '|' + label : ''), l = cart.filter(function (c) { return c.key === key; })[0];
      if (l) l.q++; else cart.push({key: key, id: item.id, name: item.name + (label ? ' (' + label + ')' : ''), price: item.price + (extra || 0), q: 1});
      save(); toast('➕ ' + item.name + ' ajouté');
    }
    // Menu
    var cats = []; O.items.forEach(function (it) { if (cats.indexOf(it.cat) < 0) cats.push(it.cat); });
    root.innerHTML = SIM + (O.search ? '<label class="vd-field"><span class="vd-sr">Rechercher un produit</span><input type="search" data-search placeholder="🔎 Rechercher un produit…"></label>' : '') +
      '<div class="vd-strip" role="group" aria-label="Rayons">' + ['Tout'].concat(cats).map(function (c, j) { return '<button type="button" class="vd-chip" aria-pressed="' + (j === 0) + '">' + esc(c) + '</button>'; }).join('') + '</div><div class="vd-grid" data-items></div>';
    var grid = $('[data-items]', root), cat = 'Tout', q = '';
    function draw() {
      var list = O.items.filter(function (it) { return (cat === 'Tout' || it.cat === cat) && (!q || (it.name + ' ' + (it.desc || '')).toLowerCase().indexOf(q) >= 0); });
      grid.innerHTML = list.length ? list.map(function (it) {
        var k = O.items.indexOf(it), simple = !it.opts;
        return '<article class="vd-card">' + m(it.img, it.e, it.name) + '<div class="vd-card-b">' + (it.tag ? '<span class="vd-tag">' + esc(it.tag) + '</span>' : '') +
          '<h3>' + esc(it.name) + '</h3>' + (it.desc ? '<p>' + esc(it.desc) + '</p>' : '') + '<div class="vd-meta"><span class="vd-price">' + euro(it.price) + (it.unit ? '<small style="font:600 .75rem system-ui;color:var(--muted)"> / ' + esc(it.unit) + '</small>' : '') + '</span>' +
          (simple && O.stepper ? '<span class="vd-qty" data-qty="' + esc(it.id) + '"><button type="button" aria-label="Retirer" data-minus="' + k + '">−</button><span>0</span><button type="button" aria-label="Ajouter" data-plus="' + k + '">+</button></span>'
            : '<button type="button" class="vd-add" data-k="' + k + '">' + (simple ? '+ Ajouter' : 'Composer →') + '</button>') + '</div></div></article>';
      }).join('') : '<p class="vd-empty">Aucun produit ne correspond.</p>';
      media(grid); refresh();
    }
    root.addEventListener('click', function (e) {
      var t = e.target.closest('button'); if (!t) return;
      if (t.classList.contains('vd-chip')) { $$('.vd-chip', root).forEach(function (o) { o.setAttribute('aria-pressed', 'false'); }); t.setAttribute('aria-pressed', 'true'); cat = t.textContent; draw(); }
      if (t.dataset.k != null) { var it = O.items[+t.dataset.k]; if (it.opts) compose(it); else add(it); }
      if (t.dataset.plus != null) add(O.items[+t.dataset.plus]);
      if (t.dataset.minus != null) { var id = O.items[+t.dataset.minus].id, l = cart.filter(function (c) { return c.key === id; })[0]; if (l) { l.q--; if (!l.q) cart.splice(cart.indexOf(l), 1); save(); } }
    });
    var s = $('[data-search]', root); if (s) s.addEventListener('input', function () { q = s.value.trim().toLowerCase(); draw(); });
    draw();
    // Composition (taille, viande, sauces…)
    function compose(it) {
      box.innerHTML = '<button type="button" class="vd-x" aria-label="Fermer">✕</button><h3>' + esc(it.name) + '</h3><p style="margin:0 0 12px;color:var(--muted)">' + esc(it.desc || '') + '</p>' +
        it.opts.map(function (o, j) {
          return '<fieldset style="border:0;padding:0;margin:0 0 14px"><legend style="font-weight:900;margin-bottom:6px">' + esc(o.n) + (o.max ? ' <small style="color:var(--muted)">(jusqu’à ' + o.max + ')</small>' : '') + '</legend><div class="vd-pick">' +
            o.c.map(function (c, k) {
              var lab = Array.isArray(c) ? c[0] : c, px = Array.isArray(c) ? c[1] : 0;
              return '<label class="vd-opt" style="flex-direction:row;align-items:center;gap:8px"><input type="' + (o.max ? 'checkbox' : 'radio') + '" name="o' + j + '" value="' + k + '"' + (!o.max && k === 0 ? ' checked' : '') + '> ' + esc(lab) + (px ? ' <small>+' + euro(px) + '</small>' : '') + '</label>';
            }).join('') + '</div></fieldset>';
        }).join('') + '<button type="button" class="vd-btn b" style="width:100%" data-ok></button>';
      sheet.hidden = false;
      var ok = $('[data-ok]', box);
      function calc() {
        var extra = 0, labels = [];
        it.opts.forEach(function (o, j) {
          var picked = $$('input[name=o' + j + ']:checked', box);
          if (o.max && picked.length > o.max) { picked[picked.length - 1].checked = false; picked.pop(); toast('Maximum ' + o.max + ' choix'); }
          picked.forEach(function (p) { var c = o.c[+p.value]; labels.push(Array.isArray(c) ? c[0] : c); extra += Array.isArray(c) ? c[1] : 0; });
        });
        ok.textContent = 'Ajouter · ' + euro(it.price + extra);
        return [extra, labels.join(', ')];
      }
      box.onchange = calc; calc();
      ok.onclick = function () { var r = calc(); add(it, null, r[0], r[1]); close(); };
      $('.vd-x', box).onclick = close; ok.focus();
    }
    // Panier et validation
    bar.lastChild.onclick = checkout;
    function checkout() {
      if (!cart.length) return;
      var x = modeObj();
      box.innerHTML = '<button type="button" class="vd-x" aria-label="Fermer">✕</button><h3>🛒 Mon panier</h3>' + SIM +
        cart.map(function (l, i) { return '<div class="vd-line"><span>' + l.q + ' × ' + esc(l.name) + '</span><span>' + euro(itemPrice(l)) + ' <button type="button" class="vd-x" style="float:none;width:28px;height:28px" data-del="' + i + '" aria-label="Retirer ' + esc(l.name) + '">✕</button></span></div>'; }).join('') +
        '<p style="font-weight:900;margin:14px 0 6px">Comment souhaitez-vous la recevoir ?</p><div class="vd-pick" data-modes>' + O.modes.map(function (o) {
          return '<button type="button" class="vd-opt" aria-pressed="' + (o.id === mode) + '" data-mode="' + o.id + '"><span class="e" aria-hidden="true">' + o.e + '</span>' + esc(o.l) + '<small>' + esc(o.sub || '') + '</small></button>';
        }).join('') + '</div>' +
        '<p style="font-weight:900;margin:14px 0 6px">' + esc(x.whenLabel || 'Pour quand ?') + '</p><div data-slots></div>' +
        '<form novalidate style="margin-top:14px">' + contactFields({address: !!x.address, noteLabel: O.noteLabel || 'Une précision ?', notePh: O.notePh}) + '<p class="vd-err" role="alert"></p></form>' +
        '<div data-tot></div><button type="button" class="vd-btn b" style="width:100%" data-go>✅ Valider ma commande</button><p style="font-size:.8rem;color:var(--muted);text-align:center">' + esc(O.payNote || 'Paiement sur place ou à la livraison (CB, espèces).') + '</p>';
      sheet.hidden = false;
      var when = null, tot = $('[data-tot]', box);
      function totals() {
        var f = fee(), min = x.min || 0;
        tot.innerHTML = '<div class="vd-line"><span>Sous-total</span><span>' + euro(sub()) + '</span></div>' + (x.fee ? '<div class="vd-line"><span>' + esc(x.l) + '</span><span>' + (f ? euro(f) : 'Offerte 🎁') + '</span></div>' : '') +
          '<div class="vd-line tot"><span>Total</span><span>' + euro(sub() + f) + '</span></div>' + (min && sub() < min ? '<p class="vd-err">Minimum de commande pour la ' + esc(x.l.toLowerCase()) + ' : ' + euro(min) + '.</p>' : '');
      }
      totals();
      // Créneaux : dès que possible aujourd'hui (snack) ou sur plusieurs jours (drive).
      if (x.whenText) $('[data-slots]', box).innerHTML = '<p class="vd-empty">' + esc(x.whenText) + '</p>';
      else slotPicker($('[data-slots]', box), {hours: x.hours || D.hours, days: x.days || 1, step: x.step || 10, dur: x.step || 10, lead: x.lead || O.prep || 20, rate: x.rate == null ? 15 : x.rate, salt: x.id, onPick: function (w) { when = w; }});
      if (!x.whenText && !$('.vd-slot', box)) $('[data-slots]', box).innerHTML = '<p class="vd-empty">Nous sommes fermés pour le moment : en démo, vous pouvez quand même valider pour voir la suite.</p>';
      $$('[data-mode]', box).forEach(function (b) { b.onclick = function () { mode = b.dataset.mode; checkout(); }; });
      $$('[data-del]', box).forEach(function (b) { b.onclick = function () { cart.splice(+b.dataset.del, 1); save(); if (cart.length) checkout(); else close(); }; });
      $('.vd-x', box).onclick = close;
      $('[data-go]', box).onclick = function () {
        var form = $('form', box), err = $('.vd-err', form), r = readContact(form, {address: !!x.address});
        if (!r[0]) { err.textContent = r[1]; if (form.elements[r[2]]) form.elements[r[2]].focus(); return; }
        if (x.min && sub() < x.min) { err.textContent = 'Ajoutez encore ' + euro(x.min - sub()) + ' pour la ' + x.l.toLowerCase() + '.'; return; }
        if ($('.vd-slot', box) && !when) { err.textContent = 'Choisissez un horaire.'; return; }
        done(r[0], x, when);
      };
    }
    function done(c, x, w) {
      var code = ref(O.refPrefix || 'CMD'), total = sub() + fee(), lines = cart.map(function (l) { return l.q + '× ' + l.name; }), items = lines.join(', ');
      var when = w ? (dayKey(w.day) === dayKey(new Date()) ? 'aujourd’hui' : 'le ' + dateFr(w.day)) + ' à ' + hmFr(w.t) : x.whenText ? x.whenText.toLowerCase() : 'dès que possible';
      var rec = {ref: code, what: items, total: total, mode: x.l, when: when, nom: c.nom, tel: c.tel, at: Date.now()};
      var all = store.get('orders', []); all.push(rec); store.set('orders', all.slice(-60));
      cart = []; save(); close();
      var target = $('#vd-order-done');
      ticket(target, {
        emoji: x.e, title: 'Commande envoyée !', ref: code, client: c,
        lines: ['🧾 ' + esc(items), x.e + ' ' + esc(x.l) + ' · ' + esc(when) + (c.adresse ? ' · ' + esc(c.adresse) : ''), '💶 Total ' + euro(total) + ' · ' + esc(O.payShort || 'paiement à la réception')],
        extra: '<div class="vd-track" aria-live="polite">' + O.track.map(function (t) { return '<div><span class="e" aria-hidden="true">' + t[0] + '</span>' + esc(t[1]) + '</div>'; }).join('') + '</div><p style="font-size:.78rem;color:var(--muted);margin:0">Suivi en direct (accéléré pour la démo).</p>',
        smsClient: D.name + ' : commande ' + code + ' reçue ! ' + x.l + ' ' + when + '. Total ' + euro(total) + '. On vous prévient par SMS dès qu’elle est prête 🔥',
        smsPro: '🔔 NOUVELLE COMMANDE ' + code + ' — ' + x.l + ' ' + when + ' : ' + items + '. Total ' + euro(total) + '. ' + c.nom + ' ' + c.tel + (c.adresse ? ' · ' + c.adresse : '') + (c.note ? ' · Note : ' + c.note : ''),
        mailSubject: 'Votre commande ' + code + ' — ' + D.name,
        mailBody: 'Bonjour ' + c.nom + ',\n\nMerci pour votre commande !\n\n' + lines.join('\n') + '\n\n' + x.l + ' : ' + when + (c.adresse ? '\nAdresse : ' + c.adresse : '') + '\nTotal : ' + euro(total) + '\nRéférence : ' + code + '\n\n' + D.name,
        onNew: function () { target.innerHTML = ''; root.scrollIntoView({behavior: 'smooth'}); }
      });
      var steps = $$('.vd-track div', target), i = 0;
      (function tick() { steps.forEach(function (s, j) { s.className = j < i ? 'done' : j === i ? 'on' : ''; }); if (i++ < steps.length - 1) setTimeout(tick, 4500); else toast(O.readyToast || '🔔 SMS envoyé : votre commande est prête !'); })();
      pro();
    }
    refresh();
  }

  /* ---------- Devis (artisan, entreprise) ---------- */
  function quote(root) {
    var Q = D.quote, st = {photos: []};
    var steps = ['Projet', 'Détails', 'Visite', 'Coordonnées'];
    function head(i) { return SIM + '<ol class="vd-steps">' + steps.map(function (s, j) { return '<li class="' + (j === i ? 'on' : j < i ? 'done' : '') + '">' + s + '</li>'; }).join('') + '</ol>'; }
    function estimate() { if (!st.type || !st.qty) return null; var u = Q.urgency.filter(function (x) { return x[0] === st.urg; })[0] || [0, '', 1]; return [Math.round(st.type.low * st.qty * u[2] / 10) * 10, Math.round(st.type.high * st.qty * u[2] / 10) * 10]; }
    function step(i) {
      var html = head(i), e = estimate();
      if (st.type) html += '<div class="vd-sum"><b>' + esc(st.type.l) + '</b>' + (st.qty ? ' · ' + st.qty + ' ' + esc(st.type.unit) : '') + (e ? '<br>Estimation indicative : <b>' + euro(e[0]) + ' – ' + euro(e[1]) + ' HT</b>' : '') + (st.when ? '<br>Visite : <b>' + dateFr(st.when.day) + ' à ' + hmFr(st.when.t) + '</b>' : '') + '</div>';
      if (i === 0) html += '<div class="vd-pick">' + Q.types.map(function (t, k) { return '<button type="button" class="vd-opt" aria-pressed="' + (st.type === t) + '" data-k="' + k + '"><span class="e" aria-hidden="true">' + t.e + '</span>' + esc(t.l) + '<small>' + esc(t.hint) + '</small></button>'; }).join('') + '</div>';
      if (i === 1) html += '<label class="vd-field">Quantité (' + esc(st.type.unit) + ') *<input name="qty" type="number" min="1" max="100000" inputmode="numeric" value="' + (st.qty || '') + '" placeholder="' + esc(st.type.ph || 'Ex. 25') + '"><small>Une estimation suffit, elle sera vérifiée lors de la visite.</small></label>' +
        '<p style="font-weight:800;margin:0 0 6px">Délai souhaité</p><div class="vd-strip" data-urg>' + Q.urgency.map(function (u) { return '<button type="button" class="vd-chip" aria-pressed="' + (st.urg === u[0]) + '" data-u="' + esc(u[0]) + '">' + esc(u[1]) + '</button>'; }).join('') + '</div>' +
        '<label class="vd-field" style="margin-top:10px">Décrivez votre projet<textarea name="desc" maxlength="1500" placeholder="' + esc(st.type.descPh || 'Matériaux, accès, état actuel…') + '">' + esc(st.desc || '') + '</textarea></label>' +
        '<label class="vd-field">Photos du chantier (facultatif)<input type="file" name="photos" accept="image/*" multiple><small>Démo : les photos restent sur votre téléphone, elles ne sont pas envoyées.</small></label><div class="vd-gal" data-prev style="grid-template-columns:repeat(4,1fr)"></div><p class="vd-err" role="alert"></p>';
      if (i === 2) html += '<p style="margin:0 0 10px;color:var(--muted)">Choisissez un créneau pour une <b>visite gratuite</b> sur place (devis détaillé remis sous 48 h).</p><div data-slots></div>';
      if (i === 3) html += '<form novalidate>' + contactFields({address: true, noteLabel: 'Accès, code portail, disponibilités…'}) + '<p class="vd-err" role="alert"></p></form>';
      html += '<div class="vd-nav-steps">' + (i ? '<button type="button" class="vd-btn sm alt" data-back>← Retour</button>' : '<span></span>') + '<button type="button" class="vd-btn ' + (i === 3 ? 'b' : '') + '" data-next' + (i === 0 && !st.type || i === 2 && !st.when ? ' disabled' : '') + '>' + (i === 3 ? '📨 Recevoir mon devis' : 'Continuer →') + '</button></div>';
      root.innerHTML = html;
      var next = $('[data-next]', root), back = $('[data-back]', root);
      if (back) back.onclick = function () { step(i - 1); };
      if (i === 0) $$('.vd-opt', root).forEach(function (b) { b.onclick = function () { var t = Q.types[+b.dataset.k]; if (st.type !== t) { st.qty = 0; } st.type = t; step(1); }; });
      if (i === 1) {
        st.urg = st.urg || Q.urgency[1][0];
        $$('[data-u]', root).forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.u === st.urg)); b.onclick = function () { st.urg = b.dataset.u; $$('[data-u]', root).forEach(function (o) { o.setAttribute('aria-pressed', String(o === b)); }); }; });
        var prev = $('[data-prev]', root), fi = root.querySelector('input[name=photos]');
        var showPrev = function () { prev.innerHTML = st.photos.map(function (u) { return '<div class="vd-media" style="aspect-ratio:1;grid-column:auto;grid-row:auto"><img src="' + u + '" alt="Photo jointe"></div>'; }).join(''); };
        fi.onchange = function () { Array.prototype.slice.call(fi.files, 0, 8).forEach(function (f) { st.photos.push(URL.createObjectURL(f)); }); st.photos = st.photos.slice(-8); showPrev(); };
        showPrev();
        next.onclick = function () {
          var q = +root.querySelector('input[name=qty]').value; st.desc = root.querySelector('textarea[name=desc]').value.trim();
          if (!(q > 0)) { $('.vd-err', root).textContent = 'Indiquez une quantité approximative.'; root.querySelector('input[name=qty]').focus(); return; }
          st.qty = q; step(2);
        };
      }
      if (i === 2) slotPicker($('[data-slots]', root), {hours: Q.visitHours || D.hours, step: 60, dur: 60, lead: 18 * 60, rate: 35, salt: 'visite', onPick: function (w) { st.when = w; next.disabled = !w; }});
      if (i === 0 || i === 2) { if (!next.onclick) next.onclick = function () { step(i + 1); }; }
      if (i === 3) next.onclick = function () {
        var form = $('form', root), r = readContact(form, {address: true});
        if (!r[0]) { $('.vd-err', root).textContent = r[1]; if (form.elements[r[2]]) form.elements[r[2]].focus(); return; }
        done(r[0]);
      };
    }
    function done(c) {
      var e = estimate(), code = ref('DEV'), when = dateFr(st.when.day) + ' à ' + hmFr(st.when.t);
      var all = store.get('quotes', []); all.push({ref: code, what: st.type.l + ' · ' + st.qty + ' ' + st.type.unit, est: e, when: when, nom: c.nom, tel: c.tel, at: Date.now()}); store.set('quotes', all.slice(-60));
      var start = new Date(st.when.day); start.setHours(Math.floor(st.when.t / 60), st.when.t % 60);
      ticket(root, {
        emoji: '📐', title: 'Demande de devis reçue !', ref: code, client: c,
        lines: ['🛠️ <b>' + esc(st.type.l) + '</b> · ' + st.qty + ' ' + esc(st.type.unit), '💶 Estimation indicative : <b>' + euro(e[0]) + ' – ' + euro(e[1]) + ' HT</b>', '📅 Visite gratuite le <b>' + esc(when) + '</b>', '📍 ' + esc(c.adresse), st.photos.length ? '📸 ' + st.photos.length + ' photo(s) jointe(s)' : ''].filter(Boolean),
        smsClient: D.name + ' : merci ' + c.nom.split(' ')[0] + ' ! Demande ' + code + ' bien reçue (' + st.type.l + '). Visite gratuite le ' + when + '. Devis détaillé sous 48 h.',
        smsPro: '🔔 Nouveau devis ' + code + ' : ' + st.type.l + ' ' + st.qty + ' ' + st.type.unit + ' (est. ' + euro(e[0]) + '–' + euro(e[1]) + '). Visite ' + when + ' · ' + c.adresse + '. ' + c.nom + ' ' + c.tel,
        mailSubject: 'Votre demande de devis ' + code + ' — ' + D.name,
        mailBody: 'Bonjour ' + c.nom + ',\n\nNous avons bien reçu votre demande.\n\nProjet : ' + st.type.l + ' (' + st.qty + ' ' + st.type.unit + ')\nEstimation indicative : ' + euro(e[0]) + ' – ' + euro(e[1]) + ' HT\nVisite gratuite : ' + when + '\nAdresse : ' + c.adresse + '\nRéférence : ' + code + '\n\nLe devis définitif vous sera remis après la visite.\n\n' + D.name,
        ics: {title: 'Visite devis — ' + D.name, start: start, dur: 60},
        onNew: function () { st = {photos: []}; step(0); }
      });
      pro();
    }
    step(0);
  }

  /* ---------- Espace pro (démo) : ce que voit le commerçant ---------- */
  function pro() {
    var el = $('#vd-pro'); if (!el) return;
    var kind = D.booking ? 'bookings' : D.order ? 'orders' : 'quotes', rows = store.get(kind, []).slice().reverse();
    var fake = (D.proFake || []).map(function (r) { r.fake = 1; return r; });
    var list = rows.concat(fake), money = list.reduce(function (s, r) { return s + (r.total || r.price || (r.est ? r.est[0] : 0) || 0); }, 0);
    var k = D.proKpis || ['Réservations', 'Chiffre prévu', 'SMS envoyés', 'Avis 5★'];
    el.innerHTML = '<h3>📊 Espace pro · tableau de bord</h3><p>Ce que voit ' + esc(D.name) + ' sur son téléphone. Vos essais de la démo apparaissent en premier.</p>' + SIM +
      '<div class="vd-kpis"><div class="vd-kpi"><b>' + list.length + '</b><small>' + esc(k[0]) + '</small></div><div class="vd-kpi"><b>' + (D.booking && D.booking.kind === 'table' ? list.reduce(function (s, r) { return s + (r.covers || 0); }, 0) : euro(money)) + '</b><small>' + esc(k[1]) + '</small></div><div class="vd-kpi"><b>' + list.length * 3 + '</b><small>' + esc(k[2]) + '</small></div><div class="vd-kpi"><b>' + (D.rating || '4,9') + '</b><small>' + esc(k[3]) + '</small></div></div>' +
      '<div class="vd-tw"><table class="vd-table"><thead><tr><th>Réf.</th><th>Quand</th><th>Quoi</th><th>Client</th><th>Statut</th></tr></thead><tbody>' +
      list.slice(0, 8).map(function (r) {
        var when = r.day ? dateFr(fromKey(r.day)).replace(/^\w+ /, '') + ' ' + r.time.replace(':', 'h') : r.when || '';
        return '<tr><td>' + esc(r.ref) + '</td><td>' + esc(when) + '</td><td>' + esc(r.what) + (r.staff ? ' · ' + esc(r.staff) : '') + '</td><td>' + esc(r.fake ? r.nom : r.nom.split(' ')[0]) + '</td><td><span class="vd-st ' + (r.fake ? 'ok">Confirmé' : 'wait">Nouveau') + '</span></td></tr>';
      }).join('') + '</tbody></table></div>';
  }

  /* ---------- Partage par SMS / QR code (pour démarcher) ---------- */
  function share() {
    var b = document.createElement('button'); b.type = 'button'; b.className = 'vd-fab'; b.textContent = '📤 Partager'; document.body.appendChild(b);
    var s = document.createElement('div'); s.className = 'vd-sheet'; s.hidden = true; s.setAttribute('role', 'dialog'); s.setAttribute('aria-modal', 'true'); s.setAttribute('aria-label', 'Partager ce site');
    var url = location.href.split('#')[0], t = D.name + ' — ' + (D.tagline || ''), e = encodeURIComponent;
    s.innerHTML = '<div class="vd-sheet-box"><button type="button" class="vd-x" aria-label="Fermer">✕</button><h3>📤 Partager</h3><p style="margin:0 0 12px;color:var(--muted);font-size:.9rem;word-break:break-all">' + esc(url) + '</p><div class="vd-share">' +
      '<a href="' + smsHref('', t + ' ' + url) + '"><span>📱</span>SMS</a><a target="_blank" rel="noopener" href="https://wa.me/?text=' + e(t + ' ' + url) + '"><span>💬</span>WhatsApp</a><button type="button" data-cp><span>🔗</span>Copier</button></div>' +
      '<div class="vd-qr" aria-label="QR code de cette page"></div><p style="text-align:center;font-size:.82rem;color:var(--muted);margin:0">📷 À scanner avec l’appareil photo</p></div>';
    document.body.appendChild(s);
    var qr = false;
    b.onclick = function () {
      s.hidden = false; $('.vd-x', s).focus();
      if (qr) return; qr = true;
      var sc = document.createElement('script'); sc.src = '/assets/vendor/qrcode.min.js';
      sc.onload = function () { try { new window.QRCode($('.vd-qr', s), {text: url, width: 170, height: 170, correctLevel: window.QRCode.CorrectLevel.M}); } catch (x) { /* Le lien reste copiable. */ } };
      document.head.appendChild(sc);
    };
    $('.vd-x', s).onclick = function () { s.hidden = true; b.focus(); };
    s.onclick = function (ev) { if (ev.target === s) s.hidden = true; };
    $('[data-cp]', s).onclick = function () { (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(function () { toast('Lien copié ✓'); }).catch(function () { prompt('Copiez ce lien :', url); }); };
  }

  /* ---------- Visionneuse de la galerie ---------- */
  function lightbox() {
    var lb = document.createElement('div'); lb.className = 'vd-lightbox'; lb.hidden = true; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true'); lb.setAttribute('aria-label', 'Photo agrandie'); lb.innerHTML = '<img alt=""><button type="button" class="vd-x" aria-label="Fermer">✕</button>';
    document.body.appendChild(lb);
    var returnFocus = null;
    function show(item) {
      var img = item && $('img', item); if (!img || !img.complete || !img.naturalWidth) return;
      returnFocus = item; lb.firstChild.src = img.currentSrc || img.src; lb.firstChild.alt = img.alt; lb.hidden = false; lb.lastChild.focus();
    }
    function hide() { lb.hidden = true; if (returnFocus) returnFocus.focus(); }
    document.addEventListener('click', function (e) {
      var item = e.target.closest('.vd-gal .vd-media'); if (item) show(item);
    });
    lb.onclick = function (e) { if (e.target === lb || e.target.closest('button')) hide(); };
    document.addEventListener('keydown', function (e) {
      if (!lb.hidden) {
        if (e.key === 'Escape') { e.preventDefault(); hide(); }
        else if (e.key === 'Tab') { e.preventDefault(); lb.lastChild.focus(); }
      } else if ((e.key === 'Enter' || e.key === ' ') && e.target.matches('.vd-gal .vd-media')) { e.preventDefault(); show(e.target); }
    });
  }

  // Menu du jour (restaurant) : choisi selon le jour de la semaine.
  function dayMenu(el) {
    var d = new Date().getDay(), mm = D.dayMenu[d] || D.dayMenu.def;
    el.innerHTML = '<div class="vd-sum" style="margin:0 0 10px"><b>' + JOURS[d].charAt(0).toUpperCase() + JOURS[d].slice(1) + '</b> · ' + esc(D.dayMenuPrice) + '</div>' + mm.map(function (x) { return '<div class="vd-line"><span><b>' + esc(x[0]) + '</b> · ' + esc(x[1]) + '</span></div>'; }).join('');
  }

  /* ---------- Vérification d'âge (produits réservés aux majeurs) ---------- */
  function ageGate() {
    if (!D.ageGate || store.get('majeur', false)) return;
    var g = document.createElement('div'); g.className = 'vd-sheet vd-age'; g.setAttribute('role', 'dialog'); g.setAttribute('aria-modal', 'true'); g.setAttribute('aria-labelledby', 'vd-age-t');
    g.innerHTML = '<div class="vd-sheet-box" style="text-align:center"><div style="font-size:3rem" aria-hidden="true">🔞</div><h3 id="vd-age-t">Avez-vous 18 ans ou plus ?</h3>' +
      '<p style="color:var(--muted)">' + esc(D.ageGate) + '</p><div class="vd-btns" style="justify-content:center"><button type="button" class="vd-btn b" data-y>Oui, j’ai 18 ans ou plus</button><a class="vd-btn alt" href="https://vmunivers.fr/">Non, quitter</a></div></div>';
    document.body.appendChild(g); document.documentElement.style.overflow = 'hidden';
    $('[data-y]', g).onclick = function () { store.set('majeur', true); g.remove(); document.documentElement.style.overflow = ''; };
    $('[data-y]', g).focus();
  }

  window.VD = {m: m, media: media, euro: euro, esc: esc};
  document.addEventListener('DOMContentLoaded', function () {
    media(document);
    document.addEventListener('toggle', function (event) { if (event.target.tagName === 'DETAILS' && event.target.open) media(event.target); }, true);
    $$('[data-vd-hours]').forEach(hoursTable);
    $$('[data-vd-daymenu]').forEach(dayMenu);
    if ($('#vd-booking') && D.booking) booking($('#vd-booking'));
    if ($('#vd-order') && D.order) order($('#vd-order'));
    if ($('#vd-quote') && D.quote) quote($('#vd-quote'));
    pro(); share(); lightbox(); ageGate();
    var y = $('[data-year]'); if (y) y.textContent = new Date().getFullYear();
  });
})();
