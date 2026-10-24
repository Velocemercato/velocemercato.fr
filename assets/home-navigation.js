/* Garder les anciens liens de match et de vidéo accessibles dans le volet secondaire. */
(() => {
  function reveal(hash, scroll = false) {
    let id;
    try { id = decodeURIComponent(hash.replace(/^#/, '')); } catch (_) { return; }
    const target = document.getElementById(id);
    if (!target) return;
    let node = target;
    while (node) {
      if (node.tagName === 'DETAILS') node.open = true;
      node = node.parentElement;
    }
    if (!scroll) return;
    // Un bloc encore masqué (quiz, sondages pas encore chargés) : on vise le volet en attendant.
    const go = () => {
      const visible = !target.closest('[hidden]');
      (visible ? target : (target.closest('details') || target)).scrollIntoView({block:'start', behavior:'instant'});
      return visible;
    };
    // Le volet charge ensuite ses blocs (quiz, vidéos…) : on recale la vue une fois le contenu arrivé.
    requestAnimationFrame(go);
    setTimeout(go, 700);
    setTimeout(go, 1500);
  }
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (link) reveal(link.getAttribute('href'), link.getAttribute('href') === location.hash);
  });
  addEventListener('hashchange', () => reveal(location.hash, true));
  if (location.hash) reveal(location.hash, true);
})();
