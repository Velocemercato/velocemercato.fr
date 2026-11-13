// VM Studio — assistant IA (lot 1).
// L'IA reçoit le projet SANS les photos (remplacées par IMG_1, IMG_2…) et une consigne en français,
// puis renvoie une PROPOSITION de projet validée par un schéma. Rien n'est appliqué sans l'accord de Romain.
// La clé reste un secret Cloudflare (ANTHROPIC_API_KEY) : jamais envoyée au navigateur, jamais journalisée.
import Anthropic from '@anthropic-ai/sdk';
import { betaZodOutputFormat } from '@anthropic-ai/sdk/helpers/beta/zod';
import { z } from 'zod';

const TYPES = ['titre', 'texte', 'image', 'galerie', 'produits', 'bouton', 'contact', 'page'];
const FORMATS = ['site', 'carte', 'flyer', 'affiche', 'post', 'story'];
const s = (n) => z.string().max(n).optional();

const Bloc = z.object({
  t: z.enum(TYPES),
  titre: s(200), sous: s(300), texte: s(3000), legende: s(200), bouton: s(80), lien: s(500),
  image: s(40), src: s(40), tel: s(40), email: s(120), adresse: s(300),
  pos: z.enum(['haut', 'gauche', 'droite']).optional(),
  taille: z.enum(['normal', 'grand', 'tres-grand']).optional(),
  items: z.array(z.object({ nom: z.string().max(120), prix: z.string().max(40) })).max(30).optional(),
  images: z.array(z.string().max(40)).max(24).optional(),
});
const Proposition = z.object({
  explication: z.string().max(400),
  doc: z.object({
    format: z.enum(FORMATS),
    theme: z.object({ c1: z.string().max(7), c2: z.string().max(7), fond: z.string().max(7), texte: z.string().max(7) }),
    blocs: z.array(Bloc).max(60),
  }),
});

const SYSTEME = `Tu es l'assistant de mise en page de VM Studio (création de sites, cartes de visite, flyers, affiches, posts réseaux).
Tu reçois un projet au format JSON et une consigne en français. Tu renvoies le projet COMPLET modifié selon la consigne, et une explication courte en français.
Règles :
- Ne change que ce que la consigne demande ; garde tout le reste à l'identique (textes, ordre, couleurs).
- Les photos sont représentées par des repères IMG_1, IMG_2… : tu peux les déplacer entre blocs, jamais en inventer.
- Position d'une photo dans un bloc « titre » : champ pos (haut, gauche, droite). Taille du titre : champ taille (normal, grand, tres-grand).
- Couleurs au format #rrggbb. Liens : https://, mailto: ou tel: uniquement.
- Le bloc « page » sépare les pages (recto / verso d'une carte, pages d'un flyer).
- N'invente ni prix, ni numéro de téléphone, ni adresse, ni avis client : laisse vide si l'information manque.`;

