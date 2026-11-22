const $ = id => document.getElementById(id);
const themeStyles = {
  editorial: { name: 'Éditorial', accent: '#d9a67d', background: '#291d1e', ink: '#fff1da' },
  workshop: { name: 'Atelier clair', accent: '#355bb7', background: '#edf2ff', ink: '#18243c' },
  manga: { name: 'Manga original', accent: '#ff763b', background: '#23203b', ink: '#fff5e8' },
  dimension: { name: 'Relief animé', accent: '#c1a2ff', background: '#221934', ink: '#fff2ff' }
};
const defaults = {
  name: '', tagline: '', type: 'site', theme: 'manga', accent: themeStyles.manga.accent,
  photo: '', sections: [{ title: 'Présentation', text: '' }, { title: 'Contact', text: '' }], notes: ''
};
const studioHost = 'https://atelier.velocemercato.fr';
const storageKey = 'vm-studio-brouillon-v1';
const suiviKey = 'vm-studio-suivi-prive-v1';
let suivi = null;
try { suivi = JSON.parse(localStorage.getItem(suiviKey)); } catch {}
const history = [];
const short = (value, length) => typeof value === 'string' ? value.slice(0, length) : '';
const color = /^#[0-9a-f]{6}$/i;
function safeURL(value) {
  try { const u = new URL(value); return ['https:', 'mailto:', 'tel:'].includes(u.protocol) && !u.username && !u.password ? u.href : ''; } catch { return ''; }
}
const validPhoto = value => typeof value === 'string' && value.length < 850000 && /^data:image\/(?:jpeg|png|webp);base64,[a-z0-9+/]+=*$/i.test(value);
const element = (tag, text, className) => {
  const node = document.createElement(tag);
  if (text) node.textContent = text;
  if (className) node.className = className;
  return node;
};
function validate(raw) {
  if (!raw || (raw.version && raw.version !== 1)) throw Error('Ce fichier de brouillon est incompatible.');
  const theme = Object.hasOwn(themeStyles, raw.theme) ? raw.theme : defaults.theme;
  return {
    name: short(raw.name, 80), tagline: short(raw.tagline, 150), notes: short(raw.notes, 1200),
    theme, type: raw.type === 'app' ? 'app' : 'site',
    accent: color.test(raw.accent) ? raw.accent : themeStyles[theme].accent,
    button: short(raw.button, 60), link: safeURL(raw.link),
    photo: validPhoto(raw.photo) ? raw.photo : '',
    sections: Array.isArray(raw.sections) ? raw.sections.slice(0, 10).filter(Boolean).map(section =>
      ({ title: short(section.title, 80), text: short(section.text, 1600) })) : structuredClone(defaults.sections)
  };
}
let draft = structuredClone(defaults);
try {
  const saved = localStorage.getItem(storageKey);
  if (saved) draft = validate(JSON.parse(saved));
} catch {}
let activeSection = -1;
let pendingPhoto = 0;
let pendingSave;

