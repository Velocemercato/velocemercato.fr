import foot from './data/foot.json';
import actus from './data/actus.json';
import gaming from './data/gaming.json';
import footBaseline from './data/foot-baseline.json';
import actusBaseline from './data/actus-baseline.json';
import gamingBaseline from './data/gaming-baseline.json';

const pages = 'https://velocemercato.pages.dev';
const collector = 'https://vm-flux-3min.velocemercato87.workers.dev';
const feeds = new Map([
  ['/articles.json', { additions: foot, baseline: footBaseline }],
  ['/actus/news.json', { additions: actus, baseline: actusBaseline }],
  ['/vm-gaming/news.json', { additions: gaming, baseline: gamingBaseline }]
]);

function sourceKeys(article) {
  const sources = Array.isArray(article.sources) ? article.sources : [];
  return sources.flatMap(({ url } = {}) => {
    const link = URL.parse(url ?? '');
    if (!link || !['http:', 'https:'].includes(link.protocol)) return [];
    link.hash = '';
    for (const key of Array.from(link.searchParams.keys())) {
      if (/^(utm_|fbclid$|at_)/i.test(key)) link.searchParams.delete(key);
    }
    return [link.href.replace(/\/$/, '')];
  });
}

function merge(base, additions) {
  const result = [...base];
  const ids = new Set(base.map(item => item.id));
  const links = new Set(base.flatMap(sourceKeys));
  for (const article of additions) {
    const keys = sourceKeys(article);
    if (ids.has(article.id) || keys.some(key => links.has(key))) continue;
    ids.add(article.id);
    keys.forEach(key => links.add(key));
    result.push(article);
  }
  return result.sort((a, b) => Date.parse(b.publishedAt ?? b.createdAt) - Date.parse(a.publishedAt ?? a.createdAt));
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (request.method !== 'GET' || !feeds.has(url.pathname)) {
      if (url.hostname === 'velocemercato.fr') return fetch(request);
      return new Response(null, { status: 404 });
    }
    const base = await fetch(new URL(url.pathname, pages));
    if (!base.ok) return base;
    const originals = await base.clone().json().catch(() => null);
    if (!Array.isArray(originals)) return base;
    let live = [];
    try {
      const response = await fetch(new URL(url.pathname, collector), { signal: AbortSignal.timeout(5000) });
      if (response.ok) {
        const json = await response.json();
        if (Array.isArray(json)) live = json;
      }
    } catch {}
    const { additions, baseline } = feeds.get(url.pathname);
    const existing = [...new Map([...originals, ...baseline, ...live].map(article => [article.id, article])).values()];
    const entries = merge(existing, additions);
    return Response.json(entries, { headers: { 'Cache-Control': 'no-store' } });
  }
};
