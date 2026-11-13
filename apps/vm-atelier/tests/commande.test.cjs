// Le client compose son site sur /studio et l'envoie : le site est sauvegardé, Romain le corrige, le client suit en direct.
const { chromium } = require('playwright');
const B = 'http://127.0.0.1:8787';
const ok = (c, m) => { console.log((c ? 'OK   ' : 'ECHEC') + ' ' + m); if (!c) process.exitCode = 1; };
const PNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==', 'base64');
(async () => {
  const br = await chromium.launch(); const errs = [];
  const cl = await br.newPage({ viewport: { width: 390, height: 844 } }); cl.on('pageerror', e => errs.push(e.message));
  await cl.goto(B + '/studio'); await cl.fill('#nom', 'Pizzeria Marco'); await cl.fill('#slogan', 'Pizzas au feu de bois');
  await cl.setInputFiles('#photo', { name: 'p.png', mimeType: 'image/png', buffer: PNG }); await cl.waitForTimeout(400);
  await cl.fill('#cnom', 'Marco'); await cl.fill('#ctel', '06 12 34 56 78'); await cl.check('#cgv'); await cl.click('#envoyer');
  await cl.waitForFunction(() => /envoyée/.test(document.getElementById('msg').textContent));
  const lien = await cl.getAttribute('#msg a', 'href');
  ok(lien && lien.startsWith('https://atelier.velocemercato.fr/salon/'), 'client : reçoit son lien de suivi sur le domaine VM (' + (lien || '').slice(0, 45) + '…)');
  // Romain retrouve le site du client dans l'atelier
  const ad = await br.newPage({ viewport: { width: 1300, height: 900 } }); ad.on('pageerror', e => errs.push(e.message));
  await ad.goto(B + '/admin'); await ad.fill('#tok', 'test-admin-123'); await ad.click('#entrer'); await ad.waitForSelector('#app:not(.hide)');
  await ad.click('#ongCmd'); await ad.waitForSelector('#cmds button:has-text("Ouvrir son site")');
  await ad.click('#cmds button:has-text("Ouvrir son site")'); await ad.waitForSelector('#vEdit:not(.hide)');
  const txt = await ad.textContent('#apercu');
  ok(/Pizzeria Marco/.test(txt) && /feu de bois/.test(txt) && await ad.$('#apercu img'), 'atelier : le site composé par le client est sauvegardé (nom, accroche, photo)');
  // Romain corrige, le client le voit
  const tp = await br.newPage({ viewport: { width: 390, height: 844 } }); await tp.goto(lien.replace('https://atelier.velocemercato.fr', B));
  await tp.waitForFunction(() => /Pizzeria Marco/.test(document.getElementById('site').textContent));
  const premier = ad.locator('#blocs .card').first(); const champs = premier.locator('input:not([type=file])');
  await champs.nth(0).fill('Pizzeria Marco — Le vrai goût italien');
  await tp.waitForFunction(() => /vrai goût italien/.test(document.getElementById('site').textContent), null, { timeout: 8000 });
  ok(true, 'client : voit la correction de Romain en direct sur son lien');
  ok(errs.length === 0, 'aucune erreur JavaScript ' + errs.join(' | '));
  await br.close();
})();
