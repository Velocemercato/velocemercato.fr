// Studio client : choix du produit (carte, flyer…), aperçu en direct, vérification avant envoi,
// page de présentation, et contrôle de toutes les pages en 320 / 390 / 768 / 1300 px.
const { chromium } = require('playwright');
const B = 'http://127.0.0.1:8787';
const ok = (c, m) => { console.log((c ? 'OK   ' : 'ECHEC') + ' ' + m); if (!c) process.exitCode = 1; };
const ratio = (p, sel) => p.evaluate((s) => { const r = document.querySelector(s).getBoundingClientRect(); return r.width / r.height; }, sel);
(async () => {
  const br = await chromium.launch(); const errs = [];
  // Page de présentation
  const la = await br.newPage({ viewport: { width: 1300, height: 900 } }); la.on('pageerror', (e) => errs.push('accueil ' + e.message));
  await la.goto(B + '/');
  ok((await la.getAttribute('meta[name=robots]', 'content')) === 'index,follow', 'présentation indexable par Google');
  ok((await la.locator('.vm-page').count()) >= 3 && /Salon Léa/.test(await la.textContent('#exSite')), 'exemples de site, carte, flyer, post affichés');
  await la.click('a.tuile[href="/studio?p=flyer"]'); await la.waitForURL(/studio\?p=flyer/);
  ok((await la.getAttribute('.prod[data-p=flyer]', 'aria-pressed')) === 'true', 'tuile « Flyer » → le studio s’ouvre sur le flyer');
  await la.screenshot({ path: process.env.SHOT_DIR + '/v-studio-flyer.png' });
  // Studio : carte de visite
  const cl = await br.newPage({ viewport: { width: 390, height: 844 } }); cl.on('pageerror', (e) => errs.push('studio ' + e.message));
  await cl.goto(B + '/studio?p=carte');
  await cl.fill('#nom', 'Garage Paulo'); await cl.fill('#slogan', 'Mécanique toutes marques'); await cl.fill('#vtel', '06 11 22 33 44'); await cl.fill('#vadr', '3 rue du Moulin');
  ok((await cl.locator('#apercu .vm-page').count()) === 2 && Math.abs(await ratio(cl, '#apercu .vm-page') - 85 / 55) < 0.05, 'carte : recto + verso au format 85×55 en direct');
  ok(/Garage Paulo/.test(await cl.textContent('#apercu')) && /3 rue du Moulin/.test(await cl.textContent('#apercu')), 'carte : nom et adresse visibles dans l’aperçu');
  ok((await cl.textContent('#total')) === '29 €' && await cl.isHidden('#zSite'), 'carte : 29 €, options de site masquées');
  await cl.uncheck('#verso'); ok((await cl.locator('#apercu .vm-page').count()) === 1, 'carte : recto seul si on décoche le verso');
  await cl.check('.optv[value=logo]'); ok((await cl.textContent('#total')) === '78 €', 'carte + logo : 78 €');
  await cl.click('.prod[data-p=story]'); ok(Math.abs(await ratio(cl, '#apercu .vm-page') - 9 / 16) < 0.05, 'story : format vertical 9:16');
  await cl.click('.prod[data-p=affiche]'); ok(Math.abs(await ratio(cl, '#apercu .vm-page') - 297 / 420) < 0.05 && (await cl.textContent('#total')) === '98 €', 'affiche A3 + logo : 98 €');
  await cl.click('.prod[data-p=carte]'); await cl.check('#verso');
  // Mobile : l'aperçu reste visible pendant qu'on remplit ses coordonnées
  await cl.fill('#cnom', 'Paulo'); await cl.fill('#cmail', 'paulo@example.com'); await cl.check('#cgv');
  await cl.locator('#cmsg').scrollIntoViewIfNeeded();
  const apv = await cl.evaluate(() => { const r = document.getElementById('apv').getBoundingClientRect(); return [Math.round(r.top), Math.round(r.bottom)]; });
  ok(apv[0] <= 1 && apv[1] > 100, 'téléphone : l’aperçu reste collé en haut pendant la saisie (' + apv + ')');
  await cl.fill('#cmsg', 'Je veux du bleu'); await cl.fill('#c1', '#1f6feb');
  // Vérifier avant d'envoyer
  await cl.click('#envoyer'); await cl.waitForSelector('#verif:not(.hide)');
  ok((await cl.locator('#vApercu .vm-page').count()) === 2 && /Total : 78 €/.test(await cl.textContent('#vTotal')), 'vérification : la carte et le prix exact avant l’envoi');
  ok(await cl.evaluate(() => document.activeElement.id === 'vOk'), 'clavier : le bouton « J’envoie » a le focus');
  await cl.screenshot({ path: process.env.SHOT_DIR + '/v-verif.png' });
  await cl.keyboard.press('Escape'); ok(await cl.isHidden('#verif') && (await cl.textContent('#msg')) === '', 'Échap / Modifier : retour sans rien envoyer');
  await cl.click('#envoyer'); await cl.click('#vOk'); await cl.waitForFunction(() => /envoyée/.test(document.getElementById('msg').textContent));
  ok(/78 €/.test(await cl.textContent('#msg')) && /carte de visite/.test(await cl.textContent('#msg')), 'envoyée : ' + (await cl.textContent('#msg')).slice(0, 70));
  const lien = (await cl.getAttribute('#msg a', 'href')).replace('https://atelier.velocemercato.fr', B);
  const sa = await br.newPage({ viewport: { width: 390, height: 844 } }); sa.on('pageerror', (e) => errs.push('salon ' + e.message));
  await sa.goto(lien); await sa.waitForFunction(() => document.querySelectorAll('#site .vm-page').length === 2);
  ok(Math.abs(await ratio(sa, '#site .vm-page') - 85 / 55) < 0.05, 'lien de suivi : le client retrouve sa carte au bon format');
  // Le serveur recalcule le prix et impose le format du produit (le navigateur n'est pas cru)
  const r = await cl.evaluate(() => fetch('/api/commande', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ cgv: true, config: { produit: 'flyer', options: ['video', 'logo'], pack: true }, doc: { format: 'site', blocs: [{ t: 'titre', titre: 'X' }] }, contact: { nom: 'Test', email: 't@example.com' } }) }).then((x) => x.json()));
  ok(r.ok && r.total === 88, 'serveur : flyer + logo = 88 € (option vidéo et pack ignorés) → ' + r.total);
  const sb = await br.newPage(); await sb.goto(r.lien.replace('https://atelier.velocemercato.fr', B)); await sb.waitForFunction(() => document.querySelector('#site .vm-page'));
  ok(Math.abs(await ratio(sb, '#site .vm-page') - 148 / 210) < 0.05, 'serveur : le format flyer est imposé même si le navigateur envoie « site »');
  // Clavier : on choisit un produit sans souris
  await cl.goto(B + '/studio'); await cl.focus('.prod[data-p=flyer]'); await cl.keyboard.press('Enter');
  ok((await cl.getAttribute('.prod[data-p=flyer]', 'aria-pressed')) === 'true', 'clavier : choix du produit avec Entrée');
  // Toutes les pages, toutes les tailles : pas de débordement horizontal
  const rap = [];
  for (const w of [320, 390, 768, 1300]) for (const pth of ['/', '/studio', '/studio?p=carte', '/studio?p=affiche', '/voir', '/admin']) {
    const pg = await br.newPage({ viewport: { width: w, height: 800 } }); pg.on('pageerror', (e) => errs.push(pth + '@' + w + ' ' + e.message));
    await pg.goto(B + pth); await pg.waitForTimeout(150);
    const d = await pg.evaluate(() => document.documentElement.scrollWidth - innerWidth); if (d > 1) rap.push(pth + '@' + w + ' +' + d + 'px');
    if (w === 320 && pth === '/') await pg.screenshot({ path: process.env.SHOT_DIR + '/v-accueil-320.png', fullPage: true });
    if (w === 1300 && pth === '/') await pg.screenshot({ path: process.env.SHOT_DIR + '/v-accueil-1300.png', fullPage: true });
    await pg.close();
  }
  ok(rap.length === 0, '24 affichages (6 pages × 320/390/768/1300 px) sans débordement ' + rap.join(', '));
  ok(errs.length === 0, 'aucune erreur JavaScript ' + errs.join(' | '));
  await br.close();
})();
