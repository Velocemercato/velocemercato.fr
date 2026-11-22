export const CREATION_STYLE = `
.compose{padding:clamp(18px,3vw,32px);background:linear-gradient(145deg,#1c2031,#11131d 72%);border:1px solid #3e4662;border-radius:20px;margin-bottom:14px;min-width:0}
.compose h1{font:600 clamp(28px,4.5vw,48px)/1.02 Georgia,serif;margin:0 0 9px;letter-spacing:-.034em}
.compose p{margin:8px 0 14px}.compose .intro{color:#c8cbda;max-width:44ch}.compose textarea{min-height:100px;resize:vertical}
.compose-tools,.compose-exemples,.preview-tools,.composition-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.compose-tools{margin-top:10px}.compose-tools button{margin:0}.compose-exemples button,.composition-actions button{font-size:13px;padding:8px 11px;margin:0}
.compose .note{font-size:12px;color:#bbc0d1;margin:7px 0}.compose [role=status]{margin:8px 0 0;font-size:14px;color:#f4cf55;overflow-wrap:anywhere}.compose [role=status]:empty{display:none}
.directions{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:9px 0 12px}
.direction{margin:0;width:100%;border:1px solid #464d62;border-radius:10px;padding:8px;background:#141724;color:#f4f5fa;text-align:left;line-height:1.25}
.direction[aria-pressed=true]{border-color:#f4cf55;outline:1px solid #f4cf55}.direction i{display:block;margin-bottom:5px;height:16px;border-radius:5px}.direction small{display:block;color:#bec3d4;margin-top:2px}
.composition-editor summary{cursor:pointer;padding:11px 0}.composition-editor label{margin-top:7px}
.composition-section{padding:10px 0;border-top:1px solid #383f56;min-width:0}.composition-actions{justify-content:flex-end}.composition-actions button:disabled{opacity:.45;cursor:default}
#apercu.is-phone{max-width:390px;margin-inline:auto}.preview-tools{justify-content:flex-end}.preview-tools button{margin:0}
.vm-designed{container-type:inline-size;isolation:isolate;color:var(--s-ink);overflow-wrap:anywhere;line-height:1.55}
.vm-designed .site-shell{width:min(100%,1100px);margin:auto;padding:clamp(14px,4.5cqi,56px)}
.vm-designed h1,.vm-designed h2,.vm-designed p{max-width:100%}
.vm-designed h1{font:var(--s-head);font-size:clamp(31px,8.5cqi,88px);line-height:.98;letter-spacing:-.06em;margin:0 0 16px;text-wrap:balance}
.vm-designed h2{font:var(--s-head);font-size:clamp(22px,4.15cqi,46px);line-height:1.07;letter-spacing:-.035em;margin:0 0 12px;text-wrap:balance}
.vm-designed p{margin:0;white-space:pre-wrap}.vm-designed a{color:inherit}.vm-designed img{display:block;max-width:100%;width:100%;object-fit:cover}
.vm-designed .site-hero{padding:clamp(18px,5.2cqi,65px);margin-bottom:clamp(18px,4.5cqi,42px);min-height:clamp(190px,34cqi,380px);display:grid;align-items:center;gap:clamp(14px,3cqi,36px);position:relative}
.vm-designed .site-hero-copy{z-index:1;min-width:0}.vm-designed .site-hero p{max-width:44ch;font-size:clamp(14px,2.4cqi,21px)}.vm-designed .site-hero img{height:100%;min-height:140px;max-height:430px}
.vm-designed .site-section{padding:clamp(16px,3.6cqi,44px) 0;border-top:1px solid color-mix(in srgb,var(--s-ink) 23%,transparent);position:relative}
.vm-designed .site-section p{max-width:65ch}.vm-designed .site-link{display:inline-block;margin-top:16px;padding:.7em 1.15em;border:1px solid currentColor;font-weight:700;text-decoration:none;border-radius:99px}
.vm-designed .site-items{display:grid;gap:9px;grid-template-columns:repeat(auto-fit,minmax(min(100%,140px),1fr));margin-top:16px}
.vm-designed .site-items div{padding:14px;background:color-mix(in srgb,var(--s-accent) 10%,transparent);border-top:2px solid var(--s-accent);display:grid;gap:4px}
.vm-designed .site-gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,130px),1fr));gap:10px}.vm-designed .site-gallery img{aspect-ratio:1}
.vm-designed .site-contact a{display:block;width:fit-content;margin-top:6px;text-underline-offset:3px}
.vm-designed.editorial{--s-head:500 1em Georgia,serif}.vm-designed.editorial .site-hero{border-block:1px solid currentColor;text-align:center;background:radial-gradient(ellipse at 50% 100%,color-mix(in srgb,var(--s-accent) 25%,transparent),transparent 72%)}
.vm-designed.editorial .site-hero p{margin-inline:auto}.vm-designed.editorial .site-hero img{border-radius:50% 50% 8px 8px}.vm-designed.editorial .site-link{border-radius:0}
.vm-designed.contraste{--s-head:850 1em system-ui,sans-serif}.vm-designed.contraste .site-hero{background:var(--s-accent);color:var(--s-on-accent);border-radius:3px 28px 3px 3px}
.vm-designed.contraste .site-hero h1{letter-spacing:-.075em}.vm-designed.contraste .site-items div{border:1px solid color-mix(in srgb,var(--s-accent) 40%,transparent)}
.vm-designed.atelier{--s-head:650 1em system-ui,sans-serif}.vm-designed.atelier .site-hero{border-radius:30px;background:linear-gradient(125deg,color-mix(in srgb,var(--s-accent) 17%,transparent),transparent);border:1px solid color-mix(in srgb,var(--s-accent) 28%,transparent)}
.vm-designed.atelier .site-hero img,.vm-designed.atelier .site-items div{border-radius:14px}.vm-designed.atelier .site-items div{border-top:0}
.vm-designed.manga,.vm-designed.dimension{--s-head:820 1em Impact,'Arial Black',system-ui,sans-serif}
.vm-designed.manga .site-hero,.vm-designed.dimension .site-hero{isolation:isolate;background:radial-gradient(circle at 86% 22%,color-mix(in srgb,var(--s-accent) 43%,transparent),transparent 49%),linear-gradient(125deg,#322449,#151022);border-radius:16px}
.vm-designed.manga .site-hero h1{text-transform:uppercase;text-shadow:3px 3px #000}
.vm-designed.dimension .site-hero{perspective:540px}
.vm-designed.dimension .site-hero::after{content:'';position:absolute;z-index:-1;top:16%;right:14%;width:30%;aspect-ratio:1;border:2px solid var(--s-accent);border-radius:16px;transform:rotateX(43deg) rotateY(-24deg) rotateZ(19deg);background:color-mix(in srgb,var(--s-accent) 18%,transparent)}
@container (min-width:460px){.vm-designed .site-hero.has-photo{grid-template-columns:1.08fr .92fr;text-align:left}.vm-designed .site-hero.photo-left{grid-template-columns:.92fr 1.08fr}.vm-designed .site-hero.photo-left img{order:-1}.vm-designed.editorial .site-hero.has-photo p{margin-inline:0}}
@media(max-width:860px){.studio>div:first-child{display:contents}.studio #composition{order:-2}.studio .apv{position:static;margin:0}.studio .apv .card{border-radius:14px}}
@media(max-width:760px){.compose{margin-top:0}.preview-tools{justify-content:flex-start}.direction small{display:none}}
`;

