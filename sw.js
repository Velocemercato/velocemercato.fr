// Application VM : les pages s'ouvrent même avec une mauvaise connexion (dernière version gardée en mémoire).
const CACHE = 'vm-app-v3';
const HORS_LIGNE = '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Hors connexion</title><body style="margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#060b1d;color:#fff;font:16px system-ui;text-align:center;padding:20px"><div><div style="font-size:48px">📡</div><h1 style="font-size:1.4rem">Pas de connexion</h1><p>Cette page n\'a pas encore été gardée en mémoire. Reconnecte-toi et réessaie.</p><button onclick="location.reload()" style="font:700 1rem system-ui;padding:12px 18px;border-radius:999px;border:0;background:#f4cf55">Réessayer</button></div>';
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(['/', '/vm/', '/app/icon-192.png'])).catch(() => {}).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(n => n !== CACHE).map(n => caches.delete(n)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET' || new URL(r.url).origin !== location.origin) return;
  const page = r.mode === 'navigate';
  const statique = /\.(css|js|webp|png|jpg|jpeg|svg|woff2?)$/.test(new URL(r.url).pathname);
  // Réseau d'abord (actus toujours fraîches), sinon la copie gardée en mémoire.
  e.respondWith(fetch(r).then(res => {
    if (res.ok && (page || statique)) { const cp = res.clone(); caches.open(CACHE).then(c => c.put(r, cp)); }
    return res;
  }).catch(() => caches.match(r).then(m => {
    if (m) return m;
    // Une PAGE sans copie : page « hors connexion ». Une donnée (JSON) ou une image : vraie erreur, jamais du HTML à la place.
    if (page) return new Response(HORS_LIGNE, { status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' } });
    return new Response('', { status: 504, statusText: 'Hors connexion' });
  })));
});
