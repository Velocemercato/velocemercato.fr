"""Vitrine des deux sites : VM Studio (4 packs à prix fixe, scène manga) en grand,
puis la chaîne YouTube Véloce Mercato et les outils gratuits.
Usage : python vitrine.py [chemin/vers/vmunivers]  — remplace le bloc entre <!--vmvitrine--> et <!--/vmvitrine-->."""
import re
import sys
from pathlib import Path

SITE = 'https://velocemercato.fr'
YOUTUBE = 'https://www.youtube.com/@VeloceMercato'

CSS = '''<style id="vmvitrine-css">
.vmv{--vg:#f4cf55;--vn:#04060f;max-width:1180px;margin:16px auto;padding-left:max(12px,env(safe-area-inset-left,0px));padding-right:max(12px,env(safe-area-inset-right,0px));display:grid;gap:12px;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;box-sizing:border-box}
.vmv *{box-sizing:border-box}
.vmv a{text-decoration:none}
.vmv-big,.vmv-card{position:relative;overflow:hidden;isolation:isolate;display:flex;align-items:flex-end;background:var(--vn);border:3px solid #000;box-shadow:5px 5px 0 #000}
.vmv-big{border-radius:22px;min-height:460px}
.vmv-card{border-radius:18px;min-height:250px}
.vmv-card>img,.vmv-big>.vmv-bg{position:absolute;inset:0;z-index:-2;width:100%;height:100%;object-fit:cover;display:block}
.vmv-big>.vmv-bg{object-position:50% 68%}
.vmv-big::before,.vmv-card::before{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(180deg,rgba(4,6,15,.05) 0%,rgba(4,6,15,.5) 42%,rgba(4,6,15,.96) 100%)}
.vmv-in{padding:20px;max-width:760px;min-width:0}
.vmv-card .vmv-in{padding:16px}
.vmv-eye{display:inline-block;font:900 12px/1.2 system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;padding:7px 11px;border-radius:999px;background:var(--vg);color:#0b1533}
.vmv-yt .vmv-eye{background:#ff1f3d;color:#fff}
.vmv-free .vmv-eye{background:#3ddc84;color:#04210f}
.vmv h2,.vmv h3{font-family:Impact,"Arial Black","Arial Narrow",sans-serif;font-style:italic;font-weight:900;text-transform:uppercase;color:#fff;text-shadow:0 3px 0 #000;letter-spacing:.01em;text-wrap:balance}
.vmv h2{font-size:clamp(30px,6.2vw,56px);line-height:.98;margin:12px 0 8px}
.vmv h3{font-size:clamp(24px,4.6vw,34px);line-height:1;margin:10px 0 6px}
.vmv h2 b,.vmv h3 b{color:var(--vg);font-weight:900}
.vmv p{color:#eef1f8;font:600 16px/1.4 system-ui,sans-serif;margin:0 0 12px;max-width:60ch}
.vmv-prices{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 14px;padding:0;list-style:none}
.vmv-prices li{background:rgba(4,6,15,.72);border:1px solid rgba(244,207,85,.55);color:#fff;border-radius:10px;padding:7px 10px;font:700 14px/1.2 system-ui,sans-serif}
.vmv-prices li b{color:var(--vg);font-variant-numeric:tabular-nums}
.vmv-cta{display:flex;flex-wrap:wrap;gap:8px}
.vmv-btn{display:inline-flex;align-items:center;gap:6px;font:900 15px/1 system-ui,sans-serif;padding:13px 18px;border-radius:999px;background:var(--vg);color:#0b1533!important;border:2px solid #000;box-shadow:3px 3px 0 #000}
.vmv-yt .vmv-btn{background:#ff1f3d;color:#fff!important}
.vmv-free .vmv-btn{background:#3ddc84;color:#04210f!important}
.vmv-big:hover .vmv-btn,.vmv-card:hover .vmv-btn{transform:translate(-1px,-1px);box-shadow:4px 4px 0 #000}
.vmv-big:focus-visible,.vmv-card:focus-visible{outline:3px solid #fff;outline-offset:3px}
.vmv-credit{display:block;margin-top:10px;color:#c9cfe2;font:500 12px/1.3 system-ui,sans-serif}
.vmv-duo{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.vmv-card.vmv-yt>img{object-position:50% 30%}
.vmv-card.vmv-free>img{object-position:78% 40%}
.vmv-free::before{background:linear-gradient(180deg,rgba(4,6,15,.35) 0%,rgba(4,6,15,.75) 40%,rgba(4,6,15,.97) 100%)}
@media(max-width:680px){.vmv-duo{grid-template-columns:1fr}.vmv-big{min-height:520px}.vmv-in{padding:16px}}
@media(prefers-reduced-motion:reduce){.vmv-btn{transform:none!important}}
.vmv-try{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.vmv-t{display:block;padding:16px 18px;border-radius:18px;border:3px solid #000;box-shadow:5px 5px 0 #000;background:#fff;color:#0b1533!important}
.vmv-t.gold{background:linear-gradient(135deg,#f4cf55,#ffb703)}
.vmv-t .k{display:inline-block;font:900 11px/1 system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;background:#0b1533;color:#fff;padding:6px 9px;border-radius:99px}
.vmv-t b.p{display:block;font:900 26px/1.1 system-ui,sans-serif;margin:8px 0 4px}
.vmv-t span.d{display:block;font:600 14px/1.35 system-ui,sans-serif}
.vmv-t span.go{display:inline-block;margin-top:10px;font:900 14px/1 system-ui,sans-serif;text-decoration:underline;color:#0b1533!important}
@media(max-width:680px){.vmv-try{grid-template-columns:1fr}}
.vmv-two{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.vmv-pill{display:flex;align-items:center;gap:12px;padding:16px 18px;border-radius:18px;border:3px solid #000;box-shadow:5px 5px 0 #000;color:#0b1533!important;font:900 17px/1.2 system-ui,sans-serif}
.vmv-pill small{display:block;font:600 13px/1.3 system-ui,sans-serif;opacity:.85;margin-top:3px}
.vmv-pill span.e{font-size:30px}
.vmv-pub{background:linear-gradient(135deg,#f4cf55,#ffb703)}.vmv-don{background:linear-gradient(135deg,#ffe3ec,#ffc2d4)}
.vmv-pill:hover{transform:translate(-1px,-1px);box-shadow:6px 6px 0 #000}
@media(max-width:680px){.vmv-two{grid-template-columns:1fr}}
</style>'''


