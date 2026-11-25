// Generation de site hors ligne (cout zero) : modele de site multipage a partir d'un brief + edition par la discussion.
// Un fournisseur LLM pourra etre branche plus tard (src/providers.js) ; il exigera une decision de budget.
export const TODO = 'À compléter';
export const SECTORS = {
  artisan: { label: 'Artisan / dépannage', services: ['Devis gratuit', 'Intervention rapide', 'Travaux sur mesure'], cta: 'Demander un devis' },
  club: { label: 'Club / association sportive', services: ['Inscriptions', 'Entraînements', 'Événements du club'], cta: 'Nous rejoindre' },
  commerce: { label: 'Commerce de proximité', services: ['Nos produits', 'Conseils personnalisés', 'Commande et retrait'], cta: 'Nous rendre visite' },
  restaurant: { label: 'Restaurant / café', services: ['Carte du moment', 'Réservation', 'Vente à emporter'], cta: 'Réserver' },
  services: { label: 'Services / indépendant', services: ['Premier échange offert', 'Accompagnement', 'Suivi'], cta: 'Prendre contact' },
  association: { label: 'Association', services: ['Nos actions', 'Adhésion', 'Agenda'], cta: 'Nous contacter' },
};
const COLORS = { bleu: '#1d4ed8', rouge: '#c81e1e', vert: '#15803d', orange: '#c2410c', violet: '#6d28d9', noir: '#111827', rose: '#be185d', jaune: '#a16207' };
const LIM = { pages: 8, blocks: 12, str: 2000, items: 20, images: 12 };
const clip = (s, n) => String(s ?? '').replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g, '').trim().slice(0, n);

