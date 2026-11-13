(() => {
  // Au moins 15 articles dans chaque volet avant le lien vers la rubrique complète (20 si disponibles).
  const VOLET_ARTICLES = 20;
  const site = 'https://velocemercato.fr';
  const refreshInterval = 10 * 60_000;
  const feeds = {
    foot: ['/articles.json'],
    multisport: ['/multisport/actualites.json'],
    actus: ['/actus/news.json', '/belfort/actus.json', '/actus/regions-accueil.json'],
    gaming: ['/vm-gaming/news.json'],
    pastille: ['/studio/diffusions.json'],
  };
  const region = document.querySelector('#choix-region');
  const regionLink = document.querySelector('#lien-region');
  const regionalList = document.querySelector('#titres-region');
  const belfortList = document.querySelector('#actus-belfort');
  const regionalSite = 'https://france3-regions.franceinfo.fr/';
  const sportsSources = /^(?:l['’]équipe|eurosport|bbc sport|ouest-france|dazn|le figaro|le monde(?:\.fr)?|franceinfo|france 24|sud ouest|rugbyrama|tennis actu|inside basket|f1 news|f1news\.fr|ski-nordique\.net|flashscore\.fr|velo 101|velo-club|totalvelo.*|nhl\.com|sports auto moto|turbo\.fr|touchdown actu|motorcycle sports|rugby scope|actu\.fr|tv5monde|lanouvellerepublique\.fr)$/i;
  const panels = document.querySelectorAll('.espace-rubrique');
  const snapshots = JSON.parse(document.querySelector('#instantane-veloce').textContent);
  const dateFormat = new Intl.DateTimeFormat('fr-FR', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Paris',
  });
  let regionalRows = snapshots.regions ?? {};
  let timer;
  let version = 0;

  function safeLink(value) {
    try {
      const url = new URL(value);
      return url.protocol === 'https:' && !url.username && !url.password ? url.href : null;
    } catch {
      return null;
    }
  }

  function fromArticle(item, key) {
    const source = (Array.isArray(item?.sources) ? item.sources : []).find(row => safeLink(row?.url));
    const ownLink = key === 'foot' && /^[a-z0-9][a-z0-9-]{1,99}$/i.test(item?.id ?? '')
      ? site + '/a/' + item.id + '.html' : null;
    return {title: item?.titre, source: source?.nom, date: item?.publishedAt, summary: item?.resume, url: ownLink || source?.url, original: source?.url,
      championnat: item?.championnat, zone: item?.zone};
  }

  function formatRows(key, primary) {
    if (key === 'multisport') {
      return Object.entries(primary?.sports ?? {}).flatMap(([sport, items]) =>
        (Array.isArray(items) ? items : [])
          .filter(item => sportsSources.test(item?.source?.trim() ?? '') && window.VM_Multisport?.isRelevant(sport, item?.titre))
          .slice(0, 3)
          .map(item => ({title: item.titre, source: item.source, date: item.date,
            url: item.url, theme: sport.toUpperCase()})))
        .sort((a, b) => String(b.date).localeCompare(String(a.date)));
    }
    if (key === 'pastille') {
      return (Array.isArray(primary) ? primary : [])
        .filter(item => item?.plateformes?.youtube?.status === 'published')
        .map(item => ({title: item.titre, date: item.date_publication, source: 'La Pastille TV',
          url: item.plateformes.youtube.url, genres: item.universes}));
    }
    return (Array.isArray(primary) ? primary : []).slice(0, VOLET_ARTICLES)
      .map(item => fromArticle(item, key));
  }

  function formatRegion(local) {
    return (Array.isArray(local?.titres) ? local.titres : []).slice(0, 2).map(item => ({
      title: item?.t, date: item?.d, source: item?.s, url: item?.u, theme: 'Régions',
    }));
  }

  // Volet Foot : cartes illustrées comme « Derniers ajouts » du Multisport.
  function footVisuel(item) {
    const t = (String(item.championnat || '') + ' ' + String(item.zone || '') + ' ' + item.title).toUpperCase();
    if (/BLEUS|EQUIPE DE FRANCE|ÉQUIPE DE FRANCE|NATIONS|SÉLECTION|SELECTION|ZIDANE/.test(t)) return ['vm-carte-international', '🇫🇷 BLEUS'];
    if (/CHAMPIONS|EUROPA|CONFERENCE|LIGUE DES CHAMPIONS|C1|C3/.test(t)) return ['vm-carte-europe', '🏆 EUROPE'];
    if (/MERCATO|TRANSFERT/.test(t)) return ['vm-carte-foot', '🔁 MERCATO'];
    if (/LIGUE 1|LIGUE 2|PSG|OM\b|OL\b|LENS|LILLE|MONACO|NANTES|RENNES|NICE|FRANCE/.test(t)) return ['vm-carte-france', '⚽ LIGUE 1'];
    return ['vm-carte-foot', '⚽ FOOT'];
  }
  function depuis(d) {
    const t = Date.parse(d); if (!t) return '';
    const m = Math.round((Date.now() - t) / 60000);
    if (m < 60) return 'Il y a ' + Math.max(m, 1) + ' min';
    const h = Math.round(m / 60);
    return h < 24 ? 'Il y a ' + h + ' heure' + (h > 1 ? 's' : '') : dateFormat.format(new Date(t));
  }
  function renderCards(list, clean, limit) {
    list.classList.add('vm-cards');
    const entries = clean.slice(0, limit).map(item => {
      const li = document.createElement('li');
      const a = document.createElement('a'); a.href = safeLink(item.url); a.className = 'vm-card';
      const [img, badge] = footVisuel(item);
      const fig = document.createElement('span'); fig.className = 'vm-card-img';
      const im = document.createElement('img'); im.src = '/img/vm-art/' + img + '.webp'; im.alt = ''; im.loading = 'lazy'; im.width = 120; im.height = 80;
      const b = document.createElement('span'); b.className = 'vm-card-badge'; b.textContent = badge;
      fig.append(im, b);
      const txt = document.createElement('span'); txt.className = 'vm-card-txt';
      const strong = document.createElement('b'); strong.textContent = item.title;
      const small = document.createElement('small'); small.textContent = [depuis(item.date), item.source].filter(Boolean).join(' · ');
      txt.append(strong, small);
      const chev = document.createElement('span'); chev.className = 'vm-card-chev'; chev.textContent = '›'; chev.setAttribute('aria-hidden', 'true');
      a.append(fig, txt, chev); li.append(a);
      return li;
    });
    list.replaceChildren(...entries);
    return entries.length;
  }

  function renderList(list, rows, limit = VOLET_ARTICLES) {
    const clean = rows.filter(item => typeof item?.title === 'string' && item.title.trim() && safeLink(item.url));
    if (list.closest('#rubrique-foot')) return renderCards(list, clean, limit);
    const entries = clean.slice(0, limit).map(item => {
      const li = document.createElement('li');
      const link = document.createElement('a');
      link.href = safeLink(item.url);
      link.textContent = item.title;
      li.append(link);
      const date = new Date(item.date);
      const details = [item.theme, item.source, !isNaN(date) ? dateFormat.format(date) : null].filter(Boolean);
      if (details.length) {
        const meta = document.createElement('small');
        meta.textContent = details.join(' · ');
        li.append(meta);
      }
      if (typeof item.summary === 'string' && item.summary.trim()) {
        const summary = document.createElement('p');
        summary.textContent = item.summary;
        li.append(summary);
      }
      if (safeLink(item.original) && safeLink(item.original) !== link.href) {
        const original = document.createElement('a');
        original.href = safeLink(item.original);
        original.textContent = 'Lire la source originale';
        li.append(original);
      }
      return li;
    });
    list.replaceChildren(...entries);
    return entries.length;
  }

  function render(panel, key, rows) {
    if (key !== 'pastille') return renderList(panel.querySelector('.articles-rubrique'), rows);

    const lists = [...panel.querySelectorAll('[data-replay]')];
    const genres = new Set(lists.map(list => list.dataset.replay).filter(key => key !== 'autres'));
    const byDate = [...rows].sort((a,b) => (Date.parse(b.date) || 0) - (Date.parse(a.date) || 0));
    let count = 0;
    for (const list of lists) {
      const category = list.dataset.replay;
      const matching = byDate.filter(row => {
        const keys = Array.isArray(row.genres) ? row.genres : [];
        return category === 'autres' ? !keys.some(key => genres.has(key)) : keys.includes(category);
      });
      const total = renderList(list, matching, matching.length);
      count += total;
      if (!total) {
        const empty = document.createElement('li');
        empty.textContent = 'Aucun replay publié dans cette catégorie pour le moment.';
        list.append(empty);
      }
    }
    return count;
  }

  function updateRegion() {
    const choice = region.value;
    regionLink.href = choice === 'outre-mer'
      ? 'https://la1ere.franceinfo.fr/'
      : regionalSite + (choice ? choice + '/' : '');
    regionLink.textContent = choice
      ? 'Voir les actualités de ' + region.selectedOptions[0].textContent
      : 'Voir les actualités régionales · France 3';
    const rows = Array.isArray(regionalRows[choice]) ? regionalRows[choice] : [];
    regionalList.hidden = !renderList(regionalList, rows);
    belfortList.hidden = choice !== 'bourgogne-franche-comte' || !belfortList.children.length;
  }

  if (region && regionLink && regionalList && belfortList) {
    try { region.value = localStorage.getItem('vm-accueil-region') || ''; } catch {}
    if (region.selectedIndex < 0) region.selectedIndex = 0;
    updateRegion();
    region.addEventListener('change', () => {
      updateRegion();
      try { localStorage.setItem('vm-accueil-region', region.value); } catch {}
    });
  }


  // Emplacement sponsorisé en bas de chaque volet (sauf VM Studio) : une campagne tirée au hasard
  // parmi les offres VM et l'espace partenaire. Aucun chiffre d'audience ni gain n'est promis.
  const campagnes = [
    {tag: 'SERVICE PRO', titre: 'Un site web ou une pub pour ton commerce ?',
      texte: 'VM Studio crée ton site à prix fixe, essai 7 jours à 49 €.',
      lien: '/web-studio.html#offres', bouton: 'Découvrir VM Studio →'},
    {tag: 'COMMUNAUTÉ', titre: 'Rejoins Véloce Arena !',
      texte: 'Ligues, coupes et défis EA SPORTS FC avec la communauté.',
      lien: '/gaming.html', bouton: 'Voir l’Arena →'},
    {tag: 'SPONSOR', titre: 'Espace partenaire disponible',
      texte: 'Affiche ta marque devant les passionnés de foot, de sport et de gaming de Véloce Mercato.',
      lien: 'mailto:velocemercato.fr@gmail.com?subject=R%C3%A9servation%20espace%20partenaire', bouton: 'Devenir partenaire →'},
  ];
  for (const dialog of document.querySelectorAll('dialog.espace-rubrique')) {
    if (dialog.id === 'rubrique-studio' || dialog.querySelector('.vm-sponsor')) continue;
    const c = campagnes[Math.floor(Math.random() * campagnes.length)];
    const aside = document.createElement('aside');
    aside.className = 'vm-sponsor';
    aside.setAttribute('aria-label', 'Contenu sponsorisé');
    const tag = document.createElement('span'); tag.className = 'vm-sponsor-tag'; tag.textContent = c.tag;
    const titre = document.createElement('strong'); titre.textContent = c.titre;
    const texte = document.createElement('span'); texte.textContent = c.texte;
    const lien = document.createElement('a'); lien.href = c.lien; lien.textContent = c.bouton;
    aside.append(tag, titre, texte, lien);
    dialog.appendChild(aside);
  }

  async function fetchFeed(path) {
    const publicOrigin = ['velocemercato.fr', 'www.velocemercato.fr'].includes(location.hostname)
      ? location.origin : site;
    const response = await fetch(publicOrigin + path, {cache: 'no-store', signal: AbortSignal.timeout(7000)});
    if (!response.ok) throw new Error('Flux indisponible');
    return response.json();
  }

  async function refresh(panel, key, expectedVersion) {
    const status = panel.querySelector('.etat-rubrique');
    try {
      const [main, local, regions] = await Promise.allSettled(feeds[key].map(fetchFeed));
      if (!panel.open || version !== expectedVersion) return;
      if (key === 'actus') {
        if (local?.status === 'fulfilled') renderList(belfortList, formatRegion(local.value));
        if (regions?.status === 'fulfilled' && regions.value && typeof regions.value === 'object') {
          regionalRows = regions.value;
        }
        updateRegion();
      }
      if (main.status !== 'fulfilled') throw new Error('Flux indisponible');
      const rows = formatRows(key, main.value);
      if (rows.some(row => typeof row.title === 'string' && row.title.trim() && safeLink(row.url))) {
        render(panel, key, rows);
        status.textContent = 'Dernières informations disponibles';
      } else {
        status.textContent = 'Aucun nouveau contenu dans ce flux.';
      }
    } catch {
      if (!panel.open || version !== expectedVersion) return;
      status.textContent = panel.querySelector('.articles-rubrique').children.length
        ? 'Dernières informations enregistrées · actualisation indisponible' : 'Flux indisponible. Ouvre la rubrique complète.';
    }
  }

  function openPanel(key) {
    const panel = document.getElementById('rubrique-' + key);
    if (!panel || typeof panel.showModal !== 'function') return false;
    if (!panel.open) panel.showModal();
    if (!feeds[key]) return true;
    clearInterval(timer);
    const expectedVersion = ++version;
    const saved = snapshots[key] ?? [];
    render(panel, key, key === 'multisport' ? saved.filter(row => window.VM_Multisport?.isRelevant(String(row.theme ?? '').toLowerCase(), row.title)) : saved);
    if (key === 'actus' && belfortList && !belfortList.children.length) {
      renderList(belfortList, snapshots.belfort ?? []);
      updateRegion();
    }
    refresh(panel, key, expectedVersion);
    timer = setInterval(() => refresh(panel, key, expectedVersion), refreshInterval);
    return true;
  }

  for (const panel of panels) panel.addEventListener('close', () => {
    clearInterval(timer);
    version++;
  });
  for (const link of document.querySelectorAll('[data-rubrique]')) {
    link.addEventListener('click', event => {
      if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      if (openPanel(link.getAttribute('data-rubrique'))) event.preventDefault();
    });
  }
  function openFootAnchor() {
    if (['#actualites-du-jour', '#feed-title'].includes(location.hash)) openPanel('foot');
  }
  window.addEventListener('hashchange', openFootAnchor);
  openFootAnchor();
})();