def block(img):
    """img : préfixe des images ('' = images du site courant)."""
    return f'''<!--vmvitrine-->{CSS}
<section class="vmv" id="vitrine" aria-label="À la une chez VM">
<a class="vmv-big" id="vm-studio" href="{SITE}/web-studio.html#tarifs" aria-labelledby="vmv-t1">
<img class="vmv-bg" src="{img}/img/studio/manga-vm-studio.webp" alt="" width="941" height="1672" loading="lazy">
<span class="vmv-in">
<span class="vmv-eye">VM Studio · commerces et artisans · 100 % à distance</span>
<h2 id="vmv-t1">Votre commerce. <b>Votre site.</b></h2>
<p>4 packs à prix fixe. Vous envoyez vos infos et vos photos, vous validez la maquette, on met en ligne.</p>
<ul class="vmv-prices"><li>Mini <b>290 €</b></li><li>Starter <b>590 €</b></li><li>Business <b>990 €</b></li><li>Max <b>1 490 €</b></li></ul>
<span class="vmv-cta"><span class="vmv-btn">Voir les 4 packs et les démos →</span></span>
<small class="vmv-credit">Prix de création TTC · illustration IA, personnages inventés</small>
</span></a>
<div class="vmv-try" aria-label="Essayer avant d’acheter">
<a class="vmv-t" href="{SITE}/web-studio.html?offre=essai#essai"><span class="k">Sans engagement</span><b class="p">Essai 7 jours · 49 €</b><span class="d">Votre vrai site en ligne une semaine, avec vos infos, vos photos et 2 posts Facebook &amp; Instagram.</span><span class="go">Je teste →</span></a>
<a class="vmv-t gold" href="{SITE}/web-studio.html?offre=lancement#essai"><span class="k">Nouveau</span><b class="p">Lancement 1 mois · 149 €</b><span class="d">Votre site 1 mois + 100 cartes de visite avec QR à glisser dans vos commandes. Déduits du pack si vous continuez.</span><span class="go">Je lance →</span></a>
</div>
<div class="vmv-duo">
<a class="vmv-card vmv-yt" href="{YOUTUBE}" target="_blank" rel="noopener" aria-labelledby="vmv-t2">
<img src="{img}/img/studio/plateau-veloce-600.webp" alt="" width="600" height="1066" loading="lazy">
<span class="vmv-in"><span class="vmv-eye">▶ YouTube</span>
<h3 id="vmv-t2">La chaîne <b>Véloce Mercato</b></h3>
<p>Les JT foot, actus et gaming chaque jour, et le mag du dimanche à 11 h.</p>
<span class="vmv-btn">S’abonner gratuitement</span></span></a>
<a class="vmv-card vmv-free" href="https://vmunivers.fr/?theme=quotidien#projets" aria-labelledby="vmv-t3">
<img src="{img}/img/v2-papiers-800.webp" alt="" width="800" height="450" loading="lazy">
<span class="vmv-in"><span class="vmv-eye">🎁 100 % gratuit</span>
<h3 id="vmv-t3">Les outils <b>gratuits</b> VM</h3>
<p>Emploi, CV, papiers, recettes, météo : utiles tous les jours, sans inscription.</p>
<span class="vmv-btn">Les découvrir</span></span></a>
<div class="vmv-two">
<a class="vmv-pill vmv-pub" href="{SITE}/pub/"><span class="e">📣</span><span>Votre pub chez VM<small>Commerces et artisans · encart discret · dès 9,90 €/mois</small></span></a>
<a class="vmv-pill vmv-don" href="{SITE}/soutenir.html"><span class="e">💛</span><span>Soutenir VM<small>Un petit don aide à garder tout gratuit</small></span></a>
</div>
</section><!--/vmvitrine-->'''


