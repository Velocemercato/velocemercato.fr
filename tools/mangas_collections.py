#!/usr/bin/env python3
"""Génère les cartes « collections officielles » à partir d'un seul fichier de données.

- mangas/collections.json → accueil (volet Manga & Séries), /mangas/ et /mangas/catalogue/
- series/collections.json  → /series/ (VM Séries de mon enfance), si le fichier existe

Chaque série a soit une playlist YouTube officielle (« playlist »), soit une vidéo officielle
(« video »), soit seulement un lien vers la plateforme légale (« url »). Lancer après toute
modification des données : python tools/mangas_collections.py
"""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CIBLES = {
    'mangas/collections.json': ['index.html', 'mangas/index.html', 'mangas/catalogue/index.html'],
    'series/collections.json': ['series/index.html'],
}
BLOC = re.compile(r'(<div class="vm-collections">)(.*?)(</div>\s*</section>)', re.S)
PLAYLIST = re.compile(r'^PL[A-Za-z0-9_-]{10,60}$')
VIDEO = re.compile(r'^[A-Za-z0-9_-]{11}$')


def e(value):
    return html.escape(str(value or ''), quote=True)


def carte(s):
    titre = s['title']
    playlist = s.get('playlist', '')
    video = s.get('video', '')
    url = s.get('url', '')
    source = s.get('source', '')
    vignette = s.get('thumbnail') or (f'https://i.ytimg.com/vi/{video}/hqdefault.jpg' if VIDEO.match(video) else '')
    img = f'<img src="{e(vignette)}" alt="" loading="lazy" width="480" height="270">' if vignette else ''
    if PLAYLIST.match(playlist):
        bouton = (f'<button class="vm-collection-play" data-playlist="{e(playlist)}" '
                  f'aria-label="Lire les épisodes de {e(titre)}">▶ Lire les épisodes</button>')
    elif VIDEO.match(video):
        bouton = (f'<button class="vm-collection-play" data-video="{e(video)}" '
                  f'aria-label="Lire {e(titre)}">▶ {e(s.get("playLabel") or "Lire la vidéo")}</button>')
    else:
        bouton = f'<a class="vm-collection-play" href="{e(url)}">Voir la saison sur {e(source)}</a>'
    liens = f'<a href="{e(url)}">Ouvrir sur {e(source)} ↗</a>' if url else ''
    if s.get('alternative'):
        liens += f'<a href="{e(s["alternative"])}">{e(s.get("alternativeLabel") or "Voir aussi")}</a>'
    return (f'<article class="tile vm-collection" data-title="{e(titre.lower())}">'
            f'<div class="vm-collection-screen">{img}{bouton}</div>'
            f'<div class="vm-collection-content"><h3>{e(titre)}</h3><small>{e(s.get("label"))}</small>'
            f'<p>{e(s.get("summary"))}</p>{liens}</div></article>')


def verifier(series, fichier):
    vus = set()
    for s in series:
        cle = s['title'].lower()
        if cle in vus:
            raise SystemExit(f'{fichier} : « {s["title"]} » est en double')
        vus.add(cle)
        if not (PLAYLIST.match(s.get('playlist', '')) or VIDEO.match(s.get('video', '')) or s.get('url', '').startswith('https://')):
            raise SystemExit(f'{fichier} : « {s["title"]} » n’a ni playlist, ni vidéo, ni lien https')
        if s.get('public') == 'adulte':
            raise SystemExit(f'{fichier} : « {s["title"]} » est réservé aux adultes et reste hors des collections familiales')


def main(racine=ROOT):
    total = 0
    for donnees, pages in CIBLES.items():
        chemin = Path(racine) / donnees
        if not chemin.is_file():
            continue
        series = json.loads(chemin.read_text(encoding='utf-8'))['series']
        verifier(series, donnees)
        contenu = ''.join(carte(s) for s in series)
        for page in pages:
            p = Path(racine) / page
            if not p.is_file():
                print(f'{page} absente : ignorée')
                continue
            s = p.read_text(encoding='utf-8')
            nouveau, n = BLOC.subn(lambda m: m.group(1) + contenu + m.group(3), s, count=1)
            if not n:
                raise SystemExit(f'{page} : bloc <div class="vm-collections"> introuvable')
            if nouveau != s:
                p.write_text(nouveau, encoding='utf-8')
            total += 1
        print(f'{donnees} : {len(series)} séries dans {", ".join(pages)}')
    return total


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT)
