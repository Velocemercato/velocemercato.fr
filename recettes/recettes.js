// Recettes VM : recherche, catégories, filtres, fiche détaillée, portions, liste de courses et favoris.
(() => {
  const esc = window.VMP ? window.VMP.esc : (t => String(t ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c])));
  const $ = id => document.getElementById(id);
  const CATS = ['Entrées', 'Plats', 'Desserts', 'Petit-déj & goûter', 'Apéro', 'Sauces & bases'];
  const CAT_EMOJI = {'Entrées': '🥗', 'Plats': '🍲', 'Desserts': '🍰', 'Petit-déj & goûter': '☕', 'Apéro': '🧀', 'Sauces & bases': '🥄'};
  const FAV_KEY = 'vm-recettes-favoris';
  const etat = {q: '', cat: '', f: new Set()};
  let recettes = [];
  let portions = 0;

  // Favoris : stockage local du navigateur, la page fonctionne aussi s’il est bloqué.
  const lireFavs = () => { try { return new Set(JSON.parse(localStorage.getItem(FAV_KEY) || '[]')); } catch (e) { return new Set(); } };
  let favs = lireFavs();
  const ecrireFavs = () => { try { localStorage.setItem(FAV_KEY, JSON.stringify([...favs])); } catch (e) { /* stockage indisponible */ } };

  const norm = t => String(t).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  const total = r => r.prep + r.cuisson + (r.repos || 0);
  const estRapide = r => r.prep + r.cuisson <= 30 && !r.repos;
  const duree = min => min < 60 ? `${min} min` : `${Math.floor(min / 60)} h${min % 60 ? ' ' + String(min % 60).padStart(2, '0') : ''}`;
  const tagsDe = r => {
    const t = [];
    if (estRapide(r)) t.push('rapide');
    r.tags.forEach(x => t.push(x));
    if (r.region) t.push('📍 ' + r.region);
    if (r.saison && r.saison !== "toute l'année") t.push(r.saison);
    return t;
  };

  function correspond(r) {
    if (etat.cat && r.categorie !== etat.cat) return false;
    if (etat.f.has('rapide') && !estRapide(r)) return false;
    if (etat.f.has('vege') && !r.tags.includes('végétarien')) return false;
    if (etat.f.has('budget') && r.budget !== '€') return false;
    if (etat.f.has('region') && !r.region) return false;
    if (etat.f.has('favs') && !favs.has(r.id)) return false;
    if (etat.q) {
      const mots = norm(etat.q).split(/\s+/).filter(Boolean);
      const texte = r._index;
      if (!mots.every(m => texte.includes(m))) return false;
    }
    return true;
  }

  const visuel = (r, grand) => r.image
    ? `<img class="rc-img" src="/assets/illustrations/${esc(r.image)}-480.webp" srcset="/assets/illustrations/${esc(r.image)}-480.webp 480w, /assets/illustrations/${esc(r.image)}-960.webp 960w" sizes="${grand ? '(max-width: 700px) 100vw, 640px' : '(max-width: 600px) 100vw, 320px'}" width="960" height="640" alt="" loading="lazy" decoding="async">`
    : `<div class="rc-img rc-emoji" data-c="${esc(r.categorie)}" aria-hidden="true">${esc(r.emoji || CAT_EMOJI[r.categorie])}</div>`;
  const meta = r => `<span>⏱️ ${duree(r.prep + r.cuisson)}${r.repos ? ' + repos' : ''}</span><span>${esc(r.difficulte)}</span><span title="Budget">${esc(r.budget)}</span><span>👥 ${r.portions}</span>`;

  function carte(r) {
    const fav = favs.has(r.id);
    return `<article class="rc-carte"><a class="rc-lien" href="#r=${esc(r.id)}" aria-label="${esc(r.titre)} : voir la recette">${visuel(r)}</a>
      <button type="button" class="rc-fav" data-fav="${esc(r.id)}" aria-pressed="${fav}" aria-label="${fav ? 'Retirer des favoris' : 'Ajouter aux favoris'} : ${esc(r.titre)}">${fav ? '★' : '☆'}</button>
      <div class="rc-corps"><span class="rc-cat">${esc(r.categorie)}</span><h3><a href="#r=${esc(r.id)}">${esc(r.titre)}</a></h3>
      <div class="rc-meta">${meta(r)}</div>
      <div class="rc-tags">${tagsDe(r).map(t => `<span>${esc(t)}</span>`).join('')}</div></div></article>`;
  }

  function rendreJour() {
    // Même recette pour tout le monde le même jour (date locale), on évite les sauces et bases.
    const pool = recettes.filter(r => r.categorie !== 'Sauces & bases');
    const d = new Date();
    const jour = Math.floor(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 86400000);
    const r = pool[(jour * 7) % pool.length];
    $('jour').innerHTML = `<a class="rc-jour-in" href="#r=${esc(r.id)}">${visuel(r, true)}<div><span class="rc-cat">⭐ Recette du jour · ${d.toLocaleDateString('fr-FR', {weekday: 'long', day: 'numeric', month: 'long'})}</span><h2>${esc(r.titre)}</h2><div class="rc-meta">${meta(r)}</div><span class="btn">Voir la recette</span></div></a>`;
  }

  function rendreListe() {
    const list = recettes.filter(correspond);
    $('compte').textContent = list.length === recettes.length ? `${list.length} recettes` : `${list.length} recette${list.length > 1 ? 's' : ''} sur ${recettes.length}`;
    if (!list.length) {
      const msg = etat.f.has('favs') && !favs.size ? 'Aucun favori pour l’instant : touchez ☆ sur une recette pour la retrouver ici.' : 'Aucune recette ne correspond à ces critères.';
      $('liste').innerHTML = `<div class="vide rc-vide"><p>${msg}</p><button type="button" class="btn" id="reset">Aucune recette ? Voir toutes les recettes</button></div>`;
      $('reset').onclick = reset;
      return;
    }
    $('liste').innerHTML = list.map(carte).join('');
  }

  function rendreChips() {
    $('cats').innerHTML = ['', ...CATS].map(c => `<button type="button" data-cat="${esc(c)}" aria-pressed="${etat.cat === c}">${c ? CAT_EMOJI[c] + ' ' + esc(c) : 'Toutes'}</button>`).join('');
    document.querySelectorAll('#filtres [data-f]').forEach(b => b.setAttribute('aria-pressed', etat.f.has(b.dataset.f)));
  }

  function reset() {
    etat.q = ''; etat.cat = ''; etat.f.clear(); $('q').value = '';
    rendreChips(); rendreListe();
  }

  // ---------- Fiche détaillée ----------
  const UNITE_COURTE = {'c. à soupe': 'c. à s.', 'c. à café': 'c. à c.'};
  const INSECABLES = ['pincée', 'noix', 'poignée', 'bouquet', 'branche'];
  const FRACTIONS = {0.25: '¼', 0.5: '½', 0.75: '¾'};
  function quantite(q, u, k) {
    if (q == null) return '';
    let v = q * k;
    const metrique = ['g', 'cl', 'ml'].includes(u);
    if (metrique) v = v >= 100 ? Math.round(v / 10) * 10 : v >= 20 ? Math.round(v / 5) * 5 : u === 'g' ? Math.max(1, Math.round(v)) : Math.round(v * 2) / 2 || 0.5;
    else if (['kg', 'l'].includes(u)) v = Math.round(v * 100) / 100;
    else if (INSECABLES.includes(u)) return Math.max(1, Math.round(v)) + ' ' + u;
    else {
      v = Math.round(v * 4) / 4 || 0.25;
      const ent = Math.floor(v), dec = v - ent;
      const txt = (ent ? ent : '') + (dec ? (ent ? ' ' : '') + FRACTIONS[dec] : '');
      return (txt || '0') + (u ? ' ' + (UNITE_COURTE[u] || u) : '');
    }
    if (u === 'g' && v >= 1000) return String(Math.round(v / 10) / 100).replace('.', ',') + ' kg';
    return String(v).replace('.', ',') + ' ' + u;
  }

  // Accord simple au singulier quand il ne reste qu’une unité (« 1 œuf », « ½ oignon »).
  const SINGULIERS = {'œufs': 'œuf', 'oignons': 'oignon', 'carottes': 'carotte', 'tomates': 'tomate', 'poireaux': 'poireau', 'navets': 'navet', 'échalotes': 'échalote', 'bananes': 'banane', 'pommes': 'pomme', 'gousses': 'gousse', 'blancs': 'blanc', 'jaunes': 'jaune', 'cornichons': 'cornichon', 'amandes': 'amande', 'yaourts': 'yaourt', 'grandes': 'grande', 'cerneaux': 'cerneau', 'saucisses': 'saucisse'};
  const libelle = (i, k) => {
    if (i.q == null || i.u || i.q * k > 1.01) return i.n;
    const [mot, ...reste] = i.n.split(' ');
    return SINGULIERS[mot] ? [SINGULIERS[mot], ...reste].join(' ').replace('grande tranches', 'grande tranche') : i.n;
  };
  function ingredientsHTML(r) {
    const k = portions / r.portions;
    return r.ingredients.map(i => `<li><b>${esc(quantite(i.q, i.u, k))}</b><span>${esc(libelle(i, k))}</span></li>`).join('');
  }

  function listeCourses(r) {
    const k = portions / r.portions;
    return `Liste de courses — ${r.titre} (${portions} pers.)\n` + r.ingredients.map(i => `- ${(quantite(i.q, i.u, k) + ' ' + libelle(i, k)).trim()}`).join('\n') + '\nRecette : https://velocemercato.fr/recettes/#r=' + r.id;
  }

  async function copier(texte, bouton) {
    const ok = () => { bouton.textContent = '✅ Liste copiée'; setTimeout(() => { bouton.textContent = '📋 Copier la liste de courses'; }, 2500); };
    try { await navigator.clipboard.writeText(texte); ok(); return; } catch (e) { /* repli ci-dessous */ }
    const ta = document.createElement('textarea'); ta.value = texte; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    let reussi = false; try { reussi = document.execCommand('copy'); } catch (e) { reussi = false; }
    ta.remove();
    if (reussi) ok(); else window.prompt('Copiez la liste :', texte);
  }

  function ouvrir(r) {
    portions = r.portions;
    const fav = favs.has(r.id);
    $('ficheIn').innerHTML = `<div class="rc-fiche-tete"><button type="button" class="rc-fermer" id="fermer" aria-label="Fermer la recette">✕</button>${visuel(r, true)}</div>
      <div class="rc-fiche-corps"><span class="rc-cat">${esc(r.categorie)}${r.region ? ' · 📍 ' + esc(r.region) : ''}</span>
      <h2 id="ficheTitre">${esc(r.titre)}</h2>
      <div class="rc-meta"><span>Préparation ${duree(r.prep)}</span>${r.cuisson ? `<span>Cuisson ${duree(r.cuisson)}</span>` : '<span>Sans cuisson</span>'}${r.repos ? `<span>Repos ${duree(r.repos)}</span>` : ''}<span>${esc(r.difficulte)}</span><span>Budget ${esc(r.budget)}</span></div>
      <div class="rc-tags">${tagsDe(r).map(t => `<span>${esc(t)}</span>`).join('')}</div>
      <div class="rc-actions"><button type="button" class="rc-fav-l" data-fav="${esc(r.id)}" aria-pressed="${fav}">${fav ? '★ Dans mes favoris' : '☆ Ajouter aux favoris'}</button></div>
      <div class="rc-deux"><section><h3>Ingrédients</h3>
      <div class="rc-portions" role="group" aria-label="Nombre de personnes"><button type="button" id="moins" aria-label="Une personne de moins">−</button><output id="nbp" aria-live="polite">${portions} pers.</output><button type="button" id="plus" aria-label="Une personne de plus">+</button></div>
      <ul class="rc-ingr" id="ingr">${ingredientsHTML(r)}</ul>
      <button type="button" class="btn" id="copier">📋 Copier la liste de courses</button></section>
      <section><h3>Préparation</h3><ol class="etapes rc-etapes">${r.etapes.map(e => `<li>${esc(e)}</li>`).join('')}</ol>
      ${r.astuce ? `<p class="rc-astuce"><b>Astuce :</b> ${esc(r.astuce)}</p>` : ''}</section></div></div>`;
    const maj = () => { $('nbp').textContent = portions + ' pers.'; $('ingr').innerHTML = ingredientsHTML(r); $('moins').disabled = portions <= 1; };
    $('moins').onclick = () => { if (portions > 1) { portions--; maj(); } };
    $('plus').onclick = () => { if (portions < 30) { portions++; maj(); } };
    $('copier').onclick = e => copier(listeCourses(r), e.currentTarget);
    $('fermer').onclick = fermer;
    maj();
    const dlg = $('fiche');
    if (!dlg.open) { if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', ''); }
    dlg.scrollTop = 0;
    document.title = r.titre + ' – Recettes Véloce Mercato';
  }

  const titreInitial = document.title;
  function fermer() {
    if (location.hash.startsWith('#r=')) history.replaceState(null, '', location.pathname + location.search);
    fermerDialog();
  }
  function fermerDialog() {
    const dlg = $('fiche');
    if (dlg.open) { if (dlg.close) dlg.close(); else dlg.removeAttribute('open'); }
    document.title = titreInitial;
  }

  function route() {
    const m = location.hash.match(/^#r=([a-z0-9-]+)/);
    const r = m && recettes.find(x => x.id === m[1]);
    if (r) ouvrir(r); else fermerDialog();
  }

  function basculerFav(id) {
    if (favs.has(id)) favs.delete(id); else favs.add(id);
    ecrireFavs();
    rendreListe();
    const b = document.querySelector('#ficheIn .rc-fav-l');
    if (b && b.dataset.fav === id) { const on = favs.has(id); b.setAttribute('aria-pressed', on); b.textContent = on ? '★ Dans mes favoris' : '☆ Ajouter aux favoris'; }
  }

  function brancher() {
    let t;
    $('q').addEventListener('input', e => { clearTimeout(t); t = setTimeout(() => { etat.q = e.target.value.trim(); rendreListe(); }, 120); });
    $('cats').addEventListener('click', e => { const b = e.target.closest('[data-cat]'); if (!b) return; etat.cat = b.dataset.cat; rendreChips(); rendreListe(); });
    $('filtres').addEventListener('click', e => { const b = e.target.closest('[data-f]'); if (!b) return; const f = b.dataset.f; if (etat.f.has(f)) etat.f.delete(f); else etat.f.add(f); rendreChips(); rendreListe(); });
    document.addEventListener('click', e => { const b = e.target.closest('[data-fav]'); if (b) { e.preventDefault(); basculerFav(b.dataset.fav); } });
    const dlg = $('fiche');
    dlg.addEventListener('click', e => { if (e.target === dlg) fermer(); });
    dlg.addEventListener('cancel', e => { e.preventDefault(); fermer(); });
    window.addEventListener('hashchange', route);
    window.addEventListener('popstate', route);
  }

  async function charger() {
    $('liste').innerHTML = '<p class="rc-charge">Chargement des recettes…</p>';
    try {
      const res = await fetch('recettes.json', {cache: 'no-cache'});
      if (!res.ok) throw new Error('HTTP ' + res.status);
      recettes = await res.json();
      if (!Array.isArray(recettes) || !recettes.length) throw new Error('vide');
    } catch (e) {
      $('liste').innerHTML = '<div class="vide rc-vide"><p>Impossible de charger les recettes (connexion ?).</p><button type="button" class="btn" id="reessayer">Réessayer</button></div>';
      $('reessayer').onclick = charger;
      return;
    }
    recettes.forEach(r => { r._index = norm([r.titre, r.categorie, r.region || '', ...r.tags, ...r.ingredients.map(i => i.n)].join(' ')); });
    $('nb').textContent = recettes.length;
    try { const q = new URLSearchParams(location.search).get('q'); if (q) { etat.q = q.slice(0, 60); $('q').value = etat.q; } } catch (e) { /* paramètre ignoré */ }
    rendreJour(); rendreChips(); rendreListe(); route();
  }

  brancher();
  charger();
})();
