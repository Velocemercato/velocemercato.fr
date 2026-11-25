// Rendu statique du site (HTML sans JavaScript, accessible, responsive). Tout le texte est echappe.
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const safeHref = (h) => (/^([a-z0-9-]+\.html|tel:[+0-9 ]{3,20}|mailto:[^\s"<>]{3,120}|https:\/\/[^\s"<>]{3,200})$/.test(h || '') ? h : '#');
const lum = (hex) => { const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255).map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4)); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; };
export const css = (t) => {
  const bg = t.dark ? '#0f172a' : '#ffffff', fg = t.dark ? '#e5e7eb' : '#111827', card = t.dark ? '#1e293b' : '#f3f4f6', on = lum(t.primary) > 0.4 ? '#111827' : '#ffffff';
  const link = t.dark ? (lum(t.primary) < 0.2 ? '#93c5fd' : t.primary) : (lum(t.primary) > 0.4 ? '#1d4ed8' : t.primary);
  return `*{box-sizing:border-box}body{margin:0;font:17px/1.6 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:${bg};color:${fg}}a{color:${link}}
.skip{position:absolute;left:-999px}.skip:focus{left:8px;top:8px;background:#fff;color:#000;padding:8px;z-index:9}
header{background:${t.primary};color:${on};padding:14px 5vw;display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between}
header strong{font-size:1.2rem}nav{display:flex;flex-wrap:wrap;gap:6px 16px}nav a{color:${on};text-decoration:none;padding:6px 2px;border-bottom:2px solid transparent}nav a[aria-current=page]{border-color:${on}}
main{max-width:1000px;margin:0 auto;padding:24px 5vw 48px}section{margin:36px 0}h1{font-size:clamp(2rem,6vw,3.2rem);line-height:1.1;margin:.2em 0}h2{font-size:1.6rem}
.hero{padding:40px 24px;border-radius:16px;background:${card}}.btn{display:inline-block;background:${t.primary};color:${on};padding:12px 22px;border-radius:10px;text-decoration:none;font-weight:700;margin-top:10px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}.card{background:${card};border-radius:12px;padding:16px}.card h3{margin:.2em 0}.price{font-weight:700}
img{max-width:100%;height:auto;border-radius:12px}footer{padding:24px 5vw;border-top:1px solid ${t.dark ? '#334155' : '#e5e7eb'};font-size:.9rem}
.pv{background:#fde68a;color:#111;padding:8px 5vw;font:600 14px system-ui;text-align:center}`
  + (t.style === 'prestige'
    ? `body{font-family:Georgia,'Times New Roman',serif}h1,h2,h3{font-weight:600;letter-spacing:.01em}.hero{border-radius:4px;border:1px solid ${t.primary}}.card{border-radius:4px;border-left:3px solid ${t.primary}}.btn{border-radius:2px;text-transform:uppercase;letter-spacing:.06em;font-size:.9rem}img{border-radius:2px}`
    : `h1,h2{font-weight:900;text-transform:uppercase;letter-spacing:.02em}.hero{border:3px solid ${t.dark ? '#e5e7eb' : '#111827'};box-shadow:8px 8px 0 ${t.primary}}.card{border:2px solid ${t.dark ? '#e5e7eb' : '#111827'};box-shadow:4px 4px 0 ${t.primary}}.btn{border:2px solid ${t.dark ? '#e5e7eb' : '#111827'};box-shadow:3px 3px 0 ${t.dark ? '#e5e7eb' : '#111827'}}`);
};
function block(b, site) {
  const T = b.title ? `<h2>${esc(b.title)}</h2>` : '';
  if (b.type === 'hero') return `<section class="hero"><h1>${esc(b.title)}</h1><p>${esc(b.subtitle)}</p>${b.image ? `<img src="photos/${esc(b.image)}" alt="${esc(b.imageAlt)}">` : ''}${b.cta ? `<a class="btn" href="${esc(safeHref(b.cta.href))}">${esc(b.cta.label)}</a>` : ''}</section>`;
  if (b.type === 'text') return `<section>${T}<p>${esc(b.body).replace(/\n/g, '<br>')}</p></section>`;
  if (b.type === 'services') return `<section>${T}<div class="grid">${b.items.map((i) => `<div class="card"><h3>${esc(i.name)}</h3>${i.desc ? `<p>${esc(i.desc)}</p>` : ''}${i.price ? `<p class="price">${esc(i.price)}</p>` : ''}</div>`).join('')}</div></section>`;
  if (b.type === 'gallery') return `<section>${T}${b.images.length ? `<div class="grid">${b.images.map((i) => `<img src="photos/${esc(i.src)}" alt="${esc(i.alt)}" loading="lazy">`).join('')}</div>` : '<p>Les photos arrivent bientôt.</p>'}</section>`;
  if (b.type === 'contact') { const c = site.contact; return `<section>${T}<div class="card"><address style="font-style:normal">${c.address ? `<p>${esc(c.address)}</p>` : ''}${c.phone ? `<p>Téléphone : <a href="tel:${esc(c.phone)}">${esc(c.phone)}</a></p>` : ''}${c.email ? `<p>E-mail : <a href="mailto:${esc(c.email)}">${esc(c.email)}</a></p>` : ''}${c.hours ? `<p>Horaires : ${esc(c.hours)}</p>` : ''}</address></div></section>`; }
  return '';
}
const shell = (site, title, active, inner, preview) => `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)} — ${esc(site.name)}</title>${preview ? '<meta name="robots" content="noindex,nofollow">' : ''}<link rel="stylesheet" href="style.css"></head><body><a class="skip" href="#main">Aller au contenu</a>${preview ? '<div class="pv">Aperçu privé — site non publié</div>' : ''}<header><strong>${esc(site.name)}</strong><nav aria-label="Navigation">${site.pages.map((p) => `<a href="${p.slug === 'accueil' ? 'index' : p.slug}.html"${p.slug === active ? ' aria-current="page"' : ''}>${esc(p.title)}</a>`).join('')}</nav></header><main id="main">${inner}</main><footer>© ${esc(site.name)} · <a href="mentions-legales.html">Mentions légales</a></footer></body></html>`;
export function renderSite(site, { preview = false } = {}) {
  const files = { 'style.css': css(site.theme), 'robots.txt': preview ? 'User-agent: *\nDisallow: /\n' : 'User-agent: *\nAllow: /\n' };
  for (const p of site.pages) files[(p.slug === 'accueil' ? 'index' : p.slug) + '.html'] = shell(site, p.title, p.slug, p.blocks.map((b) => block(b, site)).join(''), preview);
  const l = site.legal;
  files['mentions-legales.html'] = shell(site, 'Mentions légales', 'mentions', `<h1>Mentions légales</h1><p>Éditeur du site : ${esc(l.owner) || '—'}${l.siret ? ` — SIRET ${esc(l.siret)}` : ''}.</p>${site.contact.email ? `<p>Contact : ${esc(site.contact.email)}</p>` : ''}${l.host ? `<p>Hébergeur : ${esc(l.host)}</p>` : ''}<p>Ce site ne dépose aucun cookie et n'utilise aucun traceur.</p>`, preview);
  return files;
}
