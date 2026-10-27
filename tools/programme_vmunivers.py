#!/usr/bin/env python3
"""Génère studio/programme-vmunivers.html : le programme VM Univers du jour (et des 2 jours suivants),
prêt à copier-coller sur TikTok, Snapchat ou ailleurs. Mêmes contenus et mêmes textes que la publication
automatique Facebook/Instagram (tools/publier_meta.py), calculés dans le navigateur.

Usage : python tools/programme_vmunivers.py  (à relancer seulement si la liste des projets change)
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import publier_meta as M  # noqa: E402
import vmstats  # noqa: E402

DATA = {
    'debut': M.DEBUT_UNIVERS.isoformat(),
    'heures': {day.isoformat(): list(hours) for day, hours in M.HEURES_UNIVERS.items()},
    'defaut': list(M.HEURES_UNIVERS_DEFAUT),
    'rotations': M.ROTATIONS,
}

PAGE = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Programme VM Univers</title>
<meta name="description" content="Les publications VM Univers du jour, prêtes à copier-coller sur TikTok, Snapchat ou ailleurs.">
<meta name="robots" content="noindex"><meta name="theme-color" content="#04060f">
<link rel="icon" href="/app/univers-192.png">
<style>
:root{--bg:#0b1533;--card:#121d44;--ink:#fff;--muted:#c9d0ea;--gold:#f4cf55;--red:#ff4757;--blue:#3f7bff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
header{padding:18px 16px;background:linear-gradient(135deg,#1d3fb8,#0b1533 60%,#5a0a18);border-bottom:3px solid var(--gold)}
header h1{margin:0;font-size:1.5rem}header p{margin:4px 0 0;color:var(--muted);font-size:.95rem}
main{max-width:760px;margin:0 auto;padding:16px}
.day{margin:22px 0 8px;font-weight:900;color:var(--gold);text-transform:uppercase;letter-spacing:.06em}
.post{display:grid;grid-template-columns:120px 1fr;gap:14px;background:var(--card);border:2px solid #2a3a78;border-radius:16px;padding:12px;margin:10px 0}
.post.now{border-color:var(--gold);box-shadow:0 0 0 3px #f4cf5544}
.media{width:120px;aspect-ratio:9/16;border-radius:12px;object-fit:cover;background:#000}
.media.img{aspect-ratio:1;align-self:start}
.h{font-weight:900;font-size:1.05rem}.t{display:inline-block;font-size:.72rem;font-weight:900;border-radius:6px;padding:1px 7px;margin-right:6px}
.t.video{background:var(--red)}.t.carte{background:var(--blue)}
pre{white-space:pre-wrap;font:13px/1.45 system-ui,sans-serif;background:#0b1533;border:1px dashed #4a5a98;border-radius:10px;padding:9px;margin:8px 0}
.btns{display:flex;flex-wrap:wrap;gap:8px}
button,a.b{font:800 .9rem system-ui,sans-serif;border:0;border-radius:999px;padding:9px 14px;background:var(--gold);color:#0b1533;text-decoration:none;cursor:pointer}
a.b.alt{background:#fff}
.tip{background:#121d44;border-radius:14px;padding:12px 14px;color:var(--muted);font-size:.92rem}
@media(max-width:480px){.post{grid-template-columns:92px 1fr}.media{width:92px}}
</style></head><body>
<header><h1>📅 Programme VM Univers</h1><p>Facebook et Instagram : publiés automatiquement. Ici : copie-colle sur TikTok, Snapchat…</p></header>
<main>
<div class="tip">1) <b>📋 Copier le texte</b> · 2) <b>⬇️ Enregistrer</b> la vidéo ou l'image · 3) Publie sur TikTok/Snap et colle le texte. Ajoute cette page à ton écran d'accueil.</div>
<div id="liste"></div>
</main>
<script>
var D=__DATA__;
function iso(d){return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}
function heures(d){return D.heures[iso(d)]||D.defaut}
function jours(a,b){return Math.round((Date.UTC(b.getFullYear(),b.getMonth(),b.getDate())-Date.UTC(a.getFullYear(),a.getMonth(),a.getDate()))/864e5)}
var debut=new Date(D.debut+'T12:00:00');
function contenu(d,h){var hs=heures(d),r=hs.indexOf(h);r=r<0?0:r;
 var l=D.rotations[r%D.rotations.length],it=Object.assign({},l[jours(debut,d)%l.length]);
 if(it.type==='video')it.video='/media/promos/'+it.video_id+'-vertical.mp4';return it}
function texte(it){var fin=it.type==='video'?'\\nVidéo réalisée avec l’aide de l’IA.':'';
 return it.titre+'\\n\\n'+it.pitch+'\\n\\n👉 Lien en bio\\nTous nos projets : vmunivers.fr'+fin+'\\n\\n'+it.tags}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var L=document.getElementById('liste'),now=new Date(),html='';
for(var k=0;k<3;k++){var d=new Date(now);d.setDate(d.getDate()+k);
 html+='<div class="day">'+(k===0?'Aujourd’hui':k===1?'Demain':'Après-demain')+' · '+d.toLocaleDateString('fr-FR',{weekday:'long',day:'numeric',month:'long'})+'</div>';
 heures(d).forEach(function(h){var it=contenu(d,h),tx=texte(it),cur=k===0&&now.getHours()===h;
  var m=it.type==='video'?'<video class="media" src="'+it.video+'" poster="'+it.video.replace('.mp4','.jpg')+'" preload="none" controls playsinline></video>':'<img class="media img" src="/app/'+it.icon+'-512.png" alt="">';
  var dl=it.type==='video'?it.video:'/app/'+it.icon+'-512.png';
  html+='<div class="post'+(cur?' now':'')+'">'+m+'<div><div class="h">'+h+' h · <span class="t '+it.type+'">'+(it.type==='video'?'🎬 VIDÉO':'✨ CARTE')+'</span>'+esc(it.name)+'</div>'+
   '<pre>'+esc(tx)+'</pre><div class="btns"><button type="button" data-t="'+esc(tx)+'">📋 Copier le texte</button><a class="b alt" href="'+dl+'" download>⬇️ Enregistrer</a></div></div></div>'})}
L.innerHTML=html;
L.addEventListener('click',function(e){var b=e.target.closest('button[data-t]');if(!b)return;
 navigator.clipboard.writeText(b.getAttribute('data-t')).then(function(){b.textContent='✅ Copié !';setTimeout(function(){b.textContent='📋 Copier le texte'},1800)})});
</script>
</body></html>
"""


def main():
    out = ROOT / 'studio/programme-vmunivers.html'
    out.write_text(vmstats.add(PAGE.replace('__DATA__', json.dumps(DATA, ensure_ascii=False))), encoding='utf-8')
    print('Écrit :', out.relative_to(ROOT))


if __name__ == '__main__':
    main()
