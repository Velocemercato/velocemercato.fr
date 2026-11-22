import assert from 'node:assert/strict';
import { registerHooks } from 'node:module';

registerHooks({
  resolve(specifier, context, next) {
    if (specifier === 'cloudflare:workers') return { url: 'data:text/javascript,export class DurableObject {}', shortCircuit: true };
    return next(specifier, context);
  }
});
const { default: worker } = await import('../src/index.js');
const endpoint = 'https://atelier.velocemercato.fr/api/studio/transmission';
const origin = 'https://velocemercato.fr';
let saved;
const env = { STORE: { idFromName() {}, get() { return { fetch: async (_url, init) => {
  saved = JSON.parse(init.body);
  return Response.json({ ok: true, id: 'TEST-PROJET', salon: '0123456789ABCDEFGHIJKLMNOP' });
} }; } } };
const payload = { nom: 'Client Test', email: 'essai@example.test', consentement: 'oui', projet: 'Ajoutez un espace membre',
  draft: { name: 'Maquettes VTT', type: 'app', theme: 'dimension', accent: '#a175ef', tagline: 'Le sport à deux roues',
    photo: 'data:image/webp;base64,AAAA', sections: [{ title: 'Catalogue', text: 'Vélos électriques.' }] } };
const send = (body, from = origin) => worker.fetch(new Request(endpoint, {
  method: 'POST', headers: { origin: from, 'content-type': 'application/json' }, body: JSON.stringify(body)
}), env);
assert.equal((await worker.fetch(new Request(endpoint, { headers: { origin } }), env)).headers.get('access-control-allow-origin'), origin);
assert.equal((await send(payload, 'https://other.example')).status, 403);
assert.equal((await send({ ...payload, consentement: '' })).status, 400);
assert.equal((await send({ ...payload, projet: 'n'.repeat(960000) })).status, 400);
assert.equal(saved, undefined);
const response = await send(payload);
assert.equal(response.status, 200);
assert.equal((await response.json()).lien, 'https://atelier.velocemercato.fr/salon/0123456789ABCDEFGHIJKLMNOP');
assert.equal(saved.op, 'commande');
assert.equal(saved.a.total, 0);
assert.equal(saved.a.config.type, 'demande');
const doc = JSON.parse(saved.a.doc);
assert.equal(doc.style, 'dimension');
assert.equal(doc.blocs[0].titre, payload.draft.name);
assert.equal(doc.blocs[0].image, payload.draft.photo);
assert.equal(doc.blocs[1].titre, 'Catalogue');
assert.doesNotMatch(saved.a.doc, /example.test/);
console.log('Transmission vérifiée avec stockage simulé : accès, consentement, maquette et photo, référence et salon.');
