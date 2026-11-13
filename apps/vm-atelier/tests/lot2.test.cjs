// Lot 2 : lien client (code + session de consultation), version figée / en cours, plusieurs ouvertures, révocation.
const { chromium } = require('playwright');
const B = 'http://127.0.0.1:8787';
const ok = (c, m) => { console.log((c ? 'OK   ' : 'ECHEC') + ' ' + m); if (!c) process.exitCode = 1; };
(async () => {
  const br = await chromium.launch(); const errs = [];
  const ad = await br.newPage({ viewport: { width: 1300, height: 900 } }); ad.on('pageerror', e => errs.push(e.message));
  await ad.goto(B + '/admin'); await ad.fill('#tok', 'test-admin-123'); await ad.click('#entrer'); await ad.waitForSelector('#app:not(.hide)');
  await ad.fill('#npNom', 'Boulangerie Rose'); await ad.click('#creer'); await ad.waitForSelector('#vEdit:not(.hide)');
  await ad.click('.add[data-t=titre]'); await ad.fill('#blocs .card input:not([type=file])', 'Version 1'); await ad.waitForFunction(() => /enregistré/.test(document.getElementById('etat').textContent));
  async function creer(opts) {
    await ad.click('#bCode'); await ad.selectOption('#lVersion', opts.version); await ad.selectOption('#lMode', opts.mode);
    const avant = await ad.$eval('#partage', e => e.textContent);
    await ad.click('#lCreer'); await ad.waitForFunction(a => document.getElementById('partage').textContent !== a && document.querySelector('#partage .code'), avant);
    return ad.textContent('#partage .code');
  }
  async function ouvrir(code, ctx) { const p = await (ctx || await br.newContext()).newPage(); p.on('pageerror', e => errs.push(e.message)); await p.goto(B + '/voir'); await p.fill('#code', code); await p.click('#ok'); await p.waitForTimeout(600); return p; }
  const figee = await creer({ version: 'figee', mode: 'unique' });
  ok(/^[A-Z0-9]{16}$/.test(figee) && await ad.$('#partage button:has-text("Copier le lien")') && await ad.$('#partage button:has-text("Copier le code")'), 'atelier : lien + code, boutons Copier le lien / Copier le code');
  // Aperçus de liens (WhatsApp, robots) : GET et HEAD sur /voir ne consomment rien
  const h = await (await fetch(B + '/voir#' + figee, { method: 'HEAD' })).status; await fetch(B + '/voir');
  const a = await ouvrir(figee);
  ok(h === 200 && /Version 1/.test(await a.textContent('#site')), 'client : code ouvert après passage d’un robot (HEAD/GET ne consomment pas)');
  await a.reload(); await a.waitForTimeout(1600);
  ok(/Version 1/.test(await a.textContent('#site')) && /encore/.test(await a.textContent('#reste')), 'actualisation pendant la session : l’aperçu reste ouvert (compte à rebours)');
  const b = await ouvrir(figee);
  ok(/déjà utilisé/.test(await b.textContent('#msg')), '2e navigateur avec le même code : refusé');
  // Version figée vs en cours
  await ad.fill('#blocs .card input:not([type=file])', 'Version 2'); await ad.waitForFunction(() => /enregistré/.test(document.getElementById('etat').textContent));
  await a.reload(); await a.waitForTimeout(800);
  ok(/Version 1/.test(await a.textContent('#site')), 'version figée : le client voit toujours la version validée (V1)');
  const live = await creer({ version: 'live', mode: 'multi' });
  const c1 = await ouvrir(live), c2 = await ouvrir(live);
  ok(/Version 2/.test(await c1.textContent('#site')) && /Version 2/.test(await c2.textContent('#site')), 'plusieurs ouvertures + dernière version : 2 navigateurs voient la V2');
  // Révocation : la session ouverte se ferme
  await ad.waitForSelector('#codesBox button:has-text("Révoquer")');
  ad.once('dialog', d => d.accept()); await ad.locator('#codesBox div', { hasText: 'en cours' }).locator('button').first().click(); await ad.waitForTimeout(700);
  await c1.reload(); await c1.waitForTimeout(800);
  ok(!(await c1.isVisible('#site')) && await c1.isVisible('#porte'), 'révocation : la consultation ouverte est fermée');
  const c3 = await ouvrir(live); ok(/révoqué|invalide/.test(await c3.textContent('#msg')), 'révocation : le code ne s’ouvre plus');
  ok(/révoqué/.test(await ad.textContent('#codesBox')) && /ouvert le/.test(await ad.textContent('#codesBox')), 'atelier : liste des liens avec état (ouvert le…, révoqué)');
  // Concurrence : 8 ouvertures simultanées d’un code unique → 1 seule session
  const u = await creer({ version: 'figee', mode: 'unique' });
  const res = await c3.evaluate(c => Promise.all([...Array(8)].map(() => fetch('/api/voir/ouvrir', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ code: c }) }).then(r => r.status))), u);
  ok(res.filter(x => x === 200).length === 1, '8 ouvertures simultanées : une seule session (' + res + ')');
  // Fermer l'aperçu
  const f = await ouvrir(await creer({ version: 'live', mode: 'multi' }), await br.newContext());
  await f.click('#fermer'); await f.waitForTimeout(800); await f.reload(); await f.waitForTimeout(600);
  ok(await f.isVisible('#porte'), '« Fermer l’aperçu » termine la session');
  ok(errs.length === 0, 'aucune erreur JavaScript ' + errs.join(' | '));
  await br.close();
})();
