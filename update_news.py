#!/usr/bin/env python3
"""Veille football : brèves attribuées à leur source, sans IA ni invention."""
import datetime as dt
import email.utils
import hashlib
import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

PATH = Path('articles.json')
NOW = dt.datetime.now(dt.timezone.utc)
MAX_AGE = dt.timedelta(hours=18)
MAX_NEW = 5
MAX_TOTAL = 150
QUERIES = {
    'FRANCE': 'football Ligue 1 Ligue 2 National mercato',
    'INTERNATIONAL': 'football mercato Europe international',
    'FEMININ': 'football féminin France Europe',
    'AMATEUR': 'football National 2 National 3 amateur',
}
# Noms de médias acceptés : ne constitue pas une vérification indépendante.
SOURCES = ('lequipe', "l'equipe", 'l’équipe', 'rmc sport', 'franceinfo',
           'france bleu', 'ouest-france', 'le parisien', 'afp', 'reuters',
           'bbc sport', 'the guardian', 'goal.com', 'goal', 'eurosport',
           'foot mercato', 'maxifoot', 'so foot', 'skysports', 'sky sports')
BLOCK = re.compile(r'\b(pronostic|paris sportifs|cote[s]?|casino|billetterie|streaming ill[eé]gal)\b', re.I)
MATCH = re.compile(r'\b(match|r[eé]sultat|score|victoire|d[eé]faite|classement|journ[eé]e|calendrier)\b', re.I)
MERCATO = re.compile(r'\b(mercato|transfert|recrutement|prolongation|pr[eê]t|signature|s.engage|rejoindrait|quitterait)\b', re.I)


def clean(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', '', s or ''))).strip()


def fetch(query):
    params = urllib.parse.urlencode({'q': query, 'hl': 'fr', 'gl': 'FR', 'ceid': 'FR:fr'})
    req = urllib.request.Request('https://news.google.com/rss/search?' + params,
                                 headers={'User-Agent': 'VeloceMercatoBot/1.0'})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return ET.fromstring(resp.read(2_000_000))


def accepted(source):
    s = source.casefold().replace('é', 'e').replace('è', 'e').replace('ê', 'e')
    return any(name.replace('é', 'e').replace('è', 'e').replace('ê', 'e') in s for name in SOURCES)


def load_existing():
    if not PATH.exists():
        return []
    value = json.loads(PATH.read_text(encoding='utf-8'))
    if not isinstance(value, list):
        raise ValueError('articles.json doit contenir une liste JSON')
    return value


def main():
    existing = load_existing()
    seen = {str(a.get('id')) for a in existing if isinstance(a, dict)}
    additions = []
    for zone, query in QUERIES.items():
        try:
            root = fetch(query)
        except Exception as exc:
            print(f'{zone}: source RSS inaccessible ({type(exc).__name__})')
            continue
        for item in root.findall('./channel/item'):
            title = clean(item.findtext('title'))
            link = clean(item.findtext('link'))
            source_el = item.find('source')
            source = clean(source_el.text if source_el is not None else '')
            pub = clean(item.findtext('pubDate'))
            if not title or not link or not source or not accepted(source) or BLOCK.search(title):
                continue
            if not link.startswith('https://'):
                continue
            try:
                date = email.utils.parsedate_to_datetime(pub).astimezone(dt.timezone.utc)
            except (TypeError, ValueError, OverflowError):
                continue
            if not NOW - MAX_AGE <= date <= NOW + dt.timedelta(minutes=10):
                continue
            # Retirer le suffixe « - Média » si Google News l'ajoute.
            if title.casefold().endswith(' - ' + source.casefold()):
                title = title[:-(len(source) + 3)].strip()
            if len(title) < 25 or len(title) > 190:
                continue
            ident = 'rss-' + hashlib.sha256((source.casefold() + '|' + title.casefold()).encode()).hexdigest()[:20]
            if ident in seen:
                continue
            seen.add(ident)
            cat = 'MERCATO' if MERCATO.search(title) else ('MATCHS' if MATCH.search(title) else 'ACTUALITES')
            # Un titre de média ne prouve pas une information : attribution explicite.
            resume = f'{source} rapporte : « {title} ». Consultez la source pour les détails et les éventuelles mises à jour.'
            additions.append({
                'id': ident,
                'publishedAt': date.isoformat(timespec='seconds').replace('+00:00', 'Z'),
                'titre': title,
                'resume': resume,
                'texte': resume + '\n\nCette brève reprend uniquement le titre publié par la source citée. Véloce Mercato ne confirme pas indépendamment cette information.',
                'zone': 'FRANCE' if zone in ('FRANCE', 'AMATEUR', 'FEMININ') else 'INTERNATIONAL',
                'categorie': cat,
                'championnat': 'FEMININ' if zone == 'FEMININ' else ('NATIONAL' if zone == 'AMATEUR' else ''),
                'tag': 'RUMEUR' if cat == 'MERCATO' else cat,
                'sources': [{'nom': source, 'url': link}],
            })
    additions.sort(key=lambda a: a['publishedAt'], reverse=True)
    additions = additions[:MAX_NEW]
    if not additions:
        print('Aucune nouvelle brève admissible ; aucun changement.')
        return
    merged = additions + existing
    merged.sort(key=lambda a: str(a.get('publishedAt', '')), reverse=True)
    PATH.write_text(json.dumps(merged[:MAX_TOTAL], ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(additions)} nouvelles brèves attribuées ; {len(merged[:MAX_TOTAL])} articles conservés.')


if __name__ == '__main__':
    main()
