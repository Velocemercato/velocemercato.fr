import { compactHeader, compactHome, compactStyle } from './home-compact.mjs';
import { amazonFooter, amazonSelection } from './amazon-selection.mjs';
import { gamingPressScript, multisportEdition, pronosPage, verifiedAdvice } from './public-content.mjs';
import { renderKit, renderKitCards } from './kit-reseaux.mjs';
import { pronoKitContent, readPronoDesk } from './prono-desk.mjs';
import { htmlResponse, polish, sitemap } from './site-polish.mjs';
import { footServiceWorker, pwaIcon } from './pwa-assets.mjs';
import { logo } from './logo.mjs';
import { latestPastille, liveBootstrap, livePaths, liveResponse } from './live-data.mjs';

const VELOCE_ORIGIN = 'https://velocemercato.pages.dev';
const UNIVERS_ORIGIN = 'https://vmunivers.pages.dev';

const SCORE_STYLE = '<style id="vm-readable-scores">#sTicker .sviewport{min-width:0;overflow-x:auto}#sRun{animation:none!important;transform:none!important;padding-left:0!important}</style>';

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

async function articleFallback(pathname, method, missing) {
  const id = /^\/a\/([a-z0-9][a-z0-9-]{1,99})(?:\.html)?$/.exec(pathname)?.[1];
  if (!id || missing.status !== 404) return missing;

  const path = '/a/' + id;
  const canonical = 'https://velocemercato.fr' + path;
  const origins = [
    'https://raw.githubusercontent.com/Velocemercato/velocemercato.fr/main',
    'https://cdn.jsdelivr.net/gh/Velocemercato/velocemercato.fr@main'
  ];
  const unavailable = reason => {
    const headers = new Headers(missing.headers);
    headers.set('X-VM-Article-Fallback', reason);
    return new Response(missing.body, { status: missing.status, headers });
  };
  try {
    const html = await Promise.any(origins.map(async origin => {
      const file = new URL(origin + path + '.html');
      file.searchParams.set('vm', String(Math.floor(Date.now() / 120_000)));
      const source = await fetch(file, { signal: AbortSignal.timeout(4500) });
      if (!source.ok) throw new Error('source-' + source.status);
      const body = await source.text();
      if (!body.includes('<link rel="canonical" href="' + canonical + '.html">') &&
          !body.includes('<link rel="canonical" href="' + canonical + '">')) throw new Error('source-non-conforme');
      return body;
    }));
    return new Response(method === 'HEAD' ? null : html, {
      headers: { 'Content-Type': 'text/html; charset=utf-8', 'X-Content-Type-Options': 'nosniff' }
    });
  } catch (error) {
    const reason = error.errors?.map(item => /^source-(?:\d{3}|non-conforme)$/.test(item.message) ?
      item.message : item.name === 'TimeoutError' ? 'delai' : 'connexion').join(', ');
    return unavailable(reason || 'source-indisponible');
  }
}

