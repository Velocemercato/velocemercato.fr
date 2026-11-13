// prono.velocemercato.fr : relais vers le site VM Prono hébergé par ChatGPT Sites.
// Le visiteur ne voit que l'adresse VM. Rien n'est stocké ici : requêtes et réponses passent telles quelles,
// en remplaçant seulement l'adresse d'origine par l'adresse VM (liens, redirections, contrôle d'origine).
export default {
  async fetch(req, env) {
    const ici = new URL(req.url);
    const origine = new URL(env.ORIGINE);
    const cible = new URL(ici.pathname + ici.search, origine);
    const h = new Headers(req.headers);
    h.delete('host');
    // Le site d'origine refuse les envois dont l'en-tête Origin n'est pas le sien : on le traduit.
    if (h.get('origin') === ici.origin) h.set('origin', origine.origin);
    const ref = h.get('referer');
    if (ref && ref.startsWith(ici.origin)) h.set('referer', origine.origin + ref.slice(ici.origin.length));
    const rep = await fetch(cible, { method: req.method, headers: h, body: ['GET', 'HEAD'].includes(req.method) ? undefined : req.body, redirect: 'manual' });
    const out = new Headers(rep.headers);
    const loc = out.get('location');
    if (loc) out.set('location', loc.split(origine.origin).join(ici.origin));
    out.delete('content-length');
    const type = out.get('content-type') || '';
    if (/text\/html|javascript|json|text\/css|xml|manifest/.test(type)) {
      const texte = (await rep.text()).split(origine.origin).join(ici.origin).split(origine.host).join(ici.host);
      return new Response(texte, { status: rep.status, statusText: rep.statusText, headers: out });
    }
    return new Response(rep.body, { status: rep.status, statusText: rep.statusText, headers: out });
  },
};
