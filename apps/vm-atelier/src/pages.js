import { PRIX, devis } from './prix.js';

// ---------- Styles communs de l'interface VM ----------
const CSS = `:root{--bg:#07080d;--card:#11131d;--line:#2b3046;--txt:#f3f4f8;--muted:#a9b0c4;--gold:#f4cf55;--red:#e52643;--ok:#3ccf7a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
header.vm{padding:14px 16px;border-bottom:2px solid var(--red);display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
header.vm h1{margin:0;font-size:1.25rem}.test{background:var(--gold);color:#111;border-radius:999px;padding:2px 9px;font-weight:800;font-size:.72rem}
a{color:var(--gold)}.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px;margin:0 0 12px}
label{display:block;font-weight:700;margin:10px 0 4px;font-size:.88rem}
input,textarea,select{width:100%;background:#0b0d16;color:var(--txt);border:1px solid var(--line);border-radius:9px;padding:9px;font:inherit}
input[type=checkbox]{width:auto;margin-right:6px}input[type=color]{height:40px;padding:2px}
button{cursor:pointer;border:0;border-radius:10px;padding:10px 14px;font-weight:800;margin:4px 4px 4px 0;font:inherit;font-weight:800}
.p{background:var(--gold);color:#111}.g{background:#1b2033;color:var(--txt)}.r{background:#3a1520;color:#ffb3bf}
.muted{color:var(--muted);font-size:.85rem}.msg{color:var(--gold);min-height:1.2em}.hide{display:none!important}
.grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;padding:16px;max-width:1300px;margin:auto}
@media(max-width:860px){.grid{grid-template-columns:1fr}}
.row{display:grid;grid-template-columns:1fr 1fr;gap:8px}.code{font:700 1.15rem ui-monospace,monospace;background:#000;border:1px dashed var(--gold);padding:10px;border-radius:9px;word-break:break-all}
.ligne{display:flex;justify-content:space-between;gap:8px;border-bottom:1px dashed var(--line);padding:5px 0}.total{font-size:1.5rem;font-weight:900;color:var(--gold);text-align:right}
.ecran{border:1px solid var(--line);border-radius:14px;overflow:hidden;min-height:420px}
.legal{color:var(--muted);font-size:.78rem;text-align:center;padding:14px}`;

