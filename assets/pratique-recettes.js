(() => {
  const {esc, json} = window.VMP;
  const recettes = JSON.parse(document.getElementById('data-recettes').textContent);
  const $ = id => document.getElementById(id);
  const MOMENTS = [['matin', '☀️ Matin'], ['midi', '🥗 Midi'], ['soir', '🌙 Soir']];
  // La recette change chaque jour, et différemment selon le repas.
  const jourIndex = () => { const now = new Date(); const start = new Date(now.getFullYear(), 0, 0); return Math.floor((now - start) / 86400000); };
  const filtrees = () => recettes.filter(r =>
    (!$('fRegime').value || r.regime === $('fRegime').value) &&
    (!$('fObj').value || r.objectif === $('fObj').value) &&
    (!$('fOcc').value || r.occasion === $('fOcc').value));
  const carte = r => `<article class="rec"><span class="moment">${esc(r.moment)}</span><h3>${esc(r.nom)}</h3><div class="tags"><span>${esc(r.regime)}</span><span>${esc(r.objectif)}</span><span>${esc(r.occasion)}</span></div><ul>${r.ingredients.map(i => `<li>${esc(i)}</li>`).join('')}</ul><p>${esc(r.etapes)}</p></article>`;
  function rendre() {
    const list = filtrees();
    const jour = MOMENTS.map(([m, label]) => {
      const dans = list.filter(r => r.moment === m);
      if (!dans.length) return `<p class="vide">${label} : aucune recette pour ces filtres.</p>`;
      return carte(dans[(jourIndex() + dans.length) % dans.length]);
    }).join('');
    $('jour').innerHTML = jour;
    $('liste').innerHTML = list.map(carte).join('') || '<p class="vide">Aucune recette pour ces filtres.</p>';
  }
  ['fRegime', 'fObj', 'fOcc'].forEach(id => $(id).onchange = rendre);
  rendre();
})();
