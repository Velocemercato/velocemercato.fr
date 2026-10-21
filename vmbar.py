"""Barre de navigation commune des univers VM (Foot, Gaming, Actus, Vidéos, Studio, Soutenir).
Usage : python vmbar.py  (met à jour les pages)  ;  build_pages.py l'utilise pour les articles."""
import re,sys
CSS='''<style id="vmbar-css">
.vmbar{background:#04060f;border-bottom:1px solid rgba(255,255,255,.12);font:700 13px/1 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;position:relative;z-index:70}
.vmbar-in{max-width:1180px;margin:0 auto;display:flex;align-items:center;gap:4px;padding:6px max(10px,env(safe-area-inset-left,0px));overflow-x:auto;scrollbar-width:none}
.vmbar-in::-webkit-scrollbar{display:none}
.vmbar a{flex:none;color:#cfd6ea;text-decoration:none;padding:7px 10px;border-radius:999px;letter-spacing:.04em;text-transform:uppercase;white-space:nowrap}
.vmbar a:hover{background:rgba(255,255,255,.08);color:#fff}
.vmbar a:focus-visible{outline:2px solid #f4cf55;outline-offset:2px}
.vmbar .vmb-logo small{font:800 9px/1 system-ui,sans-serif;font-style:normal;letter-spacing:.06em;margin-left:4px;vertical-align:middle}
.vmbar .vmb-logo{font:italic 900 18px/1 Impact,"Arial Black",sans-serif;color:#04060f;background:linear-gradient(135deg,#ffe58a,#f4cf55 55%,#c9971a);padding:6px 9px;border-radius:8px;margin-right:4px;letter-spacing:.02em}
.vmbar a.on{color:#04060f;background:#fff}
.vmbar a.on.f{background:#f4cf55}.vmbar a.on.g{background:#d6ff6e}.vmbar a.on.a{background:#ff5a6e;color:#fff}
.vmbar .vmb-don{margin-left:auto;background:#f4cf55;color:#0b1533}
.vmbar a.s{background:#e1243a;color:#fff}.vmbar a.s.on{background:#fff;color:#e1243a}
@media(max-width:520px){.vmbar a{padding:7px 8px;font-size:12px}}
</style>'''

APP_COL={'foot': '#060b1d', 'gaming': '#0b0a1c', 'actus': '#0a1430', 'arena': '#140a14', 'tv': '#0a0814', 'allolivre': '#c4121b', 'annonces': '#c4121b', 'papiers': '#14100a'}
def app_head(app='foot'):
    app=app if app in APP_COL else 'foot'
    return f'<link rel="manifest" href="/app/{app}.webmanifest" id="vmapp-m"><meta name="theme-color" content="{APP_COL[app]}" id="vmapp-t"><link rel="apple-touch-icon" href="/app/{app}-apple.png" id="vmapp-i">'
