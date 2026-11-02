(()=>{'use strict';
const KEY='vm-sport-favori';
const CFG={
 nba:{label:'NBA',emoji:'🏀',desc:'Basket US, franchises, joueurs, playoffs : les actualités de la semaine au même endroit.',official:'https://www.nba.com/games',officialLabel:'Scores & calendrier NBA',videos:'https://www.youtube.com/@NBA',videoLabel:'Vidéos de la NBA (chaîne officielle)',program:{widget:'scores',type:'competition',id:'149',href:'https://tv-sports.fr/basket/nba/scores',label:'Scores NBA'}},
 nfl:{label:'NFL',emoji:'🏈',desc:'Football américain, franchises, matches et temps forts de la semaine.',official:'https://www.nfl.com/schedules/',officialLabel:'Calendrier et matches NFL',videos:'https://www.youtube.com/@NFL',videoLabel:'Vidéos de la NFL (chaîne officielle)',program:{widget:'programme',type:'competition',id:'172',href:'https://tv-sports.fr/football-americain/nfl',label:'Programme TV NFL'}},
 f1:{label:'FORMULE 1',emoji:'🏎️',desc:'Grand Prix, écuries, pilotes et paddocks : tout ton univers F1.',official:'https://www.formula1.com/en/results/2026/races',officialLabel:'Résultats officiels de Formule 1',videos:'https://www.youtube.com/@F1',videoLabel:'Vidéos Formula 1 (chaîne officielle)',program:{widget:'programme',type:'sport',id:'102',href:'https://tv-sports.fr/formule-1/',label:'Programme TV Formule 1'}},
 motogp:{label:'MOTOGP',emoji:'🏍️',desc:'Les pilotes, les circuits et les courses : l’actualité moto en un clic.',official:'https://www.motogp.com/en/results',officialLabel:'Résultats officiels MotoGP',videos:'https://www.youtube.com/@motogp',videoLabel:'Vidéos MotoGP (chaîne officielle)',program:{widget:'programme',type:'sport',id:'677',href:'https://tv-sports.fr/motogp/',label:'Programme TV MotoGP'}},
 tennis:{label:'TENNIS',emoji:'🎾',desc:'ATP, WTA, tournois et grands chelems, selon l’actualité de la semaine.',official:'https://www.atptour.com/en/scores/current',officialLabel:'Résultats ATP',videos:'https://www.youtube.com/@atptour',videoLabel:'Vidéos ATP Tour',program:null},
 rugby:{label:'RUGBY',emoji:'🏉',desc:'Top 14, XV de France et grands tournois internationaux.',official:'https://www.sixnationsrugby.com/en/m6n/fixtures',officialLabel:'Calendrier Six Nations',videos:'https://www.youtube.com/@SixNationsRugby',videoLabel:'Vidéos Six Nations',program:null},
 cyclisme:{label:'CYCLISME',emoji:'🚴',desc:'Courses, pelotons, grands tours et actualités du vélo.',official:'https://www.uci.org/competition-hub',officialLabel:'Compétitions UCI',videos:'https://www.youtube.com/@letourdefrance',videoLabel:'Vidéos Tour de France',program:null},
 nhl:{label:'NHL',emoji:'🏒',desc:'Hockey sur glace, franchises US et canadiennes, matches et playoffs.',official:'https://www.nhl.com/scores',officialLabel:'Résultats officiels NHL',videos:'https://www.youtube.com/@NHL',videoLabel:'Vidéos NHL (chaîne officielle)',program:null},
 mlb:{label:'MLB',emoji:'⚾',desc:'Baseball américain : World Series, équipes et stars.',official:'https://www.mlb.com/scores',officialLabel:'Résultats officiels MLB',videos:'https://www.youtube.com/@MLB',videoLabel:'Vidéos MLB (chaîne officielle)',program:null},
 mma:{label:'MMA / UFC',emoji:'🥊',desc:'Arts martiaux mixtes, grands combats, calendriers et actualités UFC.',official:'https://www.ufc.com/events',officialLabel:'Calendrier officiel UFC',videos:'https://www.youtube.com/@ufc',videoLabel:'Vidéos UFC (chaîne officielle)',program:null}
};
const $=id=>document.getElementById(id);
const safe=(u)=>{try{const x=new URL(u);return x.protocol==='https:'?x.href:null}catch{return null}};
let current='nba',feed=null,currentRubrique='une';
const RUBRIQUES=['une','france','europe','international'];
const RUBRIQUE_LABELS={une:'À la une',france:'France',europe:'Europe',international:'International'};
function choose(k,history=true){
 if(!Object.prototype.hasOwnProperty.call(CFG,k))k='nba';
 current=k;const c=CFG[k];document.body.dataset.sport=k;
 try{localStorage.setItem(KEY,k)}catch{}
 if(history){currentRubrique='une';const url=new URL(location.href);url.searchParams.set('sport',k);url.searchParams.delete('rubrique');window.history.pushState({sport:k,rubrique:'une'},'',url.pathname+url.search+url.hash)}
 else {const wanted=new URL(location.href).searchParams.get('rubrique');currentRubrique=RUBRIQUES.includes(wanted)?wanted:'une';}
 document.querySelectorAll('[data-sport-choice]').forEach(b=>{const sel=b.dataset.sportChoice===k;b.setAttribute('aria-pressed',String(sel));if(sel)b.scrollIntoView({behavior:'auto',block:'nearest',inline:'nearest'})});
 $('sport-hero').dataset.ball=c.emoji;
 $('sport-title').replaceChildren(document.createTextNode('VÉLOCE '));const em=document.createElement('em');em.textContent=c.label;$('sport-title').append(em);
 document.title='Véloce '+c.label+' — actus, résultats et vidéos | Véloce Mercato';
 $('sport-description').textContent=c.desc;$('news-heading').textContent=c.emoji+' '+c.label+' : à la une';
 $('results-heading').textContent='🏆 '+c.label+' : résultats & programme';
 $('results-blurb').textContent=k==='nba'?'Scores et matches NBA fournis par un service externe, actualisés selon sa disponibilité.':'Calendrier, résultats et programme publiés par les sites spécialisés.';
 $('video-heading').textContent='🎬 Vidéos '+c.label;
 $('video-note').textContent='Les éditions originales de La Pastille '+c.label+' ne sont pas encore produites. Voici les publications de la chaîne officielle.';
 $('favorite-message').textContent='Préférence « '+c.label+' » mémorisée sur cet appareil. Tu peux changer de sport à tout moment.';
 renderResults(c);renderRubriqueTabs();renderNews();renderRegionalOverview();renderTicker();
}
function addLink(box,label,url){const u=safe(url);if(!u)return;const a=document.createElement('a');a.href=u;a.target='_blank';a.rel='noopener noreferrer';a.textContent='↗ '+label;box.append(a)}
function renderResults(c){const links=$('results-links');links.replaceChildren();addLink(links,c.officialLabel,c.official);const vids=$('video-links');vids.replaceChildren();addLink(vids,c.videoLabel,c.videos);
 const p=$('program');p.replaceChildren();if(!c.program){const small=document.createElement('p');small.className='placeholder';small.textContent='Résultats officiels accessibles avec le lien ci-dessus. Pas de widget de score direct intégré pour ce sport.';p.append(small);return}
 const button=document.createElement('button');button.type='button';button.textContent='📊 Charger '+c.program.label;const fallback=document.createElement('p');fallback.textContent='Widget externe TV Sports, chargé uniquement après ton clic.';p.append(button,fallback);
 button.addEventListener('click',()=>{const sport=c.program;const anchor=document.createElement('a');anchor.className='tvsports-widget';anchor.href=sport.href;anchor.dataset.widget=sport.widget;anchor.dataset.targetType=sport.type;anchor.dataset.targetId=sport.id;anchor.dataset.limit='10';anchor.dataset.theme='auto';if(sport.widget==='programme')anchor.dataset.directOnly='0';anchor.textContent=sport.label;
 p.replaceChildren(anchor);const script=document.createElement('script');script.src='https://tv-sports.fr/widget.js';script.async=true;script.onerror=()=>{const a=document.createElement('a');a.href=sport.href;a.target='_blank';a.rel='noopener noreferrer';a.textContent='Ouvrir le programme sur TV Sports';p.append(a)};p.append(script);
 },{once:true});
}
function humanDate(s){const d=new Date(s);return Number.isNaN(d.getTime())?'Date non disponible':d.toLocaleString('fr-FR',{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'})}

function allNews(){
return (feed?.sports?.[current]||[]).filter(a=>a&&a.titre&&a.url&&a.source&&a.date)
.filter(a=>{let t=Date.parse(a.date);return Number.isFinite(t)&&Date.now()-t>=-60000&&Date.now()-t<=7*86400000});
}
function categories(item){
return Array.isArray(item.rubriques)?item.rubriques.filter(x=>RUBRIQUES.includes(x)):['international'];
}
function listFor(region){const all=allNews();return region==='une'||region==='international'?all:all.filter(a=>categories(a).includes(region));}
function renderRubriqueTabs(){
for(const button of document.querySelectorAll('[data-news-rubrique]')){
const reg=button.dataset.newsRubrique;
button.setAttribute('aria-pressed',String(currentRubrique===reg));
}
for(const el of document.querySelectorAll('[data-count-rubrique]')){
 const count=listFor(el.dataset.countRubrique).length;el.textContent=feed?String(count):'';
}
$('news-heading').textContent=CFG[current].emoji+' '+CFG[current].label+' : '+RUBRIQUE_LABELS[currentRubrique];
}
function selectRubrique(rubrique,updateUrl=true){
if(!RUBRIQUES.includes(rubrique))return;currentRubrique=rubrique;
if(updateUrl){const url=new URL(location.href);
 if(rubrique==='une')url.searchParams.delete('rubrique');else url.searchParams.set('rubrique',rubrique);
 window.history.pushState({sport:current,rubrique},'',url.pathname+url.search+url.hash)}
renderRubriqueTabs();renderNews();
}
function renderTicker(){
const el=$('sport-ticker');el.replaceChildren();
const rows=allNews().slice(0,3);
if(!rows.length){el.textContent='Les nouvelles vérifiées des sept derniers jours apparaîtront ici.';return}
for(const [i,row] of rows.entries()){
const link=safe(row.url);if(!link||new URL(link).hostname!=='news.google.com')continue;
if(i){const sep=document.createElement('span');sep.textContent='   ◆   ';el.append(sep)}
const a=document.createElement('a');a.href=link;a.target='_blank';a.rel='noopener noreferrer';a.textContent=row.titre;a.style.color='inherit';a.style.textDecoration='none';el.append(a);
}}
function renderNews(){
const box=$('sport-news');box.replaceChildren();
const rows=listFor(currentRubrique);
renderRubriqueTabs();
if(!rows.length){
const p=document.createElement('p');p.className='placeholder';
p.textContent=feed?(currentRubrique==='une'||currentRubrique==='international'
?'Pas de titre récent vérifié pour ce sport cette semaine. Les prochaines mises à jour pourront compléter la rubrique.'
:'Aucun titre vérifié pour la rubrique '+RUBRIQUE_LABELS[currentRubrique]+' cette semaine. Nous n’attribuons pas artificiellement une zone géographique à un article.')
:'Chargement du fil sourcé de la semaine en cours.';
box.append(p);return}
$('date-source').textContent='Titres sourcés · '+humanDate(feed.misAJour)+' · '+rows.length+' articles';
const c=CFG[current];
for(const [i,item] of rows.slice(0,20).entries()){
const link=safe(item.url);if(!link||new URL(link).hostname!=='news.google.com')continue;
const card=document.createElement('article');card.className='vm-news-card';
const emoji=document.createElement('div');emoji.className='vm-news-icon';emoji.textContent=c.emoji;emoji.setAttribute('aria-hidden','true');
const body=document.createElement('div');
const a=document.createElement('a');a.href=link;a.target='_blank';a.rel='noopener noreferrer';a.textContent=item.titre;
const meta=document.createElement('div');meta.className='vm-news-meta';meta.textContent='📰 '+item.source+' · '+humanDate(item.date);
const tags=document.createElement('div');tags.className='vm-news-tags';
for(const zone of categories(item)){const t=document.createElement('span');t.textContent=RUBRIQUE_LABELS[zone];tags.append(t)}
body.append(a,meta,tags);card.append(emoji,body);box.append(card);
}}
function renderRegionalOverview(){
for(const reg of ['france','europe','international']){
const holder=$('region-'+reg);holder.replaceChildren();
const rows=listFor(reg).slice(0,3);
if(!rows.length){const empty=document.createElement('p');empty.className='placeholder';empty.textContent='Aucune actualité sourcée dans cette rubrique cette semaine.';holder.append(empty);continue}
for(const row of rows){const link=safe(row.url);if(!link||new URL(link).hostname!=='news.google.com')continue;
const container=document.createElement('div'),a=document.createElement('a'),small=document.createElement('small');
a.href=link;a.target='_blank';a.rel='noopener noreferrer';a.textContent=row.titre;small.textContent=row.source+' · '+humanDate(row.date);
container.append(a,small);holder.append(container);
}}
}
async function loadNews(){try{const r=await fetch('/multisport/actualites.json?v='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error('http');const d=await r.json();if(!d||typeof d.sports!=='object')throw Error('format');feed=d;renderNews();renderRegionalOverview();renderTicker()}catch{feed=null;renderNews();renderRegionalOverview();renderTicker()}}
function init(){const p=new URL(location.href).searchParams.get('sport');let stored;try{stored=localStorage.getItem(KEY)}catch{}choose(p&&CFG[p]?p:stored&&CFG[stored]?stored:'nba',Boolean(!p));
 document.querySelectorAll('[data-sport-choice]').forEach(button=>button.addEventListener('click',()=>choose(button.dataset.sportChoice)));
 document.querySelectorAll('[data-home-foot]').forEach(a=>a.addEventListener('click',()=>{try{localStorage.setItem(KEY,'foot')}catch{}}));
 document.querySelectorAll('[data-news-rubrique]').forEach(button=>button.addEventListener('click',()=>selectRubrique(button.dataset.newsRubrique)));
 document.querySelectorAll('[data-open-rubrique]').forEach(button=>button.addEventListener('click',()=>{selectRubrique(button.dataset.openRubrique);$('actus-sport').scrollIntoView({behavior:'smooth',block:'start'})}));
 window.addEventListener('popstate',()=>{const q=new URL(location.href).searchParams.get('sport');choose(q&&CFG[q]?q:'nba',false)});
 loadNews();document.addEventListener('visibilitychange',()=>{if(!document.hidden)loadNews()});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();