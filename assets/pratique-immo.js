(() => {
  const $ = id => document.getElementById(id);
  // Week-end : prochain vendredi et dimanche, en heure locale.
  const now = new Date();
  const ven = new Date(now); ven.setDate(now.getDate() + ((5 - now.getDay() + 7) % 7));
  const dim = new Date(ven); dim.setDate(ven.getDate() + 2);
  const iso = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  const fr = d => d.toLocaleDateString('fr-FR', {weekday: 'short', day: 'numeric', month: 'short'});
  $('weekend').textContent = `du ${fr(ven)} au ${fr(dim)}`;
  document.querySelectorAll('a.airbnb').forEach(a => {
    a.href = `https://www.airbnb.fr/s/${encodeURIComponent(a.dataset.region)}/homes?checkin=${iso(ven)}&checkout=${iso(dim)}`;
  });
})();