export const RENDU_CREATION = `
function dessinerSite(root,doc,accent,fond,texte){
 var wrap=E('div',''),shell=E('div','');wrap.className='vm-designed '+doc.style;shell.className='site-shell';
 var luminosite=[1,3,5].reduce(function(n,i,j){var v=parseInt(accent.slice(i,i+2),16)/255;return n+[.2126,.7152,.0722][j]*(v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4))},0);
 wrap.style.setProperty('--s-accent',accent);wrap.style.setProperty('--s-on-accent',luminosite>.179?'#101411':'#fff');wrap.style.setProperty('--s-ink',texte);wrap.style.background=fond;wrap.setAttribute('aria-label','Aperçu du site');root.appendChild(wrap);wrap.appendChild(shell);
 function lien(label,url){if(!label||!okLien(url))return null;var a=E('a','',label);a.className='site-link';a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a}
 function image(url,alt){if(!okImg(url))return null;var i=E('img');i.src=url;i.alt=alt||'';return i}
 var cible=doc.blocs.findIndex(function(b){return b&&(b.t==='produits'||b.t==='texte'||(b.t==='contact'&&(b.tel||b.email||b.adresse)))});
 doc.blocs.forEach(function(b,i){
  if(!b||b.t==='page')return;
  var s=E('section');s.className='site-section';s.setAttribute('data-bloc',i);
  if(b.t==='titre'){
   s.className='site-hero';var c=E('div');c.className='site-hero-copy';c.appendChild(E(i===0?'h1':'h2','',b.titre||'Votre activité'));if(b.sous)c.appendChild(E('p','',b.sous));
   var a=lien(b.bouton,b.lien);if(!a&&b.bouton&&cible>=0){a=E('a','',b.bouton);a.className='site-link';a.href='#'+root.id+'-section-'+cible;a.onclick=function(e){e.preventDefault();var n=shell.querySelector('[data-bloc="'+cible+'"]');if(n){n.focus({preventScroll:true});n.scrollIntoView({block:'nearest'})}}}
   if(a)c.appendChild(a);s.appendChild(c);var m=image(b.image,b.legende);if(m){s.classList.add('has-photo');if(b.pos==='gauche')s.classList.add('photo-left');s.appendChild(m)}
  }else if(b.t==='texte'){if(b.titre)s.appendChild(E('h2','',b.titre));if(b.texte)s.appendChild(E('p','',b.texte))}
  else if(b.t==='produits'){if(b.titre)s.appendChild(E('h2','',b.titre));var g=E('div');g.className='site-items';(Array.isArray(b.items)?b.items:[]).forEach(function(p){if(!p||typeof p!=='object')return;var r=E('div');r.appendChild(E('b','',p.nom));if(p.prix)r.appendChild(E('span','',p.prix));g.appendChild(r)});if(g.childElementCount)s.appendChild(g)}
  else if(b.t==='galerie'){var gal=E('div');gal.className='site-gallery';(Array.isArray(b.images)?b.images:[]).forEach(function(u){var im=image(u);if(im){im.loading='lazy';gal.appendChild(im)}});if(b.titre&&gal.childElementCount)s.appendChild(E('h2','',b.titre));if(gal.childElementCount)s.appendChild(gal)}
  else if(b.t==='image'){var im=image(b.src,b.legende);if(im){im.loading='lazy';s.appendChild(im)}if(b.legende)s.appendChild(E('p','',b.legende))}
  else if(b.t==='contact'){
   s.classList.add('site-contact');if(b.tel||b.email||b.adresse)s.appendChild(E('h2','',b.titre||'Contact'));
   [['tel','tel:'],['email','mailto:']].forEach(function(q){var v=typeof b[q[0]]==='string'?b[q[0]].trim():'';var a=lien(v,q[1]+v.replace(/\\s/g,''));if(a){a.className='';s.appendChild(a)}});
   if(b.adresse)s.appendChild(E('p','',b.adresse));
  }else if(b.t==='bouton'){var a=lien(b.texte,b.lien);if(a)s.appendChild(a)}
  if(s.childElementCount){s.id=root.id+'-section-'+i;s.tabIndex=-1;shell.appendChild(s)}
 })
}
function activerDictee(zone,bouton,etat){
 var Recon=window.SpeechRecognition||window.webkitSpeechRecognition;
 if(!Recon){bouton.hidden=true;return}
 var rec=null;
 bouton.onclick=function(){
   if(rec){rec.stop();return}
   var initial=zone.value.trim(), limite=zone.maxLength>0?zone.maxLength:1500;
   try{rec=new Recon();rec.lang='fr-FR';rec.interimResults=true;
     rec.onstart=function(){bouton.textContent='Arrêter la dictée';bouton.setAttribute('aria-pressed','true');etat.textContent='Dictée en cours…'};
     rec.onresult=function(e){var ajout=Array.from(e.results,function(r){return r[0].transcript}).join(' ');zone.value=[initial,ajout.trim()].filter(Boolean).join(' ').slice(0,limite)};
     rec.onerror=function(){etat.textContent='Micro indisponible. Vous pouvez écrire ou utiliser le micro de votre clavier.'};
     rec.onend=function(){rec=null;bouton.textContent='Dicter';bouton.setAttribute('aria-pressed','false');if(etat.textContent==='Dictée en cours…')etat.textContent='Relisez votre texte avant de continuer.'};
     rec.start()
   }catch(e){rec=null;etat.textContent='La dictée est indisponible dans ce navigateur.'}
 }
}
`;

