import { redirects } from './verified-urls.mjs';

const publicHosts = new Set(['velocemercato.fr', 'vmunivers.fr']);
const legacyAnchor = '/#actualites-du-jour';
const vuAdditions = ['/kit-du-jour'];
const vmAdditions = ['/kit-du-jour', '/scores/', '/mangas/'];

function normalLink(href, origin) {
  if (!href || href.startsWith('#')) return href;
  let url;
  try { url = new URL(href, origin); } catch { return href; }
  if (url.hostname === 'velocemercato.pages.dev' && /^\/a\//.test(url.pathname)) {
    url.hostname = 'velocemercato.fr';
  }
  if (!publicHosts.has(url.hostname) || !['http:', 'https:'].includes(url.protocol)) return href;
  url.protocol = 'https:';
  const mapped = Object.hasOwn(redirects[url.hostname] ?? {}, url.pathname)
    ? redirects[url.hostname][url.pathname] : null;
  if (mapped) url.pathname = mapped;
  if (url.hostname === 'velocemercato.fr' && url.pathname + url.hash === legacyAnchor) {
    url.hash = 'feed-title';
  }
  if (!mapped && url.href === new URL(href, origin).href) return href;
  return href.startsWith('/') && !href.startsWith('//') && url.origin === origin.origin
    ? url.pathname + url.search + url.hash
    : url.href;
}

export async function sitemap(response, universe) {
  if (!response.ok) return response;
  const xml = await response.text();
  const locations = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map(match => match[1]);
  const host = universe ? 'vmunivers.fr' : 'velocemercato.fr';
  const base = new URL('https://' + host);
  const paths = new Set([...locations.map(location => normalLink(location, base)),
    ...(universe ? vuAdditions : vmAdditions).map(path => base.origin + path)]);
  const content = [...paths].filter(location => location.startsWith(base.origin + '/') && !location.includes('?'))
    .map(location => '  <url><loc>' + location + '</loc></url>').join('\n');
  return new Response('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + content + '\n</urlset>\n', {
    headers: { 'Content-Type': 'application/xml; charset=utf-8', 'Cache-Control': 'public, max-age=300' }
  });
}

const mobileStyle = `<style id="vm-audit-polish">
:where(a,button,input,select,textarea,summary):focus-visible{outline:3px solid #e39b17;outline-offset:3px}
:where(main,section,h2,h3)[id]{scroll-margin-top:88px}
.vm-flash-toggle{display:block;max-width:100%;margin:6px 12px;padding:6px 10px;border-radius:6px;border:1px solid currentColor;background:#132144;color:#fff;font:600 .78rem system-ui;cursor:pointer}
body:has(#ticker[hidden]) .vm-flash-toggle{display:none}
.vm-flash-paused *{animation-play-state:paused!important}
@media(prefers-reduced-motion:reduce){#tickerRun,.home-tickers [class*="run"]{animation:none!important;transform:none!important}}
@media(max-width:640px){
  .vmfab,.vminst.show,.vm-alert-fab{position:static!important;inset:auto!important;max-width:calc(100% - 24px);margin:10px 12px!important}
  .hero-manga-promo{position:static!important;inset:auto!important;transform:none!important;display:inline-flex;max-width:100%;margin:12px 0 0}
}
</style>`;

const flashButton = '<button type="button" class="vm-flash-toggle" aria-controls="ticker" aria-pressed="false">Mettre le flash en pause</button>';
const flashScript = `<script>
document.addEventListener('click', event => {
  const button = event.target.closest('.vm-flash-toggle');
  if (!button) return;
  const ticker = document.getElementById(button.getAttribute('aria-controls'));
  if (!ticker) return;
  const paused = ticker.classList.toggle('vm-flash-paused');
  button.setAttribute('aria-pressed', String(paused));
  button.textContent = paused ? 'Reprendre le flash' : 'Mettre le flash en pause';
});
</script>`;

export function polish(rewriter, url, universe) {
  const host = universe ? 'vmunivers.fr' : 'velocemercato.fr';
  const publicUrl = new URL(url.pathname, 'https://' + host);
  const pathname = publicUrl.pathname;
  let shareImage = false;
  rewriter.on('a[href]', {
    element(link) {
      const href = link.getAttribute('href');
      const next = normalLink(href, publicUrl);
      if (next && next !== href) link.setAttribute('href', next);
    }
  }).on('link[rel="canonical"][href]', {
    element(link) {
      const href = link.getAttribute('href');
      const next = normalLink(href, publicUrl);
      if (next && next !== href) link.setAttribute('href', next);
    }
  }).on('img[src="/img/logo-vm-officiel.png"]', {
    element(img) {
      img.setAttribute('src', '/assets/vm-logo-optimized.webp');
    }
  }).on('meta[property="og:image"]', {
    element() { shareImage = true; }
  }).on('head', {
    element(head) {
      head.onEndTag(end => {
        end.before(mobileStyle, { html: true });
        if (!shareImage && !pathname.startsWith('/demos/')) {
          const image = universe
            ? 'https://vmunivers.fr/app/logo-vm-officiel.png'
            : 'https://velocemercato.fr/img/partage-velocemercato.jpg';
          end.before('<meta property="og:image" content="' + image + '">', { html: true });
        }
      });
    }
  });

  if (!universe && ['/actus/', '/vm-gaming/'].includes(pathname)) {
    rewriter.on('#ticker', {
      element(ticker) { ticker.before(flashButton + flashScript, { html: true }); }
    });
  }
  if (!universe && pathname.startsWith('/multisport/')) {
    rewriter.on('a.region[href^="#list-"]', {
      element(link) {
        link.setAttribute('data-region', link.getAttribute('href').slice('#list-'.length));
        link.setAttribute('href', '#actualites');
      }
    });
  }
  if (!universe && pathname === '/') {
    rewriter.on('.quiz-tag', {
      element(tag) { tag.setInnerContent('🧠 LE QUIZ VM'); }
    }).on('a[href="/pronos/#pronos-du-jour"]', {
      element(link) {
        if (!link.getAttribute('class')) link.prepend('18+ · ');
      }
    });
  }
  if (universe && pathname === '/') {
    rewriter.on('.vmv-credit', {
      text(chunk) { chunk.replace(chunk.text.replace(/Prix de création TTC/g, 'Prix de création')); }
    });
  }
  return rewriter;
}

export function htmlResponse(rewritten, https) {
  const headers = new Headers(rewritten.headers);
  for (const key of ['Content-Length', 'ETag', 'Last-Modified']) headers.delete(key);
  headers.set('Cache-Control', 'no-store');
  headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  headers.set('X-Content-Type-Options', 'nosniff');
  if (https) headers.set('Strict-Transport-Security', 'max-age=300');
  return new Response(rewritten.body, { status: rewritten.status, headers });
}
