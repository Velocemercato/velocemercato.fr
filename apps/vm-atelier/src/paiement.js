// VM Studio — paiement Stripe Checkout (lot 3).
// La session est créée côté serveur à partir du devis enregistré (jamais d'un montant envoyé par le navigateur).
// Le paiement est confirmé en interrogeant Stripe côté serveur (payment_status === 'paid'), pas par la page « merci ».
// Clé : secret Cloudflare STRIPE_SECRET_KEY. Une clé « live » est refusée tant que STRIPE_REEL n'est pas « oui »
// (accord écrit de Romain requis avant tout encaissement réel).

export function stripeConfigure(env) { return !!(env.STRIPE_SECRET_KEY && String(env.STRIPE_SECRET_KEY).trim()); }
export function modeStripe(env) { return /^(sk|rk)_live_/.test(String(env.STRIPE_SECRET_KEY || '')) ? 'reel' : 'test'; }

function formulaire(obj, prefixe = '', out = new URLSearchParams()) {
  for (const [k, v] of Object.entries(obj)) {
    const cle = prefixe ? `${prefixe}[${k}]` : k;
    if (v !== null && typeof v === 'object') formulaire(v, cle, out);
    else if (v !== undefined) out.append(cle, String(v));
  }
  return out;
}
async function stripe(env, methode, chemin, corps, f = fetch) {
  const res = await f((env.STRIPE_BASE_URL || 'https://api.stripe.com') + chemin, {
    method: methode,
    headers: { Authorization: 'Bearer ' + env.STRIPE_SECRET_KEY, 'Content-Type': 'application/x-www-form-urlencoded', 'Stripe-Version': '2024-06-20' },
    body: corps ? formulaire(corps).toString() : undefined,
  });
  const j = await res.json().catch(() => ({}));
  if (!res.ok) throw Object.assign(new Error((j.error && j.error.message) || 'Stripe ' + res.status), { statut: res.status });
  return j;
}

// Crée la page de paiement Stripe pour une commande (lignes et prix du devis serveur, en centimes entiers).
export async function creerPaiement(env, commande, domaine, f) {
  if (!stripeConfigure(env)) return { erreur: 'stripe_non_connecte', message: 'Paiement à connecter : ajoute le secret STRIPE_SECRET_KEY (clé de test) sur vm-atelier.' };
  if (modeStripe(env) === 'reel' && env.STRIPE_REEL !== 'oui') return { erreur: 'stripe_reel_bloque', message: 'Clé Stripe réelle détectée : encaissement réel bloqué tant que Romain n’a pas donné son accord écrit (STRIPE_REEL=oui).' };
  const lignes = (commande.config && Array.isArray(commande.config.lignes) ? commande.config.lignes : []).filter((l) => Number(l[1]) > 0);
  if (!lignes.length) return { erreur: 'commande_vide', message: 'Commande sans montant.' };
  const corps = {
    mode: 'payment', client_reference_id: commande.id, 'metadata[commande]': commande.id, locale: 'fr',
    success_url: domaine + '/paiement/retour?c=' + encodeURIComponent(commande.id),
    cancel_url: domaine + '/paiement/retour?c=' + encodeURIComponent(commande.id) + '&annule=1',
  };
  lignes.forEach((l, i) => {
    corps[`line_items[${i}][quantity]`] = 1;
    corps[`line_items[${i}][price_data][currency]`] = 'eur';
    corps[`line_items[${i}][price_data][unit_amount]`] = Math.round(Number(l[1]) * 100);
    corps[`line_items[${i}][price_data][product_data][name]`] = String(l[0]).slice(0, 120);
  });
  if (commande.contact && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(commande.contact.email || '')) corps.customer_email = commande.contact.email;
  try {
    const s = await stripe(env, 'POST', '/v1/checkout/sessions', corps, f);
    return { ok: true, session: s.id, url: s.url, mode: s.livemode ? 'reel' : 'test' };
  } catch (e) {
    return { erreur: e.statut === 401 ? 'stripe_cle_invalide' : 'stripe_erreur', message: e.statut === 401 ? 'Clé Stripe refusée.' : 'Stripe a refusé la création du paiement : ' + e.message };
  }
}

// Vérifie auprès de Stripe si la session est payée (source de vérité côté serveur).
export async function verifierPaiement(env, session, f) {
  if (!stripeConfigure(env) || !session) return { paye: false };
  try {
    const s = await stripe(env, 'GET', '/v1/checkout/sessions/' + encodeURIComponent(session), null, f);
    return { paye: s.payment_status === 'paid' && s.status === 'complete', statut: s.status, montant: s.amount_total };
  } catch (e) { return { paye: false, erreur: true }; }
}
