const ORIGIN = 'https://velocemercato.pages.dev';

const SCORE_STYLE = '<style id="vm-readable-scores">#sTicker .sviewport{min-width:0;overflow-x:auto}#sRun{animation:none!important;transform:none!important;padding-left:0!important}</style>';

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const isPreview = url.hostname.endsWith('.workers.dev');
    if (url.hostname !== 'velocemercato.fr' && !isPreview) {
      return new Response(null, { status: 404 });
    }

    if (url.pathname !== '/' || !['GET', 'HEAD'].includes(request.method)) {
      return isPreview ? new Response(null, { status: 404 }) : fetch(request);
    }

    const response = await fetch(new URL('/' + url.search, ORIGIN), {
      method: request.method,
      headers: { Accept: 'text/html' },
      redirect: 'manual'
    });
    if (request.method === 'HEAD' || !response.ok ||
        !response.headers.get('Content-Type')?.includes('text/html')) {
      return response;
    }

    const rewritten = new HTMLRewriter().on('#actualites-du-jour', {
      element(element) {
        element.remove();
      }
    }).on('head', {
      element(element) {
        element.append(SCORE_STYLE, { html: true });
      }
    }).transform(response);

    const headers = new Headers(rewritten.headers);
    for (const name of ['Content-Length', 'ETag', 'Last-Modified']) {
      headers.delete(name);
    }
    headers.set('Cache-Control', 'no-store');
    return new Response(rewritten.body, { status: rewritten.status, headers });
  }
};
