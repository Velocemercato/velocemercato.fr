(()=>{'use strict';
const KEY='vm-sport-favori';
const CFG={
 nba:{label:'NBA',emoji:'🏀',desc:'Basket US, franchises, joueurs, playoffs : les actualités de la semaine au même endroit.',official:'https://www.nba.com/games',officialLabel:'Scores & calendrier NBA',videos:'https://www.youtube.com/@NBA',videoLabel:'Vidéos de la NBA (chaîne officielle)',program:{widget:'scores',type:'competition',id:'149',href:'https://tv-sports.fr/basket/nba/scores',label:'Scores NBA'}},
 nfl:{label:'NFL',emoji:'🏈',desc:'Football américain, franchises, matches et temps forts de la semaine.',official:'https://www.nfl.com/schedules/',officialLabel:'Calendrier et matches NFL',videos:'https://www.youtube.com/@NFL',videoLabel:'Vidéos de la NFL (chaîne officielle)',program:{widget:'programme',type:'competition',id:'172',href:'https://tv-sports.fr/football-americain/nfl',label:'Programme TV NFL'}},
 f1:{label:'FORMULE 1',emoji:'🏎️',desc:'Grand Prix, écuries, pilotes et paddocks : tout ton univers F1.',official:'https://www.formula1.com/en/results/2026/races',officialLabel:'Résultats officiels de Formule 1',videos:'https://www.youtube.com/@F1',videoLabel:'Vidéos Formula 1 (chaîne officielle)',program:{widget:'programme',type:'sport',id:'102',href:'https://tv-sports.fr/formule-1/',label:'Programme TV Formule 1'}},
 motogp:{label:'MOTOGP',emoji:'🏍️',desc:'Les pilotes, les circuits et les courses : l’actualité moto en un clic.',official:'https://www.motogp.com/en/results',officialLabel:'Résultats officiels MotoGP',videos:'https://www.youtube.com/@motogp',videoLabel:'Vidéos MotoGP (chaîne officielle)',program:{widget:'programme',type:'sport',id:'677',href:'https://tv-sports.fr/motogp/',label:'Programme TV MotoGP'}},
 tennis:{label:'TENNIS',emoji:'🎾',desc:'ATP, WTA, tournois et grands chelems, selon l’actualité de la semaine.',official:'https://www.atptour.com/en/scores/current',officialLabel:'Résultats ATP',videos:'https://www.youtube.com/@atptour',videoLabel:'Vidéos ATP Tour',program:null},
 rugby:{label:'RUGBY',emoji:'🏉',desc:'Top 14, XV de France et grands tournois internationaux.',official:'https://www.sixnationsrugby.com/en/m6n/fixtures',officialLabel:'Calendrier Six Nations',videos:'https://www.youtube.com/@SixNationsRugby',videoLabel:'Vidéos Six Nations',program:null},
 cyclisme:{label:'CYCLISME',emoji:'🚴',desc:'Courses, pelotons, grands tours et actualités du vélo.',official:'https://www.uci.org/competition-hub',officialLabel:'Compétitions UCI',videos:'https://www.youtube.com/@letourdefrance',videoLabel:'Vidéos Tour de France',program:null}
};
const $=id=>document.getElementById(id);
const safe=(u)=>{try{const x=new URL(u);return x.protocol==='https:'?x.href:null}catch{return null}};
let current='nba',feed=null;
function choose(k,history=true){
 if(!Object.prototype.hasOwnProperty.call(CFG,k))k='nba';
 current=k;const c=CFG[k];document.body.dataset.sport=k;
 try{localStorage.setItem(KEY,k)}catch{}
 if(history){const url=new URL(location.href);url.searchParams.set('sport',k);window.history.pushState({sport:k},'',url.pathname+url.search+url.hash)}
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
 renderResults(c);renderNews();
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
function renderNews(){const box=$('sport-news');box.replaceChildren();const rows=(feed?.sports?.[current]||[]).filter(a=>a&&a.titre&&a.url&&a.source&&a.date).filter(a=>{let t=Date.parse(a.date);return Number.isFinite(t)&&Date.now()-t>=-60000&&Date.now()-t<=7*86400000});
 if(!rows.length){const p=document.createElement('p');p.className='placeholder';p.textContent=feed?'Pas de titre vérifié des sept derniers jours dans ce sport. Consulte les sources officielles pendant la prochaine mise à jour.':'Le fil sport est en cours de préparation. Les articles apparaîtront après une récupération de sources vérifiées.';box.append(p);return}
 $('date-source').textContent='Titres sourcés · relevé du '+humanDate(feed.misAJour);
 for(const [i,item]of rows.slice(0,18).entries()){const link=safe(item.url);if(!link||new URL(link).hostname!=='news.google.com')continue;
 const a=document.createElement('a');a.href=link;a.target='_blank';a.rel='noopener noreferrer';a.textContent=item.titre;
 const meta=document.createElement('small');meta.textContent='Source : '+item.source+' · '+humanDate(item.date);
 const card=document.createElement(i?'article':'article');card.className=i?'newsitem':'feature';card.append(a,document.createElement('br'),meta);box.append(card);}
}
async function loadNews(){try{const r=await fetch('/multisport/actualites.json?v='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error('http');const d=await r.json();if(!d||typeof d.sports!=='object')throw Error('format');feed=d;renderNews()}catch{feed=null;renderNews()}}
function init(){const p=new URL(location.href).searchParams.get('sport');let stored;try{stored=localStorage.getItem(KEY)}catch{}choose(p&&CFG[p]?p:stored&&CFG[stored]?stored:'nba',Boolean(!p));
 document.querySelectorAll('[data-sport-choice]').forEach(button=>button.addEventListener('click',()=>choose(button.dataset.sportChoice)));
 document.querySelectorAll('[data-home-foot]').forEach(a=>a.addEventListener('click',()=>{try{localStorage.setItem(KEY,'foot')}catch{}}));
 window.addEventListener('popstate',()=>{const q=new URL(location.href).searchParams.get('sport');choose(q&&CFG[q]?q:'nba',false)});
 loadNews();document.addEventListener('visibilitychange',()=>{if(!document.hidden)loadNews()});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();