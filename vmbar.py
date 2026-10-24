"""Barre de navigation commune des univers VM (Foot, Gaming, Actus, Vidéos, Studio, Soutenir).
Usage : python vmbar.py  (met à jour les pages)  ;  build_pages.py l'utilise pour les articles."""
import re,sys
CSS='''<style id="vmbar-css">
.vmbar{background:#04060f;border-bottom:1px solid rgba(255,255,255,.12);font:700 13px/1 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;position:sticky;top:0;z-index:80}
.vmbar+header{top:49px!important}
.vmbar-in{max-width:1180px;margin:0 auto;display:flex;align-items:center;gap:4px;padding:6px max(10px,env(safe-area-inset-left,0px));overflow-x:auto;scrollbar-width:none}
.vmbar-in::-webkit-scrollbar{display:none}
.vmbar-in{min-height:48px}
.vmbar a{flex:none;color:#cfd6ea;text-decoration:none;padding:7px 10px;border-radius:999px;letter-spacing:.04em;text-transform:uppercase;white-space:nowrap}
.vmbar a:hover{background:rgba(255,255,255,.08);color:#fff}
.vmbar a:focus-visible{outline:2px solid #f4cf55;outline-offset:2px}
.vmbar .vmb-logo small{font:800 9px/1 system-ui,sans-serif;font-style:normal;letter-spacing:.06em;margin-left:4px;vertical-align:middle}
.vmbar .vmb-logo{font:italic 900 18px/1 Impact,"Arial Black",sans-serif;color:#04060f;background:linear-gradient(135deg,#ffe58a,#f4cf55 55%,#c9971a);padding:6px 9px;border-radius:8px;margin-right:4px;letter-spacing:.02em}
.vmbar .vmb-logo{position:sticky;left:0;z-index:2;box-shadow:6px 0 0 #04060f;font-size:15px;min-height:36px;display:flex;flex-direction:column;justify-content:center;gap:3px;align-items:center}
.vmbar .vmb-logo small{margin:0;font-size:8px}
.vmbar a.on{color:#04060f;background:#fff}
.vmbar a.on.f{background:#f4cf55}.vmbar a.on.g{background:#d6ff6e}.vmbar a.on.a{background:#ff5a6e;color:#fff}
.vmbar .vmb-don{margin-left:auto;background:#f4cf55;color:#0b1533}
.vmbar a.p{background:linear-gradient(135deg,#ffe58a,#f4cf55 55%,#c9971a);color:#0b1533;font-weight:900}.vmbar a.p.on{background:#fff;color:#0b1533;box-shadow:inset 0 0 0 2px #f4cf55}.vmbar a.s{background:#e1243a;color:#fff}.vmbar a.s.on{background:#fff;color:#e1243a}
@media(max-width:520px){.vmbar a{padding:7px 8px;font-size:12px}}
</style>'''

APP_COL={'autopart':'#05080f','location':'#000000','menu':'#05080f','pro':'#05080f','cv':'#05080f','emploi':'#05080f','univers':'#000000','foot': '#060b1d', 'gaming': '#0b0a1c', 'actus': '#0a1430', 'arena': '#140a14', 'tv': '#0a0814', 'allolivre': '#c4121b', 'annonces': '#c4121b', 'papiers': '#14100a',
 'recettes':'#07080f','produits':'#07080f','sport':'#07080f','immo':'#07080f','rdv':'#07080f','meteo':'#000000','comparateur':'#c4121b','boutique':'#07080f','belfort':'#07080f','pub':'#05080f','services':'#080c12','pepite':'#0a1a33','radio':'#060b1d','studio':'#05080f'}
# Nom affiché sous l'icône sur l'écran d'accueil (iPhone) : identique au short_name du manifeste.
APP_NOM={'autopart':'VM Auto','location':'VM Detailing','menu':'Menu QR','pro':'Pro Local','cv':'VM CV','emploi':'VM Emploi','univers':'VM Univers','foot':'VM Foot','gaming':'VM Gaming','actus':'VM Actus','arena':'VM Arena','tv':'Pastille TV','allolivre':'AlloLivre','annonces':'VM Annonces','papiers':'Papiers',
 'recettes':'Recettes','produits':'Produits','sport':'Sport','immo':'Immo','rdv':'RDV du jour','meteo':'Météo','comparateur':'Comparateur','boutique':'Boutique','belfort':'VM Belfort','pub':'Pub VM','services':'VM Services','pepite':'Pépite FC','radio':'VM Radio','studio':'VM Studio'}
