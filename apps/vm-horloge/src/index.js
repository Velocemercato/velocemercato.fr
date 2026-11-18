// vm-horloge — lance les robots GitHub de Véloce Mercato à heure fixe (Cloudflare Cron, toutes les 10 min).
// Aucune publication n'est faite ici : on appuie seulement sur le bouton « Run workflow » des robots existants,
// qui gardent leurs propres garde-fous (anti-doublons, quotas par page, règles éditoriales).

// Plan : [fichier du robot, entrées, condition sur l'heure UTC (h) et la minute (m) du tic]
export const PLAN = [
  ['editorial-vm.yml', null, (h, m) => true],                                  // publications FB/IG : toutes les 10 min
  ['actualites.yml', { test: 'false' }, (h, m) => m % 20 === 0],               // brèves foot : toutes les 20 min
  ['deployer-accueil-cloudflare.yml', null, (h, m) => m % 20 === 10],          // mise en ligne du site, 10 min après
  ['actus.yml', { test: 'false' }, (h, m) => m === 0 || m === 30],             // actus générales : toutes les 30 min
  ['gaming.yml', { test: 'false' }, (h, m) => m === 10 || m === 40],           // actus gaming : toutes les 30 min
  ['multisport-flux.yml', null, (h, m) => m === 0 && h % 2 === 0],             // multisport : toutes les 2 h
  ['publier-meta.yml', { article: '' }, (h, m) => (m === 0 || m === 30) && h >= 4 && h <= 21], // pastilles, 5 h-22 h Paris
];

export function aLancer(date) {
  const h = date.getUTCHours(), m = date.getUTCMinutes() - (date.getUTCMinutes() % 10);
  return PLAN.filter(([, , quand]) => quand(h, m));
}

export async function lancer(env, fichier, inputs, f = fetch) {
  const base = env.GITHUB_API || 'https://api.github.com';
  const r = await f(`${base}/repos/${env.DEPOT}/actions/workflows/${fichier}/dispatches`, {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + env.GITHUB_TOKEN, Accept: 'application/vnd.github+json', 'User-Agent': 'vm-horloge', 'X-GitHub-Api-Version': '2022-11-28', 'Content-Type': 'application/json' },
    body: JSON.stringify(inputs ? { ref: 'main', inputs } : { ref: 'main' }),
  });
  return r.status; // 204 = lancé
}

export async function tic(env, date, f = fetch) {
  if (!env.GITHUB_TOKEN) return [{ erreur: 'GITHUB_TOKEN absent : rien n’est lancé' }];
  const out = [];
  for (const [fichier, inputs] of aLancer(date)) {
    try { out.push({ fichier, statut: await lancer(env, fichier, inputs, f) }); }
    catch (e) { out.push({ fichier, statut: 'erreur réseau' }); }
  }
  console.log(JSON.stringify({ heure: date.toISOString(), lancements: out }));
  return out;
}

export default {
  async scheduled(event, env, ctx) { ctx.waitUntil(tic(env, new Date(event.scheduledTime))); },
  async fetch(req, env) {
    const now = new Date();
    // Diagnostic : /?diag=1 lance une fois le robot de publication et affiche la réponse exacte de GitHub.
    if (new URL(req.url).searchParams.get('diag') === '1') {
      if (!env.GITHUB_TOKEN) return new Response('GITHUB_TOKEN absent', { status: 500 });
      const base = env.GITHUB_API || 'https://api.github.com';
      const r = await fetch(`${base}/repos/${env.DEPOT}/actions/workflows/editorial-vm.yml/dispatches`, {
        method: 'POST',
        headers: { Authorization: 'Bearer ' + env.GITHUB_TOKEN, Accept: 'application/vnd.github+json', 'User-Agent': 'vm-horloge', 'X-GitHub-Api-Version': '2022-11-28', 'Content-Type': 'application/json' },
        body: JSON.stringify({ ref: 'main' }),
      });
      const texte = (await r.text()).slice(0, 300);
      const sens = { 204: '✅ OK : GitHub accepte, le robot de publication est lancé.', 401: '❌ Jeton refusé (mal copié ou expiré).', 403: '❌ Jeton sans la permission « Actions : Read and write ».', 404: '❌ Jeton sans accès au dépôt velocemercato.fr (Repository access).', 422: '❌ Paramètres refusés par GitHub.' }[r.status] || 'Réponse inattendue';
      return new Response(`Statut GitHub : ${r.status}\n${sens}\n${texte}`, { headers: { 'content-type': 'text/plain; charset=utf-8' } });
    }
    return new Response(JSON.stringify({ ok: true, jeton_present: !!env.GITHUB_TOKEN, prochain_tic: aLancer(new Date(Math.ceil(now / 6e5) * 6e5)).map((x) => x[0]) }, null, 2),
      { headers: { 'content-type': 'application/json; charset=utf-8' } });
  },
};
