// Paiement Stripe (lot 3) sans appel réel : réponses de Stripe simulées.
import { creerPaiement, verifierPaiement, modeStripe } from '../src/paiement.js';
const ok = (c, m) => { console.log((c ? 'OK   ' : 'ECHEC') + ' ' + m); if (!c) process.exitCode = 1; };
const commande = { id: 'AB12CD34', contact: { email: 'lea@example.com' }, config: { lignes: [['Site vitrine (1 page)', 290], ['Pack 3 ans', 390]], total: 680 } };
let envoi = null;
const f = async (u, init) => { envoi = { u, init, form: new URLSearchParams(init.body || '') }; return new Response(JSON.stringify({ id: 'cs_test_1', url: 'https://checkout.stripe.com/c/pay/cs_test_1', livemode: false }), { status: 200 }); };
let r = await creerPaiement({ STRIPE_SECRET_KEY: 'sk_test_x' }, commande, 'https://atelier.velocemercato.fr', f);
ok(r.ok && r.url.startsWith('https://checkout.stripe.com/') && r.mode === 'test', 'session Checkout créée en mode test');
ok(envoi.form.get('line_items[0][price_data][unit_amount]') === '29000' && envoi.form.get('line_items[1][price_data][unit_amount]') === '39000' && envoi.form.get('line_items[0][price_data][currency]') === 'eur', 'montants pris dans le devis serveur, en centimes (290 € + 390 €)');
ok(envoi.form.get('success_url').startsWith('https://atelier.velocemercato.fr/paiement/retour?c=AB12CD34') && envoi.form.get('metadata[commande]') === 'AB12CD34', 'retour sur le domaine VM vérifié, commande en référence');
ok(envoi.init.headers.Authorization === 'Bearer sk_test_x' && !envoi.init.body.includes('sk_test_x'), 'clé uniquement dans l’en-tête');
r = await creerPaiement({}, commande, 'x'); ok(r.erreur === 'stripe_non_connecte', 'sans clé : « paiement à connecter »');
r = await creerPaiement({ STRIPE_SECRET_KEY: 'sk_live_x' }, commande, 'x', f); ok(r.erreur === 'stripe_reel_bloque', 'clé réelle bloquée sans accord écrit (STRIPE_REEL)');
ok(modeStripe({ STRIPE_SECRET_KEY: 'rk_live_x' }) === 'reel' && modeStripe({ STRIPE_SECRET_KEY: 'sk_test_x' }) === 'test', 'détection test / réel');
r = await creerPaiement({ STRIPE_SECRET_KEY: 'sk_test_x' }, { ...commande, config: { lignes: [] } }, 'x', f); ok(r.erreur === 'commande_vide', 'commande sans montant refusée');
const sess = (paid) => async () => new Response(JSON.stringify({ id: 'cs_test_1', status: paid ? 'complete' : 'open', payment_status: paid ? 'paid' : 'unpaid' }), { status: 200 });
ok((await verifierPaiement({ STRIPE_SECRET_KEY: 'sk_test_x' }, 'cs_test_1', sess(true))).paye === true, 'paiement confirmé par Stripe côté serveur');
ok((await verifierPaiement({ STRIPE_SECRET_KEY: 'sk_test_x' }, 'cs_test_1', sess(false))).paye === false, 'session non payée : pas confirmée');
