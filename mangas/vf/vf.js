/* Bibliothèque VF : n'affiche QUE les liens « verifie » + « VF_CONFIRME » + France autorisée. */
(function(){
  'use strict';
  var etat=document.querySelector('[data-vf-etat]');
  var liste=document.querySelector('[data-vf-liste]');
  if(!etat||!liste)return;
  var ID=/^[A-Za-z0-9_-]{11}$/;
  function el(tag,cls,txt){var e=document.createElement(tag);if(cls)e.className=cls;if(txt!=null)e.textContent=txt;return e;}
  function carte(r){
    var m=/[?&]v=([A-Za-z0-9_-]{11})$/.exec(String(r.url_officielle||''));
    if(!m||!ID.test(m[1]))return null;
    var id=m[1],url='https://www.youtube.com/watch?v='+id;
    var a=el('article','panel vf-carte'),body=el('div','card-body');
    if(r.embed_autorise===true){
      var v=el('div','video');v.setAttribute('data-youtube-id',id);v.setAttribute('data-title',String(r.titre_vm||'Épisode'));
      var p=el('div','video-poster');p.style.backgroundImage="url('https://i.ytimg.com/vi/"+id+"/hqdefault.jpg')";
      var b=el('button',null,'▶ Regarder en VF');b.type='button';p.appendChild(b);v.appendChild(p);a.appendChild(v);
    }
    body.appendChild(el('h3',null,String(r.titre_vm||r.titre_youtube||'')));
    var meta=el('div','vf-meta');
    meta.appendChild(el('span','vf','VF'));
    if(r.qualite&&r.qualite!=='inconnue')meta.appendChild(el('span',null,r.qualite));
    meta.appendChild(el('span',null,'Gratuit · YouTube'));
    body.appendChild(meta);
    body.appendChild(el('p','fine','Publié par la chaîne officielle '+String(r.chaine_youtube||'')+'. Vérifié le '+String(r.date_verification||'').slice(0,10)+'.'));
    var d=el('a','direct',r.embed_autorise===true?'Ouvrir sur YouTube ↗':'Regarder chez le diffuseur ↗');
    d.href=url;d.target='_blank';d.rel='noopener';body.appendChild(d);
    a.appendChild(body);return a;
  }
  fetch('/bibliotheque-vf/verifications.json',{cache:'no-store'}).then(function(r){
    if(!r.ok)throw new Error('absent');return r.json();
  }).then(function(data){
    var ok=(data.resultats||[]).filter(function(r){
      return r.statut==='verifie'&&r.audio==='VF_CONFIRME'&&r.accessible_france===true&&r.droits_verifies===true;});
    var n=0;ok.forEach(function(r){var c=carte(r);if(c){liste.appendChild(c);n++;}});
    var b=data.bilan||{};
    etat.textContent=n?(n+' lien'+(n>1?'s':'')+' VF vérifié'+(n>1?'s':'')+' · '+(b.candidat||0)+' encore à vérifier · contrôle du '+String(data.date||'').slice(0,10)+'.')
      :'Aucun lien VF n’est encore vérifié. Le contrôle automatique tourne chaque matin : les épisodes apparaîtront ici dès que leur VF sera prouvée.';
    if(n&&window.VMPlayer)window.VMPlayer();
  }).catch(function(){
    etat.textContent='Le premier contrôle automatique n’a pas encore eu lieu : revenez demain matin.';
  });
})();
