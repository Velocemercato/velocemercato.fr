#!/usr/bin/env python3
"""Le fil express : les derniers TITRES de la presse, avec le lien vers l'article d'origine.

Aucun appel à l'IA (gratuit) : on recopie seulement le titre, le nom du média, l'heure et le lien,
comme un agrégateur. Même liste de médias autorisés que les robots (robots.txt respecté côté lecture
des articles ; ici on ne lit que les flux RSS publics prévus pour ça).
"""

import datetime as dt
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import update_news as robot

FOOT = list(robot.FEEDS)
FOOT_HOSTS = set(robot.ALLOWED_HOSTS)
import update_actus  # noqa: E402  (remplit robot.FEEDS avec les flux d'actualité générale)
ACTUS = list(robot.FEEDS)
ACTUS_HOSTS = set(robot.ALLOWED_HOSTS)
import update_gaming  # noqa: E402
GAMING = list(robot.FEEDS)
GAMING_HOSTS = set(robot.ALLOWED_HOSTS)

# Titres seulement (pas de réécriture IA) : médias demandés par le responsable VM, avec lien vers l'article d'origine.
FOOT += [
    ('FRANCE', 'FRANCE', "L'Équipe", 'https://dwh.lequipe.fr/api/edito/rss?path=/Football/'),
    ('FRANCE', 'FRANCE', 'So Foot', 'https://www.sofoot.com/rss.xml'),
    ('INTERNATIONAL', 'INTERNATIONAL', 'Goal', 'https://www.goal.com/feeds/fr/news'),
    ('FRANCE', 'FRANCE', '20 Minutes', 'https://www.20minutes.fr/feeds/rss-football.xml'),
    ('FRANCE', 'FRANCE', 'Le Parisien', 'https://feeds.leparisien.fr/leparisien/rss/sports/football'),
]
ACTUS += [
    ('FRANCE', 'FRANCE', '20 Minutes', 'https://www.20minutes.fr/feeds/rss-une.xml'),
    ('FRANCE', 'FRANCE', 'Le Monde', 'https://www.lemonde.fr/rss/une.xml'),
    ('FRANCE', 'FRANCE', "L'Est Républicain", 'https://www.estrepublicain.fr/rss'),
    ('FRANCE', 'FRANCE', 'Le Figaro', 'https://www.lefigaro.fr/rss/figaro_actualites.xml'),
    ('FRANCE', 'FRANCE', 'BFMTV', 'https://www.bfmtv.com/rss/news-24-7/'),
]
GAMING += [
    ('GAMING', 'GAMING', 'Journal du Geek', 'https://www.journaldugeek.com/feed/'),
    ('GAMING', 'GAMING', 'IGN France', 'https://fr.ign.com/feed.xml'),
    ('GAMING', 'GAMING', 'Numerama', 'https://www.numerama.com/feed/'),
]
EXTRA_HOSTS = {'lequipe.fr', 'sofoot.com', 'goal.com', '20minutes.fr', 'leparisien.fr', 'lemonde.fr', 'estrepublicain.fr',
               'lefigaro.fr', 'bfmtv.com', 'journaldugeek.com', 'ign.com', 'numerama.com'}

robot.rss_items = update_gaming._rss_items  # lecture brute des flux
robot.ALLOWED_HOSTS = FOOT_HOSTS | ACTUS_HOSTS | GAMING_HOSTS | EXTRA_HOSTS
robot.MAX_AGE_HOURS = 36
robot.BLOCK = re.compile(r'\b(horoscope|bon plan|promo(tion)?s?|soldes?|code promo|jeu concours|concours|'
                         r'giveaway|pronostics?|paris sportifs|cotes?|casino|sponsoris[eé]|publi-?rédactionnel)\b', re.I)
OUT = Path('fil.json')
KEEP = {'foot': 200, 'actus': 200, 'gaming': 120}


def grab(job):
    kind, feed = job
    try:
        _, posts = robot.rss_items(feed)
    except Exception as exc:
        print(f'Flux muet {feed[2]} : {type(exc).__name__}', flush=True)
        return []
    return [{'k': kind, 't': p['title'][:180], 'u': p['url'], 's': p['source'],
             'd': p['date'].isoformat(timespec='seconds').replace('+00:00', 'Z')} for p in posts]


def main():
    jobs = [('foot', f) for f in FOOT] + [('actus', f) for f in ACTUS] + [('gaming', f) for f in GAMING]
    rows = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        for items in pool.map(grab, jobs):
            rows.extend(items)
    if not rows:
        print('Aucun titre récupéré : fil inchangé.')
        return
    seen, out, count = set(), [], {}
    for r in sorted(rows, key=lambda r: r['d'], reverse=True):
        key = robot.normal(r['t'])[:70]
        if key in seen or r['u'] in seen:
            continue
        seen.update((key, r['u']))
        if count.get(r['k'], 0) >= KEEP[r['k']]:
            continue
        count[r['k']] = count.get(r['k'], 0) + 1
        out.append(r)
    OUT.write_text(json.dumps({'maj': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
                               'titres': out}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('Fil express : ' + ', '.join(f'{k} {v}' for k, v in count.items()))


if __name__ == '__main__':
    main()