export const FORMULAIRE_CREATION = `<section class="compose" id="composition" aria-labelledby="compositionTitre">
<h1 id="compositionTitre">À quoi doit ressembler votre site&nbsp;?</h1>
<p class="intro">Décrivez votre activité, le style que vous aimez et ce que vos visiteurs doivent pouvoir faire.</p>
<label for="brief">Votre brief</label>
<textarea id="brief" rows="4" maxlength="1500" placeholder="Un site pour mon atelier de vélos à Belfort. Du vert profond, mes services et un bouton pour prendre rendez-vous."></textarea>
<div class="compose-tools"><button type="button" class="p" id="proposerSite">Créer un aperçu</button><button type="button" class="g" id="dicter" aria-pressed="false">Dicter</button><button type="button" class="g hide" id="retourSite">Annuler la dernière version</button></div>
<p class="note">Le brief peut être traité par un outil de création automatisée. Gardez vos coordonnées pour le formulaire. La dictée utilise votre navigateur.</p>
<p id="compositionEtat" role="status"></p>
<details id="exemplesSite"><summary>Essayer une maquette de départ</summary>
<div class="compose-exemples"><button type="button" class="g" data-maquette="cafe">Café</button><button type="button" class="g" data-maquette="velo">Atelier vélo</button><button type="button" class="g" data-maquette="interieur">Architecture d’intérieur</button></div>
<p class="note">Ces maquettes utilisent des exemples fictifs que vous pouvez remplacer.</p></details>
<div id="editionSite" class="hide">
<p>Choisir une direction visuelle</p><div class="directions" id="directions" role="group" aria-label="Direction visuelle"></div>
<details class="composition-editor"><summary>Modifier les sections à la main</summary>
<div id="sectionsSite"></div>
<label for="galerieSite">Photos de la galerie (6 maximum)</label><input id="galerieSite" type="file" accept="image/png,image/jpeg,image/webp" multiple>
<div class="composition-actions"><button type="button" class="g hide" id="effacerGalerie">Retirer la galerie</button></div>
<label for="telSite">Téléphone à afficher sur le site</label><input id="telSite" type="tel" maxlength="40">
<label for="mailSite">E-mail à afficher sur le site</label><input id="mailSite" type="email" maxlength="120">
<label for="adresseSite">Adresse ou horaires à afficher</label><textarea id="adresseSite" rows="2" maxlength="300"></textarea>
<div class="composition-actions"><button type="button" class="g" id="ajouterTexte">Ajouter une section</button><button type="button" class="g" id="ajouterOffre">Ajouter des services</button></div>
</details>
</div></section>`;

