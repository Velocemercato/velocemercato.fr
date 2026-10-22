/* Les sites d'actualité affichent le dernier JT réellement publié de leur univers. */
document.querySelectorAll('[data-pastille-universe]').forEach(async section => {
  const name = section.dataset.pastilleUniverse;
  const status = section.querySelector('[role=status]');
  try {
    const response = await fetch('/studio/emissions.json', {cache:'no-store'});
    if (!response.ok) throw new Error('Liste indisponible');
    const rows = await response.json();
    const episode = rows.filter(row => row.publie === true && row.univers === name && Pastille.valid(row.video))
      .sort((a,b) => String(b.date).localeCompare(String(a.date)))[0];
    if (!episode) {status.textContent='Le prochain JT sera affiché ici dès sa publication.';return;}
    section.querySelector('h2').textContent=episode.titre;
    status.textContent=new Date(episode.date).toLocaleString('fr-FR',{timeZone:'Europe/Paris',dateStyle:'medium',timeStyle:'short'});
    const link=section.querySelector('a');link.href=Pastille.page(episode);link.textContent='Voir et partager ce JT';
    const video=document.createElement('video');video.controls=true;video.playsInline=true;video.preload='none';
    if (Pastille.poster(episode)) video.poster=Pastille.poster(episode);
    section.append(video);
    if ('IntersectionObserver' in window) {
      const observer=new IntersectionObserver(entries=>{if(entries.some(entry=>entry.isIntersecting)){Pastille.mount(video,episode);observer.disconnect();}},{rootMargin:'150px'});
      observer.observe(video);
    } else Pastille.mount(video,episode);
  } catch (_) {status.textContent='Le JT est momentanément indisponible. Retrouvez les émissions dans VM Studio.';}
});
