const github = 'https://raw.githubusercontent.com/Velocemercato/velocemercato.fr/main';
const pages = 'https://velocemercato.pages.dev';
const mirror = 'https://vm-masque-une.velocemercato87.workers.dev';
const minute = 60_000;
const hour = 60 * minute;

export const livePaths = new Set([
  '/fil.json', '/scores.json', '/matchs.json', '/videos.json', '/flash.json',
  '/studio/emissions.json', '/studio/diffusions.json'
]);

function timestamp(value, now) {
  const time = Date.parse(value);
  return Number.isFinite(time) && time <= now ? time : 0;
}

function publishedAt(row) {
  return row?.publishedAt ?? row?.date_publication ?? row?.date;
}

function validated(path, data, now) {
  if (path === '/scores.json' || path === '/fil.json') {
    const key = path === '/scores.json' ? 'matchs' : 'titres';
    const time = timestamp(data?.maj, now);
    return time && Array.isArray(data?.[key]) ? { data, time } : null;
  }
  if (!Array.isArray(data)) return null;
  if (path === '/matchs.json') {
    const rows = data.filter(row => row?.id != null && Number.isFinite(Date.parse(row.date)));
    const time = Math.max(0, ...rows.map(row => Date.parse(row.date)));
    return time ? { data: rows, time } : null;
  }
  const rows = data.filter(row => timestamp(publishedAt(row), now));
  const time = Math.max(0, ...rows.map(row => timestamp(publishedAt(row), now)));
  return time ? { data: rows, time } : null;
}

async function read(origin, path, cacheSeconds, now) {
  try {
    const url = new URL(origin + path);
    if (origin === github) url.searchParams.set('vm', Math.floor(now / (cacheSeconds * 1000)));
    const response = await fetch(url, {
      headers: { Accept: 'application/json' },
      signal: AbortSignal.timeout(4500),
      cf: { cacheEverything: true, cacheTtlByStatus: { '200-299': cacheSeconds, '400-599': 0 } }
    });
    return response.ok ? validated(path, await response.json(), now) : null;
  } catch {
    return null;
  }
}

async function current(path, now) {
  const seconds = path === '/scores.json' ? 60 : 180;
  const fresh = await read(github, path, seconds, now);
  if (fresh && now - fresh.time <= (path === '/scores.json' ? 20 * minute : 48 * hour)) return fresh;
  const baseline = await read(pages, path, seconds, now);
  if (!baseline || (fresh && fresh.time >= baseline.time)) return fresh;
  return baseline;
}

function pressCategory(row) {
  if (row.k !== 'gaming') return row;
  const url = URL.parse(row.u ?? '');
  if (!url) return row;
  const host = url.hostname.replace(/^www\./, '');
  const mixedSection = ['lesnumeriques.com', 'numerama.com', 'journaldugeek.com', 'next.ink'].includes(host);
  const aboutGames = /\b(gaming|jeux? vid[eé]o|consoles?|playstation|ps5|xbox|switch|steam|nintendo|esport|geforce|manettes?|itch\.io|gta|zelda|bioware|warzone|phantom blade|kojima)\b/i
    .test(row.t + ' ' + url.pathname.replace(/-/g, ' '));
  return mixedSection && !aboutGames ? { ...row, k: 'actus' } : row;
}

export async function liveResponse(request, path, now = Date.now()) {
  const match = await current(path, now);
  const headers = new Headers({
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
    'Vary': 'Origin'
  });
  const origin = request.headers.get('Origin');
  if (origin === 'https://velocemercato.fr' || origin === mirror) {
    headers.set('Access-Control-Allow-Origin', origin);
  }
  if (match) headers.set('X-VM-Data-Time', new Date(match.time).toISOString());

  let data = match?.data ?? null;
  const recent = new URL(request.url).searchParams.get('vm_recent') === '1';
  if (path === '/scores.json' && (!match || now - match.time > 20 * minute)) {
    data = { matchs: [], maj: null, indisponible: true };
  } else if (path === '/fil.json') {
    data = {
      titres: (data?.titres ?? []).filter(row => {
        const date = timestamp(row?.d, now);
        return date && now - date < 48 * hour;
      }).map(pressCategory),
      maj: data?.maj ?? null
    };
  } else if (path === '/flash.json' || (recent && (path === '/videos.json' || path === '/studio/emissions.json' || path === '/studio/diffusions.json'))) {
    data = (data ?? []).filter(row => now - timestamp(publishedAt(row), now) < 48 * hour);
  }
  const response = Response.json(data ?? [], { headers });
  return request.method === 'HEAD' ? new Response(null, { headers: response.headers }) : response;
}

export async function latestPastille(now = Date.now(), universe = null) {
  const source = await current('/studio/diffusions.json', now);
  return (source?.data ?? []).filter(row => {
    const time = timestamp(row.date_publication, now);
    const video = row.plateformes?.youtube;
    return (!universe || row.universes?.includes(universe)) && time && now - time <= 48 * hour && video?.status === 'published' &&
      /^https:\/\/www\.youtube\.com\/watch\?v=[\w-]{11}$/.test(video.url ?? '');
  }).sort((a, b) => Date.parse(b.date_publication) - Date.parse(a.date_publication))[0] ?? null;
}

// Already-routed homepages can read current data while the canonical paths
// still point at the Pages snapshot. Only known, read-only paths are mapped.
export const liveBootstrap = `<script id="vm-live-bootstrap">
(() => {
  const paths = new Set(${JSON.stringify([...livePaths])});
  const original = window.fetch.bind(window);
  window.fetch = (resource, options) => {
    if (typeof resource !== 'string' && !(resource instanceof URL)) return original(resource, options);
    const url = new URL(resource, document.baseURI);
    if (location.pathname === '/' && url.origin === 'https://countapi.mileshilliard.com' &&
        ['/api/v1/get/velocemercato-pastille-', '/api/v1/hit/velocemercato-pastille-'].some(prefix => url.pathname.startsWith(prefix))) {
      return Promise.resolve(new Response(null, { status: 410 }));
    }
    if (url.origin === location.origin && (!options?.method || options.method === 'GET')) {
      if (paths.has(url.pathname)) {
        const recent = url.pathname === '/studio/emissions.json' || url.pathname === '/studio/diffusions.json' || url.pathname === '/videos.json';
        return original(${JSON.stringify(mirror)} + url.pathname + (recent ? '?vm_recent=1' : ''), options);
      }
      if (url.pathname === '/prono.json') return Promise.resolve(new Response('null'));
    }
    return original(resource, options);
  };
})();
</script>`;