// ---------- Rendu d'un projet (identique partout : studio, atelier, salon, consultation) ----------
// Tout le texte passe par textContent ; liens https/mailto/tel seulement ; images https ou data:image.
const RENDU = `
function okLien(u){try{var x=new URL(u);return ['https:','mailto:','tel:'].indexOf(x.protocol)>=0&&!x.username&&!x.password}catch(e){return false}}
function okImg(u){return typeof u==='string'&&(/^data:image\\/(png|jpeg|webp|gif);base64,[A-Za-z0-9+\\/=]+$/.test(u)||/^https:\\/\\/[^\\s"'()]+$/.test(u))}
function okCoul(c,d){return /^#[0-9a-f]{6}$/i.test(c||'')?c:d}
function E(t,css,x){var e=document.createElement(t);if(css)e.style.cssText=css;if(x!=null)e.textContent=String(x);return e}
function rendre(root,doc){
 doc=doc||{};var th=doc.theme||{},c1=okCoul(th.c1,'#e52643'),c2=okCoul(th.c2,'#f4cf55'),bg=okCoul(th.fond,'#0b0c12'),tx=okCoul(th.texte,'#ffffff');
 root.replaceChildren();root.style.cssText='background:'+bg+';color:'+tx+';font:16px/1.55 system-ui,sans-serif;min-height:100%';
 var w=E('div','max-width:720px;margin:auto;padding:22px 16px');root.appendChild(w);
 var blocs=Array.isArray(doc.blocs)?doc.blocs:[];
 if(!blocs.length){w.appendChild(E('p','opacity:.55;text-align:center;padding:90px 0','Page vierge : le site apparaît ici.'));return}
 blocs.forEach(function(b){if(!b||typeof b!=='object')return;var s=E('section','margin:0 0 22px');
  if(b.t==='titre'){s.style.textAlign='center';if(okImg(b.image)){var i=E('img','width:100%;max-height:340px;object-fit:cover;border-radius:16px;border:3px solid '+c2);i.src=b.image;i.alt='';s.appendChild(i)}
   s.appendChild(E('h1','margin:14px 0 4px;font-size:2rem;color:'+tx,b.titre||''));if(b.sous)s.appendChild(E('p','margin:0;opacity:.85',b.sous));
   if(b.bouton&&okLien(b.lien)){var a=E('a','display:inline-block;margin-top:12px;background:'+c1+';color:#fff;border-radius:12px;padding:11px 18px;text-decoration:none;font-weight:800',b.bouton);a.href=b.lien;a.target='_blank';a.rel='noopener';s.appendChild(a)}}
  else if(b.t==='texte'){if(b.titre)s.appendChild(E('h2','margin:0 0 6px;color:'+c2,b.titre));s.appendChild(E('p','margin:0;white-space:pre-wrap',b.texte||''))}
  else if(b.t==='image'){if(okImg(b.src)){var im=E('img','width:100%;border-radius:14px');im.src=b.src;im.alt=b.legende||'';s.appendChild(im)}if(b.legende)s.appendChild(E('p','margin:6px 0 0;opacity:.75;text-align:center;font-size:.9rem',b.legende))}
  else if(b.t==='galerie'){var g=E('div','display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px');(b.images||[]).forEach(function(u){if(okImg(u)){var x=E('img','width:100%;aspect-ratio:1;object-fit:cover;border-radius:10px');x.src=u;x.alt='';g.appendChild(x)}});s.appendChild(g)}
  else if(b.t==='produits'){if(b.titre)s.appendChild(E('h2','margin:0 0 8px;color:'+c2,b.titre));(b.items||[]).forEach(function(p){var r=E('div','display:flex;justify-content:space-between;gap:10px;align-items:center;border:2px solid '+c1+';border-radius:12px;padding:12px;margin:8px 0');r.appendChild(E('b','',p.nom||''));r.appendChild(E('span','color:'+c2+';font-weight:900',p.prix||''));s.appendChild(r)})}
  else if(b.t==='contact'){s.style.cssText+='border-top:2px solid '+c1+';padding-top:12px;text-align:center';s.appendChild(E('h2','margin:0 0 6px;color:'+c2,b.titre||'Contact'));
   [['tel','tel:'],['email','mailto:']].forEach(function(k){var v=(b[k[0]]||'').trim();if(v){var a=E('a','display:block;color:'+tx,v);var h=k[1]+v.replace(/\\s/g,'');if(okLien(h))a.href=h;s.appendChild(a)}});
   if(b.adresse)s.appendChild(E('p','margin:6px 0 0;opacity:.8;white-space:pre-wrap',b.adresse))}
  else if(b.t==='bouton'){s.style.textAlign='center';var bt=E('a','display:inline-block;background:'+c1+';color:#fff;border-radius:12px;padding:12px 20px;text-decoration:none;font-weight:800',b.texte||'');if(okLien(b.lien)){bt.href=b.lien;bt.target='_blank';bt.rel='noopener'}s.appendChild(bt)}
  w.appendChild(s)})}
function reduirePhoto(f,max,cb){var r=new FileReader();r.onload=function(){var im=new Image();im.onload=function(){var k=Math.min(1,max/Math.max(im.width,im.height)),c=document.createElement('canvas');c.width=Math.round(im.width*k);c.height=Math.round(im.height*k);c.getContext('2d').drawImage(im,0,0,c.width,c.height);cb(c.toDataURL('image/jpeg',0.8))};im.src=r.result};r.readAsDataURL(f)}
function api(p,body){return fetch('/api/'+p,body?{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body),credentials:'same-origin'}:{credentials:'same-origin'}).then(function(r){return r.json().then(function(j){j._s=r.status;return j})})}
`;

