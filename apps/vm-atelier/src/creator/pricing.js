// Configuration UNIQUE des tarifs (prix fixes TTC, offres publiques VM Studio). Modifier ici seulement.
// Les périmètres détaillés ne sont PAS inventés : champ scope à reprendre de l'offre publique avant recette.
export const PACKS = [
  { id: 'mini', label: 'Pack Mini', price: 290, scope: '' },
  { id: 'starter', label: 'Pack Starter', price: 590, scope: '' },
  { id: 'business', label: 'Pack Business', price: 990, scope: '' },
  { id: 'max', label: 'Pack Max', price: 1490, scope: '' },
];
export const MAINTENANCE = [
  { id: 'maint19', label: 'Maintenance mensuelle (petites retouches limitées)', price: 19, period: 'mois' },
  { id: 'maint29', label: 'Maintenance mensuelle étendue (petites retouches limitées)', price: 29, period: 'mois' },
];
export const EXTRAS = [{ id: 'domaine', label: 'Nom de domaine (prix annoncé avant accord)', price: 0, variable: true }, { id: 'extra', label: 'Prestation supplémentaire', price: 0, variable: true }];
export const priceList = () => ({ currency: 'EUR', vat: 'prix TTC', packs: PACKS, maintenance: MAINTENANCE, extras: EXTRAS });
/** Lignes de devis distinctes : création, maintenance, domaine, supplémentaire. */
export function quoteLines({ pack, maintenance, domain, extras = [] } = {}) {
  const L = [], p = PACKS.find((x) => x.id === pack); if (!p) throw new Error('Pack inconnu');
  L.push({ label: `Création du site — ${p.label}`, price: p.price, kind: 'creation' });
  const m = MAINTENANCE.find((x) => x.id === maintenance); if (maintenance && !m) throw new Error('Maintenance inconnue');
  if (m) L.push({ label: m.label + ' (1er mois)', price: m.price, kind: 'maintenance' });
  if (domain && Number(domain.price) >= 0) L.push({ label: 'Nom de domaine : ' + String(domain.name || '').slice(0, 60), price: Number(domain.price), kind: 'domaine' });
  for (const e of extras.slice(0, 10)) L.push({ label: String(e.label).slice(0, 100), price: Number(e.price), kind: 'extra' });
  return L;
}
