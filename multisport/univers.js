/* VM : véritables titres par sport. Aucune vidéo, score ou statistique inventés. */
(()=>{'use strict';
const $=id=>document.getElementById(id);
const configs={
nba:{name:'NBA',icon:'🏀',img:'nba',results:'https://www.nba.com/games',videos:'https://www.youtube.com/@NBA',france:'Les Français en NBA',europe:'Les Européens en NBA',world:'Le basket US dans le monde'},
nfl:{name:'NFL',icon:'🏈',img:'nfl',results:'https://www.nfl.com/schedules/',videos:'https://www.youtube.com/@NFL',france:'La NFL vue de France',europe:'La NFL en Europe',world:'Football américain international'},
f1:{name:'FORMULE 1',icon:'🏁',img:'f1',results:'https://www.formula1.com/en/results/2026/races',videos:'https://www.youtube.com/@F1',france:'Pilotes et équipes françaises',europe:'Les Grands Prix européens',world:'La saison F1'},
motogp:{name:'MOTOGP',icon:'🏍️',img:'motogp',results:'https://www.motogp.com/en/results',videos:'https://www.youtube.com/@motogp',france:'Les pilotes français',europe:'Les Grands Prix européens',world:'Le championnat MotoGP'},
tennis:{name:'TENNIS',icon:'🎾',img:'tennis',results:'https://www.atptour.com/en/scores/current',videos:'https://www.youtube.com/@atptour',france:'Les Français en tournoi',europe:'Tournois ATP/WTA européens',world:'Le tennis mondial'},
rugby:{name:'RUGBY',icon:'🏉',img:'nfl',results:'https://www.sixnationsrugby.com/en/m6n/fixtures',videos:'https://www.youtube.com/@SixNationsRugby',france:'Top 14 et XV de France',europe:'Rugby européen',world:'Rugby international'},
cyclisme:{name:'CYCLISME',icon:'🚴',img:'europe',results:'https://www.uci.org/competition-hub',videos:'https://www.youtube.com/@letourdefrance',france:'Les Français du peloton',europe:'Les grandes classiques européennes',world:'Le cyclisme mondial'},
nhl:{name:'NHL',icon:'🏒',img:'international',results:'https://www.nhl.com/scores',videos:'https://www.youtube.com/@NHL',france:'Les hockeyeurs français',europe:'Les Européens en NHL',world:'Le hockey international'},
mlb:{name:'MLB',icon:'⚾',img:'europe',results:'https://www.mlb.com/scores',videos:'https://www.youtube.com/@MLB',france:'Baseball en France',europe:'Le baseball européen',world:'Le baseball américain'},
mma:{name:'MMA / UFC',icon:'🥊',img:'international',results:'https://www.ufc.com/events',videos:'https://www.youtube.com/@ufc',france:'Combattants français',europe:'Les rendez-vous européens',world:'Combats et événements du monde'},
ski:{name:'SKI',icon:'🎿',img:'europe',results:'https://www.fis-ski.com/',videos:'https://www.youtube.com/@fisalpine',france:'Les skieurs français',europe:'Les grandes stations européennes',world:'Les compétitions mondiales'}
};
const mode=document.body.dataset.mode;
const selected=mode==='sport'?document.body.dataset.currentSport:'portail';
const c=configs[selected]||configs.nba;
const icon=name=>configs[name]?.icon||'🏆';
const target=(row)=>{try{let u=new URL(row.url,location.origin);return ['https:','http:'].includes(u.protocol)?u.href:null}catch{return null}};
const recent=(row)=>{const t=Date.parse(row.date);return Number.isFinite(t)&&Date.now()-t>=-60000&&Date.now()-t<=7*86400000};
const fmt=t=>{let d=new Date(t);return Number.isNaN(d.getTime())?'Date non renseignée':d.toLocaleString('fr-FR',{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'})};
const create=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=String(text);return e};
/* Illustrations VM (mascotte du propriétaire) découpées dans la maquette 01 : une par sport, repli sur une image générique. */
const art=name=>'/img/vm-art/vm-carte-'+(configs[name]?.img||'europe')+'.webp';
let rows=[],video=null;
const portal=mode==='portal';
const EMPTY='Pas encore d’actu aujourd’hui pour ce sport — reviens un peu plus tard.';
const rel=t=>{const d=Date.now()-Date.parse(t);if(!Number.isFinite(d))return fmt(t);const m=Math.max(0,Math.round(d/60000));if(m<1)return 'À l’instant';if(m<60)return 'Il y a '+m+' min';const h=Math.round(m/60);if(h<24)return 'Il y a '+h+(h>1?' heures':' heure');const j=Math.round(h/24);return 'Il y a '+j+(j>1?' jours':' jour')};
const sportName=s=>configs[s]?.name||'SPORT';
function linkFor(row){const url=target(row);if(!url)return '/multisport/';return url}
function external(a,url){a.href=url;const u=new URL(url,location.origin);if(u.origin!==location.origin){a.target='_blank';a.rel='noopener noreferrer'}}
function allNews(data){
 const out=[];
 for(const [sport,items]of Object.entries(data?.sports||{})){
  if(!(sport in configs)||(!portal&&sport!==selected)||!Array.isArray(items))continue;
  for(const item of items){
   if(!window.VM_Multisport?.isRelevant(sport,item?.titre))continue;
   out.push({sport,title:item.titre,url:item.url,date:item.date,source:item.source,tags:item.rubriques||['international']});
  }
 }
 const unique=new Set();
 return out.filter(x=>x.title&&x.source&&target(x)&&recent(x)).sort((a,b)=>Date.parse(b.date)-Date.parse(a.date)).filter(x=>{const key=x.sport+'|'+x.title.toLowerCase();if(unique.has(key))return false;unique.add(key);return true}).slice(0,90);
}

function feature(prefix,row,alt){
 const a=$(prefix+'-url'),title=$(prefix+'-title'),summary=$(prefix+'-summary'),button=$(prefix+'-cta'),image=$(prefix+'-img');
 const tag=$(prefix+'-tag'),meta=$(prefix+'-meta');
 if(!row){title.textContent=prefix==='feature-a'?'Pas encore d’actu aujourd’hui':'Retrouve ton sport sur Véloce Mercato';summary.textContent='Reviens un peu plus tard : les titres sourcés du jour s’affichent dès la prochaine mise à jour.';if(meta)meta.textContent='';if(tag)tag.textContent='ACTU';external(a,'/multisport/');external(button,'/multisport/');image.src=art(selected);return}
 title.textContent=row.title;summary.textContent=portal&&meta?'Source : '+row.source+' · '+fmt(row.date):'📰 '+row.source+' · '+fmt(row.date);
 if(meta)meta.textContent='◷ '+rel(row.date);if(tag)tag.textContent=row.source==='La Pastille TV'?'PASTILLE TV':sportName(row.sport);
 image.src=art(row.sport);image.alt='Illustration originale '+(configs[row.sport]?.name||'Véloce Mercato');
 external(a,linkFor(row));external(button,linkFor(row));button.textContent=portal?'LIRE L’ACTU':'LIRE L’ACTU →';
}
function listNews(targetId,items,count,numbered){
 const el=$(targetId);el.replaceChildren();
 if(!items.length){el.append(create('p','empty',EMPTY));return}
 items.slice(0,count).forEach((r,i)=>{
  const a=create('a');external(a,linkFor(r));
  if(numbered){const li=create('li'),badge=create('b','',i+1);a.textContent=r.title;li.append(badge,a);el.append(li)}
  else{const ic=create('i','',icon(r.sport)),body=create('span','',r.title),small=create('small','',(r.source||'Source')+' · '+fmt(r.date));body.append(small);a.append(ic,body);el.append(a)}
 });
}
/* Portail (maquette 01) : vignette + sport + heure réelle de publication, sans durée inventée. */
function recentPortal(items){
 const el=$('recent-list');el.replaceChildren();
 if(!items.length){el.append(create('p','empty',EMPTY));return}
 items.slice(0,4).forEach((r,i)=>{const a=create('a');external(a,linkFor(r));
  const th=create('span','ms-thumb'),img=create('img');img.src=r.sport==='foot'&&i%2?'/img/vm-art/vm-carte-france.webp':art(r.sport);img.alt='';img.loading='lazy';img.width=1000;img.height=750;th.append(img,create('em','',(configs[r.sport]?.icon||'')+' '+sportName(r.sport)));
  const body=create('span'),t=create('span','t',r.title),small=create('small','',rel(r.date)+' · '+r.source);body.append(t,small);
  const chev=document.createElementNS('http://www.w3.org/2000/svg','svg');chev.setAttribute('aria-hidden','true');const use=document.createElementNS('http://www.w3.org/2000/svg','use');use.setAttribute('href','#i-chev');chev.append(use);
  a.append(th,body,chev);el.append(a)});
}
/* Tendances = sports les plus couverts aujourd'hui (nombre réel de titres sourcés), avec leur dernier titre. */
function trendsPortal(items){
 const el=$('follow-list');el.replaceChildren();
 const by=new Map();for(const r of items){if(!by.has(r.sport))by.set(r.sport,[]);by.get(r.sport).push(r)}
 const top=[...by.entries()].sort((a,b)=>b[1].length-a[1].length).slice(0,5);
 if(!top.length){const li=create('li');li.append(create('span','',EMPTY));el.append(li);return}
 top.forEach(([sport,list],i)=>{const li=create('li'),a=create('a','',sportName(sport)+' : '+list[0].title);external(a,'/multisport/'+sport+'/');
  const n=create('span','n',String(list.length));n.title=list.length+' actus sourcées aujourd’hui';const sr=create('span','sr-only',' actus du jour');n.append(sr);
  li.append(create('b','',i+1),a,n);el.append(li)});
}
function stories(items){
 const el=$('news-list');el.replaceChildren();
 if(!items.length){el.append(create('p','empty',EMPTY));return}
 items.slice(0,24).forEach(r=>{const box=create('article','story'),a=create('a','',r.title),small=create('small','',icon(r.sport)+' '+(configs[r.sport]?.name||'Sport')+' · '+r.source+' · '+fmt(r.date));external(a,linkFor(r));box.append(a,small);el.append(box)});
}
function fill(){
 feature('feature-a',rows[0]);feature('feature-b',rows[1]||rows[0]);
 if(portal){recentPortal(rows);trendsPortal(rows)}else{listNews('recent-list',rows,5,false);listNews('follow-list',rows,5,true)}stories(rows);
 $('france-label').textContent=mode==='sport'?c.france:'Clubs et sportifs français';
 $('europe-label').textContent=mode==='sport'?c.europe:'Compétitions et acteurs européens';
 $('international-label').textContent=mode==='sport'?c.world:'Toute l’actualité sportive mondiale';
 $('list-title').textContent=mode==='sport'?'⚡ LES ACTUS '+c.name+' DU JOUR':'⚡ TOUTES LES ACTUS DU JOUR';
 $('official-results').textContent=mode==='sport'?'Consulter les résultats officiels '+c.name+' ↗':'Choisir mon sport et ses résultats ↗';
 external($('official-results'),mode==='sport'?c.results:'/multisport/');
 $('official-videos').textContent=mode==='sport'?'Voir les vidéos officielles '+c.name+' ↗':'Les replays Multisport ↗';
 external($('official-videos'),mode==='sport'?c.videos:'/studio.html?univers=multisport#tv');
 $('video-note').textContent='Les Pastilles Multisport publiées sont regroupées dans les replays. Les vidéos des fédérations et compétitions complètent la sélection.';
 const female=rows.filter(r=>r.tags.includes('feminin')||/\bféminin(?:e|es|s)?\b|\bWTA\b|\bWNBA\b|\bPWHL\b|\bfemmes\b/i.test(r.title));
 const f=$('female-list');f.replaceChildren();
 if(!female.length){f.append(create('p','', 'Pas encore d’actu vérifiée sur les compétitions féminines aujourd’hui — reviens un peu plus tard.'))}else for(const r of female.slice(0,4)){const p=create('p'),a=create('a','',r.title);external(a,linkFor(r));p.append(a);f.append(p)}
 if(mode==='sport')for(const nav of document.querySelectorAll('.sport-nav a'))nav.setAttribute('aria-current',nav.dataset.sport===selected?'page':'false');
 if(mode==='sport'){
 const colors={nba:'#fd9d43',nfl:'#50aeff',f1:'#fd3555',motogp:'#ff5a50',tennis:'#e4db4e',ski:'#a9eaff'};
 const center=document.querySelector('.banner .scene:nth-child(2) img');if(center)center.src=art(selected);
 const hero=$('hero-title');hero.replaceChildren(create('strong','', 'VM'),document.createTextNode(' '+c.name));
 $('hero-subtitle').textContent="Ton sport, tes actus, ton univers";
 }
 // Capsules géographiques : les zones ont des URL de sélection dédiées.
 for(const [id,reg] of [['france','france'],['europe','europe'],['international','international']]){
  const a=$(id);const list=rows.filter(r=>reg==='international'||r.tags.includes(reg));
  a.href='#actualites';a.dataset.region=reg;
  a.title=list.length+' actus vérifiées de cette rubrique';
  const count=$(id+'-count');if(count)count.textContent=list.length?list.length+(list.length>1?' actus du jour':' actu du jour')+' ›':'Pas encore d’actu aujourd’hui';
 }
}
function pickRegion(reg){
 const data=rows.filter(r=>reg==='international'||r.tags.includes(reg));
 stories(data);$('list-title').textContent=reg==='france'?'🇫🇷 ACTUS FRANCE':reg==='europe'?'🇪🇺 ACTUS EUROPE':'🌍 ACTUS INTERNATIONALES';
}
async function load(){
const urls=['/multisport/actualites.json','/studio/diffusions.json'];
const results=await Promise.allSettled(urls.map(url=>fetch(url+'?t='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(url);return r.json()})));
const json=i=>results[i].status==='fulfilled'?results[i].value:null;
rows=allNews(json(0));
const videos=json(1);video=Array.isArray(videos)?videos.find(x=>(x.universes||[]).includes('multisport')&&x.plateformes?.youtube?.status==='published'):null;
fill();
if(mode==='portal'&&video&&/^https:\/\/www\.youtube\.com\/watch\?v=[A-Za-z0-9_-]{11}$/.test(video.plateformes.youtube.url)){
const row={sport:'multisport',title:video.titre,date:video.date_publication,url:video.plateformes.youtube.url,source:'La Pastille TV'};feature('feature-a',row);$('feature-a-img').src='/img/studio/plateau-veloce-600.webp';$('feature-a-play').hidden=false;$('feature-a-cta').textContent=portal?'REGARDER L’ÉPISODE':'▶ REGARDER LA PASTILLE';
}
}
function init(){
 const qp=new URL(location.href).searchParams;
 if(mode==='portal'&&configs[qp.get('sport')]){
   const dest='/multisport/'+encodeURIComponent(qp.get('sport'))+'/';
   location.replace(dest+(qp.get('rubrique')?'?rubrique='+encodeURIComponent(qp.get('rubrique')):''));return;
 }
 document.querySelectorAll('.ms-arrow').forEach(b=>b.addEventListener('click',()=>{const nav=$('sports');if(nav)nav.scrollBy({left:Number(b.dataset.scroll)*nav.clientWidth*.8,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'})}));
 document.querySelectorAll('.region').forEach(a=>a.addEventListener('click',()=>pickRegion(a.dataset.region)));
 for(const a of document.querySelectorAll('.sport-nav a'))a.addEventListener('click',()=>{try{localStorage.setItem('vm-sport-favori',a.dataset.sport)}catch{}});
 load().then(()=>{const region=qp.get('rubrique');if(['france','europe','international'].includes(region)){pickRegion(region);document.getElementById('actualites').scrollIntoView({block:'start'})}}).catch(()=>{});
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)load()});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
