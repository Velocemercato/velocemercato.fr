// Tests de l'assistant IA sans appel payant : réponses d'Anthropic simulées.
import { proposer, _test } from '../src/ia.js';
const ok = (c, m) => { console.log((c ? 'OK   ' : 'ECHEC') + ' ' + m); if (!c) process.exitCode = 1; };
const PHOTO = 'data:image/jpeg;base64,AAAA';
const doc = { format: 'site', theme: { c1: '#e52643', c2: '#f4cf55', fond: '#0b0c12', texte: '#ffffff' },
  blocs: [{ t: 'titre', titre: 'Salon Léa', image: PHOTO }, { t: 'texte', texte: 'Bonjour' }] };
const env = { ANTHROPIC_API_KEY: 'cle-de-test' };
function reponse(status, corps) { return async () => new Response(JSON.stringify(corps), { status, headers: { 'content-type': 'application/json', 'request-id': 'req_test' } }); }
function message(texte, stop = 'end_turn') {
  return { id: 'msg_1', type: 'message', role: 'assistant', model: 'claude-opus-5-5', stop_reason: stop, stop_sequence: null,
    content: [{ type: 'text', text: texte }], usage: { input_tokens: 900, output_tokens: 300 } };
}
let envoye = null;
const capture = async (url, init) => { envoye = JSON.parse(init.body); return (await reponse(200, message(JSON.stringify({
  explication: 'Photo à gauche, titre agrandi.',
  doc: { format: 'site', theme: doc.theme, blocs: [{ t: 'titre', titre: 'Salon Léa', image: 'IMG_1', pos: 'gauche', taille: 'grand' }, { t: 'texte', texte: 'Bonjour' }] } }))))(); };
let r = await proposer(env, doc, 'mets la photo à gauche et agrandis le titre', { fetch: capture });
ok(r.ok && r.doc.blocs[0].pos === 'gauche' && r.doc.blocs[0].taille === 'grand', 'réussite : proposition appliquable (photo à gauche, titre grand)');
ok(r.ok && r.doc.blocs[0].image === PHOTO, 'la vraie photo est remise à sa place après la réponse');
ok(!JSON.stringify(envoye).includes('base64'), 'aucune photo n’est envoyée à l’IA');
ok(envoye && envoye.model === 'claude-opus-5-5' && envoye.output_config && envoye.output_config.format, 'modèle et sortie structurée demandés');
ok(!('api_key' in (envoye || {})) && !JSON.stringify(envoye).includes('cle-de-test'), 'la clé n’est pas dans le corps de la requête');
r = await proposer({}, doc, 'x'); ok(r.erreur === 'ia_non_connectee', 'sans clé : « IA à connecter », aucune réussite simulée');
r = await proposer(env, doc, 'x', { fetch: reponse(401, { type: 'error', error: { type: 'authentication_error', message: 'invalid x-api-key' } }) });
ok(r.erreur === 'ia_cle_invalide', 'clé refusée : message clair');
r = await proposer(env, doc, 'x', { fetch: reponse(429, { type: 'error', error: { type: 'rate_limit_error', message: 'quota' } }) });
ok(r.erreur === 'ia_quota', 'quota épuisé : message clair');
r = await proposer(env, doc, 'x', { fetch: reponse(200, { ...message(''), stop_reason: 'refusal', stop_details: { type: 'refusal', category: null, explanation: '' } }) });
ok(r.erreur === 'ia_refus', 'refus de l’IA : rien n’est modifié');
r = await proposer(env, doc, 'x', { fetch: reponse(200, message('pas du JSON')) });
ok(r.erreur === 'ia_reponse_invalide', 'réponse illisible : rien n’est modifié');
r = await proposer(env, doc, 'x', { fetch: reponse(200, message('{"explication":"a"', 'max_tokens')) });
ok(r.erreur === 'ia_reponse_invalide', 'réponse coupée (max_tokens) : rien n’est modifié');
r = await proposer({ ...env, IA_DELAI_MS: 200 }, doc, 'x', { fetch: (u, init) => new Promise((_, rej) => { init.signal.addEventListener('abort', () => rej(Object.assign(new Error('aborted'), { name: 'AbortError' }))); }) });
ok(r.erreur === 'ia_delai', 'délai dépassé : message clair, pas de relance automatique');
// Lien dangereux ou photo inventée par l'IA : retirés
const d2 = _test.remettrePhotos({ format: 'site', theme: { c1: 'rouge' }, blocs: [{ t: 'bouton', texte: 'x', lien: 'javascript:alert(1)' }, { t: 'image', src: 'IMG_9' }] }, new Map());
ok(!d2.blocs[0].lien && !d2.blocs[1].src && !d2.theme.c1, 'lien javascript:, photo inventée et couleur invalide retirés');