def app_head(app='foot'):
    app=app if app in APP_COL else 'foot'
    return f'<link rel="manifest" href="/app/{app}.webmanifest" id="vmapp-m"><meta name="theme-color" content="{APP_COL[app]}" id="vmapp-t"><link rel="apple-touch-icon" href="/app/{app}-apple.png" id="vmapp-i"><meta name="apple-mobile-web-app-title" content="{APP_NOM[app]}" id="vmapp-n">'
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
function url(){return window.vmShareURL?window.vmShareURL():(/^#a=/.test(location.hash)?location.href:location.href.split('#')[0])}
function open(){var u=url(),t=document.title,e=encodeURIComponent;$('vmShU').textContent=t;
 $('vmS-wa').href='https://wa.me/?text='+e(t+' '+u);$('vmS-fb').href='https://www.facebook.com/sharer/sharer.php?u='+e(u);$('vmS-x').href='https://twitter.com/intent/tweet?text='+e(t)+'&url='+e(u);$('vmS-tg').href='https://t.me/share/url?url='+e(u)+'&text='+e(t);$('vmS-sms').href='sms:?&body='+e(t+' '+u);
 $('vmS-more').hidden=!navigator.share;
 if(!qr){qr=true;var s=document.createElement('script');s.src='/assets/vendor/qrcode.min.js';var fb=function(){var q=$('vmShQ');if(q.firstChild)return;var p=document.createElement('p');p.textContent='QR code indisponible. Vous pouvez copier le lien ci-dessus.';q.appendChild(p)};s.onload=function(){try{new QRCode($('vmShQ'),{text:u,width:180,height:180,correctLevel:QRCode.CorrectLevel.M})}catch(x){fb()}};s.onerror=fb;setTimeout(fb,4000);document.head.appendChild(s)}
 m.hidden=false;$('vmShX').focus()}
f.onclick=open;$('vmShX').onclick=function(){m.hidden=true;f.focus()};m.onclick=function(e){if(e.target===m)m.hidden=true};
$('vmS-more').onclick=function(){navigator.share({title:document.title,url:url()}).catch(function(){})};
$('vmS-cp').onclick=function(){var b=this;(navigator.clipboard?navigator.clipboard.writeText(url()):Promise.reject()).then(function(){b.lastChild.textContent='Copié ✓'}).catch(function(){prompt('Copie ce lien :',url())})};
document.addEventListener('keydown',function(e){if(e.key==='Escape')m.hidden=true});
if('serviceWorker' in navigator)navigator.serviceWorker.register('/sw.js').catch(function(){});
var ib=$('vmInst'),dp=null,standalone=matchMedia('(display-mode: standalone)').matches||navigator.standalone,ios=/iphone|ipad|ipod/i.test(navigator.userAgent),andr=/android/i.test(navigator.userAgent);
var mf=(($('vmapp-m')||{}).getAttribute&&$('vmapp-m').getAttribute('href'))||'',app=(mf.match(/app[/]([a-z]+)[.]webmanifest/)||[,'foot'])[1];
var NOMS={autopart:'VM Auto Particulier',location:'VM Detailing',menu:'VM Menu QR',pro:'VM Pro Local',cv:'VM CV',emploi:'VM Emploi',univers:'VM Univers',foot:'VM Foot',gaming:'VM Gaming',actus:'VM Actus',arena:'VM Arena',tv:'La Pastille TV',annonces:'VM Shop',allolivre:'AlloLivre',recettes:'VM Recettes',produits:'VM Produits locaux',sport:'VM Sport',immo:'VM Immo',rdv:'VM RDV du jour',meteo:'VM Météo',comparateur:'VM Comparateur',boutique:'VM Boutique',belfort:'VM Belfort',pub:'Publicité VM',services:'VM Services',pepite:'Pépite FC',radio:'VM Radio',studio:'VM Studio'},nom=NOMS[app]||'VM',key='vm-app-non-'+app,no=false;try{no=localStorage.getItem(key)==='1'}catch(e){}
ib.textContent='📲 Installer '+nom;
function show(){if(!no)ib.classList.add('show')}
if(!standalone){addEventListener('beforeinstallprompt',function(e){e.preventDefault();dp=e;show()});if(ios)show();}
addEventListener('appinstalled',function(){ib.classList.remove('show')});
ib.onclick=function(){
 if(dp){dp.prompt();dp.userChoice.then(function(){ib.classList.remove('show')});dp=null;return}
 if(ios){alert('Pour installer '+nom+' sur iPhone : — 1. Ouvre cette page dans Safari — 2. Bouton Partager \u2191 en bas — 3. « Sur l\u2019\u00e9cran d\u2019accueil » — 4. « Ajouter »')}

 try{localStorage.setItem(key,'1')}catch(e){}ib.classList.remove('show')};
window.vmMail=function(su,bo){var to='velocemercato.fr@gmail.com';location.href='mailto:'+to+'?subject='+encodeURIComponent(su)+'&body='+encodeURIComponent(bo);
 var d=document.getElementById('vmMailBox');if(d)d.remove();d=document.createElement('div');d.id='vmMailBox';d.setAttribute('role','dialog');
 d.style.cssText='position:fixed;left:12px;right:12px;bottom:12px;z-index:95;max-width:440px;margin:0 auto;background:#fff;color:#0b1533;border:3px solid #000;border-radius:16px;padding:14px;box-shadow:5px 5px 0 #1d3fb8;font:15px/1.4 system-ui,sans-serif';
 d.innerHTML='<b>✉️ Ton appli e-mail s\u2019ouvre avec le message prêt.</b><br>Appuie sur « Envoyer » dedans : tant que ce n\u2019est pas fait, rien n\u2019est envoyé.<br><small>Rien ne s\u2019ouvre ? Copie la demande et envoie-la à '+to+'.</small><div style="display:flex;gap:8px;margin-top:10px"><button type="button" id="vmMailCp" style="flex:1;font:800 .95rem system-ui;padding:10px;border-radius:999px;border:2px solid #000;background:#f4cf55;cursor:pointer">📋 Copier la demande</button><button type="button" id="vmMailX" style="font:800 .95rem system-ui;padding:10px 14px;border-radius:999px;border:2px solid #000;background:#fff;cursor:pointer">OK</button></div>';
 document.body.appendChild(d);document.getElementById('vmMailX').onclick=function(){d.remove()};
 document.getElementById('vmMailCp').onclick=function(){var t='À : '+to+'\\nObjet : '+su+'\\n\\n'+bo,b=this;function ok(){b.textContent='✅ Copié !'}if(navigator.clipboard)navigator.clipboard.writeText(t).then(ok,function(){prompt('Copie ce texte :',t)});else prompt('Copie ce texte :',t)}};
})();
</script>'''

def bar(active):
    items=[('f','/','⚽ Foot'),('p','/web-studio.html','💼 VM Studio'),('s','/studio.html#tv','📺 Pastille TV'),('g','/vm-gaming/','🎮 Gaming'),('a','/actus/','📰 Actus'),('r','/radio.html','📻 Radio'),('v','/#videos','🎬 Vidéos')]
    links=''.join(f'<a class="{k}{" on" if k==active else ""}" href="{h}"{" aria-current=\"page\"" if k==active else ""}>{t}</a>' for k,h,t in items)
    return f'<nav class="vmbar" aria-label="Les univers VM"><div class="vmbar-in"><a class="vmb-logo" href="https://vmunivers.fr/" aria-label="VM Univers, tous les projets">VM UNIVERS<small>TOUS LES PROJETS</small></a>{links}<a class="vmb-don" href="/soutenir.html">💛 Soutenir</a></div></nav>'
def inject(s,active,app='foot',contact='velocemercato.fr@gmail.com'):
    s=re.sub(r'<style id="vmbar-css">.*?</style>','',s,flags=re.S)
    s=re.sub(r'<nav class="vmbar".*?</div></nav>','',s,flags=re.S)
    s=re.sub(r'<style id="vmshare-css">.*?</style>','',s,flags=re.S)
    s=re.sub(r'<button type="button" class="vmfab".*?</script>','',s,flags=re.S)
    s=re.sub(r'<link rel="manifest"[^>]*id="vmapp-m"><meta[^>]*id="vmapp-t"><link[^>]*id="vmapp-i">(<meta[^>]*id="vmapp-n">)?','',s)
    s=s.replace('</head>',app_head(app)+CSS+SHARE_CSS+'</head>',1)
    s=re.sub(r'(<body[^>]*>)',lambda m:m.group(1)+bar(active),s,count=1)
    i=s.rfind('</body>')
    s=s[:i]+SHARE_HTML.replace("var to='velocemercato.fr@gmail.com'", "var to='"+contact+"'")+s[i:]
    return s
BUSINESS_PAGES = {'recettes/index.html', 'produits-locaux/index.html', 'sport/index.html', 'immo/index.html', 'rdv/index.html', 'meteo/index.html', 'vm/index.html', 'allolivre/index.html', 'services-web.html', 'groupe.html', 'pub/index.html', 'boutique/index.html', 'vm-location/index.html', 'pro/index.html', 'emploi/index.html', 'comparateur/index.html', 'shop/index.html', 'menu/index.html', 'pro-auto/index.html', 'web-studio.html', 'cv/index.html'}

def apply(path,active,app='foot'):
    contact='vminvest.fr@gmail.com' if path in BUSINESS_PAGES else 'velocemercato.fr@gmail.com'
    s=inject(open(path,encoding='utf-8').read(),active,app,contact)
    open(path,'w',encoding='utf-8').write(s)

def build_vm():
    """Preserve the explicit links to the independent portal; never regenerate a copy."""
    from pathlib import Path
    source = Path(__file__).resolve().parent / 'vm/index.html'
    (source.parent.parent / 'groupe.html').write_text(source.read_text(encoding='utf-8'), encoding='utf-8')

if __name__=='__main__':
    for p,a,*x in [('index.html','f'),('vm-gaming/index.html','g','gaming'),('actus/index.html','a','actus'),('archives.html','f'),('studio.html','s','tv'),('radio.html','r','radio'),('gaming.html','f','arena'),('soutenir.html',''),('shop/index.html','','annonces'),('allolivre/index.html','','allolivre'),('comparateur/index.html','','comparateur'),('web-studio.html','','studio'),('boutique/index.html','','boutique'),('cv/index.html','','cv'),('menu/index.html','','menu'),('pro/index.html','','pro'),('emploi/index.html','','emploi'),('belfort/index.html','','belfort'),('vm-location/index.html','','location'),('pro-auto/index.html','','autopart'),('pub/index.html','','pub'),('mentions-legales.html','')]:
        apply(p,a,*x); print('ok',p)
    build_vm(); print('ok vm/')
