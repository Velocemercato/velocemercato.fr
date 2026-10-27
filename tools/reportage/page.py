"""Page de partage d'un reportage : seulement la vidéo et l'article, sans le reste du site.
Usage : python tools/reportage/page.py vm-feminin-20261025-alexia-depagne reportages/alexia-depagne.html"""
import html
import json
import re
import sys
from pathlib import Path


IMG_LINE = re.compile(r'^!\[([^\]]*)\]\((/img/[\w/.-]+\.(?:webp|jpg|png))\)$')


def para_html(p, i, e):
    """Paragraphe d'article : intertitre (## ), photo (![légende](/img/...)) ou texte."""
    m = IMG_LINE.match(p)
    if m:
        return (f'<figure><img src="{e(m.group(2))}" alt="{e(m.group(1))}" loading="lazy">'
                f'<figcaption>{e(m.group(1))}</figcaption></figure>')
    if p.startswith('## '):
        return f'<h2>{e(p[3:])}</h2>'
    return f'<p class="chapo">{e(p)}</p>' if i == 0 else f'<p>{e(p)}</p>'

ROOT = Path(__file__).resolve().parents[2]
SITE = 'https://velocemercato.fr'


def main(ident, out):
    a = next(r for r in json.loads((ROOT / 'articles.json').read_text(encoding='utf-8')) if r.get('id') == ident)
    e = lambda s: html.escape(str(s or ''), quote=True)  # noqa: E731
    paras = [p.strip() for p in re.split(r'\n\s*\n', a['texte']) if p.strip()]
    body = '\n'.join(para_html(p, i, e)
                     for i, p in enumerate(paras))
    ess = ''.join(f'<li>{e(x)}</li>' for x in a.get('essentiel', []))
    src = ''.join(f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener nofollow">{e(s["nom"])}</a></li>' for s in a.get('sources', []))
    vm = a.get('video_vm') or {}
    dm = (a.get('video') or {}).get('dailymotion', '')
    url = f'{SITE}/{out}'
    page = f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(a['titre'])} – Véloce Mercato</title>