export default {
  async fetch(request, env) {
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
    if (!isUnivers && ['GET', 'HEAD'].includes(request.method) &&
        /^\/studio\/atelier-cf03b9883e72(?:\.html|\/)?$/.test(url.pathname)) {
      return new Response(null, { status: 302, headers: {
        location: 'https://vm-studio-prive.velocemercato87.workers.dev/',
        'cache-control': 'no-store',
        'referrer-policy': 'no-referrer',
      } });
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
    if (url.pathname === '/devis-merci') {
      const back = isUnivers ? '/professionnels/#devis' : '/web-studio#devis';
      const body = '<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>VM Studio · Merci</title><main style="font:1rem/1.6 system-ui;max-width:42rem;margin:4rem auto;padding:1rem"><h1>Merci pour votre demande</h1><p>VM Studio vous répondra à l’adresse indiquée dans le formulaire.</p><a href="' + back + '">Retour à VM Studio</a></main>';
      return htmlResponse(new Response(request.method === 'HEAD' ? null : body, {
        headers: { 'Content-Type': 'text/html; charset=utf-8' }
      }), !isPreview);
    }
    if (isUnivers && url.pathname === '/assets/pro-contact.js') {
      const js = await fetch(new URL(url.pathname + url.search, VELOCE_ORIGIN), { method: request.method });
      if (js.ok) return js;
    }
    if (!isUnivers && livePaths.has(url.pathname)) return liveResponse(request, url.pathname);
    if (!isUnivers && url.pathname === '/selection-amazon') {
      return amazonSelection(request.method === 'HEAD');
    }
    if (!isUnivers && url.pathname === '/kit-pronos') {
      const now = new Date();
      const [desk, analysis] = await Promise.all([readPronoDesk(env, now.getTime()), verifiedAdvice(now.getTime())]);
      const content = pronoKitContent(desk, analysis, now.getTime());
      const kit = renderKitCards(now, content.cards, {
        title: 'Kit Pronos VM', heading: 'VÉLOCE MERCATO · MULTISPORT', status: content.status,
        refreshIn: content.refreshIn
      });
      return request.method === 'HEAD' ? new Response(null, { headers: kit.headers }) : kit;
    }
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
      let response = isUnivers ? await universPage(request, url, isPreview) : isPreview
        ? await fetch(new URL(url.pathname + url.search, VELOCE_ORIGIN), { method: request.method, redirect: 'manual' })
        : await fetch(request);
      if (!isUnivers && response.status === 404 && url.pathname.startsWith('/a/')) {
        response = await articleFallback(url.pathname, request.method, response);
      }
      if (request.method === 'HEAD' || !response.ok ||
          !response.headers.get('Content-Type')?.includes('text/html')) return response;
      const rewriter = polish(new HTMLRewriter(), url, isUnivers);
      if (isUnivers && url.pathname === '/professionnels/') {
        rewriter.on('form[data-pro-contact]', {
          element(form) {
            form.prepend('<input type="hidden" name="_next" value="https://vmunivers.fr/devis-merci">', { html: true });
          }
        }).on('script[src="/assets/pro-contact.js"]', {
          element(script) { script.setAttribute('src', '/assets/pro-contact.js?v=20261108-devis'); }
        });
      }
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
      !isUnivers && request.method === 'GET' && (home || url.pathname === '/belfort/') ? latestPastille(Date.now(), home ? 'foot' : 'actus') : null,
      !isUnivers && url.pathname === '/pronos/' && request.method === 'GET' ? verifiedAdvice() : null
    ]);
    if (request.method === 'HEAD' || !response.ok ||
        !response.headers.get('Content-Type')?.includes('text/html')) {
      return response;
    }

    const rewriter = polish(new HTMLRewriter(), url, isUnivers);
    if (home) amazonFooter(rewriter);
    if (!isUnivers && url.pathname === '/pronos/') {
      pronosPage(rewriter, advice);
      rewriter.on('#conseil-contenu', {
        element(section) { section.after('<p><a href="/kit-pronos">Ouvrir le kit Pronos VM</a></p>', { html: true }); }
      });
    }
    if (!isUnivers && url.pathname === '/vm-gaming/') {
      rewriter.on('head', { element(head) { head.append(gamingPressScript, { html: true }); } })
        .on('#t-presse', {
          element(title) { title.setInnerContent('Derniers titres Gaming <small>Le fil de la presse, avec les liens vers les sources</small>', { html: true }); }
        }).on('#maj', {
          element(note) { note.setInnerContent('Brèves VM'); }
        });
    }

    if (studio) {
      rewriter.on('script[src="/assets/pro-contact.js"]', {
        element(script) { script.setAttribute('src', '/assets/pro-contact.js?v=20261108-devis'); }
      }).on('#tarifs', {
        element(element) {
          element.after(AD_OFFERS, { html: true });
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
      compactHome(rewriter);
      rewriter.on('body', {
        element(element) {
          element.prepend('<a class="vm-skip" href="#feed-title">Aller aux actualités</a>' + compactHeader, { html: true });
          element.append(`<script>const install=document.getElementById('vmInst');if(install)document.getElementById('vm-essentiel-install').append(install);</script>`, { html: true });
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
      }).on('head', {
        element(element) {
          element.prepend(liveBootstrap, { html: true });
          element.append(SCORE_STYLE + MOBILE_ACCESS + compactStyle, { html: true });
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
      if (url.pathname === '/scores/') {
        rewriter.on('script[src="app.js"]', {
          element(script) { script.setAttribute('src', 'app.js?v=20261108-fraicheur'); }
        });
      }
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
