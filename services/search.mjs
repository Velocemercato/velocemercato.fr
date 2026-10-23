export const categories = Object.freeze({cbd:'boutique CBD',caviste:'caviste magasin alcool',taxi:'taxi VTC'});
export function categoryOrDefault(value) {
  return Object.hasOwn(categories, value) ? value : 'cbd';
}
export function mapsSearch(category, city, open = false) {
  const location = String(city).trim().slice(0,100);
  if (!location) throw new Error('Indique une ville ou un code postal.');
  const key = categoryOrDefault(category);
  const query = `${categories[key]} ${location}${open && key !== 'taxi' ? ' ouvert maintenant' : ''}`;
  const url = new URL('https://www.google.com/maps/search/');
  url.searchParams.set('api','1');
  url.searchParams.set('query',query);
  return url.href;
}
