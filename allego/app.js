/* Allego — moteur générique : capture, lecture, confirmation, comparaison, résultats.
   Aucune donnée n'est conservée : tout reste en mémoire dans cet onglet. */
(function () {
  'use strict';
  const {SOURCES, CATEGORIES} = window.ALLEGO;
  const LIBS = {
    ocr: 'https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/dist/tesseract.min.js',
    zxing: 'https://cdn.jsdelivr.net/npm/@zxing/library@0.21.3/umd/index.min.js'
  };
  const app = document.getElementById('app');
  const $ = s => app.querySelector(s);
  const esc = v => String(v == null ? '' : v).replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  const cat = () => CATEGORIES.find(c => c.id === S.cat);

  let S = fresh();
  function fresh() {
    return {screen: 'home', demo: null, items: [], cat: null, values: {}, auto: {}, annonce: '', answers: {}, official: '', tab: 'resultats', busy: ''};
  }

  /* ---------- Effacement : rien ne survit à la session ---------- */
  let stream = null, scanTimer = null, ocrWorker = null;
  function stopCamera() {
    clearInterval(scanTimer); scanTimer = null;
    if (stream) stream.getTracks().forEach(t => t.stop());
    stream = null;
  }
  function wipe() {
    stopCamera();
    S.items.forEach(i => i.url && URL.revokeObjectURL(i.url));
    if (ocrWorker) { ocrWorker.terminate().catch(() => {}); ocrWorker = null; }
    S = fresh();
  }
  window.addEventListener('pagehide', wipe);

  /* ---------- Outils de contrôle (réellement opérationnels) ---------- */
  function luhn(d) {
    if (!/^\d{15}$/.test(d)) return false;
    let s = 0;
    for (let i = 0; i < 15; i++) { let n = +d[14 - i]; if (i % 2) { n *= 2; if (n > 9) n -= 9; } s += n; }
    return s % 10 === 0;
  }
  function gtinOk(d) {
    if (!/^(\d{8}|\d{12}|\d{13}|\d{14})$/.test(d)) return false;
    const a = d.split('').map(Number), check = a.pop();
    const sum = a.reverse().reduce((t, n, i) => t + n * (i % 2 ? 1 : 3), 0);
    return (10 - sum % 10) % 10 === check;
  }
  const toDigits = v => String(v).toUpperCase().replace(/[OQD]/g, '0').replace(/[IL|]/g, '1').replace(/S/g, '5').replace(/B/g, '8').replace(/Z/g, '2').replace(/G/g, '6').replace(/\D/g, '');
  const ident = v => String(v || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
  function normSize(v) {
    const t = String(v || '').toUpperCase().replace(',', '.');
    const n = (t.match(/\d{1,2}(?:\.5)?(?:\s?[12]\/3)?/) || [''])[0].replace(/\s/g, '');
    if (!n) return null;
    const sys = /US/.test(t) ? 'US' : /UK/.test(t) ? 'UK' : 'EU';
    return {sys, n, key: sys + n};
  }
  function normCap(v) {
    const m = String(v || '').toLowerCase().match(/(\d+(?:[.,]\d+)?)\s*(go|gb|to|tb)/);
    if (!m) return ident(v);
    const n = parseFloat(m[1].replace(',', '.'));
    return String(/t/.test(m[2]) ? n * 1024 : n) + 'GO';
  }

  /* ---------- Extraction depuis le texte lu (OCR) ou collé ---------- */
  function extract(text, c, codes) {
    const out = {};
    const T = String(text || '');
    const up = T.toUpperCase();
    // IMEI : 15 chiffres, éventuellement espacés ; on ne garde que ceux dont la clé est juste.
    const imeis = (up.replace(/(\d)[ \-](?=\d)/g, '$1').match(/\b\d{15}\b/g) || []).filter(luhn);
    if (imeis.length) out.imei = imeis[0];
    const ser = up.match(/(?:SERIAL(?:\s*NO\.?)?|S\/N|N°\s*DE\s*S[ÉE]RIE|NUM[ÉE]RO\s*DE\s*S[ÉE]RIE|\(S\))\s*[:.]?\s*([A-Z0-9]{8,14})\b/);
    if (ser) out.serie = ser[1];
    const anums = [...new Set(up.match(/\bA\d{4}\b/g) || [])];
    if (anums.length && c.id === 'airpods') {
      const AP = window.ALLEGO.AIRPODS;
      const cases = anums.filter(a => AP.some(f => f.cases.includes(a)));
      const buds = anums.filter(a => !cases.includes(a));
      if (cases.length) out.boitier = cases.join(' ');
      if (buds.length) out.ecouteurs = buds.join(' ');
    }
    const part = up.match(/\b[MFN][A-Z0-9]{3,4}[A-Z]{1,2}\/A\b/);
    if (part) out.reference = part[0];
    if (c.id === 'baskets') {
      const st = up.match(/\b([A-Z]{2}\d{4}|\d{6})[- ](\d{3})\b/) || up.match(/\b[A-Z]{1,2}\d{4}\b/);
      if (st) out.reference = st[2] ? st[1] + '-' + st[2] : st[0];
      const sz = T.match(/\b(?:EU|EUR)\s?\d{2}(?:[.,]5|\s?[12]\/3)?\b|\bUS\s?\d{1,2}(?:\.5)?\b|\btaille\s*:?\s*\d{2}(?:[.,]5)?\b/i);
      if (sz) out.taille = sz[0].replace(/taille\s*:?\s*/i, '') + (/^\d/.test(sz[0].replace(/taille\s*:?\s*/i, '')) ? ' EU' : '');
    }
    const cap = T.match(/\b\d{2,4}\s?(?:go|gb|to|tb)\b/i);
    if (cap && c.fields.some(f => f.key === 'capacite')) out.capacite = cap[0];
    const fam = c.family(T);
    if (fam.length === 1 && !/^A\d{4}$/.test(T.trim())) {
      const line = T.split(/\n/).find(l => c.family(l).length) || '';
      out.modele = line.trim().length <= 60 && line.trim() ? line.trim() : c.familyName(fam[0]);
    }
    (codes || []).forEach(k => {
      const v = k.value.trim();
      if (/^\d{12,14}$/.test(v) && gtinOk(v.padStart(13, '0'))) out.ean = out.ean || v;
      else if (/^\d{15}$/.test(v) && luhn(v)) out.imei = out.imei || v;
      else if (/^S[A-Z0-9]{10,12}$/.test(v)) out.serie = out.serie || v.slice(1); // Les boîtes Apple préfixent souvent le numéro par « S ».
      else if (/^[A-Z0-9]{10,12}$/.test(v) && !out.serie) out.serie = v;
    });
    return out;
  }

  function suggestCategory() {
    const all = S.items.map(i => i.text + ' ' + i.codes.map(k => k.value).join(' ')).join('\n') + '\n' + S.annonce;
    if (/\b\d{15}\b/.test(all.replace(/(\d) (?=\d)/g, '$1')) && (all.replace(/(\d) (?=\d)/g, '$1').match(/\b\d{15}\b/g) || []).some(luhn)) return 'telephone';
    const hit = CATEGORIES.find(c => c.keywords && c.keywords.test(all));
    return hit ? hit.id : null;
  }

  function fill(source, data) {
    const c = cat(); if (!c || !source) return;
    S.values[source] = S.values[source] || {};
    c.fields.forEach(f => {
      if (data[f.key] && f.in.includes(source) && !S.values[source][f.key]) {
        S.values[source][f.key] = data[f.key];
        S.auto[source + '.' + f.key] = true;
      }
    });
  }
  function applyItems() {
    const c = cat(); if (!c) return;
    S.items.forEach(i => { if (i.source) fill(i.source, extract(i.text, c, i.codes)); });
    if (S.annonce) fill('annonce', extract(S.annonce, c, []));
  }

  /* ---------- Chargement paresseux des bibliothèques de lecture ---------- */
  const loaded = {};
  function loadScript(src) {
    if (!loaded[src]) loaded[src] = new Promise((ok, ko) => {
      const s = document.createElement('script');
      s.src = src; s.async = true; s.crossOrigin = 'anonymous';
      s.onload = ok; s.onerror = () => { delete loaded[src]; ko(new Error('chargement impossible')); };
      document.head.appendChild(s);
    });
    return loaded[src];
  }
  async function readBarcodes(item) {
    try {
      if ('BarcodeDetector' in window) {
        const bmp = await createImageBitmap(item.blob);
        const found = await new window.BarcodeDetector().detect(bmp);
        return found.map(b => ({value: b.rawValue, format: b.format}));
      }
      await loadScript(LIBS.zxing);
      const res = await new window.ZXing.BrowserMultiFormatReader().decodeFromImageUrl(item.url);
      return [{value: res.getText(), format: String(window.ZXing.BarcodeFormat[res.getBarcodeFormat()] || '').toLowerCase()}];
    } catch (_) { return []; } // Aucun code trouvé ou lecture indisponible : la saisie manuelle reste possible.
  }
  async function readText(item) {
    await loadScript(LIBS.ocr);
    if (!ocrWorker) ocrWorker = await window.Tesseract.createWorker('eng');
    const {data} = await ocrWorker.recognize(item.blob);
    return data.text || '';
  }
  async function analyse() {
    const todo = S.items.filter(i => i.blob && !i.done);
    let ocrFailed = false;
    for (let n = 0; n < todo.length; n++) {
      const i = todo[n];
      setBusy(`Lecture de la photo ${n + 1} sur ${todo.length}… (sur votre appareil)`);
      const codes = await readBarcodes(i);
      codes.forEach(k => { if (!i.codes.some(x => x.value === k.value)) i.codes.push(k); });
      if (!ocrFailed) {
        try { i.text = await readText(i); } catch (_) { ocrFailed = true; }
      }
      i.done = true;
    }
    S.ocrFailed = ocrFailed;
    setBusy('');
    if (!S.cat) S.cat = suggestCategory();
    S.suggested = S.cat;
    applyItems();
    go('confirm');
  }
  function setBusy(t) { S.busy = t; const b = document.getElementById('busy'); if (b) { b.textContent = t; b.hidden = !t; } }

  function addPhoto(blob) {
    S.items.push({id: Math.random().toString(36).slice(2), blob, url: URL.createObjectURL(blob), text: '', codes: [], source: '', done: false});
  }

  /* ---------- Analyse : comparaisons, formats, réponses ---------- */
  const SECTION_RESULT = {coherence: 'auth', contrefacon: 'auth', provenance: 'prov', vol: 'vol'};
  const OFFICIAL = {
    correspond: 'La page affiche un produit qui correspond au modèle annoncé',
    different: 'La page affiche un autre modèle que celui annoncé',
    invalide: 'La page indique un numéro non valide ou introuvable',
    remplace: 'La page indique que le numéro correspond à un produit remplacé',
    autre: 'Autre message'
  };

  function analyseAll() {
    const c = cat(), F = [];
    S._factureMatch = false;
    const add = (result, sub, level, title, why, next, ask, source) => F.push({result, sub, level, title, why, next, ask, source});
    const used = c.sources.filter(s => S.values[s] && Object.values(S.values[s]).some(Boolean));
    const lab = s => SOURCES[s].toLowerCase();
    const rows = [];

    c.fields.forEach(f => {
      const vals = c.sources.map(s => ({s, v: (S.values[s] || {})[f.key]})).filter(x => x.v && String(x.v).trim());
      const row = {f, vals, state: vals.length > 1 ? 'same' : 'single'};
      rows.push(row);
      // Contrôles de format, sans jamais conclure à l'authenticité.
      vals.forEach(({s, v}) => {
        if (f.kind === 'imei') {
          const d = toDigits(v);
          if (luhn(d)) add('auth', 'coherence', 'info', `IMEI au format valide (${lab(s)})`, 'La clé de contrôle est correcte. Un IMEI valide peut être recopié : cela ne prouve ni l’authenticité ni l’absence de vol.', 'Vérifiez qu’il est identique sur l’écran (*#06#), la boîte et la facture.', '', 'Calcul de la clé de Luhn, sur votre appareil');
          else add('auth', 'coherence', 'alerte', `IMEI incorrect (${lab(s)})`, `« ${v} » ne respecte pas la clé de contrôle des IMEI. Le plus probable : une erreur de lecture ou de saisie.`, 'Relisez les 15 chiffres directement sur l’écran après *#06#.', '', 'Calcul de la clé de Luhn, sur votre appareil');
        }
        if (f.kind === 'gtin') {
          const d = toDigits(v);
          if (gtinOk(d)) add('auth', 'coherence', 'info', 'Code-barres lisible et valide', 'Un code-barres identifie une référence commerciale, pas cet exemplaire précis. Il peut être imprimé sur n’importe quelle boîte.', 'Ne vous fiez pas au code-barres seul.', '', 'Clé de contrôle GS1, sur votre appareil');
          else add('auth', 'coherence', 'info', 'Code-barres non valide', `« ${v} » ne respecte pas la clé de contrôle GS1 : probablement une erreur de lecture.`, 'Rescannez le code ou corrigez les chiffres.', '', 'Clé de contrôle GS1, sur votre appareil');
        }
        if (f.kind === 'serial' && c.serialLengths && !c.serialLengths.includes(ident(v).length))
          add('auth', 'coherence', 'info', `Numéro de série de longueur inhabituelle (${lab(s)})`, `Il compte ${ident(v).length} caractères ; ce fabricant en utilise généralement ${c.serialLengths.join(' ou ')}. Erreur de lecture possible.`, 'Relisez le numéro caractère par caractère.', '', 'Règle de format interne à Allego');
      });
      if (vals.length < 2 || f.kind === 'modele' || f.kind === 'anum') return;
      // Comparaison entre sources.
      const key = f.kind === 'size' ? (v => (normSize(v) || {}).key) : f.kind === 'imei' || f.kind === 'gtin' ? toDigits : f.key === 'capacite' ? normCap : ident;
      if (f.kind === 'size') {
        const sys = new Set(vals.map(x => (normSize(x.v) || {}).sys));
        if (sys.size > 1) { row.state = 'na'; add('auth', 'coherence', 'info', 'Tailles dans des systèmes différents', 'Les tailles EU, US et UK ne se comparent pas automatiquement.', 'Vérifiez la correspondance sur le guide des tailles de la marque.', '', 'Comparaison Allego'); return; }
      }
      const groups = {};
      vals.forEach(x => { const k = key(x.v) || '?'; (groups[k] = groups[k] || []).push(x.s); });
      const keys = Object.keys(groups);
      if (keys.length === 1) {
        add('auth', 'coherence', 'ok', `${f.label} identique : ${vals.map(x => lab(x.s)).join(', ')}`, 'Les informations concordent entre ces sources. Cela ne prouve pas l’authenticité : un identifiant peut être recopié sur tous les supports.', '', '', 'Comparaison Allego de vos saisies');
        if (vals.some(x => x.s === 'facture')) S._factureMatch = true;
        return;
      }
      row.state = 'diff';
      const parts = keys.map(k => groups[k].map(lab).join(' + ') + ' : « ' + vals.find(x => groups[k].includes(x.s)).v + ' »');
      const docs = vals.some(x => ['boite', 'facture', 'annonce'].includes(x.s)) && vals.some(x => ['produit', 'reglages', 'etiquette_g', 'etiquette_d'].includes(x.s));
      const lr = vals.every(x => /^etiquette_/.test(x.s));
      add('auth', 'coherence', 'alerte', `Écart : ${f.label.toLowerCase()}`, parts.join(' ; ') + '. ' + (lr
        ? 'Les deux chaussures ne portent pas la même information : paire reconstituée ou erreur de lecture.'
        : docs ? 'La boîte, la facture ou l’annonce peuvent concerner un autre exemplaire (échange en garantie, boîte récupérée, erreur de frappe). Une erreur de lecture est aussi possible.'
          : 'Une erreur de lecture est possible ; sinon, l’écart reste à expliquer.'),
      'Relisez les caractères sur l’objet lui-même, puis demandez au vendeur d’expliquer l’écart avant de payer.',
      `« Je ne retrouve pas la même information (${f.label.toLowerCase()}) partout, savez-vous pourquoi ? »`, 'Comparaison Allego de vos saisies');
      if (vals.some(x => x.s === 'facture')) add('prov', 'provenance', 'alerte', 'La facture ne correspond pas à cet exemplaire', `${f.label} de la facture différent de celui relevé ailleurs.`, 'Considérez la facture comme non rattachée à cet objet tant que l’écart n’est pas expliqué.', '', 'Comparaison Allego de vos saisies');
    });

    // Identification du modèle et cohérence des générations.
    if (c.family) {
      const fam = {};
      c.sources.forEach(s => {
        const v = S.values[s] || {};
        const txt = [v.modele, v.boitier, v.ecouteurs].filter(Boolean).join(' ');
        const set = c.family(txt);
        if (set.length) fam[s] = set;
      });
      const p = S.values.produit || {};
      if (c.id === 'airpods') {
        const AP = window.ALLEGO.AIRPODS, known = a => AP.some(f => f.buds.includes(a) || f.cases.includes(a));
        const nums = ((p.boitier || '') + ' ' + (p.ecouteurs || '')).toUpperCase().match(/\bA\d{4}\b/g) || [];
        nums.filter(a => !known(a)).forEach(a => add('auth', 'coherence', 'info', `${a} absent de la table locale`, 'La table d’Allego peut être incomplète (modèles récents). Ce n’est pas un indice de contrefaçon en soi.', 'Vérifiez ce numéro sur la page Apple « Identifier vos AirPods ».', '', 'Table locale Allego (d’après Apple, à revérifier)'));
        const bf = c.family(p.boitier), ef = c.family(p.ecouteurs);
        if (bf.length && ef.length && !bf.some(x => ef.includes(x)))
          add('auth', 'coherence', 'alerte', 'Boîtier et écouteurs de générations différentes', `Boîtier : ${bf.map(c.familyName).join(' / ')} ; écouteurs : ${ef.map(c.familyName).join(' / ')}. Un élément a pu être remplacé, ou la lecture est erronée ; les éléments peuvent ne pas fonctionner ensemble.`, 'Relisez les gravures et testez le jumelage complet.', '« Le boîtier et les écouteurs ont-ils été achetés ensemble ? »', 'Table locale Allego (d’après Apple, à revérifier)');
        const buds = (p.ecouteurs || '').toUpperCase().match(/\bA\d{4}\b/g) || [];
        if (buds.length > 1) {
          const sets = buds.map(b => c.family(b)).filter(x => x.length);
          if (sets.length > 1 && !sets.every(s => s.some(x => sets[0].includes(x))))
            add('auth', 'coherence', 'alerte', 'Les deux écouteurs ne sont pas de la même génération', buds.join(', ') + '.', 'Testez chaque écouteur et demandez l’explication.', '', 'Table locale Allego');
        }
      }
      const srcs = Object.keys(fam);
      S._ident = srcs.map(s => ({s, names: fam[s].map(c.familyName)}));
      for (let i = 0; i < srcs.length; i++) for (let j = i + 1; j < srcs.length; j++) {
        const a = fam[srcs[i]], b = fam[srcs[j]];
        if (!a.some(x => b.includes(x)))
          add('auth', 'coherence', 'alerte', `Modèle différent : ${lab(srcs[i])} / ${lab(srcs[j])}`, `${a.map(c.familyName).join(' / ')} d’un côté, ${b.map(c.familyName).join(' / ')} de l’autre. Le vendeur a pu se tromper de génération, ou les éléments ne correspondent pas.`, 'Identifiez le modèle à partir des gravures de l’objet, qui priment sur l’annonce.', '« L’annonce indique un autre modèle que celui gravé sur l’objet, pouvez-vous vérifier ? »', 'Comparaison Allego');
      }
      const all = srcs.map(s => fam[s]);
      if (all.length > 1 && all.every(a => a.some(x => all[0].includes(x))))
        add('auth', 'coherence', 'ok', 'Même modèle sur toutes les sources renseignées', srcs.map(lab).join(', ') + '.', '', '', 'Comparaison Allego');
    } else S._ident = [];

    // Résultat de la page officielle, rapporté par l'utilisateur.
    const O = S.official, src = 'Page officielle du fabricant, consultée par vous. Allego ne l’interroge pas.';
    if (O === 'correspond') add('auth', 'coherence', 'ok', 'La page officielle affiche le modèle attendu', 'Le numéro existe chez le fabricant et correspond à ce modèle. Cela ne prouve pas que l’objet devant vous porte légitimement ce numéro : un numéro valide peut être copié.', 'Vérifiez que le même numéro s’affiche dans les réglages de l’appareil.', '', src);
    if (O === 'different') add('auth', 'coherence', 'alerte', 'La page officielle affiche un autre modèle', 'Erreur de saisie possible, ou numéro provenant d’un autre produit.', 'Ressaisissez le numéro lu sur l’objet lui-même, pas sur la boîte.', '« Le numéro correspond à un autre modèle chez le fabricant, avez-vous une explication ? »', src);
    if (O === 'invalide') add('auth', 'coherence', 'alerte', 'Numéro refusé par la page officielle', 'Cause la plus fréquente : un caractère mal lu (0/O, 1/I, 5/S, 8/B). Sinon, le numéro peut être inventé.', 'Corrigez les caractères douteux et réessayez ; lisez le numéro dans les réglages de l’appareil.', '', src);
    if (O === 'remplace') add('auth', 'coherence', 'alerte', 'Numéro d’un produit remplacé', 'Le fabricant indique que ce numéro correspond à un produit remplacé. Explications possibles : (1) après un échange en garantie, la boîte ou la facture gardent l’ancien numéro alors que le produit en porte un nouveau, ce qui est courant et légitime ; (2) le numéro saisi vient de la boîte et non du produit ; (3) le numéro a été recopié d’un autre produit, comme on le voit sur certaines copies ; (4) une erreur de lecture. Ce message ne prouve ni une contrefaçon ni un vol.', 'Lisez le numéro dans Réglages > Bluetooth > (i), appareil connecté, et sous le couvercle ; vérifiez-le à son tour sur la page officielle. Demandez le document d’échange au vendeur. Si le numéro du produit lui-même est « remplacé », contactez l’assistance du fabricant avant de payer.', '« Le numéro indique un produit remplacé, avez-vous eu un échange en garantie et le document correspondant ? »', src);
    if (O === 'autre') add('auth', 'coherence', 'info', 'Message particulier de la page officielle', 'Allego ne peut pas interpréter ce message automatiquement.', 'Lisez le message et, en cas de doute, contactez l’assistance du fabricant.', '', src);

    // Réponses de la checklist.
    c.checklist.forEach(q => {
      const a = S.answers[q.id];
      if (!a || a === 'nsp') return;
      const r = SECTION_RESULT[q.section];
      if (a === q.good) {
        if (!q.isAccount) add(r, q.section, 'ok', q.q, q.weak ? 'Indice faible : à lui seul, il ne prouve rien.' : '', '', '', 'Votre constat devant le vendeur');
        else add('vol', 'vol', 'info', 'Aucune association à un autre compte constatée', 'Bon point pour l’usage. Cela ne prouve pas que l’objet n’est pas volé.', '', '', 'Votre constat devant le vendeur');
      } else {
        const level = q.isAccount ? 'attention' : q.weak ? 'info' : 'alerte';
        add(r, q.section, level, q.bad, q.why, q.next, '', 'Votre constat devant le vendeur');
      }
    });
    return {F, rows, used};
  }

  function verdicts(F) {
    const c = cat(), A = S.answers;
    const auth = F.filter(f => f.result === 'auth');
    const strongOk = c.checklist.filter(q => q.section === 'contrefacon' && !q.weak && A[q.id] === q.good).length;
    const compared = auth.some(f => f.level === 'ok' && f.sub === 'coherence');
    const authV = auth.some(f => f.level === 'alerte') ? {tone: 'warn', t: 'Anomalies détectées'}
      : compared && strongOk >= 2 ? {tone: 'good', t: 'Indices cohérents'}
        : {tone: 'none', t: 'Preuves insuffisantes'};
    const fact = A[c.checklist.find(q => q.role === 'facture').id];
    const factOk = A[c.checklist.find(q => q.role === 'facture_ok').id];
    const prov = F.filter(f => f.result === 'prov');
    const provV = prov.some(f => f.level === 'alerte' && f.title.startsWith('La facture')) ? {tone: 'warn', t: 'Document présenté, mais incohérent'}
      : fact === 'oui' && (factOk === 'oui' || S._factureMatch) ? {tone: 'good', t: 'Document présenté et cohérent, non vérifié auprès de l’émetteur'}
        : fact === 'oui' ? {tone: 'none', t: 'Document présenté, non rapproché de l’objet'}
          : fact === 'non' ? {tone: 'none', t: 'Aucun document présenté'}
            : {tone: 'none', t: 'Provenance non renseignée'};
    return {authV, provV, volV: {tone: 'none', t: 'Statut de vol non vérifiable'}};
  }

  /* ---------- Rendu ---------- */
  function go(screen) {
    if (screen !== 'capture') stopCamera();
    S.screen = screen;
    render();
    window.scrollTo(0, 0);
    const h = $('h1, h2'); if (h) { h.setAttribute('tabindex', '-1'); h.focus({preventScroll: true}); }
  }
  const demoBanner = () => S.demo ? `<div class="demo" role="note"><b>DÉMONSTRATION</b> · Données fictives : « ${esc(S.demo)} ». Aucun vrai produit, aucune vraie facture.</div>` : '';

  function render() {
    document.body.classList.toggle('is-demo', !!S.demo);
    app.innerHTML = demoBanner() + ({home, capture, confirm, results, transparence})[S.screen]() +
      `<p id="busy" class="busy" role="status" aria-live="polite" ${S.busy ? '' : 'hidden'}>${esc(S.busy)}</p>`;
    if (S.screen === 'capture') startCamera();
  }

  function home() {
    const groups = {};
    CATEGORIES.forEach(c => (groups[c.group] = groups[c.group] || []).push(c));
    return `
    <section class="hero">
      <h1>Scanne avant d’acheter.</h1>
      <p>Allego relève les informations d’un article d’occasion, les compare et vous guide pour les vérifier avec le vendeur avant de payer.</p>
      <button class="btn big primary" data-act="scan">📷 Scanner un article</button>
      <label class="btn">🖼️ Importer des photos<input type="file" accept="image/*" multiple hidden data-act="import"></label>
      <button class="btn" data-act="manual">⌨️ Saisir une référence</button>
    </section>
    <p class="privacy">🔒 Rien n’est conservé : photos, factures et numéros restent dans cet onglet et disparaissent quand vous le fermez ou touchez « Tout effacer ». La lecture se fait sur votre appareil.</p>
    <section class="card">
      <h2>Essayer avec des données fictives</h2>
      <p class="muted">Ces exemples sont inventés pour la démonstration.</p>
      <div class="row">${Object.keys(DEMOS).map(k => `<button class="btn" data-act="demo" data-k="${k}">${esc(DEMOS[k].label)}</button>`).join('')}</div>
    </section>
    <section class="card">
      <h2>Catégories</h2>
      ${Object.keys(groups).map(g => `<h3 class="grp">${esc(g)}</h3><ul class="cats">${groups[g].map(c => `<li><span aria-hidden="true">${c.icon}</span> ${esc(c.label)} <span class="tag ${c.niveau}">${c.niveau === 'complet' ? 'parcours complet' : 'contrôles génériques'}</span></li>`).join('')}</ul>`).join('')}
    </section>
    <p class="center"><button class="link" data-act="go" data-to="transparence">Ce qui fonctionne vraiment dans ce prototype</button></p>`;
  }

  function capture() {
    return `
    <h2>1. Photographier l’article</h2>
    <p class="muted">Visez l’étiquette, le numéro de série, le code-barres, la facture ou l’annonce. Prenez plusieurs photos si besoin.</p>
    <div class="cam"><video id="video" playsinline muted aria-label="Aperçu de la caméra"></video><p id="camMsg" class="cam-msg">Ouverture de la caméra…</p></div>
    <p id="liveCodes" class="muted" aria-live="polite">${S.items.filter(i => !i.blob).map(i => `Code lu : <b>${esc(i.codes[0].value)}</b>`).join('<br>')}</p>
    <div class="row">
      <button class="btn primary" data-act="shoot">📸 Prendre la photo</button>
      <label class="btn">🖼️ Importer<input type="file" accept="image/*" multiple hidden data-act="import"></label>
    </div>
    ${thumbs()}
    <div class="row sticky">
      <button class="btn" data-act="go" data-to="home">Retour</button>
      <button class="btn primary" data-act="analyse" ${S.items.length ? '' : 'disabled'}>Continuer (${S.items.length})</button>
    </div>`;
  }
  const thumbs = () => S.items.some(i => i.url) ? `<ul class="thumbs">${S.items.filter(i => i.url).map((i, n) => `<li><img src="${i.url}" alt="Photo ${n + 1}"><button class="x" data-act="rm" data-id="${i.id}" aria-label="Retirer la photo ${n + 1}">×</button></li>`).join('')}</ul>` : '';

  async function startCamera() {
    const msg = $('#camMsg'), video = $('#video');
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { msg.textContent = 'Caméra indisponible dans ce navigateur. Importez une photo ou saisissez la référence.'; return; }
    try {
      if (!stream) stream = await navigator.mediaDevices.getUserMedia({video: {facingMode: {ideal: 'environment'}, width: {ideal: 1920}}, audio: false});
      if (S.screen !== 'capture') return stopCamera();
      video.srcObject = stream; await video.play();
      msg.textContent = 'BarcodeDetector' in window ? 'Lecture des codes-barres en direct…' : 'Prenez une photo : les codes-barres seront lus ensuite.';
      if ('BarcodeDetector' in window && !scanTimer) {
        const det = new window.BarcodeDetector();
        scanTimer = setInterval(async () => {
          const v = $('#video'); if (!v || v.readyState < 2) return;
          try {
            (await det.detect(v)).forEach(b => {
              if (S.items.some(i => i.codes.some(k => k.value === b.rawValue))) return;
              S.items.push({id: Math.random().toString(36).slice(2), url: null, blob: null, text: '', codes: [{value: b.rawValue, format: b.format}], source: '', done: true});
              if (navigator.vibrate) navigator.vibrate(60);
              const l = $('#liveCodes'); if (l) l.innerHTML = S.items.filter(i => !i.blob).map(i => `Code lu : <b>${esc(i.codes[0].value)}</b>`).join('<br>');
              const b2 = $('[data-act="analyse"]'); if (b2) { b2.disabled = false; b2.textContent = `Continuer (${S.items.length})`; }
            });
          } catch (_) { /* image non exploitable : on réessaie au tour suivant */ }
        }, 450);
      }
    } catch (_) { msg.textContent = 'Accès à la caméra refusé ou impossible. Importez une photo ou saisissez la référence.'; }
  }
  function shoot() {
    const v = $('#video'); if (!v || !v.videoWidth) return;
    const cv = document.createElement('canvas');
    cv.width = v.videoWidth; cv.height = v.videoHeight;
    cv.getContext('2d').drawImage(v, 0, 0);
    cv.toBlob(b => { if (b) { addPhoto(b); render(); } }, 'image/jpeg', 0.92);
  }

  const AMB = /[0OQD1IL5S8B2Z6G]/;
  function charCheck(v, kind) {
    const s = String(v || '');
    if (!s || !['serial', 'imei', 'gtin', 'anum', 'style', 'text'].includes(kind)) return '';
    const chars = s.split('').map(ch => AMB.test(ch.toUpperCase()) ? `<span class="amb">${esc(ch)}</span>` : esc(ch)).join('');
    const n = s.split('').filter(ch => AMB.test(ch.toUpperCase())).length;
    return `<span class="mono">${chars}</span>${n ? ` <small>${n} caractère${n > 1 ? 's' : ''} souvent confondu${n > 1 ? 's' : ''} (0/O, 1/I, 5/S, 8/B…) : vérifiez-le${n > 1 ? 's' : ''} sur l’objet.</small>` : ''}`;
  }

  function confirm() {
    const c = cat();
    const groups = {};
    CATEGORIES.forEach(k => (groups[k.group] = groups[k.group] || []).push(k));
    return `
    <h2>2. Confirmer la catégorie et les caractères</h2>
    ${S.ocrFailed ? '<p class="note">La lecture du texte n’a pas pu démarrer (connexion ou appareil). Saisissez les caractères vous-même.</p>' : ''}
    <section class="card">
      <h3>Catégorie ${S.suggested && S.suggested === S.cat ? '<span class="tag">proposée par Allego, à confirmer</span>' : ''}</h3>
      <div class="chips" role="radiogroup" aria-label="Catégorie">${CATEGORIES.map(k => `<button role="radio" aria-checked="${k.id === S.cat}" class="chip ${k.id === S.cat ? 'on' : ''}" data-act="cat" data-id="${k.id}">${k.icon} ${esc(k.label)}</button>`).join('')}</div>
      ${c && c.niveau === 'partiel' ? '<p class="note">Catégorie en préparation : seuls des contrôles génériques sont proposés.</p>' : ''}
    </section>
    ${S.items.length ? `<section class="card"><h3>Ce qui a été lu</h3>${S.items.map((i, n) => `
      <div class="item">
        ${i.url ? `<img src="${i.url}" alt="Photo ${n + 1}">` : '<span class="codeonly" aria-hidden="true">▥</span>'}
        <div>
          <label>Cette ${i.url ? 'photo' : 'lecture'} montre
            <select data-act="isrc" data-id="${i.id}" ${c ? '' : 'disabled'}><option value="">— choisir —</option>${(c ? c.sources : []).map(s => `<option value="${s}" ${i.source === s ? 'selected' : ''}>${esc(SOURCES[s])}</option>`).join('')}</select>
          </label>
          ${i.codes.length ? `<p class="small">Code${i.codes.length > 1 ? 's' : ''} : ${i.codes.map(k => `<b class="mono">${esc(k.value)}</b> <span class="muted">(${esc(k.format || 'code')})</span>`).join(', ')}</p>` : ''}
          ${i.url ? `<details><summary>Texte reconnu${i.text ? '' : ' (aucun)'}</summary><textarea data-act="itext" data-id="${i.id}" rows="4">${esc(i.text)}</textarea></details>` : ''}
        </div>
      </div>`).join('')}</section>` : ''}
    ${c ? `<p class="muted">Remplissez ce que vous avez. Allego compare chaque information entre les sources. <b>Les valeurs lues automatiquement sont à vérifier.</b></p>
      ${c.sources.map(s => sourceBlock(c, s)).join('')}
      <div class="row sticky"><button class="btn" data-act="go" data-to="home">Retour</button><button class="btn primary" data-act="go" data-to="results">3. Voir les premiers indices</button></div>`
    : '<p class="note">Choisissez une catégorie pour continuer.</p>'}`;
  }
  function sourceBlock(c, s) {
    const v = S.values[s] || {};
    const filled = Object.values(v).filter(Boolean).length;
    return `<details class="card src" ${filled || s === c.sources[0] ? 'open' : ''}><summary><b>${esc(SOURCES[s])}</b> <span class="muted">${filled ? filled + ' renseigné' + (filled > 1 ? 's' : '') : 'vide'}</span></summary>
      ${s === 'annonce' ? `<label>Texte de l’annonce (copier-coller)<textarea data-act="annonce" rows="3" placeholder="Collez ici le titre et la description">${esc(S.annonce)}</textarea></label>` : ''}
      ${c.fields.filter(f => f.in.includes(s)).map(f => `
        <label>${esc(f.label)} ${S.auto[s + '.' + f.key] ? '<span class="tag auto">lu automatiquement</span>' : ''}
          <input data-act="field" data-src="${s}" data-key="${f.key}" data-kind="${f.kind}" value="${esc(v[f.key] || '')}" ${['serial', 'imei', 'gtin', 'anum', 'style'].includes(f.kind) ? 'class="mono" autocapitalize="characters" autocomplete="off" spellcheck="false"' : ''} ${f.kind === 'imei' || f.kind === 'gtin' ? 'inputmode="numeric"' : ''} placeholder="${esc(f.hint)}">
        </label>
        <p class="cc" id="cc-${s}-${f.key}">${charCheck(v[f.key], f.kind)}</p>`).join('')}
    </details>`;
  }

  const ICON = {ok: '✓', alerte: '!', attention: '!', info: 'i'};
  const findingHtml = f => `<li class="f ${f.level}"><span class="ic" aria-hidden="true">${ICON[f.level]}</span><div><b>${esc(f.title)}</b>${f.why ? `<p>${esc(f.why)}</p>` : ''}${f.next ? `<p><b>Action suivante :</b> ${esc(f.next)}</p>` : ''}${f.ask ? `<p class="ask"><b>À demander au vendeur :</b> ${esc(f.ask)}</p>` : ''}<p class="src-l">Source : ${esc(f.source)}</p></div></li>`;
  const LEVEL_LABEL = {ok: 'point concordant', alerte: 'anomalie', attention: 'à régler', info: 'information'};

  function results() {
    const c = cat();
    if (!c) { S.screen = 'confirm'; return confirm(); }
    const {F, rows} = analyseAll();
    const V = verdicts(F);
    const pending = sec => c.checklist.filter(q => sec.includes(q.section) && (!S.answers[q.id] || S.answers[q.id] === 'nsp')).map(q => q.q);
    const sorted = list => list.slice().sort((a, b) => ['alerte', 'attention', 'info', 'ok'].indexOf(a.level) - ['alerte', 'attention', 'info', 'ok'].indexOf(b.level));
    const sub = (list, title) => list.length ? `<h4>${title}</h4><ul class="fl">${sorted(list).map(findingHtml).join('')}</ul>` : `<h4>${title}</h4><p class="muted">Rien de relevé pour l’instant.</p>`;
    const authF = F.filter(f => f.result === 'auth');
    const answered = c.checklist.filter(q => S.answers[q.id]).length;

    const tabs = `<div class="tabs" role="tablist">
      <button role="tab" aria-selected="${S.tab === 'resultats'}" data-act="tab" data-t="resultats">Résultats</button>
      <button role="tab" aria-selected="${S.tab === 'checklist'}" data-act="tab" data-t="checklist">Checklist vendeur (${answered}/${c.checklist.length})</button></div>`;

    if (S.tab === 'checklist') return `<h2>4. Vérifier devant le vendeur</h2>${tabs}
      <p class="muted">Faites ces vérifications avec le vendeur, avant de payer. Vos réponses mettent à jour les résultats.</p>
      ${[['coherence', 'Correspondance des références'], ['contrefacon', 'Ouverture, jumelage et fonctionnement'], ['provenance', 'Facture et provenance'], ['vol', 'Association à un ancien compte']].map(([sec, t]) => {
        const qs = c.checklist.filter(q => q.section === sec);
        return qs.length ? `<section class="card"><h3>${t}</h3>${qs.map(q => `<fieldset class="q"><legend>${esc(q.q)}${q.weak ? ' <span class="tag">indice faible</span>' : ''}</legend>
          <div class="seg">${['oui', 'non', 'nsp'].map(a => `<button data-act="ans" data-q="${q.id}" data-a="${a}" aria-pressed="${S.answers[q.id] === a}">${a === 'nsp' ? 'Je ne sais pas' : a === 'oui' ? 'Oui' : 'Non'}</button>`).join('')}</div></fieldset>`).join('')}</section>` : '';
      }).join('')}
      ${c.expert ? `<p class="note">🧑‍🔬 ${esc(c.expert)}</p>` : ''}
      <div class="row sticky"><button class="btn primary" data-act="tab" data-t="resultats">Voir les résultats</button></div>`;

    return `<h2>3. Premiers indices</h2>${tabs}
    <section class="card">
      <h3>${c.icon} ${esc(c.label)}${c.niveau === 'partiel' ? ' <span class="tag partiel">contrôles génériques</span>' : ''}</h3>
      ${S._ident.length ? `<p><b>Modèle identifié :</b></p><ul class="plain">${S._ident.map(x => `<li>${esc(SOURCES[x.s])} : <b>${esc(x.names.join(' ou '))}</b></li>`).join('')}</ul>` : '<p class="muted">Modèle non identifié automatiquement.</p>'}
      <table class="cmp"><caption>Comparaison des informations</caption><tbody>
        ${rows.filter(r => r.vals.length).map(r => `<tr><th scope="row">${esc(r.f.label)}</th><td>${r.vals.map(x => `<span class="small muted">${esc(SOURCES[x.s])}</span><br><span class="${r.f.kind === 'modele' ? '' : 'mono'}">${esc(x.v)}</span>`).join('<hr>')}</td><td class="st ${r.state}">${{same: '', diff: '≠ différent', single: 'une seule source', na: 'non comparable'}[r.state]}</td></tr>`).join('') || '<tr><td colspan="3" class="muted">Aucune information saisie.</td></tr>'}
      </tbody></table>
      <button class="link" data-act="go" data-to="confirm">Corriger les informations</button>
    </section>

    ${c.official ? `<section class="card official">
      <h3>Vérification officielle du fabricant</h3>
      <p>${esc(c.official.note)}</p>
      ${serialsToCopy().map(x => `<button class="btn" data-act="copy" data-v="${esc(x.v)}">Copier <span class="mono">${esc(x.v)}</span> <span class="small muted">(${esc(x.from)})</span></button>`).join('')}
      ${serialsToCopy().length > 1 ? '<p class="small">Plusieurs numéros différents : vérifiez d’abord celui du produit lui-même, puis celui de la boîte.</p>' : ''}
      <a class="btn primary" href="${c.official.url}" target="_blank" rel="noopener noreferrer">${esc(c.official.label)} ↗</a>
      <fieldset class="q"><legend>Qu’affiche la page officielle ?</legend>
        ${[['', 'Pas encore consultée']].concat(Object.entries(OFFICIAL)).map(([k, t]) => `<label class="radio"><input type="radio" name="official" data-act="official" value="${k}" ${S.official === k ? 'checked' : ''}> ${esc(t)}</label>`).join('')}
      </fieldset>
    </section>` : ''}

    ${card('1', 'Authenticité', V.authV, 'Ce résultat ne certifie jamais qu’un article est authentique.',
      sub(authF.filter(f => f.sub === 'coherence'), 'Cohérence du produit') + sub(authF.filter(f => f.sub === 'contrefacon'), 'Indices de contrefaçon'),
      'Vos photos et saisies, comparaisons faites sur votre appareil' + (c.official ? ', page officielle consultée par vous' : '') + ', vos constats.',
      'Un code-barres identifie une référence, pas un exemplaire. Un numéro de série valide peut être copié. Une photo seule ne permet pas de tout authentifier. Aucun pourcentage n’est calculé : aucune méthode validée n’existe ici.',
      pending(['coherence', 'contrefacon']).concat(c.official && !S.official ? ['Consulter la page officielle du fabricant'] : []).concat(c.expert ? [c.expert] : []))}

    ${card('2', 'Provenance', V.provV, 'Documents présentés par le vendeur. Allego ne peut pas vérifier une facture auprès de l’enseigne.',
      sub(F.filter(f => f.result === 'prov'), 'Constats'),
      'Documents montrés par le vendeur et vos constats.',
      'Une facture peut être modifiée ou concerner un autre exemplaire. Seule l’enseigne émettrice peut la confirmer.',
      pending(['provenance']))}

    ${card('3', 'Signalement de vol', V.volV, 'Aucun registre accessible et fiable n’est connecté à Allego pour cette catégorie.',
      sub(F.filter(f => f.result === 'vol'), 'Constats'),
      'Aucune source autorisée connectée (police, assureurs, fabricant, opérateurs).',
      'L’absence de signalement ne prouverait pas qu’un objet n’est pas volé. Un compte encore associé ne prouve pas un vol : c’est souvent un oubli du vendeur.',
      pending(['vol']).concat(['En cas de doute sérieux : ne payez pas, ne confrontez pas le vendeur, et signalez l’annonce à la plateforme.']))}

    <section class="card"><h3>Contrôles encore indisponibles pour « ${esc(c.label)} »</h3><ul>${c.unavailable.map(u => `<li>${esc(u)}</li>`).join('')}</ul></section>
    <div class="row">
      <button class="btn" data-act="summary">Copier le résumé</button>
      <button class="btn danger" data-act="wipe">Tout effacer</button>
    </div>
    <div class="row sticky"><button class="btn primary" data-act="tab" data-t="checklist">Checklist devant le vendeur</button></div>`;
  }
  function card(n, title, v, sub, body, source, limits, todo) {
    return `<article class="res ${v.tone}" aria-labelledby="r${n}">
      <header><span class="k">${n} · ${esc(title)}</span><h3 id="r${n}">${esc(v.t)}</h3><p>${esc(sub)}</p></header>
      ${body}
      <h4>Source</h4><p>${esc(source)}</p>
      <h4>Limites</h4><p>${esc(limits)}</p>
      <h4>Reste à vérifier</h4>${todo.length ? `<ul>${todo.map(t => `<li>${esc(t)}</li>`).join('')}</ul>` : '<p class="muted">Tous les points de la checklist ont été renseignés.</p>'}
    </article>`;
  }
  function serialsToCopy() {
    const out = [];
    ['produit', 'reglages', 'boite', 'facture'].forEach(s => {
      const raw = (S.values[s] || {}).serie || (S.values[s] || {}).imei; if (!raw) return;
      const v = ident(raw), have = out.find(x => x.v === v);
      if (have) have.from += ', ' + SOURCES[s].split(' (')[0].toLowerCase(); else out.push({v, from: SOURCES[s].split(' (')[0].toLowerCase()});
    });
    return out;
  }
  function summaryText() {
    const c = cat(), {F} = analyseAll(), V = verdicts(F);
    return [S.demo ? '*** DÉMONSTRATION — DONNÉES FICTIVES ***' : '', `Allego — ${c.label}`,
      `1. Authenticité : ${V.authV.t} (ne certifie pas l’authenticité)`,
      `2. Provenance : ${V.provV.t}`, `3. Signalement de vol : ${V.volV.t}`, '',
      ...F.filter(f => f.level !== 'ok').map(f => `- ${f.title}${f.next ? ' → ' + f.next : ''}`)].filter((l, i) => l || i > 0).join('\n');
  }

  function transparence() {
    const T = [
      ['Fonctionne réellement', [
        'Caméra du téléphone, prise de plusieurs photos et import d’images (rien n’est envoyé).',
        'Lecture des codes-barres : en direct avec le détecteur intégré au navigateur (Chrome Android notamment), sinon sur photo avec la bibliothèque ZXing.',
        'Lecture du texte sur photo avec Tesseract.js, sur l’appareil (il faut une connexion pour charger la bibliothèque la première fois).',
        'Contrôle de la clé des IMEI (Luhn) et des codes-barres (GS1).',
        'Identification des AirPods par numéro A…, avec une table locale relevée d’après Apple, à revérifier.',
        'Repérage des modèles de téléphones et des marques de baskets dans le texte.',
        'Comparaison entre étiquette, boîte, réglages, annonce et facture, et détection des écarts.',
        'Checklists, résultats séparés, sources, limites et actions suivantes.',
        'Effacement : aucune donnée n’est stockée (ni serveur, ni stockage du navigateur).'
      ]],
      ['Laissé à l’utilisateur (pas simulé)', [
        'Vérification sur la page officielle d’Apple : Allego ouvre le lien, vous indiquez ce que la page affiche.',
        'Constats devant le vendeur : jumelage, réglages, compte associé, facture.'
      ]],
      ['Nécessite une API ou un partenariat', [
        'Interrogation automatique d’Apple ou d’autres fabricants (numéro de série, garantie, verrouillage d’activation).',
        'Base TAC de la GSMA pour identifier un téléphone par son IMEI ; base GSMA ou des opérateurs pour les IMEI déclarés volés.',
        'Fichier national des cycles identifiés : uniquement via un opérateur de marquage agréé.',
        'Fichiers de police ou d’assureurs : aucun accès public ; partenariat institutionnel indispensable.',
        'Fiche produit à partir d’un code-barres : base GS1 ou fournisseur commercial.',
        'Vérification d’une facture : partenariat avec les enseignes.'
      ]],
      ['Nécessite un expert', [
        'Authentification des baskets de valeur, des sacs de luxe, des montres et des bijoux.',
        'Toute conclusion fondée sur des photos de détails.'
      ]],
      ['Données de démonstration', [
        'Les trois exemples (AirPods, téléphone, baskets) sont fictifs et signalés par un bandeau « DÉMONSTRATION ».',
        'L’IMEI de démonstration est un exemple public, valide en format mais sans lien avec un vrai appareil.'
      ]]
    ];
    return `<h2>Ce qui fonctionne vraiment</h2>${T.map(([t, l]) => `<section class="card"><h3>${t}</h3><ul>${l.map(x => `<li>${esc(x)}</li>`).join('')}</ul></section>`).join('')}
      <p class="note">Les bibliothèques de lecture sont téléchargées depuis cdn.jsdelivr.net : vos images ne sont pas envoyées, seul le code est récupéré. En production, il faudra les héberger sur le site.</p>
      <div class="row"><button class="btn" data-act="go" data-to="home">Retour</button></div>`;
  }

  /* ---------- Démonstrations (fictives) ---------- */
  const DEMOS = {
    airpods: {label: '🎧 AirPods (fictif)', cat: 'airpods', official: 'remplace',
      annonce: 'Vends AirPods Pro 2 USB-C, très bon état, facture fournie.',
      values: {
        produit: {boitier: 'A2968', ecouteurs: 'A3047 A3048', serie: 'DEM4K7PQ2X'},
        boite: {modele: 'AirPods Pro (2e génération)', serie: 'DEM9X3LT8W', reference: 'DEMO2ZM/A'},
        reglages: {serie: 'DEM4K7PQ2X'},
        annonce: {modele: 'AirPods Pro 2'},
        facture: {modele: 'AirPods Pro (2e génération)', serie: 'DEM9X3LT8W'}
      }},
    telephone: {label: '📱 Téléphone (fictif)', cat: 'telephone',
      annonce: 'iPhone 13 256 Go, batterie 88 %, débloqué tout opérateur.',
      values: {
        boite: {modele: 'iPhone 13', capacite: '128 Go', imei: '490154203237518'},
        reglages: {modele: 'iPhone 13', capacite: '128 Go', imei: '490154203237518'},
        annonce: {modele: 'iPhone 13', capacite: '256 Go'},
        facture: {modele: 'iPhone 13 128 Go', imei: '490154203237518'}
      }},
    baskets: {label: '👟 Baskets (fictif)', cat: 'baskets',
      annonce: 'Nike Dunk Low blanc et noir, taille 42, portées 3 fois.',
      values: {
        etiquette_g: {reference: 'DD1391-100', taille: '42 EU', dates: '03/01/22 – 05/02/22'},
        etiquette_d: {reference: 'DD1391-100', taille: '42 EU', dates: '03/01/22 – 05/02/22'},
        boite: {modele: 'Nike Dunk Low', reference: 'DD1391-101', taille: '42 EU'},
        annonce: {modele: 'Nike Dunk Low', taille: '42'}
      }}
  };

  /* ---------- Événements ---------- */
  app.addEventListener('click', async e => {
    const b = e.target.closest('[data-act]'); if (!b || b.tagName === 'INPUT' || b.tagName === 'SELECT' || b.tagName === 'TEXTAREA') return;
    const a = b.dataset.act;
    if (a === 'scan') go('capture');
    else if (a === 'manual') go('confirm');
    else if (a === 'go') go(b.dataset.to);
    else if (a === 'shoot') shoot();
    else if (a === 'rm') { const i = S.items.find(x => x.id === b.dataset.id); if (i) URL.revokeObjectURL(i.url); S.items = S.items.filter(x => x.id !== b.dataset.id); render(); }
    else if (a === 'analyse') { stopCamera(); await analyse(); }
    else if (a === 'cat') { S.cat = b.dataset.id; S.answers = {}; applyItems(); render(); }
    else if (a === 'tab') { S.tab = b.dataset.t; render(); window.scrollTo(0, 0); }
    else if (a === 'ans') { S.answers[b.dataset.q] = b.dataset.a; const y = window.scrollY; render(); window.scrollTo(0, y); }
    else if (a === 'demo') {
      wipe(); const d = DEMOS[b.dataset.k];
      Object.assign(S, {demo: d.label.replace(/^\S+\s/, ''), cat: d.cat, values: JSON.parse(JSON.stringify(d.values)), annonce: d.annonce, official: d.official || ''});
      go('results');
    } else if (a === 'copy' || a === 'summary') {
      const txt = a === 'copy' ? b.dataset.v : summaryText();
      try { await navigator.clipboard.writeText(txt); b.textContent = 'Copié ✓'; } catch (_) { window.prompt('Copiez le texte :', txt); }
    } else if (a === 'wipe') {
      if (window.confirm('Effacer toutes les photos et informations de cette vérification ?')) { wipe(); go('home'); }
    }
  });
  app.addEventListener('change', e => {
    const t = e.target, a = t.dataset.act;
    if (a === 'import') {
      [...t.files].forEach(f => f.type.startsWith('image/') && addPhoto(f));
      t.value = '';
      if (S.items.length) { stopCamera(); analyse(); }
    } else if (a === 'isrc') {
      const i = S.items.find(x => x.id === t.dataset.id); i.source = t.value; applyItems(); render();
    } else if (a === 'official') { S.official = t.value; const y = window.scrollY; render(); window.scrollTo(0, y); }
  });
  app.addEventListener('input', e => {
    const t = e.target, a = t.dataset.act;
    if (a === 'field') {
      let v = t.value;
      if (t.dataset.kind === 'imei' || t.dataset.kind === 'gtin') { const d = toDigits(v); if (d !== v.replace(/\s/g, '')) { v = d; t.value = d; } }
      (S.values[t.dataset.src] = S.values[t.dataset.src] || {})[t.dataset.key] = v;
      delete S.auto[t.dataset.src + '.' + t.dataset.key];
      const cc = document.getElementById(`cc-${t.dataset.src}-${t.dataset.key}`); if (cc) cc.innerHTML = charCheck(v, t.dataset.kind);
    } else if (a === 'annonce') S.annonce = t.value;
    else if (a === 'itext') { const i = S.items.find(x => x.id === t.dataset.id); i.text = t.value; }
  });
  app.addEventListener('focusout', e => {
    // Après collage de l'annonce ou correction d'un texte lu : on extrait ce qui manque.
    if (['annonce', 'itext'].includes(e.target.dataset.act) && cat()) { applyItems(); render(); }
  });
  document.getElementById('wipeTop').addEventListener('click', () => { if (window.confirm('Tout effacer et revenir à l’accueil ?')) { wipe(); go('home'); } });
  document.getElementById('homeLink').addEventListener('click', e => { e.preventDefault(); if (S.screen !== 'home' && (S.items.length || S.cat) && !window.confirm('Revenir à l’accueil ? Les informations saisies seront effacées.')) return; wipe(); go('home'); });

  render();
})();
