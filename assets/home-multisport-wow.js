/* Accueil VM : page d'accueil personnalisable, sans fausses actualités.
   Source: fil.json, multisport/actualites.json, studio/diffusions.json. */
(()=>{'use strict';
const KEY='vm-sport-favori';
const SPORTS={
 foot:{name:'FOOT',emoji:'⚽',color:'#fd3b56',home:'/#feed-title',result:'/#live',caption:'L’essentiel du foot, le mercato et les derniers JT.',france:'Ligue 1, Ligue 2, clubs et talents français.',europe:'Championnats et compétitions européennes.',world:'Le football partout dans le monde.'},
 nba:{name:'NBA',emoji:'🏀',color:'#ffa447',home:'/multisport/?sport=nba',result:'https://www.nba.com/games',caption:'La NBA : franchises, stars, résultats et playoffs.',france:'Les Français et les talents de NBA.',europe:'Les joueurs européens en NBA.',world:'L’actualité des franchises NBA.'},
 nfl:{name:'NFL',emoji:'🏈',color:'#64baff',home:'/multisport/?sport=nfl',result:'https://www.nfl.com/schedules/',caption:'Football américain, NFL et grands rendez-vous.',france:'La NFL vue depuis la France.',europe:'La NFL et ses rendez-vous européens.',world:'Les franchises et joueurs NFL.'},
 f1:{name:'FORMULE 1',emoji:'🏁',color:'#fd425a',home:'/multisport/?sport=f1',result:'https://www.formula1.com/en/results/2026/races',caption:'Les pilotes, les écuries et les Grand Prix.',france:'Pilotes et écuries françaises.',europe:'Les Grands Prix et équipes d’Europe.',world:'Le championnat et tous ses circuits.'},
 motogp:{name:'MOTOGP',emoji:'🏍️',color:'#ff5b63',home:'/multisport/?sport=motogp',result:'https://www.motogp.com/en/results',caption:'Courses, pilotes et coulisses du MotoGP.',france:'Les pilotes français, dont Quartararo et Zarco.',europe:'Les Grands Prix et pilotes européens.',world:'La saison MotoGP dans le monde.'},
 tennis:{name:'TENNIS',emoji:'🎾',color:'#d1e867',home:'/multisport/?sport=tennis',result:'https://www.atptour.com/en/scores/current',caption:'Tennis ATP, WTA et tournois internationaux.',france:'Les joueurs et tournois français.',europe:'Les tournois européens.',world:'Les grands rendez-vous du tennis mondial.'},
 rugby:{name:'RUGBY',emoji:'🏉',color:'#79e0a9',home:'/multisport/?sport=rugby',result:'https://www.sixnationsrugby.com/en/m6n/fixtures',caption:'Top 14, XV de France et rugby international.',france:'Top 14 et XV de France.',europe:'Le rugby européen et les Six Nations.',world:'Le rugby partout dans le monde.'},
 cyclisme:{name:'CYCLISME',emoji:'🚴',color:'#e3cc62',home:'/multisport/?sport=cyclisme',result:'https://www.uci.org/competition-hub',caption:'Grands tours, cyclisme et stars du peloton.',france:'Courses et coureurs français.',europe:'Les classiques et grands tours européens.',world:'L’actualité mondiale du cyclisme.'},
 nhl:{name:'NHL',emoji:'🏒',color:'#8bd9ff',home:'/multisport/?sport=nhl',result:'https://www.nhl.com/scores',caption:'Hockey sur glace, NHL, scores et playoffs.',france:'Les Français dans le hockey mondial.',europe:'Les joueurs européens en NHL.',world:'Toutes les franchises NHL.'},
 mlb:{name:'MLB',emoji:'⚾',color:'#ff9683',home:'/multisport/?sport=mlb',result:'https://www.mlb.com/scores',caption:'Baseball US, équipes et World Series.',france:'Le baseball français.',europe:'Le baseball européen.',world:'Les franchises et compétitions MLB.'},
 mma:{name:'MMA / UFC',emoji:'🥊',color:'#ff656b',home:'/multisport/?sport=mma',result:'https://www.ufc.com/events',caption:'MMA et UFC, combattants et grands événements.',france:'Les combattants français.',europe:'Les rendez-vous MMA en Europe.',world:'Les événements et grandes affiches UFC.'}
};
const valid=(u)=>{try{const x=new URL(u,location.origin);return ['https:','http:'].includes(x.protocol)?x.href:null}catch{return null}};
const $=id=>document.getElementById(id);
const state={sport:'foot',sportItems:null,footItems:null,videoItems:null};
function setText(id,s){const el=$(id);if(el)el.textContent=s}
function setLink(id,url){const el=$(id),v=valid(url);if(!el||!v)return;el.href=v;if(new URL(v).origin!==location.origin){el.target='_blank';el.rel='noopener noreferrer'}else{el.removeAttribute('target');el.removeAttribute('rel')}}
function setImage(id,url,alt){const img=$(id);if(!img)return;img.src=url;img.alt=alt||''}
function recent(items){return items.filter(x=>x&&x.title&&x.url&&x.date&&Number.isFinite(Date.parse(x.date))&&Date.now()-Date.parse(x.date)>=-60000&&Date.now()-Date.parse(x.date)<7*86400000).sort((a,b)=>Date.parse(b.date)-Date.parse(a.date))}
function items(){
if(state.sport==='foot')return recent(state.footItems||[]);
const rows=state.sportItems?.sports?.[state.sport]||[];
return recent(rows.map(row=>({title:row.titre,url:row.url,date:row.date,source:row.source,regions:row.rubriques||[]})).filter(row=>row.url?.startsWith('https://news.google.com/')));
}
function time(v){const date=new Date(v);return Number.isNaN(date.getTime())?'':date.toLocaleString('fr-FR',{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'})}
function latestVideo(){
const rows=Array.isArray(state.videoItems)?state.videoItems:[];
return rows.find(v=>(v.universes||[]).includes('foot')&&v.plateformes?.youtube?.status==='published'&&/^https:\/\/www\.youtube\.com\/watch\?v=[A-Za-z0-9_-]{11}$/.test(v.plateformes.youtube.url));
}
function setFeature(prefix,item,{video=false,cover=null}={}){
 if(!item)return;
 setText(prefix+'-title',item.title);setText(prefix+'-description',item.source?'Source : '+item.source+' · '+time(item.date):'Une publication disponible sur Véloce Mercato.');
 setLink(prefix+'-media',item.url);setLink(prefix+'-link',item.url);
 const b=$(prefix+'-play');if(b)b.hidden=!video;
 setImage(prefix+'-img',cover||'/mangas/assets/vm-87.svg',cover?'Illustration Véloce Mercato':'Mascotte originale Véloce Mercato');
 setText(prefix+'-link',video?'▶ REGARDER':'LIRE L’ACTU →');
}
function updateCards(){
const sport=state.sport,c=SPORTS[sport],news=items();
const video=sport==='foot'?latestVideo():null;
if(video){
setText('wow-main-label','LE JT FOOT À REVOIR');
setFeature('wow-main',{title:video.titre||'La Pastille Foot',url:video.plateformes.youtube.url,date:video.date_publication,source:'La Pastille TV'}, {video:true,cover:'/img/studio/plateau-veloce-600.webp'});
}else if(news[0]){
setText('wow-main-label','L’ACTU DU JOUR');setFeature('wow-main',news[0],{cover:sport==='foot'?'/img/v2-mercato-800.webp':null});
}else{
setText('wow-main-label','L’ACTU DU JOUR');
setText('wow-main-title','Les dernières informations '+c.name+' arrivent avec les mises à jour.');
setText('wow-main-description','Consulte les informations disponibles et les sources officielles.');
setLink('wow-main-media',c.home);setLink('wow-main-link',c.home);
setImage('wow-main-img','/mangas/assets/vm-87.svg','Personnage manga VM');
$('wow-main-play').hidden=true;setText('wow-main-link','EXPLORER →');
}
const second=news.find((v,i)=>i>0&&v.url!==(video?.plateformes?.youtube?.url||''))||news[0];
if(second){
setFeature('wow-second',second,{cover:sport==='foot'?'/img/v2-mercato-800.webp':'/mangas/assets/vm-87.svg'});
}else{
setText('wow-second-title','Découvrir tout l’univers '+c.name);
setText('wow-second-description','Des sources officielles et des actualités sélectionnées.');
setLink('wow-second-media',c.home);setLink('wow-second-link',c.home);
$('wow-second-play').hidden=true;setImage('wow-second-img','/mangas/assets/vm-87.svg','Mascotte originale VM');setText('wow-second-link','DÉCOUVRIR →');
}
}
function create(a,cls,content){const x=document.createElement(a);if(cls)x.className=cls;if(content!==undefined)x.textContent=String(content);return x}
function renderLists(){
const news=items(),last=$('wow-latest-list'),trends=$('wow-trends-list'),expanded=$('wow-expanded-list'),c=SPORTS[state.sport];
last.replaceChildren();trends.replaceChildren();expanded.replaceChildren();
if(!news.length){const p=create('p','vm-wow-static-note','Pas d’actualité sourcée récente pour ce sport.');last.append(p);trends.append(create('li','', 'En attente d’articles récents.'));expanded.append(create('p','', 'Aucun titre daté disponible cette semaine.'));return}
for(const [i,n]of news.slice(0,5).entries()){
 const link=create('a');link.href=valid(n.url)||c.home;
 if(new URL(link.href).origin!==location.origin){link.target='_blank';link.rel='noopener noreferrer'}
 const icon=create('span','item-icon',c.emoji),copy=create('span','item-copy',n.title),small=create('small','',n.source+' · '+time(n.date));copy.append(small);link.append(icon,copy);last.append(link);
}
for(const [i,n]of news.slice(0,5).entries()){
 const li=create('li'),num=create('span','rank',i+1),a=create('a','',n.title);a.href=valid(n.url)||c.home;if(new URL(a.href).origin!==location.origin){a.target='_blank';a.rel='noopener noreferrer'}li.append(num,a);trends.append(li)
}
for(const n of news.slice(0,18)){
 const art=create('article'),a=create('a','',n.title);a.href=valid(n.url)||c.home;if(new URL(a.href).origin!==location.origin){a.target='_blank';a.rel='noopener noreferrer'}const small=create('small','',n.source+' · '+time(n.date));art.append(a,small);expanded.append(art)
}}
function updateRegions(){
const c=SPORTS[state.sport],key=state.sport;
setText('wow-france-desc',c.france);setText('wow-europe-desc',c.europe);setText('wow-world-desc',c.world);
const urls=key==='foot'?['/#feed-title','/#feed-title','/#feed-title']:['france','europe','international'].map(r=>'/multisport/?sport='+encodeURIComponent(key)+'&rubrique='+r);
for(const [id,url] of [['wow-france',urls[0]],['wow-europe',urls[1]],['wow-world',urls[2]]])setLink(id,url);
setLink('wow-full-sport-link',key==='foot'?'#live':c.result);
setText('wow-full-sport-link',key==='foot'?'🏆 SCORES & AGENDA FOOT →':'🏆 SCORES & PROGRAMME '+c.name+' →');
}
function choose(sport,{push=false}={}){
 if(!(sport in SPORTS))sport='foot';state.sport=sport;const c=SPORTS[sport];
 try{localStorage.setItem(KEY,sport)}catch{}
 if(push){const u=new URL(location.href);if(sport==='foot')u.searchParams.delete('sport');else u.searchParams.set('sport',sport);history.pushState({sport},'',u.pathname+u.search+u.hash)}
 document.body.dataset.vmSport=sport;
 $('vm-wow-app').style.setProperty('--wow-r',c.color);
 document.querySelectorAll('[data-wow-sport]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.wowSport===sport)));
 setText('vm-wow-hero-title',sport==='foot'?'VM MULTISPORT':'VM '+c.name);
 // Restore the brand heading accents without injecting HTML
 const h=$('vm-wow-hero-title');h.replaceChildren(create('strong','', 'VM'),document.createTextNode(' '),create('span','',sport==='foot'?'MULTISPORT':c.name));
 setText('wow-expanded-title',c.emoji+' ACTUS '+c.name+' — LA SEMAINE');
 setLink('wow-expanded-link',c.home);
 $('vm-wow-expanded').hidden=sport==='foot';
 updateCards();renderLists();updateRegions();
 document.title=sport==='foot'?'Véloce Mercato — Foot et Multisport, ton sport au choix':'Véloce '+c.name+' — ton univers sportif | Véloce Mercato';
}
async function fetchJSON(u){const r=await fetch(u+'?v='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error(u);return r.json()}
async function load(){
const results=await Promise.allSettled([
fetchJSON('/fil.json'),fetchJSON('/multisport/actualites.json'),fetchJSON('/studio/diffusions.json')]);
if(results[0].status==='fulfilled')state.footItems=(results[0].value.titres||[]).filter(x=>x.k==='foot'&&x.t&&x.u&&x.d).map(x=>({title:x.t,url:x.u,date:x.d,source:x.s||'Presse sportive'}));
if(results[1].status==='fulfilled')state.sportItems=results[1].value;
if(results[2].status==='fulfilled')state.videoItems=results[2].value;
updateCards();renderLists();updateRegions()
}
function boot(){
if(!$('vm-wow-app'))return;
let stored;try{stored=localStorage.getItem(KEY)}catch{}
const param=new URL(location.href).searchParams.get('sport');
choose(param in SPORTS?param:stored in SPORTS?stored:'foot');
document.querySelectorAll('[data-wow-sport]').forEach(button=>button.addEventListener('click',()=>{const s=button.dataset.wowSport;choose(s,{push:true});document.getElementById('vm-wow-app').scrollIntoView({block:'start',behavior:'smooth'})}));
addEventListener('popstate',()=>{const s=new URL(location.href).searchParams.get('sport');choose(s in SPORTS?s:'foot')});
load();
document.addEventListener('visibilitychange',()=>{if(!document.hidden)load()});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})();