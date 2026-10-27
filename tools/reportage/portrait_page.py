"""Page « Les voix du mercato » à partir d'un portrait Markdown sourcé.
Usage : python tools/reportage/portrait_page.py tools/reportage/tanzi.md portraits/loic-tanzi.html"""
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import vmstats  # noqa: E402

src, out = Path(sys.argv[1]), sys.argv[2]
md = src.read_text(encoding='utf-8')
title = re.search(r'^# (.+)$', md, re.M).group(1)
body = markdown.markdown(re.sub(r'^# .+\n', '', md, count=1, flags=re.M), extensions=['tables'])
body = re.sub(r'(https?://[^\s<]+)', r'<a href="\1" target="_blank" rel="noopener nofollow">\1</a>', body)
url = f'https://velocemercato.fr/{out}'
page = f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title} – Les voix du mercato</title>
<meta name="description" content="Portrait de Loïc Tanzi, journaliste football au groupe L'Équipe : son parcours, de Goal et RMC à L'Équipe, à partir de sources publiques.">
<link rel="canonical" href="{url}"><meta property="og:title" content="{title}"><meta property="og:url" content="{url}">
<meta property="og:image" content="https://velocemercato.fr/img/partage-velocemercato.jpg"><link rel="icon" href="/app/foot-192.png"><meta name="theme-color" content="#0b0d17">
<style>
:root{{--bg:#0b0d17;--card:#141a33;--ink:#f1ede4;--muted:#b3b9cf;--gold:#ffd23f;--line:#2a3158}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
.w{{max-width:720px;margin:0 auto;padding-block:20px 90px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
.top{{display:flex;justify-content:space-between;font:800 13px/1 system-ui;letter-spacing:.08em;text-transform:uppercase}}.top a{{color:var(--gold);text-decoration:none}}
h1{{font:italic 900 clamp(32px,7vw,52px)/1.02 Impact,"Arial Black",sans-serif;text-transform:uppercase;margin:22px 0 10px;text-wrap:balance}}
h2{{font:italic 900 26px/1.1 Impact,"Arial Black",sans-serif;text-transform:uppercase;color:var(--gold);margin:30px 0 6px}}
blockquote{{margin:0;padding:10px 14px;border-left:4px solid var(--gold);background:var(--card);border-radius:8px;color:var(--muted)}}
table{{width:100%;border-collapse:collapse;font-size:15px}}.tw{{overflow-x:auto}}th,td{{text-align:left;padding:8px;border-bottom:1px solid var(--line);vertical-align:top}}th{{color:var(--gold)}}
a{{color:var(--ink);word-break:break-word}}
.share{{position:fixed;right:max(14px,env(safe-area-inset-right,0px));bottom:calc(14px + env(safe-area-inset-bottom,0px));font:800 15px system-ui;padding:13px 18px;border-radius:999px;border:2px solid #000;background:var(--gold);color:#111;box-shadow:3px 3px 0 #000;cursor:pointer}}
</style></head><body><div class="w">
<div class="top"><a href="https://velocemercato.fr/">Véloce Mercato</a><span>Les voix du mercato</span></div>
<h1>{title}</h1>
{body.replace('<table>', '<div class="tw"><table>').replace('</table>', '</table></div>')}
</div>
<button class="share" type="button" id="share">📤 Partager</button>
<script>document.getElementById('share').addEventListener('click',function(){{var b=this,u=location.href;if(navigator.share){{navigator.share({{title:document.title,url:u}}).catch(function(){{}});return}}try{{navigator.clipboard.writeText(u).then(function(){{b.textContent='✅ Lien copié'}},function(){{b.textContent=u}})}}catch(x){{b.textContent=u}}}});</script>
</body></html>
'''
(ROOT / out).write_text(vmstats.add(page), encoding='utf-8')
print('ok', url)
