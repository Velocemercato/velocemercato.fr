const nextAdviceUrl = 'https://raw.githubusercontent.com/Velocemercato/velocemercato.fr/codex/preview-rattrapage/cloudflare/rattrapage/data/public-advice.json';
const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
const emptyAdvice = '<p><strong>Prochain avant-match en préparation</strong></p><p>L’analyse sera affichée quand la rencontre et ses sources auront été vérifiées.</p>';
const frenchDate = new Intl.DateTimeFormat('fr-FR', {
  dateStyle: 'full', timeStyle: 'short', timeZone: 'Europe/Paris',
});

export async function verifiedAdvice(now = Date.now()) {
  try {
    const url = new URL(nextAdviceUrl);
    url.searchParams.set('v', String(Math.floor(now / 60_000)));
    const r = await fetch(url, { signal: AbortSignal.timeout(3500), cf: { cacheTtl: 60 } });
    if (!r.ok) return null;
    const row = await r.json();
    const kickoff = Date.parse(row?.kickoff);
    if (typeof row?.match !== 'string' || typeof row.analysis !== 'string' ||
        !(Date.parse(row.publishedAt) <= now && now < kickoff) || !Array.isArray(row.sources)) return null;
    const sources = row.sources.filter(item => typeof item?.name === 'string' && URL.parse(item.url ?? '')?.protocol === 'https:');
    return sources.length ? { ...row, kickoff, sources } : null;
  } catch {
    return null;
  }
}

export function pronosPage(rewriter, row) {
  let intro = true;
  const advice = row ? '<h3>' + escape(row.match) + '</h3><p class="meta"><time datetime="' +
    new Date(row.kickoff).toISOString() + '">' + escape(frenchDate.format(row.kickoff)) +
    ' · heure de Paris</time></p><p>' + escape(row.analysis) +
    '</p><ul>' + row.sources.map(source => '<li><a href="' + escape(source.url) + '">' +
      escape(source.name) + '</a></li>').join('') + '</ul>' : emptyAdvice;
  rewriter.on('#conseil-contenu', {
    element(section) { section.setInnerContent(advice, { html: true }); }
  }).on('#pronos-du-jour > h2', {
    element(title) { title.setInnerContent('Analyse sportive d’avant-match'); }
  }).on('#pronos-du-jour > noscript', {
    element(note) { note.remove(); }
  }).on('#acces-vip > h2', {
    element(title) { title.setInnerContent('🔒 Demande d’accès VIP gratuit'); }
  }).on('#acces-vip > p', {
    element(note) {
      if (!intro) return;
      intro = false;
      note.setInnerContent('Le bouton ouvre un brouillon dans ta messagerie. Envoie-le pour que l’équipe reçoive ta demande. L’accès est traité manuellement.');
    }
  }).on('#acces-vip a[href^="mailto:"]', {
    element(link) { link.setInnerContent('📩 Préparer ma demande VIP'); }
  }).on('#gaming', {
    element(section) { section.append(pronosGamingScript, { html: true }); }
  });
}

const pronosGamingScript = `<script>
(() => {
  const panel = document.currentScript.parentElement;
  const heading = panel.querySelector('h2');
  if (!heading) return;
  const clock = new Intl.DateTimeFormat('fr-FR', {
    dateStyle: 'short', timeStyle: 'short', timeZone: 'Europe/Paris'
  });
  const element = (tag, text, className) => {
    const node = document.createElement(tag);
    node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  const original = source => {
    try {
      const url = new URL(source?.url);
      return source.nom && url.protocol === 'https:' && !url.username && !url.password;
    } catch { return false; }
  };
  fetch('/vm-gaming/news.json', { cache: 'no-store' }).then(response => {
    if (response.ok) return response.json();
  }).then(rows => {
    if (!Array.isArray(rows)) return;
    const now = Date.now();
    const cards = document.createDocumentFragment();
    const seen = new Set();
    for (const row of rows.slice().sort((a, b) => Date.parse(b?.publishedAt) - Date.parse(a?.publishedAt))) {
      const date = Date.parse(row?.publishedAt);
      if (!/^[a-z0-9][a-z0-9-]{1,99}$/.test(row?.id ?? '') || seen.has(row.id) ||
          !row.titre || !row.resume || !(now - 172800000 <= date && date <= now)) continue;
      const source = Array.isArray(row.sources) && row.sources.find(original);
      if (!source) continue;
      const card = element('article', '', 'news');
      const title = element('h3', '');
      const link = element('a', row.titre);
      link.href = '/vm-gaming/#a=' + encodeURIComponent(row.id);
      title.append(link);
      const sourceLink = element('a', 'Source originale', 'source');
      sourceLink.href = source.url;
      sourceLink.target = '_blank';
      sourceLink.rel = 'noopener noreferrer';
      card.append(element('p', clock.format(date) + ' · Source : ' + source.nom, 'meta'),
        title, element('p', String(row.resume).slice(0, 420)), sourceLink);
      cards.append(card);
      seen.add(row.id);
      if (seen.size === 5) break;
    }
    if (seen.size) panel.replaceChildren(heading, cards);
  }).catch(() => {});
})();
</script>`;