// Remplace les photos (data: ou https) par des repères, et garde la correspondance pour les remettre ensuite.
function sansPhotos(doc) {
  const carte = new Map(), inverse = new Map();
  const repere = (v) => {
    if (typeof v !== 'string' || !v) return v;
    if (!inverse.has(v)) { const k = 'IMG_' + (inverse.size + 1); inverse.set(v, k); carte.set(k, v); }
    return inverse.get(v);
  };
  const blocs = (Array.isArray(doc?.blocs) ? doc.blocs : []).map((b) => {
    const c = { ...b };
    if (c.image) c.image = repere(c.image);
    if (c.src) c.src = repere(c.src);
    if (Array.isArray(c.images)) c.images = c.images.map(repere);
    return c;
  });
  return { leger: { format: FORMATS.includes(doc?.format) ? doc.format : 'site', theme: doc?.theme || {}, blocs }, carte };
}
function remettrePhotos(doc, carte) {
  const vrai = (v) => (typeof v === 'string' && carte.has(v) ? carte.get(v) : undefined);
  doc.blocs = doc.blocs.map((b) => {
    const c = {};
    for (const [k, v] of Object.entries(b)) if (v !== undefined && v !== null && v !== '') c[k] = v;
    if ('image' in c) { const v = vrai(c.image); if (v) c.image = v; else delete c.image; }
    if ('src' in c) { const v = vrai(c.src); if (v) c.src = v; else delete c.src; }
    if (Array.isArray(c.images)) c.images = c.images.map(vrai).filter(Boolean);
    if (c.lien && !/^(https:\/\/|mailto:|tel:)/i.test(c.lien)) delete c.lien;
    return c;
  });
  for (const k of ['c1', 'c2', 'fond', 'texte']) if (!/^#[0-9a-f]{6}$/i.test(doc.theme[k] || '')) delete doc.theme[k];
  return doc;
}

export function iaConfiguree(env) { return !!(env.ANTHROPIC_API_KEY && String(env.ANTHROPIC_API_KEY).trim()); }

// Retourne { ok, doc, explication } ou { erreur, message } — jamais de réussite simulée.
export async function proposer(env, doc, consigne, options = {}) {
  if (!iaConfiguree(env)) return { erreur: 'ia_non_connectee', message: 'IA à connecter : ajoute le secret ANTHROPIC_API_KEY sur vm-atelier dans Cloudflare.' };
  const { leger, carte } = sansPhotos(doc);
  const client = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY, maxRetries: 0, timeout: Number(env.IA_DELAI_MS) || 90_000,
    ...(env.ANTHROPIC_BASE_URL ? { baseURL: env.ANTHROPIC_BASE_URL } : {}), ...(options.fetch ? { fetch: options.fetch } : {}) });
  let r;
  try {
    r = await client.beta.messages.create({
      model: env.ANTHROPIC_MODEL || 'claude-opus-5-5',
      max_tokens: 16000,
      betas: ['server-side-fallback-2026-07-01'],
      fallbacks: 'default',
      output_config: { effort: 'medium', format: betaZodOutputFormat(Proposition) },
      system: SYSTEME,
      messages: [{ role: 'user', content: 'Projet actuel :\n' + JSON.stringify(leger) + '\n\nConsigne : ' + String(consigne).slice(0, 1500) }],
    });
  } catch (e) {
    if (e instanceof Anthropic.AuthenticationError || e instanceof Anthropic.PermissionDeniedError) return { erreur: 'ia_cle_invalide', message: 'La clé IA est refusée par Anthropic (invalide ou sans droits).' };
    if (e instanceof Anthropic.RateLimitError) return { erreur: 'ia_quota', message: 'Quota de l’IA atteint chez Anthropic. Réessaie plus tard.' };
    if (e instanceof Anthropic.APIConnectionTimeoutError) return { erreur: 'ia_delai', message: 'L’IA a mis trop de temps. Rien n’a été modifié ; relance seulement si tu le souhaites (une relance est facturée).' };
    if (e instanceof Anthropic.APIConnectionError) return { erreur: 'ia_reseau', message: 'Connexion à l’IA impossible pour le moment.' };
    if (e instanceof Anthropic.APIError) return { erreur: 'ia_erreur', message: 'L’IA a renvoyé une erreur (' + (e.status || '?') + ').' };
    return { erreur: 'ia_erreur', message: 'Erreur inattendue pendant l’appel à l’IA : rien n’a été modifié.' };
  }
  if (r.stop_reason === 'refusal') return { erreur: 'ia_refus', message: 'L’IA a refusé cette demande.' };
  const invalide = { erreur: 'ia_reponse_invalide', message: 'Réponse de l’IA incomplète ou invalide : rien n’a été modifié.' };
  if (r.stop_reason === 'max_tokens') return invalide;
  const texte = (r.content || []).filter((b) => b.type === 'text').map((b) => b.text).join('');
  let brut; try { brut = JSON.parse(texte); } catch { return invalide; }
  const v = Proposition.safeParse(brut);
  if (!v.success) return invalide;
  const sortie = v.data;
  return { ok: true, explication: sortie.explication, doc: remettrePhotos(sortie.doc, carte),
    usage: { entree: r.usage?.input_tokens || 0, sortie: r.usage?.output_tokens || 0, modele: r.model } };
}

export const _test = { sansPhotos, remettrePhotos, Proposition };
