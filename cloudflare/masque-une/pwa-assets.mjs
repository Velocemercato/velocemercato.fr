import icon0 from './pwa-foot-512.mjs';
import icon1 from './pwa-foot-maskable-512.mjs';
import icon2 from './pwa-univers-512.mjs';
import icon3 from './pwa-univers-maskable-512.mjs';

const footIcons = new Map([
  ['/app/foot-512.png', icon0],
  ['/app/foot-maskable-512.png', icon1],
]);
const universIcons = new Map([
  ['/app/univers-512.png', icon2],
  ['/app/univers-maskable-512.png', icon3],
]);

export function pwaIcon(pathname, univers, head) {
  const encoded = (univers ? universIcons : footIcons).get(pathname);
  if (!encoded) return null;
  const bytes = head ? null : Uint8Array.from(atob(encoded), char => char.charCodeAt(0));
  return new Response(bytes, {
    headers: { 'Content-Type': 'image/png', 'Cache-Control': 'public, max-age=86400', 'X-Content-Type-Options': 'nosniff' },
  });
}

export async function footServiceWorker(response) {
  if (!response.ok) return response;
  const content = await response.text();
  if (!content.includes('"/manifest.webmanifest"')) return new Response(content, response);
  return new Response(content.replace('"/manifest.webmanifest"', '"/app/foot.webmanifest"'), {
    headers: { 'Content-Type': 'application/javascript; charset=utf-8', 'Cache-Control': 'no-cache' },
  });
}