APP_HEAD=app_head()
SHARE_CSS='''<style id="vmshare-css">
.vminst{display:none;position:fixed;left:14px;bottom:calc(14px + env(safe-area-inset-bottom,0px));z-index:75;align-items:center;gap:6px;font:800 14px/1 system-ui,sans-serif;padding:12px 16px;border-radius:999px;border:2px solid #000;background:#1d3fb8;color:#fff;box-shadow:3px 3px 0 #000;cursor:pointer}
.vminst.show{display:flex}
.vmfab{position:fixed;right:14px;bottom:calc(14px + env(safe-area-inset-bottom,0px));z-index:75;display:flex;align-items:center;gap:6px;font:800 14px/1 system-ui,sans-serif;padding:12px 16px;border-radius:999px;border:2px solid #000;background:#f4cf55;color:#0b1533;box-shadow:3px 3px 0 #000;cursor:pointer}
.vmsh{position:fixed;inset:0;z-index:90;background:rgba(5,9,23,.78);display:flex;align-items:flex-end;justify-content:center;padding:12px}
.vmsh[hidden]{display:none}
.vmsh-box{width:100%;max-width:420px;background:#fff;color:#0b1533;border:3px solid #000;border-radius:20px;padding:16px 16px 18px;box-shadow:6px 6px 0 #1d3fb8;font:15px/1.4 system-ui,sans-serif;max-height:92vh;overflow:auto}
.vmsh-box h3{margin:0 0 4px;font:900 1.25rem system-ui,sans-serif}
.vmsh-t{margin:0 0 12px;color:#4e5b7d;font-size:.85rem;word-break:break-word}
.vmsh-g{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.vmsh-g a,.vmsh-g button{display:flex;flex-direction:column;align-items:center;gap:4px;padding:10px 4px;border-radius:14px;border:2px solid #0b1533;background:#f3f5fb;color:#0b1533;font:700 .78rem system-ui,sans-serif;text-decoration:none;cursor:pointer}
.vmsh-g span{font-size:1.5rem}
.vmsh-qr{display:flex;justify-content:center;margin:14px 0 4px}.vmsh-qr canvas,.vmsh-qr img{border:8px solid #fff;outline:2px solid #0b1533;border-radius:6px}
.vmsh-c{display:block;width:100%;margin-top:12px;font:800 1rem system-ui,sans-serif;padding:12px;border-radius:999px;border:2px solid #0b1533;background:#fff;color:#0b1533;cursor:pointer}
@media print{.vmfab{display:none}}
</style>'''
SHARE_HTML='''<button type="button" class="vmfab" id="vmFab" aria-haspopup="dialog">📤 Partager</button>
<button type="button" class="vminst" id="vmInst">📲 Installer l\'app</button>
<div class="vmsh" id="vmSh" hidden role="dialog" aria-modal="true" aria-labelledby="vmShT"><div class="vmsh-box">
<h3 id="vmShT">📤 Partager cette page</h3><p class="vmsh-t" id="vmShU"></p>
<div class="vmsh-g">
<a id="vmS-wa" target="_blank" rel="noopener"><span>💬</span>WhatsApp</a>
<a id="vmS-fb" target="_blank" rel="noopener"><span>📘</span>Facebook</a>
<a id="vmS-x" target="_blank" rel="noopener"><span>✖️</span>X</a>
<a id="vmS-tg" target="_blank" rel="noopener"><span>✈️</span>Telegram</a>
<a id="vmS-sms"><span>📱</span>SMS</a>
<button type="button" id="vmS-cp"><span>🔗</span>Copier le lien</button>
</div>
<button type="button" class="vmsh-c" id="vmS-more" hidden>Plus d’options (Insta, Snap…)</button>
<div class="vmsh-qr" id="vmShQ" aria-label="QR code de la page"></div>
<p class="vmsh-t" style="text-align:center;margin:4px 0 0">📷 Fais scanner ce QR code avec l’appareil photo d’un ami</p>
<button type="button" class="vmsh-c" id="vmShX">Fermer</button>
</div></div>
<script>
(function(){var $=function(i){return document.getElementById(i)},f=$('vmFab'),m=$('vmSh'),qr=false;if(!f||!m)return;
var C='https://countapi.mileshilliard.com/api/v1/hit/',d=new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Paris',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date()).replace(/-/g,''),b=Math.floor(Date.now()/300000);
try{if(!sessionStorage.getItem('vm-vu')){sessionStorage.setItem('vm-vu','1');['vm-stats-visites-total','vm-stats-visites-'+d].forEach(function(k){fetch(C+k,{cache:'no-store'}).catch(function(){})})}}catch(e){}
['vm-stats-vues-total','vm-stats-vues-'+d,'vm-stats-live-'+b].forEach(function(k){fetch(C+k,{cache:'no-store'}).catch(function(){})});
function url(){return location.href.split('#')[0]}
function open(){var u=url(),t=document.title,e=encodeURIComponent;$('vmShU').textContent=t;
 $('vmS-wa').href='https://wa.me/?text='+e(t+' '+u);$('vmS-fb').href='https://www.facebook.com/sharer/sharer.php?u='+e(u);$('vmS-x').href='https://twitter.com/intent/tweet?text='+e(t)+'&url='+e(u);$('vmS-tg').href='https://t.me/share/url?url='+e(u)+'&text='+e(t);$('vmS-sms').href='sms:?&body='+e(t+' '+u);
 $('vmS-more').hidden=!navigator.share;
 if(!qr){qr=true;var s=document.createElement('script');s.src='https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js';var fb=function(){if($('vmShQ').firstChild)return;var i=new Image();i.width=180;i.height=180;i.alt='QR code de la page';i.src='https://api.qrserver.com/v1/create-qr-code/?size=360x360&margin=0&data='+e(u);$('vmShQ').appendChild(i)};s.onload=function(){try{new QRCode($('vmShQ'),{text:u,width:180,height:180,correctLevel:QRCode.CorrectLevel.M})}catch(x){fb()}};s.onerror=fb;setTimeout(fb,4000);document.head.appendChild(s)}
 m.hidden=false;$('vmShX').focus()}
f.onclick=open;$('vmShX').onclick=function(){m.hidden=true;f.focus()};m.onclick=function(e){if(e.target===m)m.hidden=true};
$('vmS-more').onclick=function(){navigator.share({title:document.title,url:url()}).catch(function(){})};
$('vmS-cp').onclick=function(){var b=this;(navigator.clipboard?navigator.clipboard.writeText(url()):Promise.reject()).then(function(){b.lastChild.textContent='Copié ✓'}).catch(function(){prompt('Copie ce lien :',url())})};
document.addEventListener('keydown',function(e){if(e.key==='Escape')m.hidden=true});
if('serviceWorker' in navigator)navigator.serviceWorker.register('/sw.js').catch(function(){});
var ib=$('vmInst'),dp=null,standalone=matchMedia('(display-mode: standalone)').matches||navigator.standalone,ios=/iphone|ipad|ipod/i.test(navigator.userAgent),andr=/android/i.test(navigator.userAgent);
var mf=(($('vmapp-m')||{}).getAttribute&&$('vmapp-m').getAttribute('href'))||'',app=(mf.match(/app[/]([a-z]+)[.]webmanifest/)||[,'foot'])[1];
var NOMS={foot:'VM Foot',gaming:'VM Gaming',actus:'VM Actus',arena:'VM Arena',tv:'VM TV',annonces:'VM Annonces',allolivre:'AlloLivre'},nom=NOMS[app]||'VM',key='vm-app-non-'+app,no=false;try{no=localStorage.getItem(key)==='1'}catch(e){}
ib.textContent='📲 Installer '+nom;
function show(){if(!no)ib.classList.add('show')}
if(standalone){if(app!=='foot'&&!ios)show();}
else{addEventListener('beforeinstallprompt',function(e){e.preventDefault();dp=e;show()});if(ios)show();else setTimeout(show,2500);}
addEventListener('appinstalled',function(){ib.classList.remove('show')});
ib.onclick=function(){
 if(dp){dp.prompt();dp.userChoice.then(function(){ib.classList.remove('show')});dp=null;return}
 if(standalone&&andr){location.href='intent://'+location.host+location.pathname+'#Intent;scheme=https;package=com.android.chrome;end';return}
 if(ios){alert('Pour installer '+nom+' sur iPhone : — 1. Ouvre cette page dans Safari — 2. Bouton Partager \u2191 en bas — 3. « Sur l\u2019\u00e9cran d\u2019accueil » — 4. « Ajouter »')}
 else{alert('Pour installer '+nom+' : — 1. Touche le menu \u22ee en haut \u00e0 droite de Chrome — 2. Choisis « Ajouter \u00e0 l\u2019\u00e9cran d\u2019accueil » (ou « Installer l\u2019application ») — 3. Confirme « Installer ».')}
 try{localStorage.setItem(key,'1')}catch(e){}ib.classList.remove('show')};
})();
</script>'''

