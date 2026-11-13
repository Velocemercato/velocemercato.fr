// Lot 1 VM Studio, bout en bout : Romain (ordinateur) + client (téléphone) en même temps.
// Lancer : wrangler dev (port 8787) avec ADMIN_TOKEN=test-admin-123, une clé de test et ANTHROPIC_BASE_URL vers la fausse IA locale.
const { chromium } = require('playwright');
const B = 'http://127.0.0.1:8787';
const ok = (c, m) => { console.log((c ? 'OK   ' : 'ECHEC') + ' ' + m); if (!c) process.exitCode = 1; };
const PNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==', 'base64');
(async () => {
  const br = await chromium.launch(); const errs = [];
  const ad = await br.newPage({ viewport: { width: 1300, height: 900 } }); ad.on('pageerror', e => errs.push('atelier ' + e.message));
  await ad.goto(B + '/admin'); await ad.fill('#tok', 'test-admin-123'); await ad.click('#entrer'); await ad.waitForSelector('#app:not(.hide)');
  await ad.fill('#npNom', 'Salon Léa'); await ad.click('#creer'); await ad.waitForSelector('#vEdit:not(.hide)');
  await ad.waitForFunction(() => /Opus|claude/.test(document.getElementById('iaEtat').textContent));
  ok(true, 'atelier : IA affichée comme connectée (' + (await ad.textContent('#iaEtat')).trim() + ')');
  await ad.click('.add[data-t=titre]'); await ad.fill('#blocs .card input:not([type=file])', 'Salon Léa');
  await ad.setInputFiles('#blocs .card input[type=file]', { name: 'photo.png', mimeType: 'image/png', buffer: PNG });
  await ad.waitForFunction(() => document.querySelector('#apercu img'));
  await ad.waitForFunction(() => /enregistré/.test(document.getElementById('etat').textContent));
  // Le client ouvre son lien sur son téléphone
  await ad.click('#bSalon'); const lienPublic = await ad.textContent('#partage .code');
  ok(lienPublic.startsWith('https://atelier.velocemercato.fr/salon/'), 'lien client sur le domaine VM vérifié (' + lienPublic.slice(0, 40) + '…)');
  const lien = lienPublic.replace('https://atelier.velocemercato.fr', B);
  const cl = await br.newPage({ viewport: { width: 390, height: 844 } }); cl.on('pageerror', e => errs.push('client ' + e.message));
  await cl.goto(lien); await cl.waitForFunction(() => document.getElementById('site').textContent.includes('Salon Léa'));
  ok(true, 'client : voit le site en direct');
  // Le client touche le titre et demande une modif
  await cl.click('#site [data-bloc="0"] h1'); await cl.fill('#fTxt', 'Je veux la photo à gauche et le titre plus grand'); await cl.click('#fEnv');
  await cl.waitForFunction(() => /Envoyé/.test(document.getElementById('fMsg').textContent));
  await ad.waitForFunction(() => /photo à gauche/.test(document.getElementById('avisBox').textContent), null, { timeout: 8000 });
  ok(true, 'atelier : reçoit la demande du client en direct (bloc 1)');
  // Romain la transmet à l'IA
  await ad.click('#avisBox button:has-text("Demander")'); await ad.click('#iaGo');
  await ad.waitForSelector('#iaProp:not(.hide)', { timeout: 20000 });
  const avantApp = await cl.evaluate(() => getComputedStyle(document.querySelector('#site [data-bloc="0"]')).display);
  ok(avantApp !== 'flex', 'proposition visible chez Romain mais PAS encore chez le client');
  await ad.click('#iaOui');
  await cl.waitForFunction(() => getComputedStyle(document.querySelector('#site [data-bloc="0"]')).display === 'flex' && document.querySelector('#site [data-bloc="0"] img'), null, { timeout: 8000 });
  const ordre = await cl.evaluate(() => [...document.querySelector('#site [data-bloc="0"]').children].map(e => e.tagName).join(','));
  ok(ordre.startsWith('IMG'), 'appliqué : le client voit la photo à gauche (' + ordre + ')');
  const tailleH1 = await cl.evaluate(() => parseFloat(getComputedStyle(document.querySelector('#site h1')).fontSize));
  ok(tailleH1 >= 40, 'titre agrandi chez le client (' + tailleH1 + ' px)');
  await cl.screenshot({ path: process.env.SHOT_DIR + '/lot1-client.png' });
  // Annuler, puis rétablir via l'IA… et persistance au rechargement
  await ad.click('#annuler');
  await cl.waitForFunction(() => getComputedStyle(document.querySelector('#site [data-bloc="0"]')).display !== 'flex', null, { timeout: 8000 });
  ok(true, 'annuler : le client revient à la version précédente');
  await ad.waitForFunction(() => /enregistré/.test(document.getElementById('etat').textContent));
  await ad.fill('#iaTxt', 'photo à gauche et titre plus grand'); await ad.click('#iaGo'); await ad.waitForSelector('#iaProp:not(.hide)', { timeout: 20000 }); await ad.click('#iaOui');
  await ad.waitForFunction(() => /enregistré/.test(document.getElementById('etat').textContent));
  await ad.reload(); await ad.waitForSelector('#app:not(.hide)'); await ad.click('#liste .card button');
  await ad.waitForSelector('#vEdit:not(.hide)');
  const pos = await ad.evaluate(() => getComputedStyle(document.querySelector('#apercu [data-bloc="0"]')).display);
  ok(pos === 'flex', 'sauvegardé : après rechargement la modification est toujours là');
  // Refuser une proposition : rien ne change
  await ad.fill('#iaTxt', 'teste'); await ad.click('#iaGo'); await ad.waitForSelector('#iaProp:not(.hide)', { timeout: 20000 }); await ad.click('#iaNon');
  ok(/refusée/.test(await ad.textContent('#iaMsg')), 'refuser : proposition écartée');
  // Format carte de visite avec verso
  await ad.selectOption('#eFormat', 'carte'); await ad.click('.add[data-t=page]'); await ad.click('.add[data-t=contact]');
  await cl.waitForFunction(() => document.querySelectorAll('#site .vm-page').length === 2, null, { timeout: 8000 });
  const ratio = await cl.evaluate(() => { const r = document.querySelector('#site .vm-page').getBoundingClientRect(); return (r.width / r.height).toFixed(2); });
  ok(Math.abs(ratio - 85 / 55) < 0.05, 'carte de visite : recto + verso au format 85×55 chez le client (ratio ' + ratio + ')');
  await cl.screenshot({ path: process.env.SHOT_DIR + '/lot1-carte.png' }); await ad.screenshot({ path: process.env.SHOT_DIR + '/lot1-atelier.png' });
  // Sécurité : l'IA n'est pas accessible sans être connecté, et un avis exige le bon lien
  const anon = await (await br.newContext()).newPage(); await anon.goto(B + '/');
  const st = await anon.evaluate(() => fetch('/api/admin/ia', { method: 'POST', headers: { 'content-type': 'application/json' }, body: '{"id":"x","consigne":"y"}' }).then(r => r.status));
  ok(st === 401, 'IA interdite sans connexion (' + st + ')');
  const st2 = await anon.evaluate(() => fetch('/api/salon/AAAAAAAAAAAAAAAAAAAAAAAA/avis', { method: 'POST', headers: { 'content-type': 'application/json' }, body: '{"texte":"x"}' }).then(r => r.status));
  ok(st2 === 404, 'retour client refusé avec un faux lien (' + st2 + ')');
  ok(errs.length === 0, 'aucune erreur JavaScript ' + errs.join(' | '));
  await br.close();
})();
