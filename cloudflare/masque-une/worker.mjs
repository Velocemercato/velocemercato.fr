import { renderKit } from './kit-reseaux.mjs';

const VELOCE_ORIGIN = 'https://velocemercato.pages.dev';
const UNIVERS_ORIGIN = 'https://vmunivers.pages.dev';

const SCORE_STYLE = '<style id="vm-readable-scores">#sTicker .sviewport{min-width:0;overflow-x:auto}#sRun{animation:none!important;transform:none!important;padding-left:0!important}</style>';

const MOBILE_STYLE = `<style id="vm-home-mobile">
.vm-mother-portals .vm-mobile-hub{display:none}
@media(max-width:640px){
  .vm-mother-hero>img{height:145px}
  .vm-mother-hero-copy{padding:18px 8px 10px}
  .vm-mother-hero-copy h1{font-size:clamp(1.55rem,8vw,2.4rem)}
  .vm-mother-hero-copy p{display:none}
  .vm-mother-portals{gap:7px;margin:8px auto}
  .vm-mother-portals .vm-mother-tile{
    display:flex;flex-direction:row;align-items:center;justify-content:flex-start;
    gap:7px;min-height:50px;padding:8px 10px;text-align:left;
    border:1px solid #b9304b;border-radius:9px;box-shadow:none
  }
  .vm-mother-portals .vm-mother-tile::before,.vm-mother-portals .vm-mother-tile::after,
  .vm-mother-portals .vm-mother-tile small,.vm-mother-portals .vm-mother-arrow,
  .vm-mother-columns,.vm-mother-bottom,.vm-cinema-ribbons{display:none}
  .vm-mother-portals .vm-mother-icon{flex:none;font-size:1.1rem}
  .vm-mother-portals .vm-mobile-hub{display:flex}
  .vm-mother-portals a:focus-visible{outline:2px solid #ffe16e;outline-offset:2px}
}
</style>`;
const MOBILE_LINKS = '<a class="vm-mother-tile vm-mobile-hub" href="#feed-title"><span class="vm-mother-icon" aria-hidden="true">⚽</span><strong>Actus foot</strong></a><a class="vm-mother-tile vm-mobile-hub" href="#pastille-tv"><span class="vm-mother-icon" aria-hidden="true">▶</span><strong>Pastilles vidéo</strong></a><a class="vm-mother-tile vm-mobile-hub" href="/belfort/"><span class="vm-mother-icon" aria-hidden="true">📍</span><strong>VM Belfort</strong></a>';

const AD_OFFERS = '<section class="vms-section" id="publicite-vm" aria-labelledby="titre-publicite-vm"><div class="vms-wrap"><h2 id="titre-publicite-vm">Publicité sur les sites et réseaux VM</h2><dl><dt>Véloce Mercato, VM Actus ou VM Gaming</dt><dd>Encart média à 39 €/mois. Emplacement convenu selon la disponibilité.</dd><dt>VM Belfort</dt><dd>Encart local à 29 €/mois.</dd><dt>VM Univers</dt><dd>Emplacement sur devis, selon le format et la durée.</dd><dt>Réseaux VM</dt><dd>Pack Visibilité Pro à 39 €/mois, avec une vidéo courte par mois. Pour une page ou une campagne dédiée, demande un devis.</dd></dl><p><a class="vms-btn" href="https://velocemercato.fr/pub/#packs">Voir les formats et demander un devis</a></p></div></section>';

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const isPreview = url.hostname.endsWith('.workers.dev');
    const isUnivers = url.hostname === 'vmunivers.fr' ||
      (isPreview && url.searchParams.get('site') === 'vmunivers');
    if (url.hostname !== 'velocemercato.fr' && !isUnivers && !isPreview) {
      return new Response(null, { status: 404 });
    }

    if (!['GET', 'HEAD'].includes(request.method)) {
      return isPreview ? new Response(null, { status: 404 }) : fetch(request);
    }
    if (url.pathname === '/kit-reseaux-vm') {
      const kit = await renderKit();
      return request.method === 'HEAD' ? new Response(null, { headers: kit.headers }) : kit;
    }
    const studio = !isUnivers && ['/web-studio', '/web-studio.html'].includes(url.pathname);
    if (url.pathname !== '/' && !studio) {
      return isPreview ? new Response(null, { status: 404 }) : fetch(request);
    }

    const origin = isUnivers ? UNIVERS_ORIGIN : VELOCE_ORIGIN;
    if (isPreview) url.searchParams.delete('site');
    const response = await fetch(new URL((studio ? '/web-studio' : '/') + url.search, origin), {
      method: request.method,
      headers: { Accept: 'text/html' },
      redirect: 'manual'
    });
    if (request.method === 'HEAD' || !response.ok ||
        !response.headers.get('Content-Type')?.includes('text/html')) {
      return response;
    }

    const rewriter = new HTMLRewriter();
    if (studio) {
      rewriter.on('#tarifs', {
        element(element) {
          element.after(AD_OFFERS, { html: true });
        }
      });
    } else if (isUnivers) {
      rewriter.on('section#edition-vm', {
        element(element) {
          element.remove();
        }
      });
    } else {
      rewriter.on('#actualites-du-jour', {
        element(element) {
          element.remove();
        }
      }).on('a[href="#actualites-du-jour"]', {
        element(element) {
          element.setAttribute('href', '#feed-title');
        }
      }).on('.vm-mother-portals', {
        element(element) {
          element.prepend(MOBILE_LINKS, { html: true });
        }
      }).on('head', {
        element(element) {
          element.append(SCORE_STYLE + MOBILE_STYLE, { html: true });
        }
      });
    }
    const rewritten = rewriter.transform(response);

    const headers = new Headers(rewritten.headers);
    for (const name of ['Content-Length', 'ETag', 'Last-Modified']) {
      headers.delete(name);
    }
    headers.set('Cache-Control', 'no-store');
    return new Response(rewritten.body, { status: rewritten.status, headers });
  }
};
