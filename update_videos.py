#!/usr/bin/env python3
"""Véloce Mercato — vidéos de buts des chaînes YouTube OFFICIELLES.

Lit les flux publics des chaînes officielles (ligues, FFF, UEFA…), garde les vidéos de buts,
les classe (derniers buts / plus beaux buts / buts gags) par championnat et écrit videos.json.
Le site les affiche avec le lecteur YouTube officiel : aucune vidéo n'est copiée ni hébergée.
Pas de clé API nécessaire.
"""

import datetime as dt
import html
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

OUT = Path('videos.json')
CACHE = Path('video-channels.json')   # pseudo YouTube -> identifiant de chaîne
NOW = dt.datetime.now(dt.timezone.utc)
MAX_AGE_DAYS = 21
MAX_VIDEOS = 90

# (championnat, nom affiché, pseudos possibles de la chaîne officielle) : le premier qui répond est gardé.
CHANNELS = [
    ('LIGUE_1', 'Ligue 1', ['Ligue1McDonalds', 'Ligue1']),
    ('LIGUE_2', 'Ligue 2', ['Ligue2BKT', 'Ligue2']),
    ('NATIONAL', 'FFF', ['FFF', 'fff']),
    ('BLEUS', 'Équipe de France', ['equipedefrance', 'EquipedeFrance']),
    ('EUROPE', 'Ligue des champions', ['ChampionsLeague', 'UEFAChampionsLeague']),
    ('EUROPE', 'UEFA', ['UEFA']),
    ('ETRANGER', 'Premier League', ['premierleague', 'PremierLeague']),
    ('ETRANGER', 'LaLiga', ['LaLiga', 'laliga']),
    ('ETRANGER', 'Serie A', ['SerieA', 'seriea']),
    ('ETRANGER', 'Bundesliga', ['Bundesliga', 'bundesliga']),
]

GOAL = re.compile(r"\b(buts?|goals?|golazo|résumé|resume|highlights|all goals|tous les buts|frappe|lucarne|retourné|bicyclette|panenka|ciseaux|volée)\b", re.I)
BEST = re.compile(r"(plus beaux?|plus belles?|top ?\d+|best goals?|best of|but du mois|but de la saison|goal of the (month|season|week)|golazo|chef[- ]d['’]oeuvre|incroyable|amazing|stunning|screamer|bicyclette|retourné|ciseaux|lucarne)", re.I)
GAG = re.compile(r"(gag|fails?|bloopers?|insolite|dr[ôo]le|funny|bourde|boulette|gaffe|contre son camp|own goals?|raté|ratés|miss(es)?|moments? (fous|wtf)|wtf|lol)", re.I)
SKIP = re.compile(r"(live|en direct|direct |conférence|conference|press|billet|ticket|pronostic|paris sportifs|bande-annonce|trailer)", re.I)
FEMININ = re.compile(r"(arkema|f[ée]minin|women|wsl|liga f|bleues|d1 )", re.I)
NATIONAL = re.compile(r"(national|n2|n3|coupe de france|amateur|r[ée]gional)", re.I)
UA = {'User-Agent': 'Mozilla/5.0 (compatible; VeloceMercato/2.0; +https://velocemercato.fr/)',
      'Accept-Language': 'fr-FR,fr;q=0.9'}


def get(url, limit=3_000_000):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read(limit)


def resolve(handle):
    page = get(f'https://www.youtube.com/@{handle}').decode('utf-8', 'replace')
    for pat in (r'"externalId":"(UC[\w-]{22})"', r'<meta itemprop="identifier" content="(UC[\w-]{22})"',
                r'"channelId":"(UC[\w-]{22})"', r'youtube\.com/channel/(UC[\w-]{22})'):
        m = re.search(pat, page)
        if m:
            return m.group(1)
    return None


def kind(title):
    if GAG.search(title):
        return 'GAGS'
    if BEST.search(title):
        return 'BEAUX'
    return 'DERNIERS'


def feed(channel_id):
    ns = {'a': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015',
          'media': 'http://search.yahoo.com/mrss/'}
    root = ET.fromstring(get(f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'))
    for e in root.findall('a:entry', ns):
        vid = e.findtext('yt:videoId', default='', namespaces=ns)
        title = html.unescape(e.findtext('a:title', default='', namespaces=ns)).strip()
        pub = e.findtext('a:published', default='', namespaces=ns)
        if re.fullmatch(r'[\w-]{11}', vid or '') and title and pub:
            yield vid, title, pub


def main():
    cache = json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
    old = json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else []
    found, seen = [], set()
    for champ, name, handles in CHANNELS:
        cid = next((cache[h] for h in handles if cache.get(h)), None)
        if not cid:
            for h in handles:
                try:
                    cid = resolve(h)
                except Exception as exc:
                    print(f'Chaîne @{h} : introuvable ({type(exc).__name__})', flush=True)
                    continue
                if cid:
                    cache[h] = cid
                    break
        if not cid:
            print(f'{name} : aucune chaîne officielle trouvée, ignorée.', flush=True)
            continue
        try:
            items = list(feed(cid))
        except Exception as exc:
            print(f'{name} : flux illisible ({type(exc).__name__})', flush=True)
            continue
        kept = 0
        for vid, title, pub in items:
            try:
                date = dt.datetime.fromisoformat(pub.replace('Z', '+00:00'))
            except ValueError:
                continue
            if vid in seen or NOW - date > dt.timedelta(days=MAX_AGE_DAYS) or SKIP.search(title):
                continue
            if not (GOAL.search(title) or BEST.search(title) or GAG.search(title)):
                continue
            c = champ
            if FEMININ.search(title):
                c = 'FEMININ'
            elif champ == 'NATIONAL' and not NATIONAL.search(title):
                c = 'BLEUS' if re.search(r'bleus|[ée]quipe de france', title, re.I) else 'NATIONAL'
            seen.add(vid)
            kept += 1
            found.append({'id': vid, 'titre': title[:140], 'chaine': name, 'championnat': c,
                          'type': kind(title), 'publishedAt': date.isoformat(timespec='seconds')})
        print(f'{name} : {len(items)} vidéos lues, {kept} vidéos de buts gardées.', flush=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not found:
        print('Aucune vidéo trouvée : videos.json inchangé.', flush=True)
        if not OUT.exists():
            OUT.write_text('[]\n', encoding='utf-8')
        return
    # On garde aussi les vidéos encore récentes du passage précédent (si une chaîne ne répond pas).
    ids = {v['id'] for v in found}
    for v in old:
        if isinstance(v, dict) and v.get('id') not in ids:
            try:
                if NOW - dt.datetime.fromisoformat(v['publishedAt']) <= dt.timedelta(days=MAX_AGE_DAYS):
                    found.append(v)
            except (KeyError, ValueError):
                pass
    found.sort(key=lambda v: v['publishedAt'], reverse=True)
    OUT.write_text(json.dumps(found[:MAX_VIDEOS], ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Vidéos publiées : {min(len(found), MAX_VIDEOS)}.', flush=True)


if __name__ == '__main__':
    main()
