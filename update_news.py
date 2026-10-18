#!/usr/bin/env python3
"""Veille foot : courtes brèves sourcées, sans création de faits ni texte copié."""
import datetime as dt
import email.utils
import hashlib
import html
import json
import re
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

PATH = Path('articles.json')
NOW = dt.datetime.now(dt.timezone.utc)
MAX_AGE = dt.timedelta(hours=30)
MAX_NEW = 5

# Requêtes simples : une recherche trop longue peut masquer les actus récentes.
QUERIES = (
    ('FRANCE', 'football Ligue 1'),
    ('FRANCE', 'football Ligue 2'),
    ('FRANCE', 'football National'),
    ('INTERNATIONAL', 'football mercato transferts'),
    ('INTERNATIONAL', 'football Ligue des champions'),
    ('FEMININ', 'football féminin'),
    ('AMATEUR', 'football National 2 National 3'),
)

# Sources identifiables ; leur présence ne vaut pas vérification indépendante.
SOURCES = (
    'lequipe', "l'equipe", 'rmc sport', 'franceinfo', 'france bleu',
    'ici', 'ouest-france', 'le parisien', 'afp', 'reuters', 'bbc sport',
    'the guardian', 'goal', 'eurosport', 'foot mercato', 'maxifoot',
    'so foot', 'sky sports', 'skysports', 'sports.fr', 'onze mondial',
    'france football', 'france 3', 'france televisions', 'fff', 'uefa',
)
BLOCK = re.compile(r'\b(pronostic|paris sportifs|cotes?|casino|billetterie|streaming ill[eé]gal)\b', re.I)
MATCH = re.compile(r'\b(match|matches|r[eé]sultat|score|victoire|d[eé]faite|classement|journ[eé]e|calendrier)\b', re.I)
MERCATO = re.compile(r'\b(mercato|transfert|recrutement|prolongation|pr[eê]t|signature|s.engage|rejoindrait|quitterait)\b', re.I)


def clean(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', '', value or ''))).strip()


def normal(value):
    decomposed = unicodedata.normalize('NFKD', value.casefold())
    return ''.join(c for c in decomposed if not unicodedata.combining(c)).replace('’', "'")


def accepted(source):
    name = normal(source)
    return any(re.search(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', name) for alias in SOURCES)


def fetch(query):
    args = urllib.parse.urlencode({'q': query, 'hl': 'fr', 'gl': 'FR', 'ceid': 'FR:fr'})
    request = urllib.request.Request(
        'https://news.google.com/rss/search?' + args,
        headers={'User-Agent': 'Mozilla/5.0 (compatible; VeloceMercato/1.1; +https://velocemercato.fr/)'},
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        return ET.fromstring(response.read(2_000_000))


def load_existing():
    if not PATH.exists():
        raise FileNotFoundError('articles.json absent : aucun article existant ne sera écrasé')
    articles = json.loads(PATH.read_text(encoding='utf-8'))
    if not isinstance(articles, list) or not all(isinstance(a, dict) for a in articles):
        raise ValueError('articles.json doit contenir une liste d’articles')
    return articles


def build_article(item, zone, seen, stats):
    stats['lus'] += 1
    title = clean(item.findtext('title'))
    link = clean(item.findtext('link'))
    source_element = item.find('source')
    source = clean(source_element.text if source_element is not None else '')
    pub = clean(item.findtext('pubDate'))
    if not title or not source or not accepted(source):
        stats['source_ou_titre'] += 1
        return None
    if BLOCK.search(title):
        stats['publicite_ou_paris'] += 1
        return None
    if not link.startswith('https://'):
        stats['lien_invalide'] += 1
        return None
    try:
        date = email.utils.parsedate_to_datetime(pub)
        if date.tzinfo is None:
            date = date.replace(tzinfo=dt.timezone.utc)
        date = date.astimezone(dt.timezone.utc)
    except (TypeError, ValueError, OverflowError):
        stats['date_invalide'] += 1
        return None
    if not NOW - MAX_AGE <= date <= NOW + dt.timedelta(minutes=10):
        stats['trop_ancien'] += 1
        return None
    if normal(title).endswith(' - ' + normal(source)):
        title = title[:-(len(source) + 3)].strip()
    if not 25 <= len(title) <= 190:
        stats['longueur_titre'] += 1
        return None
    ident = 'rss-' + hashlib.sha256((normal(source) + '|' + normal(title)).encode()).hexdigest()[:20]
    if ident in seen:
        stats['doublon'] += 1
        return None
    seen.add(ident)
    cat = 'MERCATO' if MERCATO.search(title) else ('MATCHS' if MATCH.search(title) else 'ACTUALITES')
    resume = f'{source} publie : « {title} ». Consultez la source pour les détails et les mises à jour.'
    stats['retenus'] += 1
    return {
        'id': ident,
        'publishedAt': date.isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'titre': title,
        'resume': resume,
        'texte': resume + '\n\nBrève basée uniquement sur le titre et la date de la source. Véloce Mercato ne confirme pas indépendamment cette information.',
        'zone': 'FRANCE' if zone in ('FRANCE', 'AMATEUR', 'FEMININ') else 'INTERNATIONAL',
        'categorie': cat,
        'championnat': 'FEMININ' if zone == 'FEMININ' else ('NATIONAL' if zone == 'AMATEUR' else ''),
        'tag': 'MERCATO' if cat == 'MERCATO' else cat,
        'sources': [{'nom': source, 'url': link}],
    }


def main():
    existing = load_existing()
    print(f'Articles déjà présents : {len(existing)}. Aucune suppression prévue.', flush=True)
    seen = {str(a.get('id')) for a in existing}
    additions = []
    successes = 0
    summary = Counter()
    for zone, query in QUERIES:
        stats = Counter()
        try:
            root = fetch(query)
            successes += 1
            for item in root.findall('./channel/item'):
                article = build_article(item, zone, seen, stats)
                if article:
                    additions.append(article)
            summary.update(stats)
            print(f'{zone} [{query}] : ' + ', '.join(f'{k}={v}' for k, v in sorted(stats.items())), flush=True)
        except Exception as exc:
            print(f'{zone} [{query}] : ERREUR RSS {type(exc).__name__} : {str(exc)[:160]}', flush=True)
    if not successes:
        raise RuntimeError('Aucun flux RSS accessible : vérifier réseau et accès Google News')
    print('Diagnostic global : ' + ', '.join(f'{k}={v}' for k, v in sorted(summary.items())), flush=True)
    additions.sort(key=lambda a: a['publishedAt'], reverse=True)
    additions = additions[:MAX_NEW]
    if not additions:
        print('Aucune nouvelle brève admissible ; articles.json conservé sans changement.', flush=True)
        return
    # Aucun article antérieur n'est supprimé, même au-delà de 150 entrées.
    merged = additions + existing
    merged.sort(key=lambda a: str(a.get('publishedAt', '')), reverse=True)
    PATH.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(additions)} nouvelles brèves ; {len(existing)} anciens articles conservés.', flush=True)


if __name__ == '__main__':
    main()
