export const PAGE = `<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>VM Prono</title>
<style>
:root{--bg:#07080d;--card:#11131d;--line:#2b3046;--txt:#f3f4f8;--muted:#a9b0c4;--gold:#f4cf55;--red:#e52643;--ok:#3ccf7a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
header{padding:16px;border-bottom:2px solid var(--red);display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
header h1{margin:0;font-size:1.3rem}.test{background:var(--gold);color:#111;border-radius:999px;padding:2px 9px;font-weight:800;font-size:.72rem}
main{max-width:760px;margin:auto;padding:14px}section{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px;margin:12px 0}
h2{margin:0 0 8px;font-size:1.05rem}.tip{border-top:1px solid var(--line);padding:10px 0}.tip:first-of-type{border-top:0}
.tip b{display:block}.meta{color:var(--muted);font-size:.82rem}.res{font-weight:800;font-size:.8rem}.gagne{color:var(--ok)}.perdu{color:#ff6b7f}
input,textarea,select{width:100%;background:#0b0d16;color:var(--txt);border:1px solid var(--line);border-radius:9px;padding:9px;font:inherit;margin:4px 0}
button{cursor:pointer;border:0;border-radius:10px;padding:10px 14px;font-weight:800;margin:4px 4px 4px 0}.p{background:var(--gold);color:#111}.g{background:#1b2033;color:var(--txt)}
.code{font:700 1.1rem ui-monospace,monospace;background:#000;border:1px dashed var(--gold);padding:10px;border-radius:9px;word-break:break-all}
.legal{color:var(--muted);font-size:.78rem;text-align:center;padding:12px}.hide{display:none}.msg{min-height:1.2em;color:var(--gold)}
</style></head><body>
<header><h1>VM Prono <span class="test">MODE TEST</span></h1><a href="https://velocemercato.fr/" style="color:var(--gold)">velocemercato.fr</a></header>
<main id="app">
 <section id="pub"><h2>🎁 Conseils publics</h2><div id="pubList" class="meta">Chargement…</div></section>
 <section id="vip"><h2>🔒 Espace VIP (gratuit, sur invitation)</h2>
  <div id="vipOff"><p class="meta">Tu as reçu un code d'invitation ? Il ne sert qu'une seule fois et active cet appareil.</p>
   <input id="code" placeholder="Code d'invitation" autocomplete="off" maxlength="64"><button class="p" id="act">Activer</button><p class="msg" id="actMsg" role="status"></p></div>
  <div id="vipOn" class="hide"><p class="meta" id="hello"></p><div id="vipList"></div><button class="g" id="out">Se déconnecter</button></div>
 </section>
 <section id="adm" class="hide"><h2>🛠 Espace Romain</h2>
  <div id="admLogin"><input id="atok" type="password" placeholder="Code administrateur" autocomplete="off"><button class="p" id="alog">Entrer</button><p class="msg" id="alogMsg"></p></div>
  <div id="admPanel" class="hide">
   <h2>Nouveau conseil</h2>
   <select id="tvis"><option value="public">Public</option><option value="vip">VIP</option></select>
   <input id="tmatch" placeholder="Match (ex. PSG – OM, Ligue 1, dim. 21 h)" maxlength="120">
   <input id="ttitle" placeholder="Sélection (ex. Victoire PSG)" maxlength="120">
   <input id="todds" placeholder="Cote (facultatif)" maxlength="20">
   <textarea id="tbody" rows="3" placeholder="Analyse" maxlength="1500"></textarea>
   <button class="p" id="tadd">Publier</button><p class="msg" id="taddMsg"></p>
   <h2>Conseils</h2><div id="atips"></div>
   <h2>Membres VIP</h2><input id="mname" placeholder="Prénom du membre" maxlength="60"><button class="p" id="minv">Créer une invitation</button>
   <div id="newCode"></div><div id="amembers"></div>
  </div>
 </section>
 <p class="legal">18+ · Les jeux d'argent comportent des risques : endettement, isolement, dépendance. Joueurs Info Service : 09 74 75 13 13. Aucun résultat garanti. Conseils rédigés et validés par le propriétaire de Véloce Mercato.</p>
</main>
<script>
(function(){'use strict';
var $=function(i){return document.getElementById(i)};
function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
function api(p,body){return fetch('/api/'+p,body?{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body),credentials:'same-origin'}:{credentials:'same-origin'}).then(function(r){return r.json().then(function(j){j._s=r.status;return j})})}
var RES={en_attente:'⏳ En attente',gagne:'✅ Gagné',perdu:'❌ Perdu',annule:'↩ Annulé'};
function drawTips(box,tips){box.replaceChildren();if(!tips||!tips.length){box.appendChild(el('p','meta','Aucun conseil validé pour le moment.'));return}
 tips.forEach(function(t){var d=el('div','tip');d.appendChild(el('b',null,t.title+(t.odds?' · cote '+t.odds:'')));d.appendChild(el('div','meta',t.match+' · publié le '+new Date(t.created).toLocaleString('fr-FR',{timeZone:'Europe/Paris'})));
 if(t.body)d.appendChild(el('p',null,t.body));d.appendChild(el('span','res '+t.result,RES[t.result]||''));box.appendChild(d)})}
function loadPublic(){api('public').then(function(j){drawTips($('pubList'),j.tips)})}
function loadVip(){api('me').then(function(m){if(!m.vip){$('vipOff').classList.remove('hide');$('vipOn').classList.add('hide');return}
 $('vipOff').classList.add('hide');$('vipOn').classList.remove('hide');$('hello').textContent='Connecté : '+m.name;api('vip').then(function(j){drawTips($('vipList'),j.tips)})})}
$('act').onclick=function(){$('actMsg').textContent='…';api('activate',{code:$('code').value}).then(function(j){
 $('actMsg').textContent=j.ok?'Bienvenue ! Accès VIP activé sur cet appareil.':(j.error==='trop_de_tentatives'?'Trop de tentatives, réessaie dans une heure.':'Code invalide, déjà utilisé ou expiré.');if(j.ok){$('code').value='';loadVip()}})};
$('out').onclick=function(){api('logout',{}).then(loadVip)};
// --- Admin ---
if(location.pathname==='/admin'){$('adm').classList.remove('hide');$('pub').classList.add('hide');$('vip').classList.add('hide');loadAdmin()}
function loadAdmin(){api('admin/state').then(function(s){if(s._s===401){$('admLogin').classList.remove('hide');$('admPanel').classList.add('hide');return}
 $('admLogin').classList.add('hide');$('admPanel').classList.remove('hide');
 var b=$('atips');b.replaceChildren();(s.tips||[]).forEach(function(t){var d=el('div','tip');d.appendChild(el('b',null,'['+t.visibility.toUpperCase()+'] '+t.title));d.appendChild(el('div','meta',t.match+' · '+t.status+' · '+(RES[t.result]||'')));
  ['gagne','perdu','annule'].forEach(function(r){var x=el('button','g',RES[r]);x.onclick=function(){api('admin/tip-status',{id:t.id,result:r}).then(loadAdmin)};d.appendChild(x)});
  var w=el('button','g',t.status==='publie'?'Retirer':'Republier');w.onclick=function(){api('admin/tip-status',{id:t.id,status:t.status==='publie'?'retire':'publie'}).then(loadAdmin)};d.appendChild(w);b.appendChild(d)});
 var m=$('amembers');m.replaceChildren();(s.members||[]).forEach(function(x){var d=el('div','tip');d.appendChild(el('b',null,x.name+(x.revoked?' (révoqué)':'')));d.appendChild(el('div','meta','Appareil actif : '+(x.appareils?'oui':'non')));
  if(!x.revoked){var n=el('button','g','Nouveau téléphone');n.onclick=function(){api('admin/reinvite',{member:x.id}).then(showCode)};var r=el('button','g','Révoquer');r.onclick=function(){if(confirm('Révoquer '+x.name+' ?'))api('admin/revoke',{member:x.id}).then(loadAdmin)};d.appendChild(n);d.appendChild(r)}
  m.appendChild(d)})})}
function showCode(j){var b=$('newCode');b.replaceChildren();if(!j.ok){b.appendChild(el('p','msg','Erreur : '+(j.error||'')));return}
 b.appendChild(el('p','meta','Code à envoyer en privé (affiché une seule fois, valable 14 jours) :'));b.appendChild(el('div','code',j.code));
 b.appendChild(el('p','meta','Message : « Ton accès VIP VM Prono : ouvre '+location.origin+' et entre ce code : '+j.code+' (usage unique). 18+ »'));loadAdmin()}
$('alog').onclick=function(){api('admin/login',{token:$('atok').value}).then(function(j){$('alogMsg').textContent=j.ok?'':'Refusé.';if(j.ok){$('atok').value='';loadAdmin()}})};
$('tadd').onclick=function(){var t={visibility:$('tvis').value,match:$('tmatch').value,title:$('ttitle').value,odds:$('todds').value,body:$('tbody').value};
 if(!t.match.trim()||!t.title.trim()){$('taddMsg').textContent='Match et sélection obligatoires.';return}
 api('admin/tip',t).then(function(j){$('taddMsg').textContent=j.ok?'Publié.':'Erreur.';if(j.ok){['tmatch','ttitle','todds','tbody'].forEach(function(i){$(i).value=''});loadAdmin()}})};
$('minv').onclick=function(){api('admin/invite',{name:$('mname').value}).then(function(j){$('mname').value='';showCode(j)})};
if(location.pathname!=='/admin'){loadPublic();loadVip()}
})();
</script></body></html>`;