<meta name="description" content="{e(a.get('resume'))}">
<link rel="canonical" href="{url}"><meta name="theme-color" content="#0b0d17">
<meta property="og:type" content="article"><meta property="og:title" content="{e(a['titre'])}"><meta property="og:description" content="{e(a.get('resume'))}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/img/reportages/alexia-depagne/partage.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/app/foot-192.png">
<style>
:root{{--bg:#0b0d17;--card:#141a33;--ink:#f1ede4;--muted:#b3b9cf;--gold:#ffd23f;--line:#2a3158}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
.w{{max-width:720px;margin:0 auto;padding-block:20px 90px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
.top{{display:flex;justify-content:space-between;align-items:center;gap:10px;font:800 13px/1 system-ui;letter-spacing:.08em;text-transform:uppercase}}
.top a{{color:var(--gold);text-decoration:none}}
.eye{{display:inline-block;margin-top:22px;background:var(--gold);color:#111;font:900 12px/1 system-ui;letter-spacing:.08em;padding:7px 11px;border-radius:999px;text-transform:uppercase}}
h1{{font:italic 900 clamp(32px,7vw,52px)/1.02 Impact,"Arial Black",sans-serif;text-transform:uppercase;margin:12px 0 10px;text-wrap:balance}}
.vid{{max-width:420px;margin:18px auto}}figure{{margin:18px 0}}figure img{{display:block;width:100%;height:auto;border-radius:14px;border:2px solid #000}}figcaption{{font-size:.8rem;opacity:.75;margin-top:6px}}.hero-ph{{margin:12px 0 4px}}video{{width:100%;aspect-ratio:9/16;border-radius:16px;background:#000;display:block}}
.vid small{{display:block;text-align:center;color:var(--muted);font-size:13px;margin-top:6px}}
.ess{{border:2px solid var(--gold);border-radius:16px;padding:14px 18px;background:var(--card)}}.ess b{{color:var(--gold)}}.ess ul{{margin:8px 0 0;padding-left:20px}}
h2{{font:italic 900 26px/1.1 Impact,"Arial Black",sans-serif;text-transform:uppercase;color:var(--gold);margin:30px 0 6px}}
.chapo{{font-weight:600;font-size:19px}}
.nm{{margin:28px 0;padding:14px;border:1px solid var(--line);border-radius:14px;background:var(--card)}}
.nm iframe{{width:100%;aspect-ratio:16/9;border:0;border-radius:10px}}
.src{{font-size:14px;color:var(--muted)}}.src a{{color:var(--ink)}}
.fin{{margin-top:30px;padding:16px;border-radius:14px;background:linear-gradient(135deg,#1d3fb8,#5a0a18);font-size:15px}}.fin a{{color:var(--gold);font-weight:800}}
.share{{position:fixed;right:max(14px,env(safe-area-inset-right,0px));bottom:calc(14px + env(safe-area-inset-bottom,0px));font:800 15px system-ui;padding:13px 18px;border-radius:999px;border:2px solid #000;background:var(--gold);color:#111;box-shadow:3px 3px 0 #000;cursor:pointer}}
button:focus-visible,a:focus-visible{{outline:3px solid #fff;outline-offset:2px}}
</style></head><body><div class="w">
<div class="top"><a href="{SITE}/">Véloce Mercato</a><span>Grand reportage</span></div>
<span class="eye">Baby-foot · portrait</span>
<h1>{e(a['titre'])}</h1>
{f'<figure class="hero-ph"><img src="{e(a["image"]["src"])}" alt="{e(a["image"].get("alt",""))}"><figcaption>{e(a["image"].get("credit",""))}</figcaption></figure>' if str((a.get('image') or {}).get('src','')).startswith('/img/reportages/') else ''}
<div class="vid"><video src="{e(vm.get('src'))}" poster="{e(vm.get('poster'))}" controls playsinline preload="metadata"></video><small>🎬 Le reportage en vidéo · voix de synthèse · reconstitution illustrée</small></div>
<div class="ess"><b>L’essentiel en 30 secondes</b><ul>{ess}</ul></div>
{body}
{f'<div class="nm"><p class="src">🎬 Le reportage de Nice-Matin, diffusé sur sa chaîne Dailymotion :</p><iframe src="https://www.dailymotion.com/embed/video/{e(dm)}" title="Reportage Nice-Matin" loading="lazy" allow="fullscreen; picture-in-picture" allowfullscreen></iframe></div>' if re.fullmatch(r'x[a-zA-Z0-9]{4,12}', dm) else ''}
<p class="src"><b>Sources :</b></p><ul class="src">{src}</ul>
<p class="src">Article rédigé avec l’aide d’une IA à partir des sources citées, sans entretien. Photos ITSF Gold WT Finals 2026 transmises par les proches d’Alexia Depagne ; elles seront retirées sur simple demande.</p>
<div class="fin">Un reportage <a href="{SITE}/">Véloce Mercato</a>. Vous aussi, faites connaître votre club ou votre activité : <a href="{SITE}/web-studio.html">VM Studio</a> crée votre site à prix fixe, à distance.</div>
</div>
<button class="share" type="button" id="share">📤 Partager</button>
<script>
document.getElementById('share').addEventListener('click',function(){{var b=this,u=location.href,t=document.title;
 if(navigator.share){{navigator.share({{title:t,url:u}}).catch(function(){{}});return}}
 try{{navigator.clipboard.writeText(u).then(function(){{b.textContent='✅ Lien copié'}},function(){{b.textContent=u}})}}catch(x){{b.textContent=u}}}});
</script>
</body></html>
'''
    import vmstats
    target = ROOT / out
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(vmstats.add(page), encoding='utf-8')
    print('ok', url)


if __name__ == '__main__':
    sys.path.insert(0, str(ROOT))
    main(sys.argv[1], sys.argv[2])
