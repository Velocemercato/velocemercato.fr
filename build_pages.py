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
<meta name="twitter:card" content="summary">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230f2470'/%3E%3Ctext x='32' y='44' font-family='Impact,sans-serif' font-size='30' font-style='italic' text-anchor='middle' fill='%23f4cf55'%3EVM%3C/text%3E%3C/svg%3E">
<script type="application/ld+json">{ld}</script>
<style>
:root{{--bg:#eef2fb;--surface:#fff;--ink:#0b1533;--muted:#4e5b7d;--royal:#1d3fb8;--head:#0f2470;--gold:#c9971a;--gold-hi:#f4cf55;--line:#0b1533}}
@media(prefers-color-scheme:dark){{:root{{--bg:#070c1f;--surface:#101833;--ink:#eef2ff;--muted:#9aa6c8;--royal:#6f8fff;--head:#050917;--gold:#e6b437;--line:#c9d3f5;color-scheme:dark}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 Barlow,system-ui,sans-serif}}
header{{background:var(--head);padding:14px 16px;border-bottom:6px solid;border-image:linear-gradient(90deg,#1d3fb8 0 33.3%,#fff 33.3% 66.6%,#e1243a 66.6%) 1}}
header a{{color:#fff;text-decoration:none;font:italic 1.6rem/1 Impact,Anton,sans-serif;letter-spacing:.03em}}header b{{color:var(--gold-hi);font-weight:400}}
main{{max-width:720px;margin:0 auto;padding:24px 16px 48px}}
article{{background:var(--surface);border:3px solid var(--line);box-shadow:6px 6px 0 var(--line);border-radius:14px;padding:22px}}
.meta{{color:var(--royal);font-weight:700;text-transform:uppercase;font-size:.85rem;letter-spacing:.06em}}
h1{{font:400 1.9rem/1.1 Impact,Anton,sans-serif;text-transform:uppercase;margin:.4em 0 .6em;text-wrap:balance}}
.src{{border-top:2px solid rgba(29,63,184,.15);margin-top:18px;padding-top:12px;font-size:.95rem}}.src a{{color:var(--royal)}}
.back{{display:inline-block;margin-top:22px;background:var(--royal);color:#fff;text-decoration:none;font-weight:700;text-transform:uppercase;padding:12px 20px;border-radius:999px;box-shadow:4px 4px 0 var(--line)}}
</style>
</head>
<body>
<header><a href="/">VÉLOCE <b>MERCATO</b></a></header>
<main>
<article>
<p class="meta">{label} · <time datetime="{iso}">{date}</time></p>
<h1>{title}</h1>
{body}
<p class="src">Source : {sources}</p>
</article>
<a class="back" href="/#a={idq}">← Toutes les brèves</a>
</main>
</body>
</html>
"""

LABELS = {'LIGUE_1': 'Ligue 1', 'LIGUE_2': 'Ligue 2', 'NATIONAL': 'National', 'FEMININ': 'Football féminin',
          'BLEUS': 'Équipe de France', 'EUROPE': "Coupes d'Europe", 'ETRANGER': 'International'}
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
        body = '\n'.join(f'<p>{e(p.strip())}</p>' for p in re.split(r'\n\s*\n', str(a['texte'])) if p.strip())
        sources = ', '.join(
            (f'<a href="{e(u)}" rel="noopener nofollow" target="_blank">{e(s.get("nom") or u)}</a>' if (u := safe_url(s.get('url'))) else e(s.get('nom')))
            for s in a.get('sources', []) if isinstance(s, dict)) or 'Véloce Mercato'
        ld = json.dumps({'@context': 'https://schema.org', '@type': 'NewsArticle', 'headline': a['titre'][:110],
                         'datePublished': a.get('publishedAt'), 'url': url, 'description': a.get('resume', ''),
                         'publisher': {'@type': 'NewsMediaOrganization', 'name': 'Véloce Mercato', 'url': SITE + '/'}},
                        ensure_ascii=False).replace('</', '<\\/')
        page = PAGE.format(title=e(a['titre']), desc=e(a.get('resume') or a['titre']), url=url, ld=ld,
                           label=e(label), iso=e(a.get('publishedAt')), date=e(date), body=body,
                           sources=sources, idq=e(a['id']))
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
             f'  <url><loc>{SITE}/archives.html</loc></url>']
    lines += [f'  <url><loc>{html.escape(u)}</loc>' + (f'<lastmod>{html.escape(d[:10])}</lastmod>' if d else '') + '</url>'
              for u, d in urls]
    lines.append('</urlset>')
    Path('sitemap.xml').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Pages : {len(written)} brèves avec leur propre page, sitemap à jour.')


if __name__ == '__main__':
    main()