function page(titre, corps, script) {
  return `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>${titre}</title><style>${CSS}</style></head><body>${corps}
<script>(function(){'use strict';${RENDU}${script}})();</script></body></html>`;
}
const ENTETE = (sous) => `<header class="vm"><h1>VM Studio <span class="test">MODE TEST</span></h1><span class="muted">${sous}</span></header>`;
const PIED = `<p class="legal">VM Studio · Véloce Mercato — prototype en mode test : aucune commande n'est facturée automatiquement.</p>`;

// ---------- Accueil ----------
export const pageAccueil = page('VM Studio', `${ENTETE('Création de sites')}
<main style="max-width:700px;margin:auto;padding:16px">
 <div class="card"><h2 style="margin-top:0">🧩 Créer mon site</h2><p class="muted">Composez votre site, voyez le prix en direct, envoyez votre demande.</p><a href="/studio"><button class="p">Commencer</button></a></div>
 <div class="card"><h2 style="margin-top:0">🔑 Voir mon projet</h2><p class="muted">Vous avez reçu un code à usage unique ?</p><a href="/voir"><button class="g">Entrer mon code</button></a></div>
</main>${PIED}`, '');

// ---------- Studio client : configuration + prix en direct + commande ----------
const cases = Object.entries(PRIX.options).map(([k, o]) =>
  `<label style="font-weight:400"><input type="checkbox" class="opt" value="${k}">${o.nom} <b>+${o.prix} €</b></label>`).join('');
const types = Object.entries(PRIX.types).map(([k, t]) => `<option value="${k}">${t.nom} — ${t.prix} €</option>`).join('');

