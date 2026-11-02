
document.querySelectorAll('[data-youtube-id]').forEach(function(el){
  const id=el.getAttribute('data-youtube-id');
  const btn=el.querySelector('button');
  if(!/^[A-Za-z0-9_-]{11}$/.test(id)||!btn)return;
  btn.addEventListener('click',function(){
    const frame=document.createElement('iframe');
    frame.setAttribute('title',el.getAttribute('data-title')||'Épisode sur YouTube');
    frame.setAttribute('allow','accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share');
    frame.setAttribute('allowfullscreen','');
    frame.setAttribute('referrerpolicy','strict-origin-when-cross-origin');
    frame.src='https://www.youtube-nocookie.com/embed/'+id+'?rel=0';
    el.replaceChildren(frame);
  });
});
document.querySelectorAll('[data-copy-link]').forEach(function(button){
  button.addEventListener('click',async function(){
    try{await navigator.clipboard.writeText(location.href);button.textContent='✓ Lien copié';}
    catch(e){window.prompt('Copie ce lien :',location.href);}
  });
});

/* Bouton d'accès aux préférences alertes sur les pages épisodes. */
(function(){const css=document.createElement('link');css.rel='stylesheet';css.href='/notifications/alertes.css';document.head.appendChild(css);const js=document.createElement('script');js.src='/notifications/alertes.js';js.defer=true;document.head.appendChild(js)})();
