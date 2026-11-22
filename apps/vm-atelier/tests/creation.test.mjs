import assert from 'node:assert/strict';
import test from 'node:test';
import { briefStudio, docCreation } from '../src/creation-service.js';
import { pageStudio, pageSalon, pageAdmin } from '../src/pages.js';

const theme = { c1: '#3155a4', c2: '#364f96', fond: '#f1f5fc', texte: '#1e2945' };
const doc = { format: 'site', style: 'atelier', theme, blocs: [
  { t: 'titre', titre: 'En Roue Libre', sous: 'Un atelier vélo à Belfort', bouton: 'Nos services', image: 'data:image/jpeg;base64,AAAA' },
  { t: 'texte', titre: 'Notre atelier', texte: 'Révision et réparation' },
] };

test('défend le périmètre du document et choisit des couleurs utilisables', () => {
  const propre = docCreation({ ...doc, style: '__proto__', theme: { fond: 'url(1)' },
    blocs: [null, ...doc.blocs, { t: 'contact', tel: '0101010101' }, { t: 'bouton', texte: 'Lien', lien: 'https://chatgpt.com/share/secret' }] });
  assert.equal(propre.style, 'editorial');
  assert.match(propre.theme.fond, /^#[\da-f]{6}$/);
  assert.equal(propre.blocs.length, 2);
  assert.equal(propre.blocs[0].image, undefined);
});

test('la création traite le brief et garde la version à retoucher sans photo ni coordonnées', async () => {
  const brief = 'Raccourcis la présentation et ajoute un bouton de réservation https://velocemercato.fr/reserver';
  const maquette = { ...doc, blocs: [
    { ...doc.blocs[0], lien: 'https://velocemercato.fr/reserver' },
    { ...doc.blocs[1], texte: 'Atelier et réparations' },
    { t: 'bouton', texte: 'Horaires', lien: 'https://example.org/invente' },
  ] };
  const r = await briefStudio({ GEMINI_API_KEY: 'test' }, {
    ...doc, blocs: [...doc.blocs, { t: 'contact', tel: '0102030405', email: 'contact@exemple.fr' }],
  }, brief, { fetch: async (_url, init) => {
    assert.ok(init.body.includes('Raccourcis la présentation'));
    assert.ok(init.body.includes('Notre atelier'));
    assert.ok(!/base64|contact@exemple|0102030405/.test(init.body));
    return Response.json({ candidates: [{ content: { parts: [{ text: JSON.stringify({ doc: maquette, explication: 'Présentation simplifiée.' }) }] } }] });
  } });
  assert.equal(r.ok, true);
  assert.equal(r.doc.style, 'atelier');
  assert.equal(r.doc.blocs[0].lien, 'https://velocemercato.fr/reserver');
  assert.equal(r.doc.blocs[1].texte, 'Atelier et réparations');
  assert.equal(r.doc.blocs.length, 2);
});

test('les pages de création et de suivi ne contiennent aucun lien vers une autre plateforme de création', () => {
  for (const html of [pageStudio, pageSalon, pageAdmin]) {
    assert.doesNotMatch(html, /https:\/\/(?:chatgpt\.com|claude\.ai)/i);
    for (const [, script] of html.matchAll(/<script>([\s\S]*?)<\/script>/g)) assert.doesNotThrow(() => new Function(script));
  }
  assert.match(pageStudio, /Créer un aperçu/);
  assert.match(pageSalon, /activerDictee\(\$\('fTxt'\)/);
});
