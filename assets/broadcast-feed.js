/* Afficher uniquement des liens confirmés, sans lecteur tiers chargé automatiquement. */
document.querySelectorAll('[data-broadcast-feed]').forEach(async section => {
  try {
    const response = await fetch('/studio/diffusions.json', {cache:'no-store'});
    if (!response.ok) return;
    const data = await response.json();
    const rows = Array.isArray(data) ? data : [];
    const valid = row => row && row.plateformes && Object.entries(row.plateformes).some(([name,p]) =>
      (name === 'youtube' && p.status === 'published' && /^https:\/\/www\.youtube\.com\/watch\?v=[A-Za-z0-9_-]{11}$/.test(p.url)) ||
      (name === 'twitch' && p.status === 'ended' && /^https:\/\/www\.twitch\.tv\/[a-z0-9_]+$/.test(p.url)));
    const latest = rows.filter(valid).sort((a,b)=>String(b.id).localeCompare(String(a.id)))[0];
    if (!latest) return;
    const title = document.createElement('h2');title.textContent=latest.titre;section.append(title);
    const description = document.createElement('p');description.textContent='Le grand JT · Foot, Actus et Gaming · programme enregistré, généré par IA';section.append(description);
    Object.entries(latest.plateformes).forEach(([name,provider])=>{
      const wrapper = {plateformes:{[name]:provider}};
      if (!valid(wrapper)) return;
      const link=document.createElement('a');link.href=provider.url;link.target='_blank';link.rel='noopener';
      link.textContent=name==='youtube'?'Voir le programme HD sur YouTube':'Retrouver la chaîne Twitch';
      const paragraph=document.createElement('p');paragraph.append(link);section.append(paragraph);
    });
    section.hidden=false;
  } catch (_) { /* Conserver les JT habituels quand aucune diffusion longue n'est disponible. */ }
});
