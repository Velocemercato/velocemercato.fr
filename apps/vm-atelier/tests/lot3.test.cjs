// Lot 3 bout en bout : commande client → lien de paiement → bouton « Payer » chez le client → paiement (faux Stripe) → commande payée.
const { chromium } = require('playwright');
const B = 'http://127.0.0.1:8787', S = 'http://127.0.0.1:9933';
const ok = (c, m) => { console.log((c ? 'OK   ' : 'ECHEC') + ' ' + m); if (!c) process.exitCode = 1; };
(async () => {
  const br = await chromium.launch(); const errs = [];
  const cl = await br.newPage({ viewport: { width: 390, height: 844 } }); cl.on('pageerror', e => errs.push(e.message));
  await cl.goto(B + '/studio'); await cl.fill('#nom', 'Garage Paulo'); await cl.fill('#cnom', 'Paulo'); await cl.fill('#cmail', 'paulo@example.com'); await cl.check('#cgv');
  await cl.click('#envoyer'); await cl.click('#vOk'); await cl.waitForFunction(() => /envoyée/.test(document.getElementById('msg').textContent));
  const lien = (await cl.getAttribute('#msg a', 'href')).replace('https://atelier.velocemercato.fr', B);
  const ad = await br.newPage({ viewport: { width: 1300, height: 900 } }); ad.on('pageerror', e => errs.push(e.message));
  await ad.goto(B + '/admin'); await ad.fill('#tok', 'test-admin-123'); await ad.click('#entrer'); await ad.waitForSelector('#app:not(.hide)');
  await ad.click('#ongCmd'); await ad.click('#cmds button:has-text("Créer le lien de paiement")');
  await ad.waitForSelector('#cmds .code'); const url = await ad.textContent('#cmds .code');
  ok(url.startsWith('https://checkout.stripe.com/') && /MODE TEST/.test(await ad.textContent('#cmds')), 'atelier : lien de paiement Stripe créé (mode test affiché)');
  const sess = await (await fetch(S + '/__dernier')).json();
  ok(sess.amount_total === 68000, 'Stripe reçoit le montant du devis serveur : 680 € (' + sess.amount_total / 100 + ' €)');
  const tp = await br.newPage({ viewport: { width: 390, height: 844 } }); tp.on('pageerror', e => errs.push(e.message)); await tp.goto(lien);
  await tp.waitForFunction(() => /Payer 680/.test(document.getElementById('payer').textContent), null, { timeout: 8000 });
  ok((await tp.getAttribute('#payer', 'href')).startsWith('https://checkout.stripe.com/'), 'client : bouton « 💳 Payer 680 € » vers Stripe sur son lien de suivi');
  // Retour sans paiement : rien n'est validé
  const r0 = await br.newPage(); await r0.goto(B + '/paiement/retour?c=' + sess.client_reference_id);
  ok(/non confirmé/.test(await r0.textContent('h1')), 'page « merci » visitée sans payer : commande NON validée');
  // Paiement (simulé chez le faux Stripe) puis retour
  await fetch(S + '/__payer/' + sess.id);
  await r0.goto(B + '/paiement/retour?c=' + sess.client_reference_id);
  ok(/Paiement reçu/.test(await r0.textContent('h1')), 'après paiement : Stripe confirme, page « Paiement reçu »');
  await r0.goto(B + '/paiement/retour?c=' + sess.client_reference_id); // 2e retour : pas de doublon
  await tp.waitForFunction(() => /Payé/.test(document.getElementById('payer').textContent), null, { timeout: 8000 });
  ok(true, 'client : le bouton devient « ✅ Payé »');
  await ad.click('#ongCmd'); await ad.waitForFunction(() => /Payée/.test(document.getElementById('cmds').textContent));
  const carte = ad.locator('#cmds .card', { hasText: sess.client_reference_id });
  ok(/Payée/.test(await carte.innerText()) && !(await carte.locator('button:has-text("lien de paiement")').count()), 'atelier : commande « ✅ Payée », plus de bouton de paiement');
  const st = await (await br.newContext()).newPage(); await st.goto(B + '/');
  const code = await st.evaluate(() => fetch('/api/admin/paiement', { method: 'POST', headers: { 'content-type': 'application/json' }, body: '{"id":"x"}' }).then(r => r.status));
  ok(code === 401, 'création de paiement interdite sans connexion (' + code + ')');
  ok(errs.length === 0, 'aucune erreur JavaScript ' + errs.join(' | '));
  await br.close();
})();
