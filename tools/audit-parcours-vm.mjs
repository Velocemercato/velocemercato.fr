// Audit public en lecture seule des liens présents sur les deux accueils.
// Usage: node tools/audit-parcours-vm.mjs
const origins = ['https://velocemercato.fr', 'https://vmunivers.fr'];
const results = [];
for (const origin of origins) {
  const home = await fetch(origin + '/').then(r => r.text());
  const links = [...home.matchAll(/href=["']([^"']+)["']/g)].map(m => m[1].replaceAll('&amp;', '&'));
  const targets = [...new Set(links.flatMap(href => {
    try { const u = new URL(href, origin); if (u.origin !== origin || /\.(?:woff2?|ttf|png|webp|jpe?g|css|ico)$/i.test(u.pathname)) return []; u.hash = ''; return [u.href]; } catch { return []; }
  }))];
  let cursor = 0;
  const rows = [];
  await Promise.all(Array.from({ length: 6 }, async () => {
    while (cursor < targets.length) {
      const url = targets[cursor++];
      try {
        const response = await fetch(url, { signal: AbortSignal.timeout(15000) });
        const html = await response.text();
        const ids = [...html.matchAll(/\bid=["']([^"']+)["']/g)].map(m => m[1]);
        const anchorLinks = [...html.matchAll(/href=["']#([^"']+)["']/g)].map(m => m[1]);
        rows.push({ url, status: response.status, final: response.url, bytes: Buffer.byteLength(html),
          title: html.match(/<title>([^<]*)<\/title>/i)?.[1] || '',
          duplicateIds: [...new Set(ids.filter((id, i) => ids.indexOf(id) !== i))],
          missingAnchors: [...new Set(anchorLinks.filter(id => !ids.includes(id)))],
          imagesWithoutAlt: [...html.matchAll(/<img\b[^>]*>/gi)].filter(m => !/\balt\s*=/.test(m[0])).length });
      } catch (e) { rows.push({ url, error: e.message }); }
    }
  }));
  rows.sort((a, b) => a.url.localeCompare(b.url));
  results.push({ origin, checked: rows.length, rows });
}
console.log(JSON.stringify({ checkedAt: new Date().toISOString(), scope: 'Pages liées depuis les accueils ; contrôles HTTP et HTML. Ne certifie pas les paiements, notifications et services tiers.', results }, null, 2));
