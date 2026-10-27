"""Pages de partage statiques, lisibles par les robots sociaux sans JavaScript."""
import vmstats
import html
import json
from pathlib import Path
import re

SITE = 'https://velocemercato.fr'
CDN = re.compile(r'^https://cdn\.jsdelivr\.net/gh/Velocemercato/velocemercato\.fr@[0-9a-f]{40}/[a-z0-9-]+\.(mp4|jpg|m4a)$')


def page_url(ident):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{1,99}', ident):
        raise ValueError('Identifiant d’émission invalide')
    return f'{SITE}/studio/episodes/{ident}.html'


def build_episode_pages(rows, root):
    folder = Path(root) / 'studio/episodes'
    folder.mkdir(parents=True, exist_ok=True)
    for row in rows:
        if row.get('publie') is not True or not CDN.fullmatch(row.get('video', '')):
            continue
        canonical = page_url(row['id'])
        row['page'] = canonical
        local = folder / 'posters' / f"{row['id']}.jpg"
        row['poster'] = f'/studio/episodes/posters/{local.name}' if local.is_file() else row.get('image', '')
        poster = f"{SITE}/studio/episodes/posters/{local.name}" if local.is_file() else row.get('image', '')
        if not (local.is_file() or CDN.fullmatch(poster)):
            poster = f'{SITE}/img/partage-velocemercato.jpg'
        esc = lambda value: html.escape(str(value), quote=True)
        data = json.dumps(row, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
        markup = f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(row['titre'])} — La Pastille</title>
<meta name="description" content="{esc(row.get('accroche', ''))}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="video.other"><meta property="og:site_name" content="Véloce Mercato — La Pastille">
<meta property="og:url" content="{esc(canonical)}"><meta property="og:title" content="{esc(row['titre'])}">
<meta property="og:description" content="{esc(row.get('accroche', ''))}">
<meta property="og:image" content="{esc(poster)}"><meta property="og:image:alt" content="{esc(row['titre'])}">
<meta property="og:video" content="{esc(row['video'])}"><meta property="og:video:secure_url" content="{esc(row['video'])}">
<meta property="og:video:type" content="video/mp4"><meta property="og:video:width" content="1280"><meta property="og:video:height" content="720">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(row['titre'])}"><meta name="twitter:image" content="{esc(poster)}">
<link rel="stylesheet" href="/assets/pastille.css"><script src="/assets/pastille-player.js" defer></script>
</head><body class="episode-page"><main>
<nav aria-label="Navigation"><a href="/">Véloce Mercato</a><a href="/studio.html#tv">Toutes les émissions</a><a href="https://vmunivers.fr/">VM Univers</a></nav>
<p class="episode-label">La Pastille · Heineguez, présentateur virtuel · émission générée par IA · personnages inventés</p>
<div class="vm-channels" role="group" aria-label="Nos chaînes vidéo"><a class="vm-channel vm-channel--youtube" href="https://www.youtube.com/@VeloceMercato" target="_blank" rel="noopener">▶ YouTube</a><a class="vm-channel vm-channel--twitch" href="https://www.twitch.tv/velocemercato" target="_blank" rel="noopener">Twitch ↗</a></div>
<h1>{esc(row['titre'])}</h1><p>{esc(row.get('accroche', ''))}</p>
<div id="episodePlayer"><video id="episodeVideo" controls playsinline preload="metadata" poster="{esc(poster)}"><source src="{esc(row['video'])}" type="video/mp4"></video></div>
<p><a href="{esc(row['video'])}" rel="noopener">Ouvrir le fichier MP4</a> · <a href="/radio.html">Écouter VM Radio</a></p>
</main><script id="episodeData" type="application/json">{data}</script></body></html>
'''
        (folder / f"{row['id']}.html").write_text(vmstats.add(markup), encoding='utf-8')