export async function multisportEdition(response) {
  if (!response.ok) return response;
  const original = await response.text();
  const code = original
    .replace('items.slice(0,7).map(', 'items.slice(0,15).map(')
    .replace("listNews('recent-list',rows,5,false)", "listNews('recent-list',rows,12,false)")
    .replace('function pickRegion(reg){', 'let activeRegion;\nfunction pickRegion(reg){\n activeRegion=reg;')
    .replace('\nfill();\n', '\nfill();\nif(activeRegion)pickRegion(activeRegion);\n')
    .replace(" document.addEventListener('visibilitychange',()=>{if(!document.hidden)load()});",
      " document.addEventListener('visibilitychange',()=>{if(!document.hidden)load()});\n window.setInterval(()=>{if(!document.hidden)load()},180000);");
  return new Response(code, {
    headers: { 'Content-Type': 'application/javascript; charset=utf-8', 'Cache-Control': 'no-cache' }
  });
}

export const gamingPressScript = `<script>
document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelector('.g-news');
  const panel = document.getElementById('presse');
  const list = document.getElementById('fxList');
  const more = document.getElementById('fxMore');
  if (!cards || !panel || !list || !more) return;
  cards.before(panel);
  let items = [];
  let limit = 12;
  const clock = new Intl.DateTimeFormat('fr-FR', {
    day:'numeric', month:'short', hour:'2-digit', minute:'2-digit', timeZone:'Europe/Paris'
  });
  function redraw() {
    const fragment = document.createDocumentFragment();
    for (const row of items.slice(0, limit)) {
      const item = document.createElement('li');
      const link = document.createElement('a');
      link.href = row.u;
      link.target = '_blank';
      link.rel = 'noopener nofollow';
      const stamp = document.createElement('time');
      stamp.dateTime = row.d;
      stamp.textContent = clock.format(new Date(row.d));
      const source = document.createElement('em');
      source.textContent = row.s + ' ↗';
      link.append(stamp, ' ' + row.t + ' ', source);
      item.append(link);
      fragment.append(item);
    }
    list.replaceChildren(fragment);
    more.hidden = items.length <= limit;
    more.textContent = 'Voir jusqu’à 50 titres';
    panel.hidden = items.length === 0;
  }
  async function update() {
    try {
      const r = await fetch('/fil.json', { cache:'no-store' });
      if (!r.ok) return;
      const data = await r.json();
      if (!Array.isArray(data.titres)) return;
      const urls = new Set();
      items = data.titres.filter(row => {
        if (row?.k !== 'gaming' || !row.t || !row.s || !Number.isFinite(Date.parse(row.d))) return false;
        let url;
        try { url = new URL(row.u); } catch { return false; }
        if (url.protocol !== 'https:') return false;
        url.hash = '';
        for (const key of Array.from(url.searchParams.keys())) {
          if (key.startsWith('utm_')) url.searchParams.delete(key);
        }
        if (urls.has(url.href)) return false;
        urls.add(url.href);
        return true;
      }).sort((a,b) => Date.parse(b.d) - Date.parse(a.d)).slice(0, 50);
      if (items.length) redraw();
    } catch { /* Le dernier affichage valide reste accessible. */ }
  }
  more.onclick = () => {
    if (!items.length) return;
    limit = 50;
    redraw();
  };
  update();
  window.setInterval(() => { if (!document.hidden) update(); }, 180000);
});
</script>`;
