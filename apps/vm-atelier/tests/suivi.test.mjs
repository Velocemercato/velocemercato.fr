import assert from 'node:assert/strict';
import { registerHooks } from 'node:module';
import { DatabaseSync } from 'node:sqlite';
import { test } from 'node:test';

registerHooks({
  resolve(specifier, context, next) {
    if (specifier === 'cloudflare:workers') {
      return { url: 'data:text/javascript,export class DurableObject { constructor(ctx,env){this.ctx=ctx;this.env=env} }', shortCircuit: true };
    }
    return next(specifier, context);
  }
});
const { default: worker, Store } = await import('../src/index.js');
const atelier = 'https://atelier.velocemercato.fr';
const site = 'https://velocemercato.fr';

test('le suivi relie un projet privé, ses messages, sa commande et sa modération', async () => {
  const db = new DatabaseSync(':memory:');
  const mails = [], fond = [];
  const env = {
    ADMIN_TOKEN: 'code-local-essai',
    STUDIO_MAIL_FROM: 'atelier@example.test',
    STUDIO_MAIL_TO: 'proprietaire@example.test',
    STUDIO_EMAIL: { async send(message) { mails.push(message); } }
  };
  const store = new Store({
    waitUntil(promise) { fond.push(promise); },
    storage: {
      sql: { exec(sql, ...args) {
        if (sql.trimStart().startsWith('SELECT')) return db.prepare(sql).all(...args);
        if (args.length) db.prepare(sql).run(...args);
        else db.exec(sql);
        return [];
      } },
      transactionSync(fn) {
        db.exec('BEGIN');
        try { const out = fn(); db.exec('COMMIT'); return out; }
        catch (error) { db.exec('ROLLBACK'); throw error; }
      }
    }
  }, env);
  env.STORE = { idFromName: x => x, get: () => ({ fetch: (url, init) => store.fetch(new Request(url, init)) }) };
  const get = (path, cookie) => worker.fetch(new Request(atelier + path, { headers: cookie ? { cookie } : {} }), env);
  const post = (path, body, origin = atelier, cookie = '') => worker.fetch(new Request(atelier + path, {
    method: 'POST', headers: { origin, cookie, 'content-type': 'application/json' }, body: JSON.stringify(body)
  }), env);
  const brouillon = { cle: crypto.randomUUID(), partager: true, draft: { name: 'Le studio test', type: 'app', sections: [] } };
  assert.equal((await post('/api/studio/suivi', { ...brouillon, partager: false }, site)).status, 400);
  assert.equal((await post('/api/studio/suivi', brouillon, 'https://hors-site.test')).status, 403);
  assert.equal((await get('/api/admin/activite')).status, 401);
  const login = await post('/api/admin/login', { token: env.ADMIN_TOKEN });
  const cookie = login.headers.get('set-cookie').split(';')[0];
  assert.equal((await (await get('/api/admin/activite', cookie)).json()).nonLues, 0);

  const creer = await post('/api/studio/suivi', brouillon, site);
  assert.equal(creer.status, 200);
  const premier = await creer.json();
  assert.equal((await (await post('/api/studio/suivi', brouillon, site)).json()).lien, premier.lien);
  const id = db.prepare('SELECT id FROM projets').get().id;
  const salon = new URL(premier.lien).pathname.replace('/salon/', '/api/salon/');
  const maj = await post('/api/studio/suivi', { ...brouillon, base: 1, draft: { ...brouillon.draft, name: 'Version client 2' } }, site);
  assert.equal((await maj.json()).version, 2);
  assert.equal((await post('/api/studio/suivi', { ...brouillon, base: 1 }, site)).status, 409);
  assert.equal((await (await get(salon)).json()).nom, 'Version client 2');
  assert.equal((await post(salon + '/avis', { texte: 'Aide sur la carte.' })).status, 200);
  const notifications = await (await get('/api/admin/activite', cookie)).json();
  assert.deepEqual(notifications.activites.map(a => a.type).sort(), ['aide', 'debut']);
  assert.ok(notifications.activites.every(a => a.lien === atelier + '/admin?projet=' + id));
  assert.equal((await (await get('/api/admin/avis?id=' + id, cookie)).json()).avis[0].texte, 'Aide sur la carte.');
  const notification = notifications.activites[0];
  await post('/api/admin/activite-lire', { id: notification.id }, atelier, cookie);
  assert.equal((await (await get('/api/admin/activite', cookie)).json()).nonLues, 1);

  const demande = { nom: 'Client', email: 'client@example.test', consentement: 'oui', draft: brouillon.draft, suivi: brouillon.cle, base: 2 };
  const commande = await (await post('/api/studio/transmission', demande, site)).json();
  assert.equal(commande.lien, premier.lien);
  assert.equal((await (await post('/api/studio/transmission', demande, site)).json()).id, commande.id);
  assert.equal(db.prepare('SELECT count(*) AS n FROM projets').get().n, 1);
  await Promise.all(fond);
  assert.equal(mails.length, 3);
  assert.ok(mails.every(m => m.to === env.STUDIO_MAIL_TO && !m.text.includes('client@example.test') && !m.text.includes('/salon/')));
  await post('/api/admin/revue', { id, revue: 'refuse' }, atelier, cookie);
  assert.equal((await get(salon)).status, 404);
  assert.equal((await post('/api/studio/suivi', { ...brouillon, base: 3 }, site)).status, 403);
  db.close();
});
