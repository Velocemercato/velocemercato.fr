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
def bar(active):
    items=[('f','/','⚽ Foot'),('s','/studio.html#tv','📺 Pastille TV'),('g','/vm-gaming/','🎮 Gaming'),('a','/actus/','📰 Actus'),('r','/radio.html','📻 Radio'),('v','/#videos','🎬 Vidéos')]
    links=''.join(f'<a class="{k}{" on" if k==active else ""}" href="{h}"{" aria-current=\"page\"" if k==active else ""}>{t}</a>' for k,h,t in items)
    return f'<nav class="vmbar" aria-label="Les univers VM"><div class="vmbar-in"><a class="vmb-logo" href="/groupe.html" aria-label="Tous les sites VM">VM <small>TOUS LES SITES</small></a>{links}<a class="vmb-don" href="/soutenir.html">💛 Soutenir</a></div></nav>'
def inject(s,active):
    s=re.sub(r'<style id="vmbar-css">.*?</style>','',s,flags=re.S)
    s=re.sub(r'<nav class="vmbar".*?</div></nav>','',s,flags=re.S)
    s=s.replace('</head>',CSS+'</head>',1)
    s=re.sub(r'(<body[^>]*>)',lambda m:m.group(1)+bar(active),s,count=1)
    return s
def apply(path,active):
    s=inject(open(path,encoding='utf-8').read(),active)
    open(path,'w',encoding='utf-8').write(s)
if __name__=='__main__':
    for p,a in [('index.html','f'),('vm-gaming/index.html','g'),('actus/index.html','a'),('archives.html','f'),('studio.html','s'),('radio.html','r'),('gaming.html','f'),('soutenir.html',''),('groupe.html',''),('shop/index.html',''),('allolivre/index.html',''),('comparateur/index.html',''),('web-studio.html',''),('mentions-legales.html','')]:
        apply(p,a); print('ok',p)
