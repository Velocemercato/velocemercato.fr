
(()=>{'use strict';const KEY='vm-alertes-v1';
const TOP={foot:['⚽ Foot','/#feed-title'],actus:['📰 VM Actus','/actus/'],gaming:['🎮 Gaming','/vm-gaming/'],pronos:['📊 Pronos','/pronos/'],mangas:['📺 Mangas','/mangas/'],nba:['🏀 NBA','/multisport/?sport=nba'],nfl:['🏈 NFL','/multisport/?sport=nfl'],f1:['🏎️ F1','/multisport/?sport=f1'],motogp:['🏍️ MotoGP','/multisport/?sport=motogp'],tennis:['🎾 Tennis','/multisport/?sport=tennis'],rugby:['🏉 Rugby','/multisport/?sport=rugby'],cyclisme:['🚴 Cyclisme','/multisport/?sport=cyclisme'],nhl:['🏒 NHL','/multisport/?sport=nhl'],mlb:['⚾ MLB','/multisport/?sport=mlb'],mma:['🥊 MMA','/multisport/?sport=mma'],ski:['🎿 Ski','/multisport/ski/']};
const empty=()=>({enabled:false,topics:Object.fromEntries(Object.keys(TOP).map(k=>[k,false])),seen:{}});
function read(){try{const s=JSON.parse(localStorage.getItem(KEY)||'null');return s?.topics&&s?.seen?s:empty()}catch{return empty()}}
function save(s){try{localStorage.setItem(KEY,JSON.stringify(s))}catch{}}
async function get(path){const r=await fetch(path+'?v='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error(path);return r}
function mk(k,id,t,u){return {k,id:String(id),title:String(t).slice(0,160),url:u,label:TOP[k][0]}}
async function latest(){const a=Object.fromEntries(Object.keys(TOP).map(k=>[k,[]]));
const vals=await Promise.allSettled([get('/fil.json').then(r=>r.json()),get('/notifications/episodes.json').then(r=>r.json()),get('/pronos/').then(r=>r.text()),get('/multisport/actualites.json').then(r=>r.json())]);
if(vals[0].status==='fulfilled'){const lines=vals[0].value.titres||[];for(const k of ['foot','actus','gaming'])a[k]=lines.filter(x=>x.k===k&&x.t&&x.d).sort((x,y)=>Date.parse(y.d)-Date.parse(x.d)).slice(0,7).map(x=>mk(k,x.d+'/'+x.t,x.t,TOP[k][1]));}
if(vals[1].status==='fulfilled')a.mangas=vals[1].value.slice(0,10).map(x=>{let u=new URL(x.url,location.origin);return mk('mangas',x.id,x.title,u.origin===location.origin?u.pathname:'/mangas/')});
if(vals[2].status==='fulfilled'){const d=new DOMParser().parseFromString(vals[2].value,'text/html'),ed=d.querySelector('header strong')?.textContent?.trim(),title=d.querySelector('#football article h3')?.textContent?.trim();if(ed)a.pronos=[mk('pronos',ed+'/'+title,title||'Nouvelle édition des pronos','/pronos/')]}
if(vals[3].status==='fulfilled'&&vals[3].value&&vals[3].value.sports){
 const now=Date.now(),windowMs=7*86400000;
 for(const k of ['nba','nfl','f1','motogp','tennis','rugby','cyclisme','nhl','mlb','mma','ski']){
  const rows=vals[3].value.sports[k]||[];
  a[k]=rows.filter(x=>x&&x.id&&x.titre&&x.date&&Number.isFinite(Date.parse(x.date))&&now-Date.parse(x.date)>=-60000&&now-Date.parse(x.date)<=windowMs).slice(0,8).map(x=>mk(k,x.id,x.titre,TOP[k][1]));
 }
}
return a}
let service=null;async function sw(){if(!('serviceWorker'in navigator))return null;if(service)return service;try{service=await navigator.serviceWorker.register('/notifications/sw.js',{scope:'/notifications/'});return service}catch{return null}}
function toast(n){const e=document.createElement('div'),a=document.createElement('a'),p=document.createElement('p');e.className='vm-alert-toast';a.href=n.url;a.textContent='Voir la nouveauté';p.textContent=n.label+' : '+n.title;e.append(p,a);document.body.append(e);setTimeout(()=>e.remove(),8500)}
async function notify(n){toast(n);if('Notification'in window&&Notification.permission==='granted')try{const s=await sw();if(s)await s.showNotification('VM • '+n.label,{body:n.title,icon:'/img/logo-vm-192.png',tag:'vm-'+n.k,data:{url:n.url}})}catch{}}
function draw(a){const box=document.getElementById('vm-alert-feed');if(!box)return;box.replaceChildren();let yes=false;for(const k of Object.keys(TOP))if(read().topics[k])for(const n of (a[k]||[]).slice(0,4)){yes=true;const art=document.createElement('article'),small=document.createElement('small'),link=document.createElement('a');small.textContent=n.label;link.href=n.url;link.textContent=n.title;art.append(small,document.createElement('br'),link);box.append(art)}if(!yes){const p=document.createElement('p');p.textContent='Choisis tes thèmes pour consulter les nouveautés.';box.append(p)}}
async function check(pop){const s=read();if(!s.enabled)return;try{const a=await latest();let dirty=false;for(const k of Object.keys(TOP)){if(!s.topics[k]||!a[k].length)continue;const now=a[k][0],old=s.seen[k];if(old!==now.id){s.seen[k]=now.id;dirty=true;if(old&&pop&&a[k].some(x=>x.id===old))await notify(now)}}if(dirty)save(s);if(document.body.classList.contains('vm-alerts-page'))draw(a)}catch{}}
function start(){if(document.body.classList.contains('vm-alerts-page')){
const status=document.getElementById('vm-alert-status');const initial=read();status.textContent=initial.enabled?'Alertes activées lorsque le site est ouvert.':'Alertes désactivées.';
for(const k of Object.keys(TOP)){const c=document.querySelector('[data-topic="'+k+'"]');c.checked=!!initial.topics[k];c.addEventListener('change',()=>{const s=read();s.topics[k]=c.checked;save(s);status.textContent='Choix enregistré sur cet appareil.'})}
document.getElementById('vm-alert-enable').addEventListener('click',async()=>{const s=read();if(!Object.values(s.topics).some(Boolean)){status.textContent='Choisis au moins un thème.';return} s.enabled=true;save(s);if('Notification'in window&&window.isSecureContext&&Notification.permission==='default')try{await Notification.requestPermission()}catch{}const a=await latest().catch(()=>null);if(a){for(const k of Object.keys(TOP))if(s.topics[k]&&a[k].length)s.seen[k]=a[k][0].id;save(s);draw(a)}status.textContent='Alertes activées pendant la visite. Pas encore de push lorsque le navigateur est fermé.'});
document.getElementById('vm-alert-disable').addEventListener('click',()=>{const s=read();s.enabled=false;save(s);status.textContent='Alertes désactivées.'});
document.getElementById('vm-alert-refresh').addEventListener('click',async()=>{try{draw(await latest());status.textContent='Nouveautés actualisées.'}catch{status.textContent='Flux temporairement indisponible.'}});
latest().then(draw).catch(()=>{});
}else{const a=document.createElement('a');a.className='vm-alert-fab';a.href='/notifications/';a.textContent='🔔 Mes alertes';a.setAttribute('aria-label','Choisir mes alertes');(document.querySelector('main')||document.body).append(a)}
if(read().enabled){sw().catch(()=>{});check(false);setInterval(()=>{if(!document.hidden)check(true)},180000);document.addEventListener('visibilitychange',()=>{if(!document.hidden)check(true)})}}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();