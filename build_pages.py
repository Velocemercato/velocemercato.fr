#!/usr/bin/env python3
"""Véloce Mercato — crée une vraie page HTML par brève (dossier a/) et le sitemap.

Google peut ainsi lire et référencer chaque brève, et un lien partagé sur les
réseaux affiche le bon titre et le bon résumé. Aucune brève n'est modifiée.
"""

import datetime as dt
import html
import json
import re
from pathlib import Path

import vmbar

SITE = 'https://velocemercato.fr'
OUT = Path('a')
ARTICLES = json.loads(Path('articles.json').read_text(encoding='utf-8'))

PAGE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} – Véloce Mercato</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:site_name" content="Véloce Mercato">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}">
<meta property="og:image" content="{site}/img/partage-velocemercato.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:locale" content="fr_FR">
<meta property="article:published_time" content="{iso}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{site}/img/partage-velocemercato.jpg">
<meta name="theme-color" content="#070c1f">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230f2470'/%3E%3Ctext x='32' y='44' font-family='Impact,sans-serif' font-size='30' font-style='italic' text-anchor='middle' fill='%23f4cf55'%3EVM%3C/text%3E%3C/svg%3E">
<script type="application/ld+json">{ld}</script>
<style>
:root{{--bg:#070c1f;--surface:#0f1a3d;--ink:#eef2ff;--muted:#a9b4d6;--royal:#6f8fff;--gold:#f4cf55;--red:#e1243a;--green:#14a35a;--c:{color}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.65 Barlow,system-ui,sans-serif}}
header{{background:#050917;padding:12px 16px;border-bottom:6px solid;border-image:linear-gradient(90deg,#1d3fb8 0 33.3%,#fff 33.3% 66.6%,#e1243a 66.6%) 1;display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}}
.logo{{color:#fff;text-decoration:none;font:italic 1.55rem/1 Impact,Anton,sans-serif;letter-spacing:.03em;text-shadow:3px 3px 0 #000}}.logo b{{color:var(--gold);font-weight:400}}
nav{{display:flex;gap:6px;flex-wrap:wrap}}nav a{{color:#0b1533;background:#fff;border:2px solid #000;border-radius:999px;padding:3px 10px;font:700 .78rem/1.4 'Barlow Condensed',system-ui,sans-serif;text-transform:uppercase;text-decoration:none;box-shadow:2px 2px 0 #000}}
nav a.don{{background:var(--gold)}}
main{{max-width:760px;margin:0 auto;padding:22px 16px 48px}}
article{{background:var(--surface);border:3px solid #000;box-shadow:7px 7px 0 var(--c);border-radius:16px;overflow:hidden}}
.cover{{background:var(--c);border-bottom:3px solid #000;display:flex;align-items:center;gap:10px;padding:10px 16px;min-height:56px}}
.cover .rub{{font:400 1.5rem/1 Impact,Anton,sans-serif;text-transform:uppercase;color:#fff;text-shadow:3px 3px 0 #000;letter-spacing:.02em}}
.badge{{margin-left:auto;flex:none;font:400 1rem/1 Impact,Anton,sans-serif;letter-spacing:.06em;padding:5px 10px 3px;border:2px solid #000;background:#fff;color:#0b1533}}
.badge.OFFICIEL{{background:var(--green);color:#fff}}.badge.RUMEUR{{background:var(--gold)}}.badge.EUROPE{{background:var(--royal);color:#fff}}
.in{{padding:18px 20px 22px}}
.meta{{color:var(--gold);font:700 .85rem/1.3 'Barlow Condensed',system-ui,sans-serif;text-transform:uppercase;letter-spacing:.07em}}
h1{{font:400 2rem/1.08 Impact,Anton,sans-serif;text-transform:uppercase;margin:.35em 0 .6em;text-wrap:balance;text-shadow:2px 2px 0 #000}}
.chapo{{font-weight:600;color:#fff;border-left:4px solid var(--c);padding-left:12px}}
.src{{border-top:2px dashed rgba(255,255,255,.2);margin-top:18px;padding-top:12px;font-size:.92rem;color:var(--muted)}}.src a{{color:var(--gold)}}
.tools{{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}}
.btn{{display:inline-flex;align-items:center;gap:6px;border:3px solid #000;border-radius:999px;padding:9px 16px;font:700 .95rem/1 'Barlow Condensed',system-ui,sans-serif;text-transform:uppercase;letter-spacing:.04em;text-decoration:none;cursor:pointer;box-shadow:3px 3px 0 #000;background:var(--royal);color:#fff}}
.btn.gold{{background:var(--gold);color:#0b1533}}.btn.red{{background:var(--red)}}
h2{{font:400 1.6rem/1 Impact,Anton,sans-serif;text-transform:uppercase;margin:28px 0 10px;color:#fff;text-shadow:3px 3px 0 var(--c)}}
.rel{{display:grid;gap:10px}}@media(min-width:640px){{.rel{{grid-template-columns:1fr 1fr}}}}
.rel a{{display:block;background:var(--surface);border:2px solid #000;border-radius:12px;padding:10px 12px;color:var(--ink);text-decoration:none;box-shadow:3px 3px 0 var(--c);line-height:1.3;font-weight:600}}
.rel a small{{display:block;color:var(--gold);font:700 .75rem/1.3 'Barlow Condensed',system-ui,sans-serif;text-transform:uppercase;letter-spacing:.06em;margin-bottom:3px}}
.ai{{font-size:.8rem;color:var(--muted);margin-top:10px}}
.react{{margin:22px 0 4px;padding:14px 16px;border:2px solid #000;border-radius:14px;background:var(--surface);box-shadow:3px 3px 0 var(--c)}}.react b{{display:block;font-size:1.1rem}}.react p{{margin:4px 0 10px;color:var(--muted)}}
footer{{text-align:center;color:var(--muted);font-size:.85rem;padding:10px 16px 34px}}footer a{{color:var(--gold)}}
</style>
</head>
<body>
<header><a class="logo" href="/">VÉLOCE <b>MERCATO</b></a><nav><a href="/">Brèves</a><a href="/#videos">Vidéos</a><a href="/archives.html">Rechercher</a><a class="don" href="/soutenir.html">💛 Soutenir</a></nav></header>
<main>
<article>
<div class="cover"><span class="rub">{label}</span>{badge}</div>
<div class="in">
<p class="meta">{label} · <time datetime="{iso}">{date}</time></p>
<h1>{title}</h1>
{body}
<p class="src">Source : {sources}</p>
<p class="ai">Brève rédigée avec l'aide d'une IA à partir de la source citée, sans ajout de faits.</p>
<div class="tools"><button class="btn" type="button" id="share">↗ Partager</button><a class="btn" id="wa" target="_blank" rel="noopener">💬 WhatsApp</a><a class="btn" id="fb" target="_blank" rel="noopener">📘 Facebook</a><a class="btn" id="xx" target="_blank" rel="noopener">✖️ X</a><a class="btn gold" href="/soutenir.html">💛 Soutenir le média</a></div>
<div class="react"><b>💬 Et toi, t'en penses quoi ?</b><p>Viens en parler avec la communauté sur notre Discord.</p><a class="btn red" href="https://discord.gg/JEgfrUtJaX" target="_blank" rel="noopener">Commenter sur Discord ↗</a></div>
</div>
</article>
{related}
<div class="tools"><a class="btn red" href="/#videos">🎬 Les vidéos de buts</a><a class="btn" href="/">← Toutes les brèves</a></div>
</main>
<footer><a href="/mentions-legales.html">Mentions légales</a> · <a href="/archives.html">Archives</a></footer>
<script>
(function(){{var u=encodeURIComponent(location.href.split('#')[0]),t=encodeURIComponent(document.title);document.getElementById('wa').href='https://wa.me/?text='+t+'%20'+u;document.getElementById('fb').href='https://www.facebook.com/sharer/sharer.php?u='+u;document.getElementById('xx').href='https://twitter.com/intent/tweet?text='+t+'&url='+u;}})();
document.getElementById('share').onclick=function(){{var d={{title:document.title,url:location.href}};if(navigator.share){{navigator.share(d).catch(function(){{}});}}else if(navigator.clipboard){{navigator.clipboard.writeText(location.href).then(function(){{alert('Lien copié !');}});}}}};
</script>
</body>
</html>
"""

LABELS = {'LIGUE_1': 'Ligue 1', 'LIGUE_2': 'Ligue 2', 'NATIONAL': 'National', 'FEMININ': 'Football féminin',
          'BLEUS': 'Équipe de France', 'EUROPE': "Coupes d'Europe", 'ETRANGER': 'International'}
COLORS = {'LIGUE_1': '#1d3fb8', 'LIGUE_2': '#0e8f8f', 'NATIONAL': '#14a35a', 'FEMININ': '#b33fd1',
          'BLEUS': '#2b5cff', 'EUROPE': '#e1243a', 'ETRANGER': '#e07b12'}
MONTHS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août',
          'septembre', 'octobre', 'novembre', 'décembre']


def safe_id(value):
    return re.sub(r'[^A-Za-z0-9_-]', '-', str(value))[:80]


def safe_url(value):
    return value if isinstance(value, str) and value.startswith('https://') else None


def main():
    OUT.mkdir(exist_ok=True)
    e = lambda v: html.escape(str(v or ''), quote=True)
    urls, written = [], set()
    for a in ARTICLES:
        if not a.get('id') or not a.get('titre') or not a.get('texte'):
            continue
        name = safe_id(a['id']) + '.html'
        url = f'{SITE}/a/{name}'
        try:
            when = dt.datetime.fromisoformat(str(a.get('publishedAt', '')).replace('Z', '+00:00'))
        except ValueError:
            when = None
        date = f'{when.day} {MONTHS[when.month - 1]} {when.year}' if when else ''
        label = LABELS.get(str(a.get('championnat', '')).upper()) or ('Mercato' if a.get('categorie') == 'MERCATO' else 'Football')
        paras = [p.strip() for p in re.split(r'\n\s*\n', str(a['texte'])) if p.strip()]
        body = '\n'.join((f'<p class="chapo">{e(p)}</p>' if i == 0 else f'<p>{e(p)}</p>') for i, p in enumerate(paras))
        sources = ', '.join(
            (f'<a href="{e(u)}" rel="noopener nofollow" target="_blank">{e(s.get("nom") or u)}</a>' if (u := safe_url(s.get('url'))) else e(s.get('nom')))
            for s in a.get('sources', []) if isinstance(s, dict)) or 'Véloce Mercato'
        ld = json.dumps({'@context': 'https://schema.org', '@type': 'NewsArticle', 'headline': a['titre'][:110],
                         'datePublished': a.get('publishedAt'), 'dateModified': a.get('publishedAt'), 'url': url, 'description': a.get('resume', ''),
                         'image': [SITE + '/img/partage-velocemercato.jpg'], 'author': {'@type': 'Organization', 'name': 'Véloce Mercato'},
                         'publisher': {'@type': 'NewsMediaOrganization', 'name': 'Véloce Mercato', 'url': SITE + '/'}},
                        ensure_ascii=False).replace('</', '<\\/')
        champ = str(a.get('championnat', '')).upper()
        tag = str(a.get('tag', '')).upper()
        badge = f'<span class="badge {e(tag)}">{e(tag)}</span>' if tag in ('OFFICIEL', 'RUMEUR', 'EUROPE', 'MERCATO') else ''
        rel = [r for r in ARTICLES if r is not a and r.get('id') and r.get('titre') and r.get('texte')
               and str(r.get('championnat', '')).upper() == champ][:4]
        if len(rel) < 4:
            rel += [r for r in ARTICLES if r is not a and r not in rel and r.get('id') and r.get('titre') and r.get('texte')][:4 - len(rel)]
        related = ('<h2>À lire aussi</h2><div class="rel">' + ''.join(
            f'<a href="/a/{safe_id(r["id"])}.html"><small>{e(LABELS.get(str(r.get("championnat", "")).upper(), "Football"))}</small>{e(r["titre"])}</a>'
            for r in rel) + '</div>') if rel else ''
        page = PAGE.format(title=e(a['titre']), desc=e(a.get('resume') or a['titre']), url=url, ld=ld,
                           label=e(label), iso=e(a.get('publishedAt')), date=e(date), body=body,
                           sources=sources, site=SITE, color=COLORS.get(champ, '#1d3fb8'),
                           badge=badge, related=related)
        page = vmbar.inject(page, 'f')
        path = OUT / name
        if not path.exists() or path.read_text(encoding='utf-8') != page:
            path.write_text(page, encoding='utf-8')
        written.add(name)
        urls.append((url, a.get('publishedAt', '')))
    # Les pages des brèves retirées du fil sont supprimées (pas de page orpheline).
    for old in OUT.glob('*.html'):
        if old.name not in written:
            old.unlink()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
             f'  <url><loc>{SITE}/</loc><changefreq>hourly</changefreq></url>',
             f'  <url><loc>{SITE}/gaming.html</loc></url>',
             f'  <url><loc>{SITE}/soutenir.html</loc></url>',
             f'  <url><loc>{SITE}/archives.html</loc></url>',
             f'  <url><loc>{SITE}/studio.html</loc></url>',
             f'  <url><loc>{SITE}/ou-regarder.html</loc></url>',
             f'  <url><loc>{SITE}/decouvrir.html</loc></url>',
             f'  <url><loc>{SITE}/radio.html</loc></url>',
             f'  <url><loc>{SITE}/shop/</loc></url>',
             f'  <url><loc>{SITE}/allolivre/</loc></url>',
             f'  <url><loc>{SITE}/comparateur/</loc></url>',
             f'  <url><loc>{SITE}/web-studio.html</loc></url>',
             f'  <url><loc>{SITE}/boutique/</loc></url>',
             f'  <url><loc>{SITE}/vm/</loc></url>',
             f'  <url><loc>{SITE}/cv/</loc></url>',
             f'  <url><loc>{SITE}/menu/</loc></url>',
             f'  <url><loc>{SITE}/pro/</loc></url>',
             f'  <url><loc>{SITE}/emploi/</loc></url>',
             f'  <url><loc>{SITE}/belfort/</loc></url>',
             f'  <url><loc>{SITE}/pub/</loc></url>',
             f'  <url><loc>{SITE}/vm-location/</loc></url>',
             f'  <url><loc>{SITE}/pro-auto/</loc></url>',
             f'  <url><loc>{SITE}/actus/</loc><changefreq>hourly</changefreq></url>']
    lines += [f'  <url><loc>{html.escape(u)}</loc>' + (f'<lastmod>{html.escape(d[:10])}</lastmod>' if d else '') + '</url>'
              for u, d in urls]
    lines.append('</urlset>')
    Path('sitemap.xml').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Pages : {len(written)} brèves avec leur propre page, sitemap à jour.')


if __name__ == '__main__':
    main()