export function validateBrief(b) {
  const e = [];
  if (!b || typeof b !== 'object') return { ok: false, errors: ['brief manquant'] };
  if (clip(b.name, 80).length < 2) e.push('nom du projet (2 caractères minimum)');
  if (!SECTORS[b.sector]) e.push('secteur inconnu');
  if (b.services !== undefined && (!Array.isArray(b.services) || b.services.length > 8)) e.push('services : 8 maximum');
  if (b.color && !/^#[0-9a-fA-F]{6}$/.test(b.color) && !COLORS[String(b.color).toLowerCase()]) e.push('couleur invalide');
  return { ok: e.length === 0, errors: e };
}

export function generateSite(brief) {
  const sec = SECTORS[brief.sector], name = clip(brief.name, 80), city = clip(brief.city, 60);
  const services = (Array.isArray(brief.services) && brief.services.length ? brief.services : sec.services).map((s) => clip(s, 60)).filter(Boolean).slice(0, 8);
  const where = city ? ` à ${city}` : '';
  const primary = !brief.color ? '#1d4ed8' : (COLORS[String(brief.color).toLowerCase()] || brief.color);
  const tagline = clip(brief.tagline, 140) || `${sec.label}${where}`;
  return {
    version: 1, name, sector: brief.sector, theme: { primary, dark: false, style: brief.style === 'prestige' ? 'prestige' : 'signature' },
    contact: { email: clip(brief.email, 120), phone: clip(brief.phone, 30), address: clip(brief.address, 160), hours: clip(brief.hours, 160) },
    legal: { owner: clip(brief.owner, 120), siret: clip(brief.siret, 20), host: '' },
    pages: [
      { slug: 'accueil', title: 'Accueil', blocks: [
        { type: 'hero', title: name, subtitle: tagline, cta: { label: sec.cta, href: 'contact.html' }, image: '', imageAlt: '' },
        { type: 'services', title: 'Ce que nous proposons', items: services.map((s) => ({ name: s, desc: '', price: '' })) },
        { type: 'text', title: `Bienvenue chez ${name}`, body: `${name} vous accueille${where}. Découvrez nos services et contactez-nous pour en parler.` } ] },
      { slug: 'services', title: 'Services', blocks: [{ type: 'services', title: 'Nos services', items: services.map((s) => ({ name: s, desc: '', price: '' })) }] },
      { slug: 'galerie', title: 'Galerie', blocks: [{ type: 'gallery', title: 'En images', images: [] }] },
      { slug: 'contact', title: 'Contact', blocks: [{ type: 'contact', title: 'Nous contacter' }] },
    ],
  };
}

export function findPlaceholders(site) {
  const found = [];
  const walk = (v, path) => { if (typeof v === 'string') { if (v.includes(TODO)) found.push(path); } else if (v && typeof v === 'object') for (const k of Object.keys(v)) walk(v[k], `${path}.${k}`); };
  walk(site, 'site'); return found;
}

export function validateSite(site, photoNames = []) {
  const e = [], ok = new Set(photoNames);
  const isStr = (s, n = LIM.str) => typeof s === 'string' && s.length <= n;
  if (!site || typeof site !== 'object') return { ok: false, errors: ['site manquant'] };
  if (!isStr(site.name, 80) || site.name.length < 2) e.push('nom invalide');
  if (!site.theme || !/^#[0-9a-fA-F]{6}$/.test(site.theme.primary || '')) e.push('couleur invalide');
  for (const k of ['email', 'phone', 'address', 'hours']) if (!isStr(site.contact?.[k] ?? '', 200)) e.push('contact.' + k + ' invalide');
  for (const k of ['owner', 'siret', 'host']) if (!isStr(site.legal?.[k] ?? '', 200)) e.push('legal.' + k + ' invalide');
  if (!Array.isArray(site.pages) || site.pages.length < 1 || site.pages.length > LIM.pages) e.push(`pages : 1 à ${LIM.pages}`);
  else {
    const slugs = new Set();
    for (const p of site.pages) {
      if (!/^[a-z0-9-]{1,30}$/.test(p.slug || '')) e.push('slug invalide'); else if (slugs.has(p.slug)) e.push('slug en double : ' + p.slug); else slugs.add(p.slug);
      if (p.slug === 'mentions-legales') e.push('slug réservé');
      if (!isStr(p.title, 80) || !p.title) e.push('titre de page invalide');
      if (!Array.isArray(p.blocks) || p.blocks.length > LIM.blocks) { e.push('blocs invalides'); continue; }
      for (const b of p.blocks) {
        if (!['hero', 'text', 'services', 'gallery', 'contact'].includes(b.type)) { e.push('type de bloc inconnu'); continue; }
        for (const k of ['title', 'subtitle', 'body', 'imageAlt']) if (b[k] !== undefined && !isStr(b[k])) e.push(`${k} trop long`);
        if (b.image && !ok.has(b.image)) e.push('photo inconnue : ' + b.image);
        if (b.cta && (!isStr(b.cta.label, 60) || !/^([a-z0-9-]+\.html|tel:[+0-9 ]{3,20}|mailto:[^\s"<>]{3,120}|https:\/\/[^\s"<>]{3,200})$/.test(b.cta.href || ''))) e.push('bouton invalide');
        if (b.items) { if (!Array.isArray(b.items) || b.items.length > LIM.items) e.push('trop de services'); else for (const it of b.items) if (!isStr(it.name, 80) || !isStr(it.desc ?? '', 400) || !isStr(it.price ?? '', 40)) e.push('service invalide'); }
        if (b.images) { if (!Array.isArray(b.images) || b.images.length > LIM.images) e.push('trop de photos'); else for (const im of b.images) { if (!ok.has(im.src)) e.push('photo inconnue : ' + im.src); if (!isStr(im.alt ?? '', 200)) e.push('texte alternatif trop long'); } }
      }
    }
    if (!slugs.has('accueil')) e.push('la page accueil est obligatoire');
  }
  return { ok: e.length === 0, errors: [...new Set(e)] };
}

/** Conditions de CONTENU pour publier (verifiees cote serveur par la barriere de publication). */
export function contentReadiness(site) {
  const r = [];
  const ph = findPlaceholders(site); if (ph.length) r.push(`texte « ${TODO} » restant (${ph.length})`);
  if (!site.contact?.email && !site.contact?.phone) r.push('au moins un e-mail ou un téléphone est requis');
  if (!site.legal?.owner) r.push('mentions légales : éditeur manquant');
  for (const p of site.pages) if (!p.blocks.length) r.push(`page vide : ${p.title}`);
  return r;
}

const slugify = (s) => clip(s, 40).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 30);

/** Discussion : interprete des consignes en francais et modifie le site. Retourne {site, reply, changed}. */
export function applyChatEdit(siteIn, text) {
  const site = structuredClone(siteIn), t = clip(text, 400), low = t.toLowerCase(), home = site.pages.find((p) => p.slug === 'accueil');
  let m;
  const ok = (reply) => ({ site, reply, changed: true });
  if ((m = low.match(/couleur(?:s)?\s*(?:principale)?\s*[:=]?\s*(#[0-9a-f]{6}|[a-zé]+)/))) {
    const c = m[1].startsWith('#') ? m[1] : COLORS[m[1]];
    if (c) { site.theme.primary = c; return ok(`Couleur principale changée (${c}).`); }
    return { site: siteIn, reply: `Couleurs disponibles : ${Object.keys(COLORS).join(', ')} ou un code #rrggbb.`, changed: false };
  }
  if (/prestige/.test(low)) { site.theme.style = 'prestige'; return ok('Thème VM Prestige activé.'); }
  if (/signature/.test(low)) { site.theme.style = 'signature'; return ok('Thème VM Signature activé.'); }
  if (/mode sombre/.test(low)) { site.theme.dark = true; return ok('Mode sombre activé.'); }
  if (/mode clair/.test(low)) { site.theme.dark = false; return ok('Mode clair activé.'); }
  if ((m = t.match(/^(?:titre|slogan)\s*(?:de l'accueil)?\s*[:=]\s*(.+)$/i))) { const h = home.blocks.find((b) => b.type === 'hero'); if (h) { h.subtitle = clip(m[1], 140); return ok('Slogan de l\'accueil mis à jour.'); } }
  if ((m = t.match(/^nom\s*(?:du site)?\s*[:=]\s*(.+)$/i))) { site.name = clip(m[1], 80); const h = home.blocks.find((b) => b.type === 'hero'); if (h) h.title = site.name; return ok('Nom du site mis à jour.'); }
  if ((m = t.match(/(?:t[ée]l[ée]phone|tel)\s*[:=]?\s*([+0-9 .]{6,20})/i))) { site.contact.phone = clip(m[1], 30); return ok('Téléphone enregistré.'); }
  if ((m = t.match(/e-?mail\s*[:=]?\s*([^\s@]+@[^\s@]+\.[^\s@]+)/i))) { site.contact.email = clip(m[1], 120); return ok('E-mail enregistré.'); }
  if ((m = t.match(/adresse\s*[:=]\s*(.+)$/i))) { site.contact.address = clip(m[1], 160); return ok('Adresse enregistrée.'); }
  if ((m = t.match(/horaires?\s*[:=]\s*(.+)$/i))) { site.contact.hours = clip(m[1], 160); return ok('Horaires enregistrés.'); }
  if ((m = t.match(/(?:[ée]diteur|propri[ée]taire)\s*[:=]\s*(.+)$/i))) { site.legal.owner = clip(m[1], 120); return ok('Éditeur des mentions légales enregistré.'); }
  if ((m = low.match(/ajoute(?:r)?\s+(?:une\s+)?page\s+(.+)$/))) {
    const title = clip(m[1], 40), slug = slugify(title);
    if (!slug || site.pages.some((p) => p.slug === slug) || ['mentions-legales'].includes(slug)) return { site: siteIn, reply: 'Nom de page indisponible.', changed: false };
    if (site.pages.length >= LIM.pages) return { site: siteIn, reply: `Maximum ${LIM.pages} pages.`, changed: false };
    site.pages.splice(site.pages.length - 1, 0, { slug, title: title[0].toUpperCase() + title.slice(1), blocks: [{ type: 'text', title: title[0].toUpperCase() + title.slice(1), body: `${TODO} : écrivez le contenu de cette page.` }] });
    return ok(`Page « ${title} » ajoutée. Il reste à écrire son texte.`);
  }
  if ((m = low.match(/supprim(?:e|er)\s+(?:la\s+)?page\s+(.+)$/))) {
    const slug = slugify(m[1]);
    if (['accueil', 'contact'].includes(slug)) return { site: siteIn, reply: 'Les pages Accueil et Contact sont obligatoires.', changed: false };
    const n = site.pages.length; site.pages = site.pages.filter((p) => p.slug !== slug);
    return site.pages.length < n ? ok('Page supprimée.') : { site: siteIn, reply: 'Page introuvable.', changed: false };
  }
  if ((m = t.match(/ajoute(?:r)?\s+(?:un\s+)?service\s+(.+?)(?:\s+(?:à|a)\s+(\d+(?:[.,]\d+)?)\s*(?:€|euros?)?)?$/i))) {
    const svc = site.pages.flatMap((p) => p.blocks).filter((b) => b.type === 'services');
    if (!svc.length) return { site: siteIn, reply: 'Aucun bloc de services trouvé.', changed: false };
    for (const b of svc) if (b.items.length < LIM.items) b.items.push({ name: clip(m[1], 80), desc: '', price: m[2] ? `${m[2].replace(',', '.')} €` : '' });
    return ok(`Service « ${clip(m[1], 80)} » ajouté.`);
  }
  return { site: siteIn, reply: 'Je sais : changer la couleur (« couleur bleu »), le slogan (« slogan : … »), le nom, le téléphone, l\'e-mail, l\'adresse, les horaires, l\'éditeur, ajouter/supprimer une page, ajouter un service (« ajoute un service Vidange à 59 € »), mode sombre/clair.', changed: false };
}
