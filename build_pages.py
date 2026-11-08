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

SITE = 'https://velocemercato.fr'
OUT = Path('a')
ARTICLES = json.loads(Path('articles.json').read_text(encoding='utf-8'))

PAGE = """<!doctype html>
<html lang="fr" data-vmt="article">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} – Véloce Mercato</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:site_name" content="Véloce Mercato">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}">
<meta property="og:image" content="{ogimg}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:locale" content="fr_FR">
<meta property="article:published_time" content="{iso}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{ogimg}">
<meta name="theme-color" content="#050608">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230f2470'/%3E%3Ctext x='32' y='44' font-family='Impact,sans-serif' font-size='30' font-style='italic' text-anchor='middle' fill='%23f4cf55'%3EVM%3C/text%3E%3C/svg%3E">
<script type="application/ld+json">{ld}</script>
<style>
:root{{--bg:#050608;--surface:#0e0e13;--ink:#f4f4f6;--muted:#b9b9c2;--royal:#c4081f;--gold:#ffc21a;--red:#e0102c;--green:#14a35a;--c:{color}}}
*{{box-sizing:border-box}}
body{{margin:0;background:radial-gradient(ellipse at 0 30%,#3a0610 0,transparent 42%),radial-gradient(ellipse at 100% 75%,#2a0610 0,transparent 40%),linear-gradient(180deg,#07080b,#030304);background-attachment:fixed;color:var(--ink);font:17px/1.65 Barlow,system-ui,sans-serif}}
header{{background:linear-gradient(180deg,#0b0c12,#050608);padding:12px 16px;border-bottom:1px solid #3a0a12;box-shadow:0 6px 18px #000c;display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}}
.logo{{color:#fff;text-decoration:none;font:italic 900 1.6rem/1 'Barlow Condensed',Impact,sans-serif;letter-spacing:.02em;text-shadow:2px 2px 0 #000}}.logo b{{color:#9fe34b;font-weight:900}}
nav{{display:flex;gap:6px;flex-wrap:wrap}}nav a{{color:#fff;background:transparent;border:2px solid #5a1420;border-radius:7px;padding:8px 11px;font:700 1rem/1 'Barlow Condensed',system-ui,sans-serif;text-transform:uppercase;text-decoration:none;min-height:40px;display:inline-flex;align-items:center}}nav a:hover{{border-color:var(--red);box-shadow:0 0 12px #ff1f3d88}}
nav a.don{{border-color:var(--gold);color:var(--gold)}}
main{{max-width:760px;margin:0 auto;padding:22px 16px 48px}}
article{{background:linear-gradient(180deg,#131318,#09090d);border:2px solid #c4081f;box-shadow:0 0 14px #ff1f3d55,inset 0 0 18px #ff1f3d14;border-radius:10px;overflow:hidden}}
.cover{{background:linear-gradient(90deg,var(--c) 32%,transparent 78%),url('/img/vm-art/vm-banniere-tetes-768.webp') right 25%/auto 300% no-repeat,#0a080c;border-bottom:2px solid #c4081f;display:flex;align-items:center;gap:10px;padding:10px 16px;min-height:56px}}
.cover .rub{{font:italic 800 1.6rem/1 'Barlow Condensed',Impact,sans-serif;text-transform:uppercase;color:#fff;text-shadow:3px 3px 0 #000;letter-spacing:.02em}}
.badge{{margin-left:auto;flex:none;font:400 1rem/1 Impact,Anton,sans-serif;letter-spacing:.06em;padding:5px 10px 3px;border:2px solid #000;background:#fff;color:#0b1533}}
.badge.OFFICIEL{{background:var(--green);color:#fff}}.badge.RUMEUR{{background:var(--gold)}}.badge.EUROPE{{background:var(--royal);color:#fff}}
.in{{padding:18px 20px 22px}}
.meta{{color:var(--gold);font:700 .85rem/1.3 'Barlow Condensed',system-ui,sans-serif;text-transform:uppercase;letter-spacing:.07em}}
h1{{font:italic 800 2.3rem/1.02 'Barlow Condensed',Impact,sans-serif;text-transform:uppercase;margin:.35em 0 .6em;text-wrap:balance;text-shadow:2px 2px 0 #000}}
.chapo{{font-weight:600;color:#fff;border-left:4px solid var(--c);padding-left:12px}}
.src{{border-top:2px dashed rgba(255,255,255,.2);margin-top:18px;padding-top:12px;font-size:.92rem;color:var(--muted)}}.src a{{color:var(--gold)}}
.tools{{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}}
.btn{{display:inline-flex;align-items:center;gap:6px;min-height:42px;border:1px solid #ff5a6e;border-radius:7px;padding:9px 16px;font:italic 800 1rem/1 'Barlow Condensed',system-ui,sans-serif;text-transform:uppercase;letter-spacing:.03em;text-decoration:none;cursor:pointer;box-shadow:0 0 12px #ff1f3d66;background:linear-gradient(180deg,#e0102c,#a8061c);color:#fff}}
.btn.gold{{background:linear-gradient(180deg,#ffd75a,#e19a00);border-color:#ffe58a;color:#120a00;box-shadow:0 0 12px #ffc21a66}}.btn.red{{background:linear-gradient(180deg,#e0102c,#a8061c)}}
h2{{font:italic 800 1.8rem/1 'Barlow Condensed',Impact,sans-serif;text-transform:uppercase;margin:28px 0 10px;color:#fff}}h2::before{{content:'♛ ';color:var(--gold)}}
.rel{{display:grid;gap:10px}}@media(min-width:640px){{.rel{{grid-template-columns:1fr 1fr}}}}
.rel a{{display:block;background:linear-gradient(180deg,#131318,#09090d);border:2px solid #3a1018;border-radius:10px;padding:10px 12px;color:var(--ink);text-decoration:none;line-height:1.3;font-weight:600}}
.rel a small{{display:block;color:var(--gold);font:700 .75rem/1.3 'Barlow Condensed',system-ui,sans-serif;text-transform:uppercase;letter-spacing:.06em;margin-bottom:3px}}
.ai{{font-size:.8rem;color:var(--muted);margin-top:10px}}
.react{{margin:22px 0 4px;padding:14px 16px;border:2px solid #c4081f;border-radius:10px;background:#0e0e13;box-shadow:0 0 12px #ff1f3d44}}.react b{{display:block;font-size:1.1rem}}.react p{{margin:4px 0 10px;color:var(--muted)}}
figure{{margin:0 0 16px}}figure img{{display:block;width:100%;height:auto;border:2px solid #000;border-radius:12px}}figcaption,.credit{{font-size:.8rem;color:var(--muted);margin-top:6px}}.vid{{position:relative;aspect-ratio:16/9;margin:16px 0 6px;border:2px solid #000;border-radius:12px;overflow:hidden;background:#000}}.vid iframe{{position:absolute;inset:0;width:100%;height:100%;border:0}}
footer{{text-align:center;color:var(--muted);font-size:.85rem;padding:10px 16px 34px}}footer a{{color:var(--gold)}}
</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;600&family=Barlow+Condensed:ital,wght@0,700;1,800&display=swap"><link rel="stylesheet" href="/assets/vm-theme.css">
</head>
<body>
<header><a class="logo" href="/">VÉLOCE <b>MERCATO</b></a><nav><a href="/">Brèves</a><a href="/#videos">Vidéos</a><a href="/archives.html">Rechercher</a><a class="don" href="/soutenir.html">💛 Soutenir</a></nav></header>
<main>
<article>
<div class="cover"><span class="rub">{label}</span>{badge}</div>
<div class="in">
<p class="meta">{label} · <time datetime="{iso}">{date}</time></p>
<h1>{title}</h1>
{media}{body}
{video}<p class="src">Source : {sources}</p>
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

LABELS = {'BABYFOOT': 'Baby-foot · portrait', 'LIGUE_1': 'Ligue 1', 'LIGUE_2': 'Ligue 2', 'NATIONAL': 'National', 'FEMININ': 'Football féminin',
          'BLEUS': 'Équipe de France', 'EUROPE': "Coupes d'Europe", 'ETRANGER': 'International'}
COLORS = {'BABYFOOT': '#b33fd1', 'LIGUE_1': '#1d3fb8', 'LIGUE_2': '#0e8f8f', 'NATIONAL': '#14a35a', 'FEMININ': '#b33fd1',
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
        # « ## Titre » = intertitre (grands formats) ; le reste reste du texte simple échappé.
        body = '\n'.join((para_html(p, i, e))
                          for i, p in enumerate(paras))
        essentiel = [str(x) for x in (a.get('essentiel') or []) if str(x).strip()][:6]
        if essentiel:
            body = ('<div class="essentiel" style="border:2px solid currentColor;border-radius:14px;padding:12px 16px;margin:0 0 18px">'
                    '<b>L’essentiel en 30 secondes</b><ul style="margin:8px 0 0;padding-left:20px">'
                    + ''.join(f'<li>{e(x)}</li>' for x in essentiel) + '</ul></div>\n' + body)
        sources = ', '.join(
            (f'<a href="{e(u)}" rel="noopener nofollow" target="_blank">{e(s.get("nom") or u)}</a>' if (u := safe_url(s.get('url'))) else e(s.get('nom')))
            for s in a.get('sources', []) if isinstance(s, dict)) or 'Véloce Mercato'
        img = a.get('image') if isinstance(a.get('image'), dict) else {}
        src = str(img.get('src') or '')
        src = src if re.fullmatch(r'/img/[\w/.-]+', src) else ''
        og = re.sub(r'\.webp$', '.jpg', src) if src and Path(re.sub(r'\.webp$', '.jpg', src).lstrip('/')).exists() else src
        ogimg = SITE + (og or '/img/partage-velocemercato.jpg')
        vid = a.get('video') if isinstance(a.get('video'), dict) else {}
        yt = str(vid.get('youtube') or '')
        ld = json.dumps({'@context': 'https://schema.org', '@type': 'NewsArticle', 'headline': a['titre'][:110],
                         'datePublished': a.get('publishedAt'), 'dateModified': a.get('publishedAt'), 'url': url, 'description': a.get('resume', ''),
                         'image': [ogimg], 'author': {'@type': 'Organization', 'name': 'Véloce Mercato'},
                         'publisher': {'@type': 'NewsMediaOrganization', 'name': 'Véloce Mercato', 'url': SITE + '/'}},
                        ensure_ascii=False).replace('</', '<\\/')
        champ = str(a.get('championnat', '')).upper()
        media = video = ''
        tag = str(a.get('tag', '')).upper()
        badge = f'<span class="badge {e(tag)}">{e(tag)}</span>' if tag in ('OFFICIEL', 'RUMEUR', 'EUROPE', 'MERCATO') else ''
        rel = [r for r in ARTICLES if r is not a and r.get('id') and r.get('titre') and r.get('texte')
               and str(r.get('championnat', '')).upper() == champ][:4]
        if len(rel) < 4:
            rel += [r for r in ARTICLES if r is not a and r not in rel and r.get('id') and r.get('titre') and r.get('texte')][:4 - len(rel)]
        related = ('<h2>À lire aussi</h2><div class="rel">' + ''.join(
            f'<a href="/a/{safe_id(r["id"])}.html"><small>{e(LABELS.get(str(r.get("championnat", "")).upper(), "Football"))}</small>{e(r["titre"])}</a>'
            for r in rel) + '</div>') if rel else ''
        if src:
            cap = f'<figcaption>{e(img.get("credit"))}</figcaption>' if img.get('credit') else ''
            media = f'<figure><img src="{e(src)}" alt="{e(img.get("alt") or a["titre"])}" width="1200" height="630">{cap}</figure>\n'
        vm = a.get('video_vm') if isinstance(a.get('video_vm'), dict) else {}
        if re.fullmatch(r'/img/[\w/.-]+\.mp4', str(vm.get('src', ''))):
            poster = str(vm.get('poster', ''))
            poster = f' poster="{e(poster)}"' if re.fullmatch(r'/img/[\w/.-]+\.(jpg|webp)', poster) else ''
            media += (f'<figure style="max-width:420px;margin:18px auto"><video src="{e(vm["src"])}"{poster} controls playsinline preload="none" '
                      f'style="width:100%;aspect-ratio:9/16;border-radius:14px;background:#000"></video>'
                      f'<figcaption>🎬 {e(vm.get("legende") or "La vidéo Véloce Mercato")}</figcaption></figure>\n')
        dm = str(vid.get('dailymotion') or '')
        leg = f'<p class="credit">🎬 {e(vid.get("legende"))}</p>\n' if vid.get('legende') else ''
        if re.fullmatch(r'x[a-zA-Z0-9]{4,12}', dm):
            video = f'<div class="vid"><iframe src="https://www.dailymotion.com/embed/video/{dm}" title="{e(vid.get("titre") or "Vidéo")}" loading="lazy" allow="fullscreen; picture-in-picture; web-share" allowfullscreen></iframe></div>\n' + leg
        elif re.fullmatch(r'[\w-]{11}', yt):
            video = f'<div class="vid"><iframe src="https://www.youtube-nocookie.com/embed/{yt}" title="{e(vid.get("titre") or "Vidéo")}" loading="lazy" allow="encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe></div>\n'
        elif (vl := safe_url(vid.get('lien'))):
            video = f'<div class="tools"><a class="btn red" href="{e(vl)}" target="_blank" rel="noopener">▶ {e(vid.get("titre") or "Voir la vidéo")}</a></div>\n'
        page = PAGE.format(title=e(a['titre']), desc=e(a.get('resume') or a['titre']), url=url, ld=ld,
                           label=e(label), iso=e(a.get('publishedAt')), date=e(date), body=body,
                           sources=sources, site=SITE, color=COLORS.get(champ, '#1d3fb8'),
                           badge=badge, related=related, media=media, video=video, ogimg=ogimg)
        page = vmbar.inject(page, 'f')
        path = OUT / name
        if not path.exists() or path.read_text(encoding='utf-8') != page:
            path.write_text(page, encoding='utf-8')
        written.add(name)
        urls.append((url, a.get('publishedAt', '')))
    # Actualiser le site public des informations RQ Pronos avec ces mêmes brèves.
    # Il n'envoie aucun post sur Facebook.
    from tools.pronos_public import build as build_pronos
    build_pronos(Path('.'))

    # Les pages des brèves retirées du fil restent en ligne (archive) :
    # les liens « À lire aussi » des brèves publiées et les partages déjà diffusés
    # continuent d'ouvrir la bonne page au lieu d'une 404 (poids négligeable, ~25 Ko par brève).
    # Seules les pages des brèves courantes sont réécrites ; aucune page n'est supprimée.
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
             f'  <url><loc>{SITE}/investisseurs.html</loc></url>',
             f'  <url><loc>{SITE}/boutique/</loc></url>',
             f'  <url><loc>{SITE}/vm/</loc></url>',
             f'  <url><loc>{SITE}/cv/</loc></url>',
             f'  <url><loc>{SITE}/menu/</loc></url>',
             f'  <url><loc>{SITE}/pro/</loc></url>',
             f'  <url><loc>{SITE}/emploi/</loc></url>',
             f'  <url><loc>{SITE}/belfort/</loc></url>',
             f'  <url><loc>{SITE}/foot-amateur/</loc><changefreq>hourly</changefreq></url>',
             f'  <url><loc>{SITE}/multisport/</loc><changefreq>hourly</changefreq></url>',
             f'  <url><loc>{SITE}/mangas/</loc></url>',
             f'  <url><loc>{SITE}/pub/</loc></url>',
             f'  <url><loc>{SITE}/pro-auto/</loc></url>',
             f'  <url><loc>{SITE}/actus/</loc><changefreq>hourly</changefreq></url>',
             f'  <url><loc>{SITE}/pronos/</loc><changefreq>hourly</changefreq></url>']
    lines += [f'  <url><loc>{html.escape(u)}</loc>' + (f'<lastmod>{html.escape(d[:10])}</lastmod>' if d else '') + '</url>'
              for u, d in urls]
    # Les brèves archivées (présentes sur le disque mais retirées du fil du jour)
    # restent référencées : leurs liens « À lire aussi » et partages restent valides.
    archived = sorted(OUT.glob('*.html'))
    lines += [f'  <url><loc>{SITE}/a/{html.escape(p.name)}</loc></url>'
              for p in archived if f'{SITE}/a/{p.name}' not in {u for u, _ in urls}]
    lines.append('</urlset>')
    Path('sitemap.xml').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    # Une sélection statique de brèves sourcées reste visible sur l'accueil
    # même quand le chargement du fil JavaScript échoue.
    from tools.home_news_static import update_index
    update_index(Path('.'), ARTICLES)
    print(f'Pages : {len(written)} brèves avec leur propre page, sitemap à jour.')


if __name__ == '__main__':
    main()
