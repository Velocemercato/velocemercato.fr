// Application VM : les pages s'ouvrent même avec une mauvaise connexion (dernière version gardée en mémoire).
const CACHE = 'vm-app-v1';
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(['/', '/app/icon-192.png'])).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(n => n !== CACHE).map(n => caches.delete(n)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET' || new URL(r.url).origin !== location.origin) return;
  // Réseau d'abord (actus toujours fraîches), sinon la copie gardée en mémoire.
  e.respondWith(fetch(r).then(res => { if (res.ok && (r.mode === 'navigate' || /\.(css|js|webp|png|jpg)$/.test(r.url))) { const cp = res.clone(); caches.open(CACHE).then(c => c.put(r, cp)); } return res; })
    .catch(() => caches.match(r).then(m => m || caches.match('/'))));
});
