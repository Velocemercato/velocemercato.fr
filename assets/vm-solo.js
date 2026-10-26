/* Appli installée seule (VM Annonces, VM Recettes…) : on masque la barre « VM Univers »
   pour que l'appli ressemble à elle-même et pas à tout le réseau VM.
   Les liens vers les autres univers restent accessibles depuis le navigateur.
   Le bouton « Partager » reste visible : on doit pouvoir partager depuis l’appli installée. */
(function () {
  var solo = matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;
  if (!solo) return;
  var root = document.documentElement;
  root.classList.add('vm-solo');
  var st = document.createElement('style');
  st.textContent = '.vm-solo .vmbar,.vm-solo #vmInst{display:none!important}' +
    '.vm-solo .vmbar+header,.vm-solo header.sticky{top:env(safe-area-inset-top,0px)!important}';
  document.head.appendChild(st);
})();