function save() {
  clearTimeout(pendingSave);
  pendingSave = setTimeout(() => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(draft));
      $('save-note').textContent = 'Brouillon enregistré sur cet appareil.';
    } catch {
      $('save-note').textContent = 'Téléchargez une copie pour conserver votre brouillon sur cet appareil.';
    }
  }, 80);
}
addEventListener('pagehide', () => {
  try { localStorage.setItem(storageKey, JSON.stringify(draft)); } catch {}
});
function remember() {
  history.push(structuredClone(draft));
  if (history.length > 12) history.shift();
  $('undo').disabled = false;
}
function status(text) { $('feedback').textContent = text; }
function updateInput(id, key, next) {
  const control = $(id);
  control.addEventListener('focus', remember, { once: true });
  control.addEventListener('input', () => {
    if (next) next(control.value);
    else draft[key] = control.value;
    refresh(false);
  });
  control.addEventListener('change', () => control.addEventListener('focus', remember, { once: true }));
}
function preview() {
  const target = $('preview');
  const focus = document.activeElement?.closest('#preview') && document.activeElement.dataset.tab;
  const main = element('div', '', 'mock ' + draft.theme);
  const style = themeStyles[draft.theme];
  main.style.setProperty('--site-bg', style.background);
  main.style.setProperty('--site-ink', style.ink);
  main.style.setProperty('--site-accent', draft.accent);
  const nav = element('nav');
  nav.setAttribute('aria-label', 'Navigation de la maquette');
  const show = index => { activeSection = index; preview(); };
  const navButton = (title, index) => {
    const button = element('button', title);
    button.type = 'button';
    button.dataset.tab = String(index);
    button.setAttribute('aria-pressed', String(activeSection === index));
    button.onclick = () => show(index);
    nav.append(button);
  };
  navButton(draft.type === 'app' ? 'Tableau de bord' : 'Accueil', -1);
  draft.sections.forEach((section, index) => {
    if (section.title) navButton(section.title, index);
  });
  main.append(nav);
  if (activeSection < 0 || !draft.sections[activeSection]) {
    const hero = element('div', '', 'mock-hero' + (draft.photo ? ' has-image' : ''));
    const copy = element('div');
    copy.append(element('h3', draft.name || (draft.type === 'app' ? 'Votre application' : 'Votre activité')));
    if (draft.tagline) copy.append(element('p', draft.tagline));
    if (draft.button) {
      const call = element(draft.link ? 'a' : 'button', draft.button, 'primary');
      if (draft.link) { call.href = draft.link; call.target = '_blank'; call.rel = 'noopener noreferrer'; }
      else { call.type = 'button'; call.onclick = () => { activeSection = draft.sections.length - 1; preview(); }; }
      copy.append(call);
    }
    hero.append(copy);
    if (draft.photo) {
      const img = element('img');
      img.src = draft.photo;
      img.alt = 'Photo principale de la maquette';
      hero.append(img);
    }
    main.append(hero);
  }
  draft.sections.forEach((section, index) => {
    if ((activeSection >= 0 && activeSection !== index) || (!section.title && !section.text)) return;
    const block = element('section', '', 'mock-section');
    block.append(element('h4', section.title || 'Rubrique'));
    if (section.text) block.append(element('p', section.text));
    main.append(block);
  });
  target.replaceChildren(main);
  if (focus !== false && typeof focus === 'string') target.querySelector('[data-tab="' + focus + '"]')?.focus({ preventScroll: true });
}
function sectionEditor() {
  $('section-editor').replaceChildren();
  draft.sections.forEach((section, index) => {
    const group = element('div', '', 'section-edit');
    for (const [key, label, limit, tag] of [['title', 'Titre', 80, 'input'], ['text', 'Texte', 1600, 'textarea']]) {
      const field = element(tag);
      field.maxLength = limit;
      if (tag === 'textarea') field.rows = 2;
      field.value = section[key];
      field.addEventListener('focus', remember, { once: true });
      field.onchange = () => field.addEventListener('focus', remember, { once: true });
      field.oninput = () => { section[key] = field.value; refresh(false); };
      const caption = element('label', label);
      caption.append(field);
      group.append(caption);
    }
    const actions = element('div', '', 'actions');
    for (const [label, movement] of [['Monter', -1], ['Descendre', 1], ['Retirer', 0]]) {
      const button = element('button', label);
      button.type = 'button';
      button.setAttribute('aria-label', label + ' la rubrique ' + (section.title || index + 1));
      button.disabled = movement === -1 && index === 0 || movement === 1 && index === draft.sections.length - 1;
      button.onclick = () => {
        remember();
        const [item] = draft.sections.splice(index, 1);
        if (movement) draft.sections.splice(index + movement, 0, item);
        activeSection = -1;
        refresh();
      };
      actions.append(button);
    }
    group.append(actions);
    $('section-editor').append(group);
  });
  $('add-section').disabled = draft.sections.length >= 10;
}
function refresh(sync = true) {
  if (sync) {
    $('project-name').value = draft.name;
    $('project-type').value = draft.type;
    $('tagline').value = draft.tagline;
    $('accent').value = draft.accent;
    $('button-label').value = draft.button || '';
    $('button-link').value = draft.link || '';
    sectionEditor();
  }
  document.querySelectorAll('[data-theme]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.theme === draft.theme)));
  $('remove-photo').hidden = !draft.photo;
  preview();
  save();
}
function chooseTheme(value) {
  draft.theme = value;
  draft.accent = themeStyles[value].accent;
}
const starters = {
 artisan: { name: 'Votre atelier', tagline: 'Un savoir-faire à découvrir près de chez vous.', theme: 'workshop', sections: [{ title: 'Nos prestations', text: 'Présentez vos trois prestations principales et leurs particularités.' }, { title: 'Notre savoir-faire', text: 'Racontez votre approche, vos matériaux et votre façon de travailler.' }, { title: 'Réalisations', text: 'Ajoutez vos références et les projets que vous souhaitez présenter.' }, { title: 'Contact et horaires', text: 'Indiquez comment vous joindre et vos horaires.' }] },
 restaurant: { name: 'Votre table', tagline: 'Une cuisine et un lieu à découvrir.', theme: 'editorial', sections: [{ title: 'La carte', text: 'Présentez vos plats, boissons et tarifs.' }, { title: 'Notre maison', text: 'Racontez votre cuisine et votre accueil.' }, { title: 'Réserver', text: 'Ajoutez votre téléphone ou votre lien de réservation.' }, { title: 'Nous trouver', text: 'Précisez votre adresse, vos horaires et les accès.' }] },
 createur: { name: 'Votre univers', tagline: 'Des créations qui ont une personnalité.', theme: 'manga', sections: [{ title: 'Créations', text: 'Présentez une sélection de vos projets.' }, { title: 'À propos', text: 'Votre démarche et ce qui rend votre univers unique.' }, { title: 'Collaborations', text: 'Expliquez les projets que vous souhaitez réaliser.' }, { title: 'Contact', text: 'Indiquez votre moyen de contact professionnel.' }] }
};
document.querySelectorAll('[data-starter]').forEach(button => {
 button.onclick = () => { remember(); const example = starters[button.dataset.starter]; if (!example) return;
 draft = validate({ ...draft, ...structuredClone(example), accent: themeStyles[example.theme].accent });
 creationRevision++; activeSection = -1; refresh(); status('Maquette de départ chargée. Remplacez les textes par vos informations, ou décrivez vos retouches.'); };
});
updateInput('project-name', 'name');
updateInput('project-type', 'type');
updateInput('tagline', 'tagline');
updateInput('accent', 'accent');
updateInput('button-label', 'button');
updateInput('button-link', 'link', value => { draft.link = safeURL(value); });
document.querySelectorAll('[data-theme]').forEach(button => {
  button.onclick = () => { remember(); chooseTheme(button.dataset.theme); refresh(); };
});
$('add-section').onclick = () => {
  if (draft.sections.length >= 10) return;
  remember();
  draft.sections.push({ title: 'Nouvelle rubrique', text: '' });
  refresh();
  $('section-editor').lastElementChild.querySelector('input').focus();
};
$('undo').onclick = () => {
  if (!history.length) return;
  pendingPhoto++;
  draft = history.pop();
  activeSection = -1;
  $('undo').disabled = !history.length;
  refresh();
  status('Version précédente rétablie.');
};
$('new-draft').onclick = () => {
  pendingPhoto++;
  remember();
  resetSuivi();
  draft = structuredClone(defaults);
  activeSection = -1;
  $('instructions').value = '';
  refresh();
  status('Nouveau brouillon ouvert. Vous pouvez revenir au précédent avec Annuler.');
  $('instructions').focus();
};
$('phone').onclick = () => {
  const phone = $('preview').classList.toggle('mobile');
  $('phone').setAttribute('aria-pressed', String(phone));
  $('phone').textContent = phone ? 'Pleine largeur' : 'Format mobile';
};
function photoData(file) {
  if (file.size > 20 * 1024 * 1024) return Promise.reject(Error('Choisissez une image de moins de 20 Mo.'));
  const url = URL.createObjectURL(file);
  const image = new Image();
  return new Promise((resolve, reject) => {
    image.onload = () => {
      URL.revokeObjectURL(url);
      try {
        const scale = Math.min(1, 1000 / Math.max(image.naturalWidth, image.naturalHeight));
        const canvas = element('canvas');
        canvas.width = Math.max(1, Math.round(image.naturalWidth * scale));
        canvas.height = Math.max(1, Math.round(image.naturalHeight * scale));
        canvas.getContext('2d').drawImage(image, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL('image/webp', .82));
      } catch { reject(Error('Cette image ne peut pas être ouverte.')); }
    };
    image.onerror = () => { URL.revokeObjectURL(url); reject(Error('Cette image ne peut pas être ouverte.')); };
    image.src = url;
  });
}
$('photo').onchange = async () => {
  const photo = $('photo').files[0];
  $('photo').value = '';
  if (!photo) return;
  const current = ++pendingPhoto;
  try {
    const data = await photoData(photo);
    if (current !== pendingPhoto) return;
    if (!validPhoto(data)) throw Error('Choisissez une photo de plus petite taille.');
    remember(); draft.photo = data; refresh(false);
    status('Photo ajoutée à la maquette.');
  } catch (error) { if (current === pendingPhoto) status(error.message); }
};
$('remove-photo').onclick = () => { pendingPhoto++; remember(); draft.photo = ''; refresh(false); status('Photo retirée.'); };

const normalize = text => text.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
const colors = { orange: '#e87136', bleu: '#6198f4', rouge: '#d74c59', violet: '#a380de', vert: '#54936c', rose: '#db80ab', or: '#d8ab55', jaune: '#ecc24a' };
function apply(text) {
  const plain = normalize(text);
  const changes = [];
  if (/\b(?:application|appli)\b/.test(plain)) { draft.type = 'app'; changes.push('format application web'); }
  else if (/\bsite (?:web|internet|vitrine)\b/.test(plain)) { draft.type = 'site'; changes.push('format site'); }
  const theme = /\b(?:3d|relief)\b/.test(plain) ? 'dimension'
    : /\b(?:manga|bd|bande dessinee)\b/.test(plain) ? 'manga'
    : /\b(?:editorial|classique|elegant)\b/.test(plain) ? 'editorial'
    : /\b(?:style clair|ambiance claire|minimaliste)\b/.test(plain) ? 'workshop' : '';
  if (theme) { chooseTheme(theme); changes.push(themeStyles[theme].name); }
  const named = plain.match(/\b(?:en|couleur|accent|titre en)\s+(orange|bleu|rouge|violet|vert|rose|or|jaune)\b/)?.[1];
  const hex = text.match(/#[\da-f]{6}\b/i)?.[0];
  if (hex || named) { draft.accent = hex || colors[named]; changes.push('couleur'); }
  const title = text.match(/(?:s[’']appelle|nom\s*:|nomme(?:r)? (?:le projet )?|titre\s*:|renomme(?:r)? (?:le site |l[’']application )?(?:en )?)\s*(.+?)(?=\n|[.!?;]|$)/iu)?.[1];
  const line = text.match(/(?:accroche\s*:|slogan\s*:)\s*(.+?)(?=\n|$)/iu)?.[1];
  if (title) { draft.name = short(title.trim(), 80); changes.push('nom'); }
  if (line) { draft.tagline = short(line.trim(), 150); changes.push('accroche'); }
  const next = text.match(/(?:ajoute(?:r)?|cr[ée]e?r?)\s+(?:une |un |la |le )?(?:rubrique|page|section|onglet)\s+[«"“]?([^»"”\n.!?;]+?)(?=\s+et\s+|[»"”\n.!?;]|$)/giu) || [];
  for (const instruction of next) {
    const name = instruction.replace(/^.*?\b(?:rubrique|page|section|onglet)\s*/iu, '').replace(/^[«"“]|[»"”]$/g, '').trim().slice(0, 80);
    if (!name || draft.sections.length >= 10 || draft.sections.some(s => normalize(s.title) === normalize(name))) continue;
    draft.sections.push({ title: name, text: '' });
    changes.push('rubrique « ' + name + ' »');
  }
  const remove = text.match(/(?:retire|supprime|enl[èe]ve)\s+(?:la |le |une |un )?(?:rubrique|page|section|onglet)\s+([^\n.!?;]+)/iu)?.[1];
  if (remove) {
    const count = draft.sections.length;
    draft.sections = draft.sections.filter(section => normalize(section.title) !== normalize(remove.trim()));
    if (draft.sections.length !== count) changes.push('rubrique retirée');
  }
  draft.notes = [draft.notes, text].filter(Boolean).join('\n').slice(-1200);
  return changes;
}
let creationRevision = 0;
document.addEventListener('input', () => creationRevision++);
document.addEventListener('click', event => { if (event.target.closest('[data-theme],#undo,#new-draft,#add-section,.section-edit button')) creationRevision++; });
function creationDocument() {
  const style = themeStyles[draft.theme];
  return { format: 'site', style: draft.theme === 'workshop' ? 'atelier' : draft.theme,
    theme: { c1: draft.accent, c2: draft.accent, fond: style.background, texte: style.ink },
    blocs: [{ t: 'titre', titre: draft.name, sous: draft.tagline, bouton: draft.button || '', lien: draft.link || '' }, ...draft.sections.map(s => ({ t: 'texte', titre: s.title, texte: s.text }))] };
}
function applyDocument(doc) {
  if (!doc || !Array.isArray(doc.blocs)) throw Error('Réponse incomplète');
  const hero = doc.blocs.find(b => b.t === 'titre');
  if (!hero) throw Error('En-tête absent');
  const themes = { atelier: 'workshop', contraste: 'manga', editorial: 'editorial', manga: 'manga', dimension: 'dimension' };
  const next = validate({ ...draft, name: hero.titre, tagline: hero.sous, button: hero.bouton, link: hero.lien, theme: themes[doc.style] || draft.theme,
    accent: doc.theme?.c1, sections: doc.blocs.filter(b => b.t !== 'titre').map(b => ({ title: b.titre || '',
      text: b.t === 'produits' ? (b.items || []).map(p => p.nom + (p.prix ? ' · ' + p.prix : '')).join('\n') : b.texte || '' })) });
  remember(); draft = next;
}
$('apply').onclick = async () => {
  const text = $('instructions').value.trim();
  if (!text) { status('Écrivez ou dictez une consigne pour commencer.'); $('instructions').focus(); return; }
  const button = $('apply'), revision = creationRevision;
  button.disabled = true; button.setAttribute('aria-busy', 'true'); status('Composition de votre aperçu…');
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 100000);
  try {
    const response = await fetch(studioHost + '/api/studio/proposer', { method: 'POST', signal: controller.signal,
      headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ brief: text, projet: draft.name ? creationDocument() : null }) });
    const result = await response.json();
    if (revision !== creationRevision) { status('Vous avez modifié la maquette pendant la création. Votre version est conservée : relancez votre consigne.'); return; }
    if (!response.ok || !result.ok) throw Error(result.message || 'Le service de création est momentanément indisponible.');
    applyDocument(result.doc); activeSection = -1; refresh();
    if ($('instructions').value.trim() === text) $('instructions').value = '';
    status(result.explication || 'Votre aperçu est prêt. Continuez à le modifier ou envoyez-le pour validation.');
  } catch (error) {
    if (revision !== creationRevision) { status('Votre version a changé et reste conservée. Relancez la consigne.'); return; }
    remember(); const changes = apply(text); activeSection = -1; refresh();
    const message = error.name === 'AbortError' ? 'La création prend trop de temps.' : /fetch|network|json|load/i.test(error.message) ? 'Le service de création est momentanément indisponible.' : error.message;
    status(message + (changes.length
      ? ' Réglages simples appliqués : ' + changes.join(', ') + '. Votre consigne reste disponible.'
      : ' Votre brouillon et votre consigne sont conservés. Vous pouvez utiliser une maquette de départ.'));
  } finally { clearTimeout(timer); button.disabled = false; button.removeAttribute('aria-busy'); }
};
const recognizer = window.SpeechRecognition || window.webkitSpeechRecognition;
let activeRecognition;
$('dictate').onclick = () => {
  if (!recognizer) {
    $('instructions').focus();
    status('Vous pouvez dicter avec le micro de votre clavier ou écrire votre demande.');
    return;
  }
  if (activeRecognition) { activeRecognition.stop(); return; }
  const initial = $('instructions').value.trim();
  const recognition = new recognizer();
  recognition.lang = 'fr-FR';
  recognition.interimResults = true;
  recognition.onstart = () => {
    $('dictate').textContent = 'Arrêter la dictée';
    $('dictate').setAttribute('aria-pressed', 'true');
    status('Dictée en cours. Selon le navigateur, la reconnaissance peut utiliser son service vocal.');
  };
  recognition.onresult = event => {
    const words = Array.from(event.results, result => result[0].transcript.trim()).join(' ');
    $('instructions').value = [initial, words].filter(Boolean).join(' ').slice(0, 1200);
  };
  recognition.onerror = () => status('Micro indisponible. Utilisez le micro du clavier ou écrivez votre idée.');
  recognition.onend = () => {
    activeRecognition = null;
    $('dictate').textContent = '🎙 Dicter';
    $('dictate').setAttribute('aria-pressed', 'false');
    if ($('feedback').textContent.startsWith('Dictée en cours')) status('Relisez votre texte, puis appliquez-le à l’aperçu.');
  };
  try { recognition.start(); activeRecognition = recognition; }
  catch { status('Le micro ne démarre pas. Vous pouvez écrire votre idée.'); }
};
if ('speechSynthesis' in window && 'SpeechSynthesisUtterance' in window) {
  $('listen').hidden = false;
  $('listen').onclick = () => {
    speechSynthesis.cancel();
    const voice = new SpeechSynthesisUtterance($('feedback').textContent);
    voice.lang = 'fr-FR';
    speechSynthesis.speak(voice);
  };
}
function saveFile() {
  const href = URL.createObjectURL(new Blob([JSON.stringify({ version: 1, ...draft }, null, 2)], { type: 'application/json' }));
  const link = element('a');
  link.href = href; link.download = 'vm-studio-brouillon.json'; link.click();
  setTimeout(() => URL.revokeObjectURL(href), 1500);
}
$('download').onclick = saveFile;
$('restore').onchange = async () => {
  const file = $('restore').files[0];
  $('restore').value = '';
  if (!file) return;
  try {
    if (file.size > 950000) throw Error();
    const raw = JSON.parse(await file.text());
    if (raw?.version !== 1 || !Array.isArray(raw.sections)) throw Error();
    const next = validate(raw);
    pendingPhoto++; remember(); resetSuivi(); draft = next; activeSection = -1; refresh();
    status('Brouillon restauré.');
  } catch { status('Ce fichier ne peut pas être ouvert. Sélectionnez un brouillon exporté par VM Studio.'); }
};
function draftSummary() {
  const details = [
    'Projet : ' + (draft.name || 'Sans titre') + ' · ' + (draft.type === 'app' ? 'Application web' : 'Site'),
    'Ambiance : ' + themeStyles[draft.theme].name + ' · ' + draft.accent,
    draft.tagline && 'Accroche : ' + draft.tagline,
    $('remaining').value.trim(),
    draft.notes && 'Consignes : ' + draft.notes,
    draft.sections.length && 'Rubriques : ' + draft.sections.map(section => section.title + (section.text ? ' (' + section.text + ')' : '')).join(' · ')
  ];
  return details.filter(Boolean).join('\n').slice(0, 1280);
}
async function shareDraft() {
  if (!('CompressionStream' in window)) return '';
  const prefix = location.origin + '/creer/#maquette=';
  for (const withPhoto of draft.photo ? [true, false] : [false]) {
    if (withPhoto && draft.photo.length > 2200) continue;
    const json = JSON.stringify({ ...draft, version: 1, photo: withPhoto ? draft.photo : '', notes: '' });
    const compressed = await new Response(new Blob([json]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer();
    if (compressed.byteLength > 760) continue;
    const encoded = btoa(String.fromCharCode(...new Uint8Array(compressed))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    return { url: prefix + encoded, withPhoto };
  }
  return '';
}
async function offerSharedDraft() {
  const token = location.hash.match(/^#maquette=([A-Za-z0-9_-]{1,1100})$/)?.[1];
  if (!token || !('DecompressionStream' in window)) return;
  try {
    const bytes = Uint8Array.from(atob(token.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0));
    const reader = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip')).getReader();
    const decoder = new TextDecoder();
    let json = '', size = 0;
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > 16000) { await reader.cancel(); return; }
      json += decoder.decode(value, { stream: true });
    }
    const raw = JSON.parse(json + decoder.decode());
    if (raw.version !== 1 || !Array.isArray(raw.sections)) return;
    const incoming = validate(raw);
    document.getElementById('creation').scrollIntoView();
    status('Une maquette partagée est prête à être ouverte.');
    const open = element('button', 'Ouvrir la maquette');
    open.type = 'button';
    open.onclick = () => {
      pendingPhoto++; remember(); resetSuivi(); draft = incoming; activeSection = -1; refresh();
      window.history.replaceState(null, '', location.pathname + location.search + '#creation');
      status('Maquette partagée ouverte.');
    };
    $('feedback').append(' ', open);
    open.focus({ preventScroll: true });
  } catch { status('Ce lien de maquette est illisible. Essayez d’importer le fichier du projet.'); }
}
async function request(path, body) {
  const response = await fetch(studioHost + path, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
  });
  return { response, result: await response.json().catch(() => ({})) };
}
function afficherSuivi() {
  const link = $('studio-help');
  const url = suivi?.lien;
  link.hidden = typeof url !== 'string' || !url.startsWith(studioHost + '/salon/');
  if (!link.hidden) link.href = url;
  else link.removeAttribute('href');
  $('share-with-studio').hidden = !!suivi?.envoye;
  $('share-with-studio').textContent = link.hidden ? 'Démarrer le suivi privé' : 'Partager mes dernières modifications';
}
function memoriserSuivi() {
  try {
    localStorage.setItem(storageKey, JSON.stringify(draft));
    if (suivi) localStorage.setItem(suiviKey, JSON.stringify(suivi));
    else localStorage.removeItem(suiviKey);
  } catch {}
}
function resetSuivi() {
  suivi = null;
  try { localStorage.removeItem(suiviKey); } catch {}
  $('follow-status').textContent = '';
  afficherSuivi();
}
$('project-follow').addEventListener('toggle', async event => {
  if (!event.currentTarget.open || suivi?.lien) return;
  const button = $('share-with-studio'), line = $('follow-status');
  if (button.disabled) return;
  button.disabled = true;
  line.textContent = 'Vérification du service…';
  try {
    const response = await fetch(studioHost + '/api/studio/suivi', { cache: 'no-store' });
    const capability = response.ok ? await response.json() : null;
    if (capability?.version !== 1) throw Error();
    line.textContent = '';
  } catch {
    line.textContent = 'Suivi privé momentanément indisponible. Vous pouvez créer votre maquette et transmettre votre demande en bas de la page.';
  } finally { button.disabled = false; }
});
$('share-with-studio').onclick = async () => {
  const button = $('share-with-studio'), line = $('follow-status');
  if (button.disabled || $('send-button').disabled) return;
  suivi ||= { cle: crypto.randomUUID(), version: null };
  const projet = suivi;
  memoriserSuivi();
  button.disabled = true;
  line.textContent = 'Partage en cours…';
  try {
    const { response, result } = await request('/api/studio/suivi', { partager: true, cle: projet.cle, base: projet.version, draft: { ...draft, notes: '' } });
    if (suivi !== projet) return;
    if (response.status === 409) {
      line.textContent = 'L’atelier a modifié ce projet. Ouvrez votre suivi pour lui envoyer vos changements.';
      return;
    }
    if (!response.ok || !result.ok) throw Error();
    Object.assign(projet, { version: result.version, lien: result.lien });
    memoriserSuivi();
    afficherSuivi();
    line.textContent = 'Votre brouillon est visible dans l’atelier privé.';
  } catch {
    if (suivi === projet) line.textContent = 'Partage indisponible. Votre brouillon est conservé sur cet appareil.';
  } finally { button.disabled = false; }
};
$('send-form').onsubmit = async event => {
  event.preventDefault();
  const statusLine = $('send-status'), button = $('send-button');
  if (button.disabled || $('share-with-studio').disabled) return;
  const projet = suivi;
  const brouillon = draft;
  const contact = {
    nom: $('client-name').value.trim(), email: $('client-email').value.trim(), consentement: $('consent').checked ? 'oui' : '',
    besoin_principal: draft.type === 'app' ? 'Application web personnalisée' : 'Site internet personnalisé',
    projet: draftSummary(), _honey: $('website-extra').value
  };
  button.disabled = true;
  statusLine.textContent = 'Transmission à l’atelier…';
  let received = false;
  try {
    const capability = await fetch(studioHost + '/api/studio/transmission', { cache: 'no-store' }).then(r => r.ok && r.json()).catch(() => null);
    const full = capability?.version === 1;
    let previewLink = '';
    if (!full) {
      previewLink = await shareDraft().catch(() => '');
      if (previewLink) {
        const caption = 'Maquette à ouvrir : ' + previewLink.url + '\n';
        contact.projet = caption + contact.projet.slice(0, 1320 - caption.length);
      }
    }
    const suiviTransmis = projet?.version ? { suivi: projet.cle, base: projet.version } : {};
    const { response, result } = await request(full ? '/api/studio/transmission' : '/api/demande',
      full ? { ...contact, ...suiviTransmis, draft: brouillon } : contact);
    if (result.error === 'projet_modifie') {
      statusLine.textContent = 'L’atelier a modifié ce projet. Utilisez le lien de suivi pour lui signaler vos dernières demandes.';
      return;
    }
    if (!response.ok || !result.success || !result.id) throw Error();
    received = true;
    statusLine.textContent = full
      ? 'Maquette reçue par VM Studio. Référence ' + result.id + '.'
      : 'Demande reçue par VM Studio. Référence ' + result.id + '.' + (previewLink ? ' Un lien de reprise est inclus.' : '') +
         ((!previewLink || (draft.photo && !previewLink.withPhoto)) ? ' Téléchargez le brouillon complet pour le joindre lors de nos échanges.' : '');
    if (full && typeof result.lien === 'string' && result.lien.startsWith(studioHost + '/salon/')) {
      if (suivi === projet) {
        suivi = { ...projet, lien: result.lien, envoye: true };
        memoriserSuivi();
        afficherSuivi();
      }
      const link = element('a', 'Ouvrir mon suivi');
      link.href = result.lien;
      statusLine.append(' ', link);
    }
    if (!full) {
      const download = element('button', 'Télécharger le brouillon');
      download.type = 'button'; download.onclick = saveFile;
      statusLine.append(' ', download);
    }
    $('send-form').reset();
  } catch {
    statusLine.textContent = 'Envoi non confirmé. Votre brouillon est conservé. Téléchargez-le ou contactez VM Studio depuis la page des prestations.';
  } finally { button.disabled = received; }
};
refresh();
afficherSuivi();
offerSharedDraft();
if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => {});

