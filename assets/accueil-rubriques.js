(() => {
  const site = 'https://velocemercato.fr';
  const refreshInterval = 10 * 60_000;
  const feeds = {
    foot: ['/articles.json'],
    multisport: ['/multisport/actualites.json'],
    actus: ['/actus/news.json', '/belfort/actus.json'],
    gaming: ['/vm-gaming/news.json'],
    pastille: ['/studio/diffusions.json'],
  };
  const panels = document.querySelectorAll('.espace-rubrique');
  const snapshots = JSON.parse(document.querySelector('#instantane-veloce').textContent);
  const dateFormat = new Intl.DateTimeFormat('fr-FR', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Paris',
  });
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
    return {title: item?.titre, source: source?.nom, date: item?.publishedAt, url: ownLink || source?.url};
  }

  function formatRows(key, primary, local) {
    if (key === 'multisport') {
      return Object.entries(primary?.sports ?? {}).flatMap(([sport, items]) =>
        (Array.isArray(items) ? items : [])
          .filter(item => !/\b(gta|xbox|playstation|jeux vidéo)\b/i.test(item?.titre ?? ''))
          .slice(0, 1)
          .map(item => ({title: item.titre, source: item.source, date: item.date,
            url: item.url, theme: sport.toUpperCase()})));
    }
    if (key === 'pastille') {
      return (Array.isArray(primary) ? primary : [])
        .filter(item => item?.plateformes?.youtube?.status === 'published')
        .map(item => ({title: item.titre, date: item.date_publication, source: 'La Pastille TV',
          url: item.plateformes.youtube.url}));
    }
    const rows = (Array.isArray(primary) ? primary : []).slice(0, key === 'actus' ? 4 : 7)
      .map(item => fromArticle(item, key));
    const region = (Array.isArray(local?.titres) ? local.titres : []).slice(0, 2).map(item => ({
      title: item?.t, date: item?.d, source: item?.s, url: item?.u, theme: 'Régions',
    }));
    return rows.concat(region);
  }

  function render(panel, rows) {
    const list = panel.querySelector('.articles-rubrique');
    const clean = rows.filter(item => typeof item?.title === 'string' && item.title.trim() && safeLink(item.url));
    const entries = clean.slice(0, 8).map(item => {
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
      return li;
    });
    list.replaceChildren(...entries);
    return entries.length;
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
      const [main, local] = await Promise.allSettled(feeds[key].map(fetchFeed));
      if (!panel.open || version !== expectedVersion) return;
      if (main.status !== 'fulfilled') throw new Error('Flux indisponible');
      const count = render(panel, formatRows(key, main.value, local?.value));
      status.textContent = count ? 'Dernières informations disponibles' : 'Aucun contenu récent dans ce flux.';
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
    render(panel, snapshots[key] ?? []);
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