export const pageStudio = page('Créer mon site — VM Studio', `${ENTETE('Votre site en quelques minutes')}
<div class="grid"><div>
 <div class="card"><h2 style="margin-top:0">1. Votre site</h2>
  <label for="nom">Nom de votre activité</label><input id="nom" maxlength="60" placeholder="Ex. : Salon Léa Coiffure">
  <label for="slogan">Phrase d'accroche</label><input id="slogan" maxlength="120" placeholder="Ex. : Coiffure femme et homme à Limoges">
  <label for="photo">Photo principale (facultatif)</label><input id="photo" type="file" accept="image/*">
  <div class="row"><div><label for="c1">Couleur principale</label><input id="c1" type="color" value="#e52643"></div><div><label for="c2">Couleur d'accent</label><input id="c2" type="color" value="#f4cf55"></div></div>
  <div class="row"><div><label for="fond">Fond</label><input id="fond" type="color" value="#0b0c12"></div><div><label for="texte">Texte</label><input id="texte" type="color" value="#ffffff"></div></div>
 </div>
 <div class="card"><h2 style="margin-top:0">2. Formule et options</h2>
  <label for="type">Formule</label><select id="type">${types}</select>
  <div class="row"><div><label for="pages">Pages en plus (+${PRIX.pageSup.prix} € chacune)</label><input id="pages" type="number" min="0" max="${PRIX.pageSup.max}" value="0"></div>
  <div><label for="langues">Langues en plus (+${PRIX.langue.prix} € chacune)</label><input id="langues" type="number" min="0" max="${PRIX.langue.max}" value="0"></div></div>
  <label>Créations</label>${cases}
  <label style="font-weight:400"><input type="checkbox" id="pack" checked>${PRIX.pack.nom} <b>+${PRIX.pack.prix} €</b></label>
  <p class="muted">Le pack 3 ans se paie en une fois. Le nom de domaine est enregistré au nom du client ; VM Studio s'occupe de tout pendant 3 ans.</p>
 </div>
 <div class="card"><h2 style="margin-top:0">3. Votre panier</h2><div id="lignes"></div><div class="total" id="total">0 €</div>
  <p class="muted">Prix TTC indicatif. Rien n'est payé maintenant : on vous recontacte pour valider, puis vous recevez un lien de paiement sécurisé.</p>
 </div>
 <div class="card"><h2 style="margin-top:0">4. Vos coordonnées</h2>
  <label for="cnom">Nom et prénom</label><input id="cnom" maxlength="80" autocomplete="name">
  <div class="row"><div><label for="cmail">E-mail</label><input id="cmail" type="email" maxlength="120" autocomplete="email"></div><div><label for="ctel">Téléphone</label><input id="ctel" type="tel" maxlength="40" autocomplete="tel"></div></div>
  <label for="cmsg">Votre demande (ce que vous voulez, vos idées)</label><textarea id="cmsg" rows="4" maxlength="1500"></textarea>
  <label style="font-weight:400"><input type="checkbox" id="cgv">J'accepte d'être recontacté au sujet de cette demande. Mes coordonnées ne servent qu'à ce projet.</label>
  <button class="p" id="envoyer">Envoyer ma demande</button><p class="msg" id="msg" role="status"></p>
  <p class="muted" id="joindre"></p>
 </div>
</div><div><div class="card" style="position:sticky;top:10px"><b>Aperçu de votre site</b><div class="ecran" id="apercu" style="margin-top:8px"></div></div></div></div>${PIED}`,
`var PRIX=${JSON.stringify(PRIX)};${devis.toString()}
var $=function(i){return document.getElementById(i)},photo='';
function cfg(){return{type:$('type').value,pages:$('pages').value,langues:$('langues').value,options:[].map.call(document.querySelectorAll('.opt:checked'),function(c){return c.value}),pack:$('pack').checked}}
function maj(){var d=devis(cfg()),L=$('lignes');L.replaceChildren();d.lignes.forEach(function(l){var r=E('div');r.className='ligne';r.appendChild(E('span','',l[0]));r.appendChild(E('b','',l[1]+' €'));L.appendChild(r)});$('total').textContent=d.total+' €';
 var blocs=[{t:'titre',titre:$('nom').value||'Votre activité',sous:$('slogan').value,image:photo}];
 if(d.type==='rendezvous')blocs.push({t:'bouton',texte:'📅 Prendre rendez-vous',lien:'https://example.com'});
 if(d.type==='boutique')blocs.push({t:'produits',titre:'Boutique',items:[{nom:'Produit 1',prix:'29 €'},{nom:'Produit 2',prix:'49 €'}]});
 blocs.push({t:'texte',titre:'À propos',texte:'Votre présentation apparaîtra ici.'});
 if(d.pages)blocs.push({t:'texte',titre:'+ '+d.pages+' page(s)',texte:'Pages supplémentaires : services, galerie, tarifs…'});
 blocs.push({t:'contact',titre:'Contact',tel:$('ctel').value,email:$('cmail').value});
 rendre($('apercu'),{theme:{c1:$('c1').value,c2:$('c2').value,fond:$('fond').value,texte:$('texte').value},blocs:blocs})}
document.addEventListener('input',maj);document.addEventListener('change',maj);
$('photo').onchange=function(){var f=this.files[0];if(f)reduirePhoto(f,1000,function(u){photo=u;maj()})};
$('envoyer').onclick=function(){$('msg').textContent='Envoi…';api('commande',{config:cfg(),cgv:$('cgv').checked,contact:{nom:$('cnom').value,email:$('cmail').value,tel:$('ctel').value,message:$('cmsg').value,projet:$('nom').value}}).then(function(j){
 var E2={contact_incomplet:'Indiquez votre nom et un e-mail ou un téléphone.',conditions_non_acceptees:'Cochez la case pour accepter d’être recontacté.',trop_de_commandes:'Trop de demandes, réessayez plus tard.'};
 $('msg').textContent=j.ok?'✅ Demande n° '+j.id+' envoyée ('+j.total+' €). Nous vous recontactons très vite.':(E2[j.error]||'Erreur, réessayez.')})};
api('config').then(function(c){var t=[];if(c.tel)t.push('📞 '+c.tel);if(c.email)t.push('✉️ '+c.email);if(t.length)$('joindre').textContent='Une question avant de valider ? '+t.join(' · ')});
maj();`);

