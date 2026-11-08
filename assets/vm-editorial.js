(() => {
  const day = new Intl.DateTimeFormat('en-CA', {timeZone: 'Europe/Paris', dateStyle: 'short'});
  const when = new Intl.DateTimeFormat('fr-FR', {timeZone: 'Europe/Paris', dateStyle: 'short', timeStyle: 'short'});
  const hours = new Intl.DateTimeFormat('fr-FR', {timeZone: 'Europe/Paris', hour: '2-digit', minute: '2-digit'});
  const create = (tag, value) => {
    const node = document.createElement(tag);
    if (value) node.textContent = value;
    return node;
  };
  function urlOf(value) {
    if (typeof value !== 'string' || !value.trim()) return null;
    try {
      const url = new URL(value, location.origin);
      if (!['https:', 'http:'].includes(url.protocol) || url.username || url.password ||
          /^\/https?:\/\//i.test(url.pathname)) return null;
      return url;
    } catch {
      return null;
    }
  }
  function link(title, url) {
    const node = create('a', title);
    node.href = url;
    return node;
  }
  async function read(path) {
    const response = await fetch(path, {cache: 'no-store'});
    if (!response.ok) throw new Error(path);
    return response.json();
  }
  function validDate(value) {
    if (!value) return null;
    const d = new Date(value);
    return Number.isFinite(d.getTime()) ? d : null;
  }
  function dateLabel(date) {
    const t = create('time', when.format(date));
    t.dateTime = date.toISOString();
    return t;
  }
  function renderArticles(host, data) {
    const rows = (Array.isArray(data) ? data : [])
      .filter(item => item?.titre)
      .sort((a, b) => (validDate(b.publishedAt)?.getTime() || 0) - (validDate(a.publishedAt)?.getTime() || 0));
    const result = [];
    for (const row of rows) {
      const id = row.id;
      const source = Array.isArray(row.sources) ? row.sources.find(item => urlOf(item?.url)) : null;
      const internal = host.dataset.vmLocal === 'true' && typeof id === 'string' && /^rss-v2-[a-f0-9]+$/.test(id)
        ? '/a/' + id + '.html' : null;
      const target = urlOf(internal || row.url || row.lien) || urlOf(source?.url);
      if (!target) continue;
      const card = create('article');
      const title = create('h3');
      title.append(link(row.titre, target.href));
      card.append(title);
      if (row.resume) card.append(create('p', row.resume));
      if (source?.nom) card.append(create('small', source.nom));
      const date = validDate(row.publishedAt);
      if (date) {
        const meta = create('p');
        meta.append(dateLabel(date));
        card.append(meta);
      }
      result.push(card);
      if (result.length === 3) break;
    }
    if (result.length) host.replaceChildren(...result);
  }
  async function renderAgenda(host) {
    const data = await read('/scores.json');
    const today = day.format(new Date());
    const matches = (Array.isArray(data.matchs) ? data.matchs : [])
      .filter(m => m.dom && m.ext && validDate(m.date) && day.format(new Date(m.date)) === today)
      .sort((a, b) => new Date(a.date) - new Date(b.date));
    if (!matches.length) return;
    const cards = matches.slice(0, 8).map(m => {
      const line = create('a');
      line.href = '/scores/';
      line.className = 'score-row';
      const time = create('time', hours.format(new Date(m.date)));
      time.className = 'hour';
      time.dateTime = m.date;
      line.append(create('span', m.comp || 'Football'), create('strong', m.dom + ' – ' + m.ext), time);
      return line;
    });
    host.replaceChildren(...cards);
  }
  async function renderAdvice(host) {
    const {publicAdvice: advice} = await read('/pronos/selection.json');
    const kickoff = validDate(advice?.kickoff);
    if (!kickoff || kickoff <= new Date() || !advice.match || !advice.analysis) return;
    const sources = Array.isArray(advice.sources)
      ? advice.sources.filter(s => s?.name && urlOf(s.url)?.protocol === 'https:') : [];
    if (!sources.length) return;
    const box = create('div');
    box.append(create('h3', advice.match), create('p', advice.analysis), dateLabel(kickoff));
    const list = create('ul');
    for (const source of sources) {
      const item = create('li');
      item.append(link(source.name, urlOf(source.url).href));
      list.append(item);
    }
    box.append(list);
    host.replaceChildren(box);
  }
  for (const el of document.querySelectorAll('[data-vm-editorial]')) {
    read(el.dataset.vmEditorial).then(data => renderArticles(el, data)).catch(() => {});
  }
  const legacyFeed = document.getElementById('actualites-du-jour');
  if (legacyFeed && !document.getElementById('feed-title')) {
    const anchor = create('span');
    anchor.id = 'feed-title';
    legacyFeed.prepend(anchor);
    if (location.hash === '#feed-title') anchor.scrollIntoView();
  }
  const agenda = document.querySelector('[data-vm-agenda]');
  if (agenda) renderAgenda(agenda).catch(() => {});
  const advice = document.querySelector('[data-vm-advice]');
  if (advice) renderAdvice(advice).catch(() => {});
})();
