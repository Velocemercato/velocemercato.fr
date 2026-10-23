// Véloce Mercato : cache limité aux ressources de ce domaine.
const CACHE = 'vm-app-v6';
const PREFIX = 'vm-app-v';
const PRECACHE = ["/", "/manifest.webmanifest", "/app/foot-192.png", "/assets/identity.css", "/assets/home-utilities.css", "/assets/vendor/qrcode.min.js"];
const OFFLINE = '<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Véloce Mercato — hors connexion</title><body style="background:#080d18;color:#fff;font:18px/1.6 system-ui;padding:32px"><h1>Véloce Mercato</h1><p>Cette page n’est pas disponible hors connexion. Reconnectez-vous et réessayez.</p></body></html>';

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(PRECACHE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(
    keys.filter(key => key.startsWith(PREFIX) && key !== CACHE).map(key => caches.delete(key))
  )).then(() => self.clients.claim()));
});
self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;
  const page = request.mode === 'navigate';
  const asset = /\.(css|js|webp|png|jpe?g|svg|woff2?|webmanifest)$/.test(url.pathname);
  // JSON, compteurs de votes et API restent exclusivement sur le réseau.
  if (!page && !asset) return;
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    try {
      const response = await fetch(request);
      if (response.ok && !response.redirected && new URL(response.url).origin === self.location.origin) {
        // Une panne de stockage ne doit jamais empêcher de lire la réponse réseau.
        try { await cache.put(request, response.clone()); } catch (_) { /* Cache facultatif. */ }
      }
      return response;
    } catch (_) {
      const saved = await cache.match(request, {ignoreSearch: page});
      if (saved) return saved;
      if (page) return new Response(OFFLINE, {status:503, headers:{'Content-Type':'text/html; charset=utf-8'}});
      return Response.error();
    }
  })());
});