// ---------- Mode salon : le client voit le site se construire en direct ----------
export const pageSalon = page('Votre site — en direct', `<div id="site"></div>
<div id="live" style="position:fixed;bottom:10px;right:10px;background:#000c;color:#fff;border-radius:999px;padding:5px 11px;font:700 12px system-ui">● en direct</div>`,
`var tok=location.pathname.split('/').pop(),v=0,el=document.getElementById('site'),live=document.getElementById('live');
function boucle(){fetch('/api/salon/'+tok+'?v='+v,{cache:'no-store'}).then(function(r){return r.json()}).then(function(j){
 if(j.error){live.textContent='lien expiré';live.style.background='#a00';return}live.style.background='#0a0c';if(!j.same){v=j.v;document.title=j.nom||'Votre site';rendre(el,j.doc)}setTimeout(boucle,1500)})
 .catch(function(){live.style.background='#a60c';setTimeout(boucle,4000)})}
rendre(el,{blocs:[]});boucle();`);

// ---------- Consultation avec code à usage unique ----------
export const pageVoir = page('Voir mon projet', `<div id="porte">${ENTETE('Consultation sécurisée')}
<main style="max-width:520px;margin:auto;padding:16px"><div class="card"><h2 style="margin-top:0">🔑 Votre code</h2>
<p class="muted">Ce code ne fonctionne <b>qu'une seule fois</b>. Dès que vous fermez ou rechargez la page, l'accès se termine ; demandez alors un nouveau code.</p>
<input id="code" maxlength="40" autocomplete="off" placeholder="Code reçu" style="text-transform:uppercase"><button class="p" id="ok">Voir mon projet</button><p class="msg" id="msg" role="status"></p></div></main></div>
<div id="site" class="hide"></div>
<div id="bandeau" class="hide" style="position:fixed;bottom:0;left:0;right:0;background:#000d;color:#fff;text-align:center;padding:7px;font:13px system-ui">Consultation unique : l'accès se termine à la fermeture de cette page.</div>`,
`var $=function(i){return document.getElementById(i)};
$('ok').onclick=function(){$('msg').textContent='…';api('voir/ouvrir',{code:$('code').value}).then(function(j){
 if(!j.ok){$('msg').textContent=j.error==='trop_de_tentatives'?'Trop d’essais, réessayez dans une heure.':'Code invalide, déjà utilisé ou expiré.';return}
 $('porte').classList.add('hide');$('site').classList.remove('hide');$('bandeau').classList.remove('hide');document.title=j.nom||'Votre projet';rendre($('site'),j.doc);
 window.addEventListener('pagehide',function(){navigator.sendBeacon('/api/voir/fermer')})})};`);

