(()=>{
'use strict';
const root=document.getElementById('vm-cinema');if(!root)return;
const SPORT={
foot:{name:'FOOT',icon:'⚽',route:'/#feed-title',video:'/#videos'},
nba:{name:'NBA',icon:'🏀',route:'/multisport/?sport=nba',video:'https://www.youtube.com/@NBA'},
nfl:{name:'NFL',icon:'🏈',route:'/multisport/?sport=nfl',video:'https://www.youtube.com/@NFL'},
f1:{name:'FORMULE 1',icon:'🏎️',route:'/multisport/?sport=f1',video:'https://www.youtube.com/@F1'},
motogp:{name:'MOTOGP',icon:'🏍️',route:'/multisport/?sport=motogp',video:'https://www.youtube.com/@motogp'},
tennis:{name:'TENNIS',icon:'🎾',route:'/multisport/?sport=tennis',video:'https://www.youtube.com/@atptour'},
rugby:{name:'RUGBY',icon:'🏉',route:'/multisport/?sport=rugby',video:'https://www.youtube.com/@SixNationsRugby'},
cyclisme:{name:'CYCLISME',icon:'🚴',route:'/multisport/?sport=cyclisme',video:'https://www.youtube.com/@letourdefrance'},
nhl:{name:'NHL',icon:'🏒',route:'/multisport/?sport=nhl',video:'https://www.youtube.com/@NHL'},
mlb:{name:'MLB',icon:'⚾',route:'/multisport/?sport=mlb',video:'https://www.youtube.com/@MLB'},
mma:{name:'MMA',icon:'🥊',route:'/multisport/?sport=mma',video:'https://www.youtube.com/@ufc'}
};
const PREF='vm-sport-favori',EL=id=>document.getElementById(id);
let current='foot',footRows=[],sportFeed=null,lastFootVideo=null;
const isTrusted=url=>{try{let u=new URL(url,location.origin);return u.protocol==='https:'||u.origin===location.origin?u.href:null}catch{return null}};
function when(date){const t=Date.parse(date||'');return Number.isFinite(t)?new Date(t).toLocaleString('fr-FR',{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'}):'Date indisponible'}
function within7(d){const t=Date.parse(d||'');const n=Date.now();return Number.isFinite(t)&&n-t>=-3600000&&n-t<7*86400000}
function relevantFoot(title){const f=/ligue\s*[12]|\bPSG\b|Marseille|\bOM\b|Lyon|\bOL\b|Lens|Rennes|Monaco|Nantes|Brest|Lille|Nice|Saint-Étienne|Montpellier|Bordeaux|Strasbourg|National|Coupe de France|fran[cç]ais|[eé]quipe de France/i;const e=/Premier League|Liga|Serie A|Bundesliga|Liga Portugal|Champions League|europ[eé]en|Liverpool|Arsenal|Manchester|Barcelon|Real Madrid|Bayern|Milan|Juventus|Napoli|Atl[eé]tico|Europa League/i;const out=['international'];if(f.test(title))out.push('france');if(e.test(title))out.push('europe');return out}
function all(){if(current==='foot')return footRows;const rows=sportFeed?.sports?.[current]||[];return rows.filter(x=>x&&x.titre&&x.date&&x.source&&isTrusted(x.url)&&within7(x.date)).map(x=>({title:String(x.titre),url:x.url,source:String(x.source),date:x.date,rubriques:Array.isArray(x.rubriques)?x.rubriques:['international']})).slice(0,22)}
function makeLink(item){const link=document.createElement('a');const url=isTrusted(item.url);link.href=url||SPORT[current].route;link.textContent=item.title||'Voir la source';if(url&&new URL(url).origin!==location.origin){link.target='_blank';link.rel='noopener noreferrer'}return link}
function text(id,value){const el=EL(id);if(el)el.textContent=value}
function setHref(id,value){const el=EL(id);if(!el)return;el.href=isTrusted(value)||value;const u=new URL(el.href);if(u.origin!==location.origin){el.target='_blank';el.rel='noopener noreferrer'}else{el.removeAttribute('target');el.removeAttribute('rel')}}
function empty(node,message){node.replaceChildren();const p=document.createElement('p');p.textContent=message;p.style.color='#aebed9';p.style.fontSize='.8rem';node.append(p)}
function list(id,rows,trend=false){const box=EL(id);box.replaceChildren();if(!rows.length){empty(box,'Aucune actualité vérifiée pour le moment.');return}for(const [idx,row] of rows.entries()){const link=makeLink(row);if(trend){const rank=document.createElement('em');rank.textContent=String(idx+1);link.prepend(rank)}const meta=document.createElement('small');meta.textContent=(row.source||'Presse')+' · '+when(row.date);link.append(meta);box.append(link)}}
function region(id,rows){const el=EL(id);el.replaceChildren();if(!rows.length){empty(el,'Pas de titre classé dans cette zone cette semaine.');return}for(const row of rows.slice(0,2)){const a=makeLink(row),meta=document.createElement('small');meta.textContent=row.source+' · '+when(row.date);el.append(a,meta)}}
function render(){
const sport=SPORT[current],rows=all();
root.dataset.activeSport=current;document.body.dataset.vmSport=current;
for(const btn of root.querySelectorAll('[data-cinema-sport]')){const active=btn.dataset.cinemaSport===current;btn.setAttribute('aria-pressed',String(active))}
text('vm-cinema-sport-name',sport.icon+' '+sport.name);
text('vm-cinema-feature-title','ACTU DU JOUR · '+sport.name);text('vm-cinema-next-title','À NE PAS MANQUER · '+sport.name);
text('vm-cinema-region-france','🇫🇷 FRANCE');text('vm-cinema-region-europe','🇪🇺 EUROPE');text('vm-cinema-region-international','🌍 INTERNATIONAL');
text('vm-cinema-sport-icon',sport.icon);text('vm-cinema-sport-icon2',sport.icon);
const first=rows[0],second=rows[1]||rows[0];
function feature(prefix,row){
 if(!row){text(prefix+'-story','Les informations arrivent sur Véloce Mercato');text(prefix+'-detail','Le robot vérifie les titres et les dates avant de les afficher.');setHref(prefix+'-link',sport.route);text(prefix+'-link','Découvrir le sport →');text(prefix+'-meta','Les actus sont actualisées automatiquement');return}
 text(prefix+'-story',row.title);text(prefix+'-detail','Source : '+row.source+' · '+when(row.date));setHref(prefix+'-link',row.url);text(prefix+'-link','LIRE L’ACTU  ›');text(prefix+'-meta','Actu sourcée · '+when(row.date));
}
feature('vm-cinema-first',first);feature('vm-cinema-second',second);
list('vm-cinema-latest',rows.slice(2,7));list('vm-cinema-trends',rows.slice(0,5),true);
const strip=EL('vm-cinema-flash-text');strip.textContent=first?'🔥 '+first.title:'Le fil '+sport.name+' sera rempli dès qu’une information récente sera vérifiée.';
setHref('vm-cinema-flash-all',sport.route);
const regions={france:rows.filter(x=>x.rubriques?.includes('france')),europe:rows.filter(x=>x.rubriques?.includes('europe')),international:rows};
region('vm-cinema-france-list',regions.france);region('vm-cinema-europe-list',regions.europe);region('vm-cinema-international-list',regions.international);
setHref('vm-cinema-page-sport',sport.route);text('vm-cinema-page-sport',current==='foot'?'⚽ VERSION FOOT COMPLÈTE':'🏆 VOIR TOUT L’UNIVERS '+sport.name);
setHref('vm-cinema-video-link',current==='foot'&&lastFootVideo?lastFootVideo:sport.video);
text('vm-cinema-video-link',current==='foot'&&lastFootVideo?'▶ REGARDER LA PASTILLE FOOT':'▶ VIDÉOS OFFICIELLES');
text('vm-cinema-foot-return',current==='foot'?'Toute la partie Foot est disponible sous cet accueil.':'Le site change pour ton sport : tu peux toujours revenir au Foot.');
const footLegacy=document.querySelector('main.home-main'),classic=document.querySelectorAll('body.home-simple > section.v2'); if(footLegacy)footLegacy.hidden=current!=='foot'; for(const element of classic)element.hidden=current!=='foot';
}
function choose(sport,record=true){if(!SPORT[sport])sport='foot';current=sport;try{localStorage.setItem(PREF,sport)}catch{}
if(record){const u=new URL(location.href);if(sport==='foot')u.searchParams.delete('sport');else u.searchParams.set('sport',sport);history.pushState({sport},'',u.pathname+u.search+u.hash)}render()}
async function getJSON(path){const r=await fetch(path+'?v='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);return r.json()}
function makeFoot(raw){return (raw?.titres||[]).filter(x=>x&&x.k==='foot'&&x.t&&x.s&&x.d&&isTrusted(x.u)&&within7(x.d)).sort((a,b)=>Date.parse(b.d)-Date.parse(a.d)).map(x=>({title:String(x.t),source:String(x.s),url:x.u,date:x.d,rubriques:relevantFoot(x.t)})).slice(0,45)}
async function refresh(){const [a,b,c]=await Promise.allSettled([getJSON('/fil.json'),getJSON('/multisport/actualites.json'),getJSON('/studio/diffusions.json')]);if(a.status==='fulfilled')footRows=makeFoot(a.value);if(b.status==='fulfilled'&&b.value?.sports)sportFeed=b.value;if(c.status==='fulfilled'){const foot=(Array.isArray(c.value)?c.value:[]).filter(x=>x?.plateformes?.youtube?.status==='published'&&x.universes?.includes('foot')&&isTrusted(x.plateformes.youtube.url)).sort((x,y)=>Date.parse(y.date_publication)-Date.parse(x.date_publication));lastFootVideo=foot[0]?.plateformes.youtube.url||null}render()}
function start(){let initial='foot';const qs=new URL(location.href).searchParams.get('sport');try{initial=qs&&SPORT[qs]?qs:SPORT[localStorage.getItem(PREF)]?localStorage.getItem(PREF):'foot'}catch{}choose(initial,false);
root.querySelectorAll('[data-cinema-sport]').forEach(btn=>btn.addEventListener('click',()=>choose(btn.dataset.cinemaSport)));
addEventListener('popstate',()=>{const sport=new URL(location.href).searchParams.get('sport');choose(sport&&SPORT[sport]?sport:'foot',false)});
refresh();document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh()});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();