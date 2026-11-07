import { gamingPressScript, multisportEdition, pronosPage, verifiedAdvice } from './public-content.mjs';
import { renderKit } from './kit-reseaux.mjs';
import { htmlResponse, polish, sitemap } from './site-polish.mjs';
import { footServiceWorker, pwaIcon } from './pwa-assets.mjs';
import { logo } from './logo.mjs';
import { latestPastille, liveBootstrap, livePaths, liveResponse } from './live-data.mjs';

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

const STUDIO_HELP = '<p class="vms-fine">Prépare ta demande, puis envoie-la dans ta messagerie. Tu peux aussi copier le texte et le coller dans le service de messagerie de ton choix.</p>';
const ANALYSIS_LINK = '<h2>Analyse sportive du jour</h2><p>Retrouve l’analyse vérifiée et son horaire sur la page dédiée.</p><p><a href="/pronos/#pronos-du-jour">Voir l’analyse sportive</a></p>';
const MOBILE_ACCESS = '<style id="vm-a11y">.vm-skip{position:absolute;left:12px;top:12px;transform:translateY(-250%);z-index:9999;background:#ffd54a;color:#111;padding:10px 14px;border-radius:5px}.vm-skip:focus{transform:none}a:focus-visible,button:focus-visible{outline:3px solid #ffd54a;outline-offset:2px}#feed-title,#actualites{scroll-margin-top:85px}@media(max-width:360px){.vm-mother-quicklinks,.vm-social-icons{flex-wrap:wrap}.vm-mother-tile strong{overflow-wrap:anywhere}}@media(prefers-reduced-motion:reduce){.home-tickers *,#sRun{animation:none!important;scroll-behavior:auto!important}}</style>';
const VELOCE_HTML = new Set(['/scores/', '/belfort/', '/actus/', '/vm-gaming/', '/multisport/', '/kit-reseaux', '/kit-reseaux.html', '/rentabilite', '/rentabilite.html', '/mangas/', '/pronos/']);

const escape = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[char]);

const AD_OFFERS = '<section class="vms-section" id="publicite-vm" aria-labelledby="titre-publicite-vm"><div class="vms-wrap"><h2 id="titre-publicite-vm">Publicité sur les sites et réseaux VM</h2><dl><dt>Véloce Mercato, VM Actus ou VM Gaming</dt><dd>Encart média à 39 €/mois. Emplacement convenu selon la disponibilité.</dd><dt>VM Belfort</dt><dd>Encart local à 29 €/mois.</dd><dt>VM Univers</dt><dd>Emplacement sur devis, selon le format et la durée.</dd><dt>Réseaux VM</dt><dd>Pack Visibilité Pro à 39 €/mois, avec une vidéo courte par mois. Pour une page ou une campagne dédiée, demande un devis.</dd></dl><p><a class="vms-btn" href="https://velocemercato.fr/pub/#packs">Voir les formats et demander un devis</a></p></div></section>';

const universNotFound = '<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Page introuvable · VM Univers</title><main><h1>Page introuvable</h1><p>Retrouve les rubriques dans l’annuaire VM Univers.</p><a href="https://vmunivers.fr/#projets">Ouvrir l’annuaire</a></main></html>';

async function universPage(request, url, preview) {
  if (url.pathname === '/index.html') return Response.redirect(new URL('/' + url.search, url), 301);
  const originUrl = new URL(url.pathname + url.search, UNIVERS_ORIGIN);
  const response = preview ? await fetch(originUrl, { method: request.method }) : await fetch(request);
  if (!response.ok || !response.headers.get('Content-Type')?.includes('text/html')) return response;
  const check = request.method === 'HEAD'
    ? await fetch(originUrl)
    : response.clone();
  const html = await check.text();
  const servesHomepage = html.includes('id="projets"') &&
    /<link\b[^>]*\brel=["']canonical["'][^>]*\bhref=["']https:\/\/vmunivers\.fr\/["']/i.test(html);
  if (!servesHomepage) return response;
  return new Response(request.method === 'HEAD' ? null : universNotFound, {
    status: 404, headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' }
  });
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const isPreview = url.hostname.endsWith('.workers.dev');
    const isUnivers = url.hostname === 'vmunivers.fr' ||
      (isPreview && url.searchParams.get('site') === 'vmunivers');
    if (url.hostname !== 'velocemercato.fr' && !isUnivers && !isPreview) {
      return new Response(null, { status: 404 });
    }

    if (!isPreview && url.protocol === 'http:') {
      url.protocol = 'https:';
      return Response.redirect(url, 301);
    }
    if (isPreview) url.searchParams.delete('site');
    if (!['GET', 'HEAD'].includes(request.method)) {
      return isPreview ? new Response(null, { status: 404 }) : fetch(request);
    }
    const icon = pwaIcon(url.pathname, isUnivers, request.method === 'HEAD');
    if (icon) return icon;
    if (!isUnivers && url.pathname === '/sw.js' && request.method === 'GET') {
      return footServiceWorker(await fetch(new URL('/sw.js', VELOCE_ORIGIN)));
    }
    if (url.pathname === '/assets/vm-logo-optimized.webp' ||
        (url.pathname === '/img/logo-vm-officiel.png' && request.headers.get('Accept')?.includes('image/webp'))) {
      return new Response(request.method === 'HEAD' ? null : logo, {
        headers: { 'Content-Type': 'image/webp', 'Cache-Control': 'public, max-age=86400', 'Vary': 'Accept' }
      });
    }
    if (isPreview && url.pathname === '/favicon.ico') {
      return Response.redirect(new URL('/assets/vm-logo-optimized.webp', url), 302);
    }
    if (!isUnivers && livePaths.has(url.pathname)) return liveResponse(request, url.pathname);
    if (url.pathname === '/kit-reseaux-vm' || url.pathname === '/kit-du-jour') {
      const now = new Date();
      const kit = await renderKit(now, await verifiedAdvice(now.getTime()));
      return request.method === 'HEAD' ? new Response(null, { headers: kit.headers }) : kit;
    }
    if (!isUnivers && url.pathname === '/multisport/univers.js' && request.method === 'GET') {
      return multisportEdition(await fetch(new URL(url.pathname + url.search, VELOCE_ORIGIN)));
    }
    if (url.pathname === '/sitemap.xml' && request.method === 'GET') {
      const origin = isUnivers ? UNIVERS_ORIGIN : VELOCE_ORIGIN;
      return sitemap(await fetch(new URL('/sitemap.xml', origin)), isUnivers);
    }
    if (isUnivers && ['/studio/reseaux', '/studio/reseaux.html', '/studio/reseaux/'].includes(url.pathname)) {
      return Response.redirect('https://vmunivers.fr/kit-du-jour' + url.search, 302);
    }
    if (isUnivers && ['/studio', '/studio/', '/studio.html'].includes(url.pathname)) {
      return Response.redirect('https://velocemercato.fr/web-studio' + url.search, 302);
    }
    const studio = !isUnivers && ['/web-studio', '/web-studio.html'].includes(url.pathname);
    const home = url.pathname === '/';
    const velocePage = !isUnivers && (VELOCE_HTML.has(url.pathname) ||
      /^\/multisport\/(nba|nfl|f1|motogp|tennis|rugby|cyclisme|nhl|mlb|mma|ski)\/$/.test(url.pathname));
    if (!home && !studio && !velocePage) {
      const response = isUnivers ? await universPage(request, url, isPreview) : isPreview
        ? await fetch(new URL(url.pathname + url.search, VELOCE_ORIGIN), { method: request.method, redirect: 'manual' })
        : await fetch(request);
      if (request.method === 'HEAD' || !response.ok ||
          !response.headers.get('Content-Type')?.includes('text/html')) return response;
      const rewriter = polish(new HTMLRewriter(), url, isUnivers);
      return htmlResponse(rewriter.transform(response), !isPreview);
    }

    const origin = isUnivers ? UNIVERS_ORIGIN : VELOCE_ORIGIN;
    const originPath = studio ? '/web-studio' : url.pathname.replace(/\.html$/, '');
    const [response, pastille, advice] = await Promise.all([
      fetch(new URL(originPath + url.search, origin), {
        method: request.method,
        headers: { Accept: 'text/html' },
        redirect: 'manual'
      }),
      !isUnivers && request.method === 'GET' && (home || url.pathname === '/belfort/') ? latestPastille(Date.now(), home ? null : 'actus') : null,
      !isUnivers && url.pathname === '/pronos/' && request.method === 'GET' ? verifiedAdvice() : null
    ]);
    if (request.method === 'HEAD' || !response.ok ||
        !response.headers.get('Content-Type')?.includes('text/html')) {
      return response;
    }

    const rewriter = polish(new HTMLRewriter(), url, isUnivers);
    if (!isUnivers && url.pathname === '/pronos/') pronosPage(rewriter, advice);
    if (!isUnivers && url.pathname === '/vm-gaming/') {
      rewriter.on('head', { element(head) { head.append(gamingPressScript, { html: true }); } })
        .on('#t-presse', {
          element(title) { title.setInnerContent('Derniers titres Gaming <small>Le fil de la presse, avec les liens vers les sources</small>', { html: true }); }
        }).on('#maj', {
          element(note) { note.setInnerContent('Brèves VM'); }
        });
    }

    if (studio) {
      rewriter.on('#tarifs', {
        element(element) {
          element.after(AD_OFFERS, { html: true });
        }
      }).on('#devis form', {
        element(element) {
          element.before(STUDIO_HELP, { html: true });
        }
      }).on('.vms-amount small', {
        text(chunk) {
          chunk.replace(chunk.text.replace(/^TTC\s*·\s*/, ''));
        }
      }).on('.vms-section#trois-offres', {
        element(element) {
          element.before('<span id="photo"></span>', { html: true });
        }
      });
    } else if (isUnivers) {
      rewriter.on('section#edition-vm', {
        element(element) {
          element.remove();
        }
      });
    } else if (home) {
      rewriter.on('body', {
        element(element) {
          element.prepend('<a class="vm-skip" href="#feed-title">Aller aux actualités</a>', { html: true });
        }
      }).on('#prono', {
        element(element) {
          element.removeAttribute('hidden');
          element.removeAttribute('aria-labelledby');
          element.setInnerContent(ANALYSIS_LINK, { html: true });
        }
      }).on('.pastille-feed[data-broadcast-feed]', {
        element(element) {
          element.remove();
        }
      }).on('h1#v2-title', {
        element(element) {
          element.tagName = 'h2';
        }
      }).on('#ptvMain', {
        element(element) {
          if (pastille) element.before('<p class="ptv-cap"><a href="' + escape(pastille.plateformes.youtube.url) +
            '">▶ ' + escape(pastille.titre) + ' sur YouTube</a></p>', { html: true });
        }
      }).on('#actualites-du-jour', {
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
          element.prepend(liveBootstrap, { html: true });
          element.append(SCORE_STYLE + MOBILE_STYLE + MOBILE_ACCESS, { html: true });
        }
      });
    } else {
      rewriter.on('head', {
        element(element) {
          element.prepend(liveBootstrap, { html: true });
          if (url.pathname === '/scores/') {
            element.append('<link rel="canonical" href="https://velocemercato.fr/scores/">', { html: true });
          }
        }
      }).on('a[href="/#actualites-du-jour"]', {
        element(element) {
          element.setAttribute('href', '/#feed-title');
        }
      });
      if (['/kit-reseaux','/kit-reseaux.html','/rentabilite','/rentabilite.html'].includes(url.pathname)) {
        rewriter.on('a[href="#modeles"], a[href="#tarifs"], a[href="#gerance"], a[href="#devis"]', {
          element(element) {
            element.setAttribute('href', '/web-studio' + element.getAttribute('href'));
          }
        });
      }
      if (url.pathname === '/belfort/') {
        rewriter.on('[data-pastille-universe="actus"]', {
          element(element) {
            element.removeAttribute('data-pastille-universe');
            element.setInnerContent('<h2>Le JT VM Actus</h2>' + (pastille
              ? '<p><a href="' + escape(pastille.plateformes.youtube.url) + '">' + escape(pastille.titre) + '</a></p>'
              : '<p>Aucune édition récente confirmée.</p>'), { html: true });
          }
        });
      }
      if (url.pathname === '/mangas/') {
        rewriter.on('a[href="#episodes"], a[href="#prochainement"]', {
          element(element) {
            element.setAttribute('href', element.getAttribute('href') === '#episodes' ? '#catalogue' : '#a-venir');
          }
        }).on('#catalogue', {
          element(element) {
            element.before('<span id="episodes"></span>', { html: true });
          }
        }).on('#a-venir', {
          element(element) {
            element.before('<span id="prochainement"></span>', { html: true });
          }
        });
      }
    }
    return htmlResponse(rewriter.transform(response), !isPreview);
  }
};
