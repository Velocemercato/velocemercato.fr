#!/usr/bin/env python3
"""VM Belfort : les titres de l'actu locale (Territoire de Belfort, nord Franche-Comté, Haute-Saône).

Gratuit (aucune IA) : on reprend seulement le titre, le média, l'heure et le lien vers l'article d'origine,
comme un agrégateur. Les flux nationaux/régionaux sont filtrés par noms de villes du secteur.
"""

import datetime as dt
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import update_news as robot

robot.MAX_AGE_HOURS = 72
robot.ALLOWED_HOSTS = {'estrepublicain.fr', 'francetvinfo.fr', 'francebleu.fr', 'ici.fr', 'lepays.fr',
                       'macommune.info', 'belfort.fr', 'leprogres.fr', 'bienpublic.com', 'vosgesmatin.fr'}
robot.BLOCK = re.compile(r'\b(horoscope|bon plan|promo(tion)?s?|soldes?|code promo|jeu concours|concours|'
                         r'giveaway|pronostics?|paris sportifs|cotes?|casino|sponsoris[eé]|publi-?rédactionnel|nécrologie|avis de décès)\b', re.I)

# (lieu, média, url, filtrer_par_ville)
FEEDS = [
    ('BELFORT', "L'Est Républicain", 'https://www.estrepublicain.fr/edition-belfort-hericourt-montbeliard/rss', False),
    ('HAUTE-SAONE', "L'Est Républicain", 'https://www.estrepublicain.fr/haute-saone/rss', False),
    ('BELFORT', "L'Est Républicain", 'https://www.estrepublicain.fr/territoire-de-belfort/rss', False),
    ('BELFORT', 'macommune.info', 'https://www.macommune.info/feed/', False),
    ('REGION', "L'Est Républicain", 'https://www.estrepublicain.fr/rss', True),
]
VILLES = re.compile(r"\b(belfort|territoire de belfort|montb[eé]liard|h[eé]ricourt|lure|champagney|ronchamp|giromagny|"
                    r"delle|beaucourt|valdoie|bavilliers|offemont|danjoutin|essert|grandvillars|plancher|luxeuil|"
                    r"vesoul|haute-sa[oô]ne|audincourt|sochaux|bethoncourt|exincourt|grand-charmont|frahier|"
                    r"chalonvillars|sermamagny|rougemont|etueffont|faverney|villersexel|saint-loup|nord franche-comt[eé])\b", re.I)
OUT = Path('belfort/actus.json')
KEEP = 150


def grab(feed):
    lieu, source, url, filtre = feed
    try:
        _, posts = robot.rss_items(('FRANCE', lieu, source, url))
    except Exception as exc:
        print(f'Flux muet {source} ({url}) : {type(exc).__name__}', flush=True)
        return []
    rows = []
    for p in posts:
        if filtre and not VILLES.search(p['title'] + ' ' + (p.get('feed_text') or '')[:300]):
            continue
        rows.append({'l': lieu, 't': p['title'][:180], 'u': p['url'], 's': source,
                     'd': p['date'].isoformat(timespec='seconds').replace('+00:00', 'Z')})
    print(f'{source} {url.split("/")[-2] if url.endswith("rss") else ""} : {len(rows)} titres', flush=True)
    return rows


def main():
    rows = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        for items in pool.map(grab, FEEDS):
            rows.extend(items)
    if not rows:
        print('Aucun titre local : fichier inchangé.')
        return
    seen, out = set(), []
    for r in sorted(rows, key=lambda r: r['d'], reverse=True):
        key = robot.normal(r['t'])[:70]
        if key in seen or r['u'] in seen:
            continue
        seen.update((key, r['u']))
        out.append(r)
        if len(out) >= KEEP:
            break
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({'maj': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
                               'titres': out}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'VM Belfort : {len(out)} titres')


if __name__ == '__main__':
    main()