def put(html, snippet, anchor_pattern):
    """Retire l'ancien bloc puis l'insère après l'ancre (une seule fois)."""
    html = re.sub(r'\n?<!--vmvitrine-->.*?<!--/vmvitrine-->', '', html, count=1, flags=re.S)
    m = re.search(anchor_pattern, html, flags=re.S)
    if not m:
        raise SystemExit('Ancre introuvable : ' + anchor_pattern)
    return html[:m.end()] + '\n' + snippet + html[m.end():]


if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    page = root / 'index.html'
    # velocemercato.fr : les actus et le JT restent en premier, la vitrine vient juste après.
    page.write_text(put(page.read_text(encoding='utf-8'), block(''), r'</section></div>(?=<section id="reseaux")'), encoding='utf-8')
    print('ok velocemercato.fr')
    if len(sys.argv) > 1:
        vm = Path(sys.argv[1]) / 'index.html'
        s = vm.read_text(encoding='utf-8')
        # vmunivers.fr : en haut du contenu, avant l'annuaire.
        anchor = r'<main>' if '<!--vmvitrine-->' not in s else r'(?=<!--vmvitrine-->)'
        s2 = re.sub(r'<section class="studio-banner" id="vm-studio".*?</section>', '', s, count=1, flags=re.S)
        m = re.search(r'<!--vmvitrine-->', s2)
        if m:  # remplace sur place
            s2 = s2[:m.start()] + block('') + re.sub(r'^.*?<!--/vmvitrine-->', '', s2[m.start():], count=1, flags=re.S)
        else:
            s2 = put(s2, block(''), r'<main>')
        vm.write_text(s2, encoding='utf-8')
        print('ok vmunivers.fr')
