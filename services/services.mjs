import {categoryOrDefault,mapsSearch} from './search.mjs';
const form = document.getElementById('search-form');
const category = document.getElementById('category');
const city = document.getElementById('city');
const open = document.getElementById('open');
category.value = categoryOrDefault(new URL(location.href).searchParams.get('categorie'));
function refresh() {
  const taxi = category.value === 'taxi';
  open.disabled = taxi;
  if (taxi) open.checked = false;
  document.getElementById('search-note').textContent = taxi
    ? 'Les coordonnées sont fournies par Google Maps. Contacte le professionnel pour convenir d’une prise en charge.'
    : 'Les résultats et les horaires sont fournis par Google Maps. Confirme les horaires avant de te déplacer.';
  document.querySelectorAll('[data-category]').forEach(link => {
    if (link.dataset.category === category.value) link.setAttribute('aria-current','true');
    else link.removeAttribute('aria-current');
  });
}
category.addEventListener('change', refresh);
document.querySelectorAll('[data-category]').forEach(link => link.addEventListener('click', event => {
  if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  event.preventDefault();
  category.value = link.dataset.category;
  const url = new URL(location.href);
  url.searchParams.set('categorie',category.value);
  history.replaceState(null,'',url);
  refresh();
  document.getElementById('recherche').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
  city.focus({preventScroll:true});
}));
form.addEventListener('submit',event => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  try { location.assign(mapsSearch(category.value,city.value,open.checked)); }
  catch (error) { city.setCustomValidity(error.message); city.reportValidity(); }
});
city.addEventListener('input',() => city.setCustomValidity(''));
refresh();
