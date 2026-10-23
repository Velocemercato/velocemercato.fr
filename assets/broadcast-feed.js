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
    const universe = section.dataset.broadcastUniverse;
    const latest = rows.filter(valid).filter(row=>!universe || (row.universes || ['foot','actus','gaming']).includes(universe))
      .sort((a,b)=>String(b.date_publication || b.date || '').localeCompare(String(a.date_publication || a.date || '')) || String(b.id).localeCompare(String(a.id)))[0];
    if (!latest) return;
    const title = document.createElement('h2');title.textContent=latest.titre;section.append(title);
    const names={foot:'Foot',actus:'Actus',gaming:'Gaming'};
    const description = document.createElement('p');description.textContent=(latest.universes || ['foot','actus','gaming']).map(name=>names[name]).filter(Boolean).join(', ')+' · programme enregistré, généré par IA';section.append(description);
    const youtube = latest.plateformes.youtube;
    if (latest.edition_at && youtube && valid({plateformes:{youtube}})) {
      const play=document.createElement('button');play.type='button';play.className='broadcast-play';
      play.textContent='▶ Lire ce JT en HD ici';
      if (/^(foot|actus|gaming)-edition-[0-9]{8}-[0-9]{4}$/.test(latest.id)) {
        const poster=document.createElement('img');poster.src='/studio/episodes/posters/'+latest.id+'.jpg';
        poster.alt='';poster.loading='lazy';play.prepend(poster);
      }
      play.addEventListener('click',()=>{
        const frame=document.createElement('iframe');frame.className='broadcast-player';
        frame.src='https://www.youtube-nocookie.com/embed/'+new URL(youtube.url).searchParams.get('v')+'?autoplay=1&rel=0';
        frame.title=latest.titre;frame.allow='autoplay; encrypted-media; picture-in-picture; fullscreen';
        frame.allowFullscreen=true;frame.referrerPolicy='strict-origin-when-cross-origin';play.replaceWith(frame);
      },{once:true});
      section.append(play);
      // Le lecteur actuel remplace l'ancien extrait de la même rubrique.
      if (universe) {
        document.querySelectorAll('[data-pastille-universe]').forEach(old=>{if(old.dataset.pastilleUniverse===universe)old.hidden=true;});
        if (universe==='foot') ['ptvMain','ptvMore'].forEach(id=>{const old=document.getElementById(id);if(old)old.hidden=true;});
      }
    }
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