// ---------- VM Studio · Atelier de Romain ----------
const TYPES_BLOCS = { titre: '🏷 Titre + photo', texte: '📝 Texte', image: '🖼 Image', galerie: '🧱 Galerie', produits: '🛒 Produits / tarifs', bouton: '🔘 Bouton', contact: '📞 Contact' };
export const pageAdmin = page('Atelier — VM', `${ENTETE('VM Studio · Atelier de Romain')}
<div id="login" class="card" style="max-width:420px;margin:16px auto"><label for="tok">Code administrateur</label><input id="tok" type="password" autocomplete="off"><button class="p" id="entrer">Entrer</button><p class="msg" id="lmsg"></p></div>
<div id="app" class="hide">
 <div style="padding:10px 16px"><button class="g" id="ongProjets">📁 Projets</button><button class="g" id="ongCmd">🧾 Commandes</button></div>
 <div id="vProjets" style="padding:0 16px"><div class="card"><div class="row"><input id="npNom" placeholder="Nom du projet" maxlength="80"><input id="npClient" placeholder="Client" maxlength="80"></div><button class="p" id="creer">+ Nouveau projet (page vierge)</button></div><div id="liste"></div></div>
 <div id="vCmd" class="hide" style="padding:0 16px"><div id="cmds"></div></div>
 <div id="vEdit" class="hide"><div class="grid"><div>
  <div class="card"><button class="g" id="retour">← Projets</button> <b id="eNom"></b> <span class="muted" id="etat"></span>
   <label for="eTitre">Nom du projet</label><input id="eTitre" maxlength="80">
   <div class="row"><div><label>Couleur principale</label><input type="color" id="tc1"></div><div><label>Accent</label><input type="color" id="tc2"></div></div>
   <div class="row"><div><label>Fond</label><input type="color" id="tfond"></div><div><label>Texte</label><input type="color" id="ttexte"></div></div></div>
  <div class="card"><b>Partager</b><br>
   <button class="p" id="bSalon">📱 Lien « salon » (en direct)</button><button class="p" id="bCode">🔑 Code à usage unique</button><button class="g" id="bNvSalon">♻️ Couper l'ancien lien salon</button><button class="r" id="bSuppr">Supprimer</button>
   <div id="partage"></div></div>
  <div class="card"><b>Ajouter un bloc</b><br>${Object.entries(TYPES_BLOCS).map(([k, n]) => `<button class="g add" data-t="${k}">${n}</button>`).join('')}</div>
  <div id="blocs"></div>
 </div><div><div class="card" style="position:sticky;top:10px"><b>Ce que voit le client</b><div class="ecran" id="apercu" style="margin-top:8px"></div></div></div></div></div>
</div>`,
`var $=function(i){return document.getElementById(i)},cur=null,minuteur=null,TB=${JSON.stringify(TYPES_BLOCS)};
function vue(n){['vProjets','vCmd','vEdit'].forEach(function(x){$(x).classList.toggle('hide',x!==n)})}
function etat(){api('admin/etat').then(function(s){if(s._s===401){$('login').classList.remove('hide');$('app').classList.add('hide');return}
 $('login').classList.add('hide');$('app').classList.remove('hide');
 var L=$('liste');L.replaceChildren();(s.projets||[]).forEach(function(p){var c=E('div');c.className='card';c.appendChild(E('b','',p.nom));c.appendChild(E('div','',(p.client?'Client : '+p.client+' · ':'')+'modifié le '+new Date(p.maj).toLocaleString('fr-FR')));c.lastChild.className='muted';
  var o=E('button','','✏️ Ouvrir');o.className='p';o.onclick=function(){ouvrir(p.id)};c.appendChild(o);L.appendChild(c)});
 var C=$('cmds');C.replaceChildren();if(!(s.commandes||[]).length)C.appendChild(E('p','','Aucune commande pour le moment.'));
 (s.commandes||[]).forEach(function(k){var c=E('div');c.className='card';c.appendChild(E('b','','N° '+k.id+' · '+k.total+' € · '+new Date(k.cree).toLocaleString('fr-FR')));
  var ct=k.contact||{};c.appendChild(E('div','',(ct.nom||'')+' · '+(ct.email||'')+' · '+(ct.tel||'')+(ct.projet?' · Projet : '+ct.projet:'')));
  if(ct.message)c.appendChild(E('p','white-space:pre-wrap',ct.message));
  ((k.config||{}).lignes||[]).forEach(function(l){var r=E('div');r.className='ligne';r.appendChild(E('span','',l[0]));r.appendChild(E('b','',l[1]+' €'));c.appendChild(r)});
  var sel=E('select','width:auto;margin-top:8px');['nouvelle','validee','payee','livree','annulee'].forEach(function(x){var o=E('option','',x);o.value=x;if(x===k.statut)o.selected=true;sel.appendChild(o)});
  sel.onchange=function(){api('admin/statut',{id:k.id,statut:sel.value})};c.appendChild(sel);
  var b=E('button','','➕ Créer le projet');b.className='g';b.onclick=function(){api('admin/creer',{nom:ct.projet||('Commande '+k.id),client:ct.nom}).then(function(j){if(j.ok)ouvrir(j.id)})};c.appendChild(b);C.appendChild(c)})})}
$('entrer').onclick=function(){api('admin/login',{token:$('tok').value}).then(function(j){$('lmsg').textContent=j.ok?'':(j.error==='admin_non_configure'?'Le secret ADMIN_TOKEN n’est pas encore défini dans Cloudflare.':'Refusé.');if(j.ok){$('tok').value='';etat()}})};
$('ongProjets').onclick=function(){vue('vProjets');etat()};$('ongCmd').onclick=function(){vue('vCmd');etat()};$('retour').onclick=function(){vue('vProjets');etat()};
$('creer').onclick=function(){api('admin/creer',{nom:$('npNom').value,client:$('npClient').value}).then(function(j){if(j.ok){$('npNom').value='';$('npClient').value='';ouvrir(j.id)}})};
function ouvrir(id){api('admin/lire?id='+encodeURIComponent(id)).then(function(p){if(p.error)return;cur=p;$('partage').replaceChildren();$('eNom').textContent=p.nom;$('eTitre').value=p.nom;
 var t=p.doc.theme||{};$('tc1').value=t.c1||'#e52643';$('tc2').value=t.c2||'#f4cf55';$('tfond').value=t.fond||'#0b0c12';$('ttexte').value=t.texte||'#ffffff';vue('vEdit');dessiner()})}
function sauver(){$('etat').textContent='…';clearTimeout(minuteur);minuteur=setTimeout(function(){api('admin/enregistrer',{id:cur.id,nom:$('eTitre').value,doc:cur.doc}).then(function(j){$('etat').textContent=j.ok?'✔ enregistré (le client le voit)':'⚠ '+(j.error||'erreur')})},500)}
['tc1','tc2','tfond','ttexte'].forEach(function(i){$(i).oninput=function(){cur.doc.theme={c1:$('tc1').value,c2:$('tc2').value,fond:$('tfond').value,texte:$('ttexte').value};rendre($('apercu'),cur.doc);sauver()}});
$('eTitre').oninput=sauver;
[].forEach.call(document.querySelectorAll('.add'),function(b){b.onclick=function(){var t=b.getAttribute('data-t'),n={t:t};
 if(t==='produits')n.items=[{nom:'',prix:''}];if(t==='galerie')n.images=[];cur.doc.blocs.push(n);dessiner();sauver()}});
function champ(parent,lab,b,k,long){var l=E('label','',lab);var i=long?E('textarea'):E('input');if(long)i.rows=3;i.value=b[k]||'';i.oninput=function(){b[k]=i.value;rendre($('apercu'),cur.doc);sauver()};parent.appendChild(l);parent.appendChild(i)}
function photo(parent,lab,cb){var l=E('label','',lab),i=E('input');i.type='file';i.accept='image/*';if(lab.indexOf('Galerie')>=0)i.multiple=true;
 i.onchange=function(){[].forEach.call(i.files,function(f){reduirePhoto(f,1200,function(u){cb(u);dessiner();sauver()})})};parent.appendChild(l);parent.appendChild(i)}
function dessiner(){var B=$('blocs');B.replaceChildren();cur.doc.blocs.forEach(function(b,ix){var c=E('div');c.className='card';var h=E('div','display:flex;justify-content:space-between;align-items:center');h.appendChild(E('b','',TB[b.t]||b.t));
 var outils=E('span');[['↑',-1],['↓',1]].forEach(function(m){var x=E('button','',m[0]);x.className='g';x.onclick=function(){var j=ix+m[1];if(j<0||j>=cur.doc.blocs.length)return;var a=cur.doc.blocs;a.splice(j,0,a.splice(ix,1)[0]);dessiner();sauver()};outils.appendChild(x)});
 var del=E('button','','✕');del.className='r';del.onclick=function(){cur.doc.blocs.splice(ix,1);dessiner();sauver()};outils.appendChild(del);h.appendChild(outils);c.appendChild(h);
 if(b.t==='titre'){champ(c,'Titre',b,'titre');champ(c,'Sous-titre',b,'sous');photo(c,'Photo',function(u){b.image=u});champ(c,'Texte du bouton (facultatif)',b,'bouton');champ(c,'Lien du bouton (https://…)',b,'lien')}
 if(b.t==='texte'){champ(c,'Titre',b,'titre');champ(c,'Texte',b,'texte',true)}
 if(b.t==='image'){photo(c,'Image',function(u){b.src=u});champ(c,'Légende',b,'legende')}
 if(b.t==='galerie'){photo(c,'Galerie (plusieurs photos)',function(u){b.images=(b.images||[]).concat([u]).slice(0,24)});c.appendChild(E('p','',(b.images||[]).length+' photo(s)'));var vg=E('button','','Vider la galerie');vg.className='g';vg.onclick=function(){b.images=[];dessiner();sauver()};c.appendChild(vg)}
 if(b.t==='produits'){champ(c,'Titre',b,'titre');(b.items||[]).forEach(function(p){var r=E('div');r.className='row';var a=E('div'),d=E('div');champ(a,'Produit / service',p,'nom');champ(d,'Prix',p,'prix');r.appendChild(a);r.appendChild(d);c.appendChild(r)});
  var ap=E('button','','+ ligne');ap.className='g';ap.onclick=function(){b.items.push({nom:'',prix:''});dessiner();sauver()};c.appendChild(ap)}
 if(b.t==='bouton'){champ(c,'Texte',b,'texte');champ(c,'Lien (https://, mailto:, tel:)',b,'lien')}
 if(b.t==='contact'){champ(c,'Titre',b,'titre');champ(c,'Téléphone',b,'tel');champ(c,'E-mail',b,'email');champ(c,'Adresse',b,'adresse',true)}
 B.appendChild(c)});rendre($('apercu'),cur.doc)}
function montrer(titre,valeur,texte){var P=$('partage');P.replaceChildren();P.appendChild(E('p','',titre));var d=E('div','',valeur);d.className='code';P.appendChild(d);
 var cp=E('button','','Copier le message');cp.className='g';cp.onclick=function(){navigator.clipboard&&navigator.clipboard.writeText(texte)};P.appendChild(cp);P.appendChild(E('p','',texte));P.lastChild.className='muted'}
$('bSalon').onclick=function(){var u=location.origin+'/salon/'+cur.salon;montrer('Lien à ouvrir sur le téléphone du client (il voit vos changements en direct) :',u,'Ouvre ce lien pour voir ton site se construire en direct : '+u)};
$('bNvSalon').onclick=function(){if(confirm('Couper l’ancien lien salon ?'))api('admin/nouveauSalon',{id:cur.id}).then(function(){ouvrir(cur.id)})};
$('bCode').onclick=function(){api('admin/code',{id:cur.id}).then(function(j){if(!j.ok)return;montrer('Code à usage unique (affiché une seule fois, valable 7 jours) :',j.code,'Ton projet est prêt : ouvre '+location.origin+'/voir et entre le code '+j.code+' (il ne marche qu’une fois).')})};
$('bSuppr').onclick=function(){if(confirm('Supprimer définitivement ce projet ?'))api('admin/supprimer',{id:cur.id}).then(function(){vue('vProjets');etat()})};
etat();`);
