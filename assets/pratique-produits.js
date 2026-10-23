(() => {
  const {esc, mail, json, val} = window.VMP;
  const $ = id => document.getElementById(id);
  let fiches = [];
  let etat = 'loading';
  function rendre() {
    if (etat !== 'ready') {
      $('producteurs').innerHTML = etat === 'loading' ? '<p class="vide" role="status">Chargement des producteurs…</p>' : '<div class="vide" role="status"><p>Impossible de charger les producteurs pour le moment.</p><button type="button" class="btn" data-retry>Réessayer</button></div>';
      const retry = $('producteurs').querySelector('[data-retry]');
      if (retry) retry.onclick = charger;
      return;
    }
    const reg = $('fReg').value, cat = $('fCat').value;
    const list = fiches.filter(f => (!reg || f.region === reg) && (!cat || f.cat === cat));
    $('producteurs').innerHTML = list.length ? list.map(f => `<article class="pcard"><h3>${esc(f.nom)}</h3><p>📍 ${esc(f.ville)} · ${esc(f.region)}</p><p><b>${esc(f.cat)}</b></p><p>${esc(f.desc)}</p>${f.web && /^https:/.test(f.web) ? `<p><a href="${esc(f.web)}" target="_blank" rel="noopener nofollow">Voir le site</a></p>` : ''}</article>`).join('')
      : '<p class="vide">Pas encore de producteur pour ce filtre. Sois le premier à ajouter ta fiche.</p>';
  }
  $('fReg').onchange = rendre; $('fCat').onchange = rendre;
  async function charger() {
    etat = 'loading'; rendre();
    try { fiches = (await json('/produits-locaux/producteurs.json')).filter(f => f && f.nom && f.region); etat = 'ready'; }
    catch (_) { etat = 'error'; }
    rendre();
  }
  charger();
  $('formProd').onsubmit = event => {
    event.preventDefault();
    const f = event.target;
    mail(`Produits locaux – fiche producteur : ${val(f, 'nom')}`, `Entreprise : ${val(f, 'nom')}\nVille : ${val(f, 'ville')}\nRégion : ${val(f, 'region')}\nProduit : ${val(f, 'cat')}\nSite : ${val(f, 'web')}\n\nDescription :\n${val(f, 'desc')}\n\n(Joins tes photos à cet e-mail.)`);
  };
})();