export const SCRIPT_CREATION = String.raw`
var maquette=null, galerieSite=[], versions=[], revision=0;
var COULEURS=['c1','c2','fond','texte'];
var etatSite=$('compositionEtat'), brief=$('brief'), boutonSite=$('proposerSite');
function paletteSite(c){COULEURS.forEach(function(k){if(/^#[a-f0-9]{6}$/i.test(c[k]||''))$(k).value=c[k]})}
function memoriserSite(){versions.push({maquette:maquette?structuredClone(maquette):null, galerie:galerieSite.slice(), nom:$('nom').value, slogan:$('slogan').value,
 theme:Object.fromEntries(COULEURS.map(function(k){return [k,$(k).value]}))});if(versions.length>12)versions.shift()}
function rafraichirSite(){
 $('effacerGalerie').classList.toggle('hide',!galerieSite.length);
 $('editionSite').classList.toggle('hide',!maquette);$('retourSite').classList.toggle('hide',!versions.length);
 boutonSite.textContent=maquette?'Proposer une retouche':'Créer un aperçu';
 brief.placeholder=maquette?'Par exemple : raccourcis l’accroche et présente d’abord les prestations.':'Un site pour mon atelier de vélos à Belfort. Du vert profond, mes services et un bouton de rendez-vous.';
 Object.keys(DIRECTIONS).forEach(function(k){$('direction-'+k).setAttribute('aria-pressed',String(!!maquette&&maquette.style===k))});
 dessinerSections();maj()
}
function prendreSite(doc){
 memoriserSite();revision++;maquette=structuredClone(doc);
 var titre=maquette.blocs.find(function(b){return b.t==='titre'});
 if(titre){$('nom').value=(titre.titre||'').slice(0,60);$('slogan').value=(titre.sous||'').slice(0,120)}
 paletteSite(maquette.theme||DIRECTIONS[maquette.style]);rafraichirSite()
}
$('retourSite').onclick=function(){
 var v=versions.pop();if(!v)return;revision++;maquette=v.maquette;galerieSite=v.galerie;$('nom').value=v.nom;$('slogan').value=v.slogan;paletteSite(v.theme);
 etatSite.textContent='Version précédente rétablie.';rafraichirSite()
};
Array.from(document.querySelectorAll('[data-maquette]')).forEach(function(b){
 b.onclick=function(){prendreSite(EXEMPLES_SITE[b.dataset.maquette]);etatSite.textContent='Maquette chargée. Vous pouvez modifier ses textes ou demander une retouche.'}
});
Object.keys(DIRECTIONS).forEach(function(k){
 var d=DIRECTIONS[k],b=E('button');b.id='direction-'+k;b.type='button';b.className='direction';b.setAttribute('aria-pressed','false');
 var sw=E('i');sw.style.background='linear-gradient(110deg,'+d.fond+' 52%,'+d.c1+' 52%)';sw.setAttribute('aria-hidden','true');
 b.append(sw,E('b','',d.nom),E('small','',d.description));$('directions').appendChild(b);
 b.onclick=function(){if(!maquette)return;memoriserSite();maquette.style=k;paletteSite(d);revision++;rafraichirSite();etatSite.textContent='Direction « '+d.nom+' » appliquée.'}
});
function contenuSite(){
 var blocs=structuredClone(maquette.blocs),titre=blocs.find(function(b){return b.t==='titre'});
 if(titre){titre.titre=$('nom').value||'Votre activité';titre.sous=$('slogan').value;if(photo)titre.image=photo}
 // Les coordonnées du devis ne sont jamais copiées dans le site.
 if(galerieSite.length)blocs.push({t:'galerie',titre:'Galerie',images:galerieSite.slice()});
 var contact={t:'contact',titre:'Contact',tel:$('telSite').value.trim(),email:$('mailSite').value.trim(),adresse:$('adresseSite').value.trim()};
 if(contact.tel||contact.email||contact.adresse)blocs.push(contact);
 return blocs
}
function dessinerSections(){
 var zone=$('sectionsSite');zone.replaceChildren();if(!maquette)return;
 function champ(parent,nom,val,max,changer,long){
   var lab=E('label','',nom),f=E(long?'textarea':'input');f.value=val||'';f.maxLength=max;if(long)f.rows=3;
   f.addEventListener('focus',function(){memoriserSite();$('retourSite').classList.remove('hide')},{once:true});
   f.addEventListener('input',function(){changer(f.value)});lab.appendChild(f);parent.appendChild(lab)
 }
 maquette.blocs.forEach(function(b,i){
  if(!['texte','produits','titre','bouton'].includes(b.t))return;
  var c=E('div');c.className='composition-section';zone.appendChild(c);
  if(b.t==='titre'){
   c.appendChild(E('b','','En-tête'));
   c.appendChild(E('p','','Le nom, l’accroche et la photo principale se modifient dans « Vos informations ».'));
   champ(c,'Texte du bouton',b.bouton,80,function(v){b.bouton=v});
   champ(c,'Lien du bouton (facultatif)',b.lien,500,function(v){b.lien=v.trim()});
   return
  }
  var actions=E('div');actions.className='composition-actions';c.appendChild(actions);
  var n=b.t==='bouton'?'Bouton':b.t==='produits'?'Services ou produits':'Texte';
  [['Monter',-1],['Descendre',1],['Retirer',0]].forEach(function(action){
   var bouton=E('button','',action[0]);bouton.className='g';bouton.type='button';bouton.setAttribute('aria-label',action[0]+' la section '+(b.titre||n));
   bouton.disabled=(action[1]===-1&&i<=1)||(action[1]===1&&i>=maquette.blocs.length-1);
   bouton.onclick=function(){memoriserSite();var l=maquette.blocs;if(action[1]){var p=i+action[1];[l[p],l[i]]=[l[i],l[p]]}else l.splice(i,1);revision++;rafraichirSite()};actions.appendChild(bouton)
  });
  if(b.t==='bouton'){champ(c,'Texte du bouton',b.texte,80,function(v){b.texte=v});champ(c,'Adresse du lien',b.lien,500,function(v){b.lien=v.trim()});return}
  champ(c,'Titre de la section',b.titre,120,function(v){b.titre=v});
  if(b.t==='texte')champ(c,'Texte',b.texte,2000,function(v){b.texte=v},true);
  if(b.t==='produits')champ(c,'Une ligne par service ou produit', (b.items||[]).map(function(p){return p.nom+(p.prix?' | '+p.prix:'')}).join('\n'),900,function(v){
   b.items=v.split('\n').map(function(l){var p=l.split('|');return{nom:p[0].trim().slice(0,120),prix:(p[1]||'').trim().slice(0,40)}}).filter(function(p){return p.nom}).slice(0,12)
  },true)
 })
}
function ajouterSection(type){
 if(!maquette||maquette.blocs.length>=18){etatSite.textContent='Vous avez atteint la limite de sections de cet aperçu.';return}
 memoriserSite();maquette.blocs.push(type==='texte'?{t:'texte',titre:'Nouvelle section',texte:''}:{t:'produits',titre:'Nos services',items:[]});revision++;rafraichirSite();
 var champs=$('sectionsSite').querySelectorAll('.composition-section');champs[champs.length-1].querySelector('input').focus()
}
$('ajouterTexte').onclick=function(){ajouterSection('texte')};$('ajouterOffre').onclick=function(){ajouterSection('produits')};
$('galerieSite').onchange=function(){
 var f=Array.from(this.files).slice(0,6);this.value='';if(!f.length)return;
 var base=revision;
 Promise.all(f.map(function(fichier){return new Promise(function(resolve){reduirePhoto(fichier,700,resolve)})})).then(function(photos){
  if(!maquette||base!==revision)return;
  memoriserSite();galerieSite=photos.filter(Boolean);revision++;rafraichirSite();
  etatSite.textContent=galerieSite.length?'Galerie mise à jour.':'Ces images ne peuvent pas être ouvertes.'
 })
};
$('effacerGalerie').onclick=function(){memoriserSite();galerieSite=[];revision++;rafraichirSite()};
activerDictee(brief,$('dicter'),etatSite);
document.addEventListener('input',function(e){if(e.target!==brief)revision++});
boutonSite.onclick=async function(){
 var texte=brief.value.trim();if(texte.length<8){etatSite.textContent='Décrivez en quelques mots ce que vous souhaitez.';brief.focus();return}
 var base=revision;boutonSite.disabled=true;boutonSite.setAttribute('aria-busy','true');etatSite.textContent='Préparation de votre aperçu…';
 try{
  var courant=maquette?{style:maquette.style,theme:DOCC.theme,blocs:contenuSite().filter(function(b){return b.t!=='galerie'&&b.t!=='contact'}).map(function(b){
   var c=Object.assign({},b);delete c.image;delete c.src;delete c.images;delete c.tel;delete c.email;delete c.adresse;return c
  })}:null;
  var j=await api('studio/proposer',{brief:texte,projet:courant});
  if(!j.ok){etatSite.textContent=j.message||'La création est indisponible. Essayez une des maquettes de départ.';return}
  if(base!==revision){etatSite.textContent='Votre aperçu a changé entre-temps. Relancez la demande pour partir de cette version.';return}
  prendreSite(j.doc);if(brief.value.trim()===texte)brief.value='';etatSite.textContent=j.explication||'Nouvel aperçu prêt. Vous pouvez continuer à le retoucher.'
 }catch(e){etatSite.textContent='Connexion interrompue. Réessayez ou partez d’une maquette.'}
 finally{boutonSite.disabled=false;boutonSite.removeAttribute('aria-busy')}
};
$('mobileApercu').onclick=function(){var oui=$('apercu').classList.toggle('is-phone');$('mobileApercu').setAttribute('aria-pressed',String(oui));$('mobileApercu').textContent=oui?'Pleine largeur':'Aperçu mobile'};
`;
