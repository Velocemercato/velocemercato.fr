(()=>{'use strict';
const $=id=>document.getElementById(id);
/* Vignettes : illustrations de la mascotte VM (maquette 01 du propriétaire), sans durée ni chiffre inventé. */
const ART=['/img/vm-art/vm-carte-foot.webp','/img/vm-art/vm-carte-france.webp','/img/vm-art/vm-carte-europe.webp','/img/vm-art/vm-carte-international.webp'];
const safe=url=>{try{const u=new URL(url,location.origin);return ['https:','http:'].includes(u.protocol)?u.href:null}catch{return null}};
const time=s=>{const d=new Date(s);return Number.isNaN(d.getTime())?'':d.toLocaleString('fr-FR',{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'})};
const el=(tag,cls,text)=>{const x=document.createElement(tag);if(cls)x.className=cls;if(text!==undefined)x.textContent=String(text);return x};
function putLink(element,url){const v=safe(url);if(!v)return;element.href=v;if(new URL(v).origin!==location.origin){element.target='_blank';element.rel='noopener noreferrer'}}
function fresh(v){const d=Date.parse(v);return Number.isFinite(d)&&Date.now()-d>=-60000&&Date.now()-d<=7*86400000}
async function get(path){const r=await fetch(path+'?v='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error(path);return r.json()}
function homeRows(json){return (json?.titres||[]).filter(x=>x.k==='foot'&&x.t&&x.u&&x.d&&fresh(x.d)&&safe(x.u)).sort((a,b)=>Date.parse(b.d)-Date.parse(a.d)).slice(0,12)}
function latestVids(json){return (Array.isArray(json)?json:[]).filter(x=>(x.universes||[]).includes('foot')&&x.plateformes?.youtube?.status==='published'&&/^https:\/\/www\.youtube\.com\/watch\?v=[\w-]{11}/.test(x.plateformes.youtube.url)).sort((a,b)=>Date.parse(b.date_publication)-Date.parse(a.date_publication));}
function drawRows(rows){if(!rows.length)return;
const a=rows[0];
$('vm-cinema-lead-title').textContent=a.t;
$('vm-cinema-lead-description').textContent='📰 '+(a.s||'Source vérifiée')+' · '+time(a.d);
putLink($('vm-cinema-lead-url'),a.u);putLink($('vm-cinema-lead-cta'),a.u);
const rec=$('vm-cinema-new-list'),trend=$('vm-cinema-trends');rec.replaceChildren();trend.replaceChildren();
for(const [i,item] of rows.slice(0,5).entries()){
const link=el('a'),badge=el('span','thumb'),pic=el('img'),text=el('b','',item.t),small=el('small','',(item.s||'Presse')+' · '+time(item.d));pic.src=ART[i%ART.length];pic.alt='';pic.loading='lazy';badge.append(pic);text.append(small);link.append(badge,text);putLink(link,item.u);rec.append(link);
const r=el('a'),number=el('span','',i+1);r.append(number,document.createTextNode(item.t));putLink(r,item.u);trend.append(r);
}}
function drawVideo(list){if(!list.length)return;const vid=list[0],url=vid.plateformes.youtube.url,id=new URL(url).searchParams.get('v');
$('vm-cinema-video-title').textContent=vid.titre||'La Pastille TV : JT Foot';
$('vm-cinema-video-description').textContent='▶ Édition publiée sur YouTube · '+time(vid.date_publication);
if(id)$('vm-cinema-video-image').src='https://i.ytimg.com/vi/'+id+'/hqdefault.jpg';
putLink($('vm-cinema-video-url'),url);putLink($('vm-cinema-video-cta'),url);
$('vm-cinema-video-cta').textContent='▶ REGARDER LE JT';
}
function init(){
document.querySelectorAll('[data-cinema-filter]').forEach(a=>a.addEventListener('click',()=>{const id=a.dataset.cinemaFilter;const b=document.querySelector('#cats button[data-cat="'+id+'"]');if(b)b.click()}));
Promise.allSettled([get('/fil.json'),get('/studio/diffusions.json')]).then(([news,vids])=>{
if(news.status==='fulfilled')drawRows(homeRows(news.value));
if(vids.status==='fulfilled')drawVideo(latestVids(vids.value));
}).catch(()=>{});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();