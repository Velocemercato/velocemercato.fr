// Test de bout en bout : lancer « npx wrangler dev --port 8787 » avec ADMIN_TOKEN=test-admin-123 dans .dev.vars, puis « node tests/navigateur.test.js ».
// Attention : la limite anti-abus (10 essais de code par heure et par IP) est conservée entre deux lancements ; repartir d’un état local vide (.wrangler/state) avant de relancer.
const { chromium } = require('playwright');
const B = 'http://127.0.0.1:8787';
const ok = (c, m) => { console.log((c ? 'OK   ' : 'ECHEC') + ' ' + m); if (!c) process.exitCode = 1; };
(async () => {
  const br = await chromium.launch();
  const errs = [];
  // 1) Studio client
  const cl = await br.newPage(); cl.on('pageerror', e => errs.push('studio ' + e.message));
  await cl.goto(B + '/studio');
  await cl.fill('#nom', 'Salon Léa');
  await cl.check('.opt[value=logo]'); await cl.fill('#pages', '2');
  ok((await cl.textContent('#total')) === (290 + 120 + 49 + 390) + ' €', 'prix en direct ' + await cl.textContent('#total'));
  ok((await cl.textContent('#apercu')).includes('Salon Léa'), 'aperçu du studio');
  await cl.click('#envoyer'); await cl.waitForTimeout(400);
  ok((await cl.textContent('#msg')).includes('Indiquez'), 'refus si contact vide');
  await cl.fill('#cnom', 'Léa'); await cl.fill('#cmail', 'lea@example.com'); await cl.check('#cgv');
  await cl.click('#envoyer'); await cl.click('#vOk'); await cl.waitForFunction(() => document.getElementById('msg').textContent.includes('✅'));
  ok((await cl.textContent('#msg')).includes('849 €'), 'commande enregistrée ' + await cl.textContent('#msg'));
  await cl.waitForTimeout(0);
  // Total falsifié côté client : recalculé par le serveur
  const fake = await cl.evaluate(() => fetch('/api/commande', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ cgv: true, contact: { nom: 'x', email: 'a@b.fr' }, config: { type: 'boutique', options: ['video'], pack: false }, total: 1 }) }).then(r => r.json()));
  ok(fake.total === 540 + 149, 'total recalculé serveur ' + fake.total);
  // 2) Atelier admin
  const ad = await br.newPage({ viewport: { width: 1300, height: 900 } }); ad.on('pageerror', e => errs.push('admin ' + e.message));
  await ad.goto(B + '/admin');
  await ad.fill('#tok', 'mauvais'); await ad.click('#entrer'); await ad.waitForTimeout(300);
  ok((await ad.textContent('#lmsg')) === 'Refusé.', 'mauvais code admin refusé');
  await ad.fill('#tok', 'test-admin-123'); await ad.click('#entrer'); await ad.waitForSelector('#app:not(.hide)');
  await ad.click('#ongCmd'); await ad.waitForTimeout(300);
  ok((await ad.textContent('#cmds')).includes('Léa'), 'commande visible dans l’atelier');
  await ad.click('#ongProjets'); await ad.fill('#npNom', 'Site Léa'); await ad.click('#creer'); await ad.waitForSelector('#vEdit:not(.hide)');
  // 3) Salon : lien ouvert sur un « téléphone »
  await ad.click('#bSalon'); const lien = (await ad.textContent('#partage .code')).replace('https://atelier.velocemercato.fr', B);
  const tel = await br.newPage({ viewport: { width: 390, height: 800 } }); tel.on('pageerror', e => errs.push('salon ' + e.message));
  await tel.goto(lien); await tel.waitForTimeout(800);
  ok((await tel.textContent('#site')).includes('Page vierge'), 'salon : page vierge');
  await ad.click('.add[data-t=titre]'); await ad.fill('#blocs .card input', 'Bienvenue chez Léa');
  await tel.waitForFunction(() => document.getElementById('site').textContent.includes('Bienvenue chez Léa'), null, { timeout: 6000 });
  ok(true, 'salon : le téléphone voit la modification en direct');
  await tel.waitForTimeout(0);
  // 4) Code à usage unique
  await ad.click('#bCode'); await ad.click('#lCreer'); await ad.waitForFunction(()=>/^[A-Z0-9]{16}$/.test((document.querySelector('#partage .code')||{}).textContent||'')); const code = await ad.textContent('#partage .code');
  const v1 = await br.newContext(); const vp = await v1.newPage(); vp.on('pageerror', e => errs.push('voir ' + e.message));
  await vp.goto(B + '/voir'); await vp.fill('#code', code); await vp.click('#ok');
  await vp.waitForSelector('#site:not(.hide)'); ok((await vp.textContent('#site')).includes('Bienvenue chez Léa'), 'code : projet affiché');
  await vp.waitForTimeout(0);
  await vp.close();
  const v2 = await (await br.newContext()).newPage(); await v2.goto(B + '/voir'); await v2.fill('#code', code); await v2.click('#ok'); await v2.waitForTimeout(500);
  ok((await v2.textContent('#msg')).includes('déjà utilisé'), 'code : 2e utilisation refusée');
  // Course : 8 ouvertures simultanées d’un nouveau code → 1 seule réussite
  await ad.click('#bCode'); await ad.click('#lCreer'); await ad.waitForFunction(c=>{var t=(document.querySelector('#partage .code')||{}).textContent;return t&&t!==c},code); const c2 = await ad.textContent('#partage .code');
  const res = await v2.evaluate(c => Promise.all([...Array(8)].map(() => fetch('/api/voir/ouvrir', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ code: c }) }).then(r => r.status))), c2);
  ok(res.filter(s => s === 200).length === 1, 'code : 1 seule réussite sur 8 simultanées ' + res);
  // Sécurité
  const st = await v2.evaluate(() => fetch('/api/admin/etat').then(r => r.status)); ok(st === 401, 'atelier interdit sans connexion');
  const xo = await v2.evaluate(() => fetch('/api/commande', { method: 'POST', headers: { 'content-type': 'application/json', }, body: '{}' }).then(r => r.status));
  ok(xo === 400, 'même origine acceptée (contrôle formulaire) ' + xo);
  await ad.waitForTimeout(0);
  ok(errs.length === 0, 'aucune erreur JavaScript ' + errs.join(' | '));
  await br.close();
})();