def bar(active):
    items=[('f','/','⚽ Foot'),('s','/studio.html#tv','📺 Pastille TV'),('g','/vm-gaming/','🎮 Gaming'),('a','/actus/','📰 Actus'),('r','/radio.html','📻 Radio'),('v','/#videos','🎬 Vidéos')]
    links=''.join(f'<a class="{k}{" on" if k==active else ""}" href="{h}"{" aria-current=\"page\"" if k==active else ""}>{t}</a>' for k,h,t in items)
    return f'<nav class="vmbar" aria-label="Les univers VM"><div class="vmbar-in"><a class="vmb-logo" href="/groupe.html" aria-label="Tous les sites VM">VM <small>TOUS LES SITES</small></a>{links}<a class="vmb-don" href="/soutenir.html">💛 Soutenir</a></div></nav>'
def inject(s,active,app='foot'):
    s=re.sub(r'<style id="vmbar-css">.*?</style>','',s,flags=re.S)
    s=re.sub(r'<nav class="vmbar".*?</div></nav>','',s,flags=re.S)
    s=re.sub(r'<style id="vmshare-css">.*?</style>','',s,flags=re.S)
    s=re.sub(r'<button type="button" class="vmfab".*?</script>','',s,flags=re.S)
    s=re.sub(r'<link rel="manifest"[^>]*id="vmapp-m"><meta[^>]*id="vmapp-t"><link[^>]*id="vmapp-i">','',s)
    s=s.replace('</head>',app_head(app)+CSS+SHARE_CSS+'</head>',1)
    s=re.sub(r'(<body[^>]*>)',lambda m:m.group(1)+bar(active),s,count=1)
    i=s.rfind('</body>')
    s=s[:i]+SHARE_HTML+s[i:]
    return s
def apply(path,active,app='foot'):
    s=inject(open(path,encoding='utf-8').read(),active,app)
    open(path,'w',encoding='utf-8').write(s)
if __name__=='__main__':
    for p,a,*x in [('index.html','f'),('vm-gaming/index.html','g','gaming'),('actus/index.html','a','actus'),('archives.html','f'),('studio.html','s','tv'),('radio.html','r','tv'),('gaming.html','f','arena'),('soutenir.html',''),('groupe.html',''),('shop/index.html','','annonces'),('allolivre/index.html','','allolivre'),('comparateur/index.html','','annonces'),('web-studio.html',''),('boutique/index.html',''),('mentions-legales.html','')]:
        apply(p,a,*x); print('ok',p)
