const products = [
  ['Gaming', 'Call of Duty: Modern Warfare 4 · PS5', 'https://amzn.to/4cHQCfA'],
  ['Déco', 'Horloge murale Kids Licensing', 'https://amzn.to/4qICIjk'],
  ['Cuisine', 'Machine sous vide Tefal Vacupack Classic', 'https://amzn.to/4zGpuYi'],
  ['Maison', 'Fauteuil rembourré chairus', 'https://amzn.to/46nN6TY'],
  ['Mode', 'Pantalon confort', 'https://amzn.to/3UlYSvx'],
  ['Service', 'Amazon Prime', 'https://www.amazon.fr/amazonprime?_encoding=UTF8&primeCampaignId=prime_assoc_ft&tag=velocemercato-21'],
];

const escape = value => value.replace(/[&<>"]/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'
})[char]);

export function amazonSelection(head = false) {
  const headers = {
    'Content-Type': 'text/html; charset=utf-8',
    'Cache-Control': 'public, max-age=300',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'X-Content-Type-Options': 'nosniff'
  };
  if (head) return new Response(null, { headers });
  const cards = products.map(([category, name, href]) =>
    '<li><small>' + escape(category) + '</small><h2>' + escape(name) + '</h2>' +
    '<a rel="sponsored nofollow noopener" href="' + escape(href) + '">Voir sur Amazon</a>' +
    '<p class="notice">Lien rémunéré par Amazon</p></li>').join('');
  return new Response(`<!doctype html><html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="canonical" href="https://velocemercato.fr/selection-amazon">
<title>Sélection Amazon · VM</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#101930;color:#fff5db;font:16px/1.55 system-ui,sans-serif}
main{width:min(100% - 32px,860px);margin:32px auto}
a,small{color:#ffdb6e}
a:focus-visible{outline:3px solid #fff;outline-offset:4px}
h1{font-size:clamp(2rem,6vw,3.5rem);line-height:1.1;margin:.4em 0}
h2{font-size:1.15rem;margin:.4em 0}
ul{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,265px),1fr));gap:12px}
li,.disclosure{padding:14px 16px;border-radius:12px;background:#192645;border:1px solid #465a83}
.notice{margin:.35em 0 0;font-size:.87rem;color:#d2daec}
li a{display:inline-block;padding:.4em 0}
</style></head><body><main>
<p><a href="https://velocemercato.fr/">Véloce Mercato</a> · <a href="https://vmunivers.fr/">VM Univers</a></p>
<h1>Sélection Amazon</h1>
<p class="disclosure">En tant que Partenaire Amazon, je réalise un bénéfice sur les achats remplissant les conditions requises.</p>
<ul>${cards}</ul>
<p class="notice">Les prix, la disponibilité et les conditions des offres sont indiqués sur Amazon.</p>
</main></body></html>`, { headers });
}

export function amazonFooter(rewriter) {
  rewriter.on('footer', {
    element(footer) {
      footer.append('<p style="margin:.65rem 0;text-align:center;font-size:.85rem"><a href="https://velocemercato.fr/selection-amazon" style="color:inherit">Sélection Amazon</a> · liens affiliés</p>', { html: true });
    }
  });
}