// ---------- Gemini (Google AI Studio, offre gratuite) ----------
const envG = { GEMINI_API_KEY: 'cle-gemini-test' };
function gemini(status, corps) { return async (url, init) => { gemini.url = url; gemini.init = init; return new Response(JSON.stringify(corps), { status, headers: { 'content-type': 'application/json' } }); }; }
const propG = { explication: 'Photo à gauche.', doc: { format: 'carte', theme: doc.theme, blocs: [{ t: 'titre', titre: 'Salon Léa', image: 'IMG_1', pos: 'gauche' }] } };
r = await proposer(envG, doc, 'photo à gauche', { fetch: gemini(200, { candidates: [{ content: { parts: [{ text: JSON.stringify(propG) }] }, finishReason: 'STOP' }], usageMetadata: { promptTokenCount: 500, candidatesTokenCount: 120 }, modelVersion: 'gemini-flash-latest' }) });
ok(r.ok && r.doc.blocs[0].pos === 'gauche' && r.doc.blocs[0].image === PHOTO && r.usage.fournisseur === 'gemini', 'Gemini : proposition valide, photo remise');
ok(gemini.init.headers['x-goog-api-key'] === 'cle-gemini-test' && !gemini.url.includes('cle-gemini-test') && !gemini.init.body.includes('base64'), 'Gemini : clé dans l’en-tête (pas dans l’adresse), aucune photo envoyée');
r = await proposer(envG, doc, 'x', { fetch: gemini(400, { error: { status: 'INVALID_ARGUMENT', message: 'API key not valid. API_KEY_INVALID' } }) });
ok(r.erreur === 'ia_cle_invalide', 'Gemini : clé refusée');
r = await proposer(envG, doc, 'x', { fetch: gemini(429, { error: { status: 'RESOURCE_EXHAUSTED' } }) });
ok(r.erreur === 'ia_quota', 'Gemini : quota gratuit atteint');
r = await proposer(envG, doc, 'x', { fetch: gemini(200, { promptFeedback: { blockReason: 'SAFETY' } }) });
ok(r.erreur === 'ia_refus', 'Gemini : refus');
r = await proposer(envG, doc, 'x', { fetch: gemini(200, { candidates: [{ content: { parts: [{ text: '{"explication":' }] }, finishReason: 'MAX_TOKENS' }] }) });
ok(r.erreur === 'ia_reponse_invalide', 'Gemini : réponse coupée');
r = await proposer({ ...envG, IA_DELAI_MS: 200 }, doc, 'x', { fetch: (u, init) => new Promise((_, rej) => init.signal.addEventListener('abort', () => rej(Object.assign(new Error('a'), { name: 'AbortError' })))) });
ok(r.erreur === 'ia_delai', 'Gemini : délai dépassé');
const { fournisseur } = await import('../src/ia.js');
ok(fournisseur({ GEMINI_API_KEY: 'g', ANTHROPIC_API_KEY: 'a' }) === 'claude' && fournisseur({ GEMINI_API_KEY: 'g', ANTHROPIC_API_KEY: 'a', IA_FOURNISSEUR: 'gemini' }) === 'gemini' && fournisseur({}) === null, 'choix du fournisseur selon les clés installées');
// Gemini saturé : 2e modèle essayé, puis message clair
let appels = [];
r = await proposer(envG, doc, 'x', { fetch: async (u) => { appels.push(u); return appels.length === 1 ? new Response('{"error":{"status":"UNAVAILABLE"}}', { status: 503 }) : new Response(JSON.stringify({ candidates: [{ content: { parts: [{ text: JSON.stringify(propG) }] }, finishReason: 'STOP' }] }), { status: 200 }); } });
ok(r.ok && appels.length === 2 && appels[1].includes('flash-lite'), 'Gemini saturé (503) : réussite avec le modèle de secours');
r = await proposer(envG, doc, 'x', { fetch: async () => new Response('{}', { status: 503 }) });
ok(r.erreur === 'ia_surcharge', 'Gemini saturé sur les 2 modèles : message « réessaie dans une minute »');
