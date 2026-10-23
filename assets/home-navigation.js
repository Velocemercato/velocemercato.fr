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
    if (scroll) requestAnimationFrame(() => target.scrollIntoView({block:'start', behavior:'instant'}));
  }
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (link) reveal(link.getAttribute('href'));
  });
  addEventListener('hashchange', () => reveal(location.hash, true));
  if (location.hash) reveal(location.hash, true);
})();
