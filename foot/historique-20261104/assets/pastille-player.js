/* Un seul média actif, lien permanent par épisode, aucune mesure d'audience. */
window.Pastille = (() => {
  const cdn = /^https:\/\/cdn\.jsdelivr\.net\/gh\/Velocemercato\/velocemercato\.fr@[0-9a-f]{40}\/[a-z0-9-]+\.(mp4|jpg|m4a)$/;
  const valid = url => typeof url === 'string' && cdn.test(url);
  const poster = episode => /^\/studio\/episodes\/posters\/[a-z0-9-]+\.jpg$/.test(episode.poster || '') ? episode.poster : (valid(episode.image) ? episode.image : '');
  const page = episode => `https://velocemercato.fr/studio/episodes/${encodeURIComponent(episode.id)}.html`;
  function selected() {
    const query = new URLSearchParams(location.search).get('episode');
    if (query) return query;
    try { return decodeURIComponent((location.hash.match(/^#tv=(.+)$/) || [,''])[1]); }
    catch (_) { return ''; }
  }
  function mount(video, episode, autoplay = false) {
    if (!valid(episode.video)) throw new Error('Source vidéo invalide');
    if (video.dataset.episode === episode.id) {
      if (autoplay) video.play().catch(() => {});
      return;
    }
    video.pause();
    const previous = video._pastille;
    if (previous) { previous.abort(); video.parentNode.querySelectorAll('.pastille-tools,.pastille-status').forEach(item => item.remove()); }
    const controller = new AbortController(); video._pastille = controller;
    const options = {signal:controller.signal};
    video.dataset.episode = episode.id;
    if (video.currentSrc !== episode.video && video.getAttribute('src') !== episode.video) video.src = episode.video;
    video.preload = 'metadata';
    if (poster(episode)) video.poster = poster(episode);
    const tools = document.createElement('div'); tools.className = 'pastille-tools';
    const label = document.createElement('label'); label.textContent = 'Vitesse';
    const speed = document.createElement('select'); speed.setAttribute('aria-label','Vitesse de lecture');
    [1,1.15,1.25,1.5].forEach(rate => { const option = document.createElement('option'); option.value=rate; option.textContent=`${rate.toLocaleString('fr-FR')}×`; speed.append(option); });
    // Les futurs rendus sont déjà accélérés ; éviter de cumuler deux accélérations.
    let rate = episode.speech_rate ? 1 : 1.15;
    try { const saved=Number(localStorage.getItem('vm-tv-speed')); if ([1,1.15,1.25,1.5].includes(saved)) rate=saved; } catch (_) {}
    speed.value=String(rate); video.defaultPlaybackRate=rate; video.playbackRate=rate;
    video.addEventListener('loadedmetadata',()=>video.playbackRate=Number(speed.value),options);
    speed.onchange=() => {video.defaultPlaybackRate=video.playbackRate=Number(speed.value);try{localStorage.setItem('vm-tv-speed',speed.value);}catch(_){}};
    label.append(speed); tools.append(label);
    const share = document.createElement('button'); share.type='button';share.textContent='Partager cette émission';tools.append(share);
    const direct = document.createElement('a');direct.href=episode.video;direct.textContent='Ouvrir le MP4';direct.rel='noopener';tools.append(direct);
    const status = document.createElement('p');status.className='pastille-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');
    video.after(tools,status);
    let timer;
    const clear = () => {clearTimeout(timer);status.textContent='';};
    controller.signal.addEventListener('abort',()=>clearTimeout(timer),{once:true});
    video.addEventListener('waiting',()=>{clearTimeout(timer);timer=setTimeout(()=>{status.textContent='Connexion lente. Vous pouvez ouvrir le MP4 ou choisir une autre émission.';},2500);},options);
    video.addEventListener('playing',clear,options);
    video.addEventListener('error',()=>{clearTimeout(timer);status.textContent='La vidéo ne se charge pas. Essayez le lien « Ouvrir le MP4 » ou revenez plus tard.';},options);
    share.onclick=async()=>{
      try {
        if (navigator.share) await navigator.share({title:episode.titre,url:page(episode)});
        else {await navigator.clipboard.writeText(page(episode));status.textContent='Lien de cette émission copié.';}
      } catch (error) {
        if (error.name!=='AbortError') {status.textContent='Copiez ce lien : '+page(episode);}
      }
    };
    if (autoplay) video.play().catch(()=>{status.textContent='Appuyez sur Lecture pour démarrer la vidéo.';});
  }
  return {valid,poster,page,selected,mount};
})();
document.addEventListener('DOMContentLoaded',()=>{
  const data=document.getElementById('episodeData'),video=document.getElementById('episodeVideo');
  if (data && video) Pastille.mount(video,JSON.parse(data.textContent));
});
