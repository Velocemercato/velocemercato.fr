import foot from './data/foot.json';
import actus from './data/actus.json';
import gaming from './data/gaming.json';
import footBaseline from './data/foot-baseline.json';
import actusBaseline from './data/actus-baseline.json';
import gamingBaseline from './data/gaming-baseline.json';

const pages = 'https://velocemercato.pages.dev';
const github = 'https://raw.githubusercontent.com/Velocemercato/velocemercato.fr/main';
const sportPreview = 'https://vm-sport-apercu.velocemercato87.workers.dev';
const advicePath = '/pronos/selection.json';
const editorialData = 'https://raw.githubusercontent.com/Velocemercato/velocemercato.fr/codex/preview-rattrapage/cloudflare/rattrapage/data';
const regionalPath = '/foot-amateur/actus.json';
const specialPaths = new Set(['/multisport/actualites.json', '/belfort/actus.json', regionalPath]);
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

async function readJson(origin, path, cacheTtl = 180) {
  try {
    const response = await fetch(origin + path, {
      signal: AbortSignal.timeout(5000),
      cf: { cacheEverything: true, cacheTtl }
    });
    if (response.ok) return await response.json();
  } catch {}
  return null;
}

function mergeLocal(base, next, keyOf = item => item.u) {
  if (!Array.isArray(base?.titres) || !Array.isArray(next?.titres)) return base ?? next;
  const titles = new Map();
  for (const item of [...base.titres, ...next.titres]) {
    if (!item?.u) continue;
    const key = keyOf(item);
    if (!titles.has(key)) titles.set(key, item);
  }
  return {
    ...base, ...next,
    maj: [base.maj, next.maj].filter(Boolean).sort().at(-1),
    titres: [...titles.values()].sort((a, b) => String(b.d).localeCompare(String(a.d)))
  };
}

function mergeSports(base, next) {
  if (!base?.sports) return next;
  if (!next?.sports) return base;
  const sports = { ...base.sports };
  for (const [sport, incoming] of Object.entries(next.sports)) {
    if (!Array.isArray(incoming)) continue;
    const rows = new Map((sports[sport] ?? []).map(item => [item.id, item]));
    for (const item of incoming) if (item?.id) rows.set(item.id, item);
    sports[sport] = [...rows.values()].sort((a, b) => String(b.date).localeCompare(String(a.date)));
  }
  return {
    ...base, ...next, sports,
    misAJour: [base.misAJour, next.misAJour].filter(Boolean).sort().at(-1)
  };
}

function reply(data) {
  return data
    ? Response.json(data, { headers: { 'Cache-Control': 'no-store' } })
    : new Response(null, { status: 503 });
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (request.method !== 'GET' || (!feeds.has(url.pathname) && !specialPaths.has(url.pathname) && url.pathname !== advicePath)) {
      if (url.hostname === 'velocemercato.fr') return fetch(request);
      return new Response(null, { status: 404 });
    }
    const path = url.pathname;
    if (path === advicePath) {
      const [legacy, advice] = await Promise.all([
        readJson(pages, path), readJson(editorialData, '/public-advice.json', 60)
      ]);
      const now = Date.now();
      const active = advice?.match && advice?.analysis && Array.isArray(advice.sources) &&
        advice.sources.length > 0 && Date.parse(advice.publishedAt) <= now && now < Date.parse(advice.kickoff);
      return reply({ ...legacy, publicAdvice: active ? advice : null });
    }
    if (specialPaths.has(path)) {
      const [base, fresh, recovered] = await Promise.all([
        readJson(pages, path), readJson(github, path),
        path === '/multisport/actualites.json' ? readJson(sportPreview, path) :
          path === regionalPath ? readJson(editorialData, '/foot-regions.json') : null
      ]);
      if (path === '/belfort/actus.json') return reply(mergeLocal(base, fresh));
      if (path === regionalPath) {
        const regionalKey = item => JSON.stringify([item.l, item.u]);
        return reply(mergeLocal(mergeLocal(base, fresh, regionalKey), recovered, regionalKey));
      }
      return reply(mergeSports(mergeSports(base, recovered), fresh));
    }
    const base = await fetch(new URL(path, pages));
    if (!base.ok) return base;
    const originals = await base.clone().json().catch(() => null);
    if (!Array.isArray(originals)) return base;
    const [current, editorial] = await Promise.all([readJson(collector, path), readJson(github, path)]);
    const live = Array.isArray(current) ? current : [];
    const { additions, baseline } = feeds.get(url.pathname);
    const existing = [...new Map([...originals, ...baseline, ...live].map(article => [article.id, article])).values()];
    const fresh = Array.isArray(editorial) ? editorial.filter(article => {
      const date = Date.parse(article.publishedAt ?? article.createdAt);
      return Number.isFinite(date) && date <= Date.now();
    }) : [];
    const entries = merge(merge(existing, additions), fresh);
    return Response.json(entries, { headers: { 'Cache-Control': 'no-store' } });
  }
};
