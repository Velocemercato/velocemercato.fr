(() => {
  const $ = id => document.getElementById(id);
  const CATS = [
    ['🩺 Médecin généraliste', 'médecin généraliste'], ['🦷 Dentiste', 'dentiste'], ['💇 Coiffeur', 'coiffeur'],
    ['🔧 Garage auto', 'garage automobile'], ['💊 Pharmacie de garde', 'pharmacie de garde'], ['🩹 Kinésithérapeute', 'kinésithérapeute']];
  const cats = $('cats');
  function rendre() {
    const ville = $('ville').value.trim();
    const ou = ville || '';
    cats.innerHTML = CATS.map(([label, q]) => {
      const cherche = encodeURIComponent(`${q} ${ou}`.trim());
      const pj = `https://www.pagesjaunes.fr/annuaire/chercherlespros?quoiqui=${encodeURIComponent(q)}&ou=${encodeURIComponent(ou)}`;
      return `<article class="pcard rdvc"><h3>${label}</h3><a href="https://www.google.com/maps/search/${cherche}" target="_blank" rel="noopener">🗺️ Carte</a><a href="${pj}" target="_blank" rel="noopener">📒 Pages Jaunes</a></article>`;
    }).join('');
  }
  $('ville').oninput = rendre;
  rendre();
})();
