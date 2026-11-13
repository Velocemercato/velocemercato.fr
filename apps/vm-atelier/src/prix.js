// Grille tarifaire VM Studio Express (en euros TTC, proposition de départ).
// Le serveur recalcule TOUJOURS le total à partir de cette grille : le prix affiché
// dans le navigateur n'est jamais pris tel quel.
export const PRIX = {
  // Ce que le client peut créer seul : un site, ou un visuel à imprimer / publier.
  produits: {
    site: { nom: 'Site internet', icone: '🌐', format: 'site' },
    carte: { nom: 'Carte de visite recto-verso (design)', icone: '💳', format: 'carte', prix: 29 },
    carte_relief: { nom: 'Carte de visite en relief (design)', icone: '✨', format: 'carte', prix: 59 },
    flyer: { nom: 'Flyer A5 (design)', icone: '📄', format: 'flyer', prix: 39 },
    affiche: { nom: 'Affiche A3 (design)', icone: '🖼️', format: 'affiche', prix: 49 },
    post: { nom: 'Publication réseaux (carré)', icone: '📱', format: 'post', prix: 19 },
    story: { nom: 'Story / Reel (vertical)', icone: '📲', format: 'story', prix: 19 },
  },
  // Options possibles pour un visuel seul (le reste ne concerne que les sites).
  optionsVisuel: ['logo', 'retouches_ia'],
  types: {
    vitrine: { nom: 'Site vitrine (1 page)', prix: 290 },
    rendezvous: { nom: 'Site + prise de rendez-vous', prix: 410 },
    boutique: { nom: 'Site + boutique en ligne', prix: 540 },
  },
  pageSup: { nom: 'Page supplémentaire', prix: 60, max: 10 },
  langue: { nom: 'Langue supplémentaire', prix: 90, max: 3 },
  options: {
    logo: { nom: 'Logo créé par IA', prix: 49 },
    carte: { nom: 'Carte de visite (design)', prix: 29 },
    carte_relief: { nom: 'Carte de visite en relief (design)', prix: 59 },
    flyer: { nom: 'Flyer ou affiche', prix: 39 },
    voix: { nom: 'Voix off IA', prix: 39 },
    musique: { nom: 'Musique IA', prix: 29 },
    mascotte: { nom: 'Mascotte / personnage 3D', prix: 99 },
    video: { nom: 'Vidéo pub IA (30 s)', prix: 149 },
    // Couvre le coût de l'IA (quelques centimes par demande) : c'est le client qui paie, pas Romain.
    retouches_ia: { nom: 'Retouches en direct avec l’assistant IA (30 jours)', prix: 29 },
  },
  pack: { nom: 'Pack 3 ans : domaine + hébergement + maintenance', prix: 390 },
};

// Calcule les lignes et le total à partir d'une configuration (valeurs non fiables).
export function devis(cfg) {
  const c = cfg && typeof cfg === 'object' ? cfg : {};
  const lignes = [];
  const produit = PRIX.produits[c.produit] ? c.produit : 'site';
  if (produit !== 'site') {
    const pr = PRIX.produits[produit];
    lignes.push([pr.nom, pr.prix]);
    const o = (Array.isArray(c.options) ? c.options : []).filter((k) => PRIX.optionsVisuel.includes(k) && PRIX.options[k]);
    for (const k of PRIX.optionsVisuel) if (o.includes(k)) lignes.push([PRIX.options[k].nom, PRIX.options[k].prix]);
    return { produit, format: pr.format, type: produit, pages: 0, langues: 0, options: PRIX.optionsVisuel.filter((k) => o.includes(k)), pack: false, lignes, total: lignes.reduce((s, l) => s + l[1], 0) };
  }
  const type = PRIX.types[c.type] ? c.type : 'vitrine';
  lignes.push([PRIX.types[type].nom, PRIX.types[type].prix]);
  const pages = Math.max(0, Math.min(PRIX.pageSup.max, parseInt(c.pages, 10) || 0));
  if (pages) lignes.push([`${PRIX.pageSup.nom} × ${pages}`, pages * PRIX.pageSup.prix]);
  const langues = Math.max(0, Math.min(PRIX.langue.max, parseInt(c.langues, 10) || 0));
  if (langues) lignes.push([`${PRIX.langue.nom} × ${langues}`, langues * PRIX.langue.prix]);
  const opts = Array.isArray(c.options) ? c.options : [];
  for (const k of Object.keys(PRIX.options)) if (opts.includes(k)) lignes.push([PRIX.options[k].nom, PRIX.options[k].prix]);
  if (c.pack !== false) lignes.push([PRIX.pack.nom, PRIX.pack.prix]);
  const total = lignes.reduce((s, l) => s + l[1], 0);
  return { produit, format: 'site', type, pages, langues, options: Object.keys(PRIX.options).filter((k) => opts.includes(k)), pack: c.pack !== false, lignes, total };
}
