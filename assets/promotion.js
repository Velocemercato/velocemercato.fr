/* Choisir le format au chargement, sans changer une lecture en cours. */
(() => {
  const vertical = matchMedia('(max-width: 700px)').matches;
  document.querySelectorAll('video[data-promo]').forEach(video => {
    if (!vertical) return;
    const id = video.dataset.promo;
    video.classList.add('is-vertical');
    video.poster = `/media/promos/${id}-vertical.jpg`;
  });
})();
