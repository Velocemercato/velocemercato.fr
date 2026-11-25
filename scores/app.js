/* VM Scores · foot en direct.
   Données réelles : /scores.json (direct, ~2 min) et /matchs.json (agenda de la semaine), source football-data.org.
   Rien n'est inventé : si la source ne répond pas, la page le dit. */
const COMPS=[['all','⚽','Toutes'],['Ligue 1','🇫🇷','Ligue 1'],['Ligue des champions','⭐','Ligue des champions'],['Premier League','🏴','Premier League'],['Liga','🇪🇸','Liga'],['Serie A','🇮🇹','Serie A'],['Bundesliga','🇩🇪','Bundesliga'],['NBA','🏀','NBA'],['NHL','🏒','NHL'],['NFL','🏈','NFL']];
const $=id=>document.getElementById(id);
const esc=t=>String(t??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const DAYFMT=new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Paris',year:'numeric',month:'2-digit',day:'2-digit'});
const HM=new Intl.DateTimeFormat('fr-FR',{hour:'2-digit',minute:'2-digit',timeZone:'Europe/Paris'});
const LONG=new Intl.DateTimeFormat('fr-FR',{weekday:'long',day:'numeric',month:'long',timeZone:'Europe/Paris'});
let comp='all',filter='all',onlyFav=false,toastTimer,DATA=[],MAJ=null,first=true,prev={},loaded=false;
let favorites=[];try{const s=JSON.parse(localStorage.getItem('vm-scores-fav')||'[]');favorites=Array.isArray(s)?s.map(String).slice(0,200):[]}catch{}
const today=()=>DAYFMT.format(new Date());$('date').value=today();
function toast(t){$('toast').textContent=t;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').textContent='',5000)}
function state(s){if(['UNAVAILABLE','POSTPONED','SUSPENDED','CANCELLED'].includes(s))return 'unavailable';return s==='IN_PLAY'||s==='PAUSED'?'live':s==='FINISHED'?'finished':'scheduled'}
function label(x){if(x.statut==='UNAVAILABLE')return 'Statut indisponible';if(x.statut==='PAUSED')return 'Mi-temps';if(x.statut==='IN_PLAY')return 'En direct';if(x.statut==='FINISHED')return 'Terminé';if(x.statut==='POSTPONED')return 'Reporté';if(x.statut==='SUSPENDED')return 'Suspendu';if(x.statut==='CANCELLED')return 'Annulé';return HM.format(new Date(x.date))}
async function get(url){try{const r=await fetch(url+'?t='+Math.floor(Date.now()/60000),{cache:'no-store'});return r.ok?await r.json():null}catch{return null}}
function freshRows(rows, timestamp, now=Date.now()) {
  const checked=Date.parse(timestamp), age=now-checked;
  const fresh=Number.isFinite(checked)&&age>=-60000&&age<=40*60000;
  return rows.map(m=>{
    const start=Date.parse(m.date), active=['IN_PLAY','PAUSED'].includes(m.statut);
    const plausible=Number.isFinite(start)&&start<=now+60000&&now-start<=8*3600000;
    const overdue=['SCHEDULED','TIMED'].includes(m.statut)&&Number.isFinite(start)&&now-start>15*60000;
    return (active&&(!fresh||!plausible)||overdue)?{...m,statut:'UNAVAILABLE'}:m;
  });
}
async function load(){
  const [live,agenda]=await Promise.all([(get('https://raw.githubusercontent.com/Velocemercato/velocemercato.fr/scores-live/scores.json').then(function(d){return d||get('/scores.json')})),get('/matchs.json')]);
  loaded=true;
  const map=new Map();
  for(const m of (Array.isArray(agenda)?agenda:[]).filter(m=>m&&m.id!=null))map.set(String(m.id),{id:String(m.id),date:m.date,sport:m.sport||'foot',comp:m.competition,home:m.domicile,away:m.exterieur,statut:m.statut,score:Array.isArray(m.score)?m.score:[null,null]});
  for(const m of (Array.isArray(live?.matchs)?live.matchs:[]).filter(m=>m&&m.id!=null))map.set(String(m.id),{id:String(m.id),date:m.date,sport:m.sport||'foot',comp:m.comp,home:m.dom,away:m.ext,statut:m.statut,score:Array.isArray(m.score)?m.score:[null,null]});
  if(!map.size&&DATA.length&&(!Array.isArray(agenda)||!Array.isArray(live?.matchs))){DATA=freshRows(DATA,null);$('maj').textContent='Source momentanément indisponible : derniers scores connus affichés.';render();return}
  const rows=freshRows([...map.values()].filter(m=>Number.isFinite(Date.parse(m.date))&&typeof m.home==='string'&&typeof m.away==='string'),live&&(live.verifie||live.maj)).sort((a,b)=>String(a.date).localeCompare(String(b.date))||String(a.comp).localeCompare(String(b.comp)));
  if(!first)alerts(rows);first=false;
  prev=Object.fromEntries(rows.map(x=>[x.id,x]));DATA=rows;MAJ=live&&live.maj;
  var VER=live&&(live.verifie||live.maj),FR={dateStyle:'short',timeStyle:'short',timeZone:'Europe/Paris'};
  var vieux=!Number.isFinite(Date.parse(VER))||Date.now()-Date.parse(VER)>40*60000||Date.parse(VER)>Date.now()+60000;
  $('maj').textContent=(rows.length?'Sources football-data.org / ESPN':'Aucun match des championnats suivis aujourd’hui (trêve ou jour sans match).')+
    (Number.isFinite(Date.parse(VER))?' · vérifié le '+new Date(VER).toLocaleString('fr-FR',FR):'')+(vieux?' · ⚠ données anciennes, robot en retard':' · actualisation automatique chaque minute.');
  renderComps();render();
}
function alerts(rows){
  for(const x of rows){if(!favorites.includes(x.id)||x.statut==='UNAVAILABLE')continue;const o=prev[x.id];if(!o||o.statut==='UNAVAILABLE')continue;const s=x.score||[],so=o.score||[];const tag=x.home+' '+(s[0]??0)+'-'+(s[1]??0)+' '+x.away;
    if($('alertStart').checked&&state(o.statut)==='scheduled'&&state(x.statut)==='live')notify('🟢 Coup d’envoi',x.home+' – '+x.away+' · '+x.comp);
    else if($('alertScore').checked&&[...s.slice(0,2),...so.slice(0,2)].length===4&&[...s.slice(0,2),...so.slice(0,2)].every(Number.isFinite)&&(s[0]+s[1])>(so[0]+so[1]))notify('⚽ But !',tag+' · '+x.comp);
    if($('alertEnd').checked&&o.statut!=='FINISHED'&&x.statut==='FINISHED')notify('🏁 Terminé',tag+' · '+x.comp)}
}
function saveFav(){try{localStorage.setItem('vm-scores-fav',JSON.stringify(favorites))}catch{toast('La sauvegarde locale est indisponible sur cet appareil.')}}
function day(x){return Number.isFinite(Date.parse(x.date))?DAYFMT.format(new Date(x.date)):''}
function renderComps(){$('sports').innerHTML=COMPS.map(c=>'<button type="button" data-sport="'+esc(c[0])+'"'+(c[0]===comp?' class="active"':'')+'><span>'+c[1]+'</span>'+esc(c[2])+'<small>'+DATA.filter(d=>(c[0]==='all'||d.comp===c[0])&&day(d)===$('date').value).length+'</small></button>').join('')}
function render(){
  document.querySelectorAll('[data-sport]').forEach(b=>b.classList.toggle('active',b.dataset.sport===comp));
  const q=$('search').value.toLocaleLowerCase('fr'),d=$('date').value||today();
  const rows=DATA.filter(x=>day(x)===d&&(comp==='all'||x.comp===comp)&&(filter==='all'||state(x.statut)===filter)&&(!onlyFav||favorites.includes(x.id))&&[x.home,x.away,x.comp].join(' ').toLocaleLowerCase('fr').includes(q));
  $('favCount').textContent=favorites.length;$('favoriteFilter').style.color=onlyFav?'#b2ef83':'';
  $('count').textContent=rows.length+' match'+(rows.length>1?'s':'')+' · '+LONG.format(new Date(d+'T12:00:00'));
  $('sportName').textContent=(COMPS.find(x=>x[0]===comp)||COMPS[0])[2].toUpperCase();
  let html='',last='';
  for(const x of rows){const st=state(x.statut),show=st==='live'||st==='finished',fav=favorites.includes(x.id);
    if(x.comp!==last){html+='<div class="league"><span>'+esc(x.comp)+'</span><small>'+esc(({foot:'Football',basket:'Basketball',hockey:'Hockey',nfl:'Football américain'})[x.sport]||'Sport')+'</small></div>';last=x.comp}
    html+='<article class="match"><button class="star '+(fav?'on':'')+'" data-fav="'+esc(x.id)+'" aria-label="'+(fav?'Retirer':'Ajouter')+' '+esc(x.home)+' – '+esc(x.away)+' des favoris" aria-pressed="'+fav+'">'+(fav?'★':'☆')+'</button><div class="clock '+(st==='live'?'live':'')+'">'+(st==='live'?'<span class="liveDot"></span>':'')+esc(label(x))+'</div><div class="teams"><div class="team"><small>'+esc(x.home.slice(0,2).toUpperCase())+'</small><b>'+esc(x.home)+'</b></div><div class="team"><small>'+esc(x.away.slice(0,2).toUpperCase())+'</small><b>'+esc(x.away)+'</b></div></div><div class="score"><span>'+(show?esc(x.score[0]??'–'):'–')+'</span><span>'+(show?esc(x.score[1]??'–'):'–')+'</span></div><button class="detailBtn" data-detail="'+esc(x.id)+'" aria-label="Détail de '+esc(x.home)+' contre '+esc(x.away)+'">↗</button></article>'}
  $('matchList').innerHTML=html||'<div class="empty">'+(DATA.length?'Aucun match pour ces filtres ce jour-là.<br>Changez de date, de compétition ou retirez un filtre.':(loaded?'Aucun score disponible pour le moment.':'Chargement des scores…'))+'</div>';
}
$('sports').onclick=e=>{const b=e.target.closest('[data-sport]');if(b){comp=b.dataset.sport;render()}};
document.querySelectorAll('[data-filter]').forEach(b=>b.onclick=()=>{filter=b.dataset.filter;document.querySelectorAll('[data-filter]').forEach(x=>x.classList.toggle('active',x===b));render()});
$('favoriteFilter').onclick=()=>{onlyFav=!onlyFav;render()};$('search').oninput=render;$('date').onchange=()=>{renderComps();render()};$('resetDate').onclick=()=>{$('date').value=today();renderComps();render()};
$('matchList').onclick=e=>{const b=e.target.closest('button');if(!b)return;
  if(b.dataset.fav){const id=b.dataset.fav;favorites=favorites.includes(id)?favorites.filter(x=>x!==id):[...favorites,id].slice(-200);saveFav();render();if(favorites.includes(id))toast('Match ajouté : alertes tant que VM Scores est ouvert.')}
  if(b.dataset.detail){const x=DATA.find(x=>x.id===b.dataset.detail);if(!x)return;const st=state(x.statut),show=st!=='scheduled';
    $('detailTitle').textContent=x.comp;
    $('detailBody').innerHTML='<h2 style="text-align:center">'+esc(x.home)+'<br><small class="muted">contre</small><br>'+esc(x.away)+'</h2><div class="bigscore">'+(show?esc(x.score[0]??'–')+' : '+esc(x.score[1]??'–'):'– : –')+'</div><p style="text-align:center">'+esc(label(x))+' · '+esc(LONG.format(new Date(x.date)))+' · '+esc(HM.format(new Date(x.date)))+'</p><div class="sep"></div><p class="note">Dernier score fourni par football-data.org / ESPN. Un direct indisponible ne confirme pas le résultat final. Le détail des buteurs n’est pas encore disponible.</p>';
    $('detail').showModal()}};
$('closeDetail').onclick=()=>$('detail').close();
async function notify(title,body){toast(title+' · '+body);const row=document.createElement('div');row.className='event';const s=document.createElement('strong');s.textContent=title;const sp=document.createElement('span');sp.textContent=body;row.append(s,sp);if($('events').querySelector('p'))$('events').replaceChildren();$('events').prepend(row);if($('events').children.length>8)$('events').lastElementChild.remove();
  if('Notification'in window&&Notification.permission==='granted'){try{const reg=await navigator.serviceWorker?.getRegistration();if(reg)await reg.showNotification(title,{body,tag:'vm-scores-'+body.slice(0,40),icon:'/app/scores-192.png'});else new Notification(title,{body})}catch{}}}
$('activateAlerts').onclick=async()=>{if(!('Notification'in window))return toast('Ce navigateur ne prend pas en charge les notifications.');try{const p=await Notification.requestPermission();$('permissionState').textContent=p==='granted'?'Notifications autorisées sur cet appareil.':p==='denied'?'Notifications refusées : les alertes restent visibles ici.':'Autorisation non accordée.'}catch{toast('Autorisation indisponible dans ce navigateur.')}};
$('simulate').onclick=()=>notify('🔔 Test VM Scores','Les alertes de tes matchs favoris s’afficheront comme ceci.');
if('Notification'in window&&Notification.permission==='granted')$('permissionState').textContent='Notifications déjà autorisées sur cet appareil.';
renderComps();render();load();setInterval(load,60000);
