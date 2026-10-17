#!/usr/bin/env python3
"""Veloce Mercato: collecte RSS et brouillon Claude, SANS publication."""
import datetime as dt
import email.utils
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

QUERIES = {
    'LIGUE_1': '"Ligue 1" (transfert OR mercato OR recrute OR prolongation OR signe)',
    'LIGUE_2': '"Ligue 2" (transfert OR mercato OR recrute OR prolongation OR signe)',
    'NATIONAL': '"National" football (transfert OR recrute OR signe)',
    'N2_N3': '"National 2" OR "National 3" football recrutement',
    'FEMININ': 'football feminin (transfert OR mercato OR recrute OR prolongation)',
    'AMATEUR': 'football amateur club recrutement transfert',
    'INTERNATIONAL': 'football transfert mercato officialise club joueur',
}
HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; VeloceMercatoTest/1.0)'}
MAX_AGE = dt.timedelta(hours=36)
KEYWORDS = re.compile(r'\b(transfert|mercato|recrut|prolong|sign(?:e|ature)|pr[eê]t|d[eé]part|arriv[eé]e|officialis|engag[eé])', re.I)
EXCLUDE = re.compile(r'\b(programme tv|cha[iî]ne tv|diffusion tv|o[uù] regarder|heure et cha[iî]ne|pronostic|cote[s]?|paris sportif[s]?|compositions? probables?|r[eé]sultat[s]?|score|calendrier|programme des matchs|tactique|classement|direct live)\b', re.I)
ACTION = re.compile(r'\b(transfert|recrut|prolong|pr[eê]t|d[eé]part|arriv[eé]e|officialis|engag[eé]|sign[eé]|signature)\b', re.I)


def get_xml(query):
    params = urllib.parse.urlencode({'q': query, 'hl': 'fr', 'gl': 'FR', 'ceid': 'FR:fr'})
    request = urllib.request.Request('https://news.google.com/rss/search?' + params, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=25) as response:
        return ET.fromstring(response.read())


def collect():
    now = dt.datetime.now(dt.timezone.utc)
    found, seen = [], set()
    for zone, query in QUERIES.items():
        try:
            root = get_xml(query)
            count = 0
            for item in root.findall('./channel/item'):
                title = (item.findtext('title') or '').strip()
                link = (item.findtext('link') or '').strip()
                source_el = item.find('source')
                source = (source_el.text or '').strip() if source_el is not None else ''
                source_url = (source_el.get('url') or '').strip() if source_el is not None else ''
                pub = item.findtext('pubDate') or ''
                try:
                    date = email.utils.parsedate_to_datetime(pub).astimezone(dt.timezone.utc)
                except (ValueError, TypeError):
                    continue
                if not (now - MAX_AGE <= date <= now + dt.timedelta(minutes=10)):
                    continue
                if not KEYWORDS.search(title) or not ACTION.search(title) or EXCLUDE.search(title):
                    continue
                identity = hashlib.sha256(re.sub(r'\s+', ' ', title.casefold()).encode()).hexdigest()
                if identity in seen or not link or not source:
                    continue
                seen.add(identity)
                count += 1
                found.append({'zone': zone, 'titre_source': title, 'source': source,
                              'url_rss': link, 'site_source': source_url,
                              'date': date.isoformat()})
            print(f'{zone}: {count} titres potentiels (non verifies)')
        except Exception as exc:
            print(f'{zone}: erreur collecte {type(exc).__name__}')
    return found


def claude_preview(candidate):
    key = os.environ.get('ANTHROPIC_API_KEY')
    if not key:
        print('Claude non lance: secret ANTHROPIC_API_KEY absent')
        return
    prompt = (
        'Tu es un assistant editorial pour un site de football. '
        'Tu disposes UNIQUEMENT de metadonnees RSS, pas du texte de la source. '
        'N affirme jamais avoir verifie un article ni inventer une citation, un montant, '
        'une date de contrat ou un fait non present dans le titre. '
        'Ne presente jamais une rumeur comme une officialisation. '
        'Redige en francais un brouillon tres prudent de 100 a 150 mots maximum, '
        'avec un titre, un court resume, puis une section "A confirmer" expliquant '
        'les limites de la verification. Indique clairement "BROUILLON NON VERIFIE". '
        'Aucune publication ne sera faite.\n\n'
        + json.dumps(candidate, ensure_ascii=False)
    )
    body = {'model': 'claude-haiku-4-5-20251001', 'max_tokens': 400,
            'messages': [{'role': 'user', 'content': prompt}]}
    request = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=json.dumps(body).encode('utf-8'),
        headers={'x-api-key': key, 'anthropic-version': '2023-06-01',
                 'content-type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            result = json.load(response)
        output = '\n'.join(x.get('text', '') for x in result.get('content', []) if x.get('type') == 'text')
        print('\n--- BROUILLON CLAUDE (NON VERIFIE, NON PUBLIE) ---')
        print(output[:3500])
        print('--- FIN BROUILLON ---')
    except urllib.error.HTTPError as exc:
        print(f'Erreur API Claude HTTP {exc.code} (aucune publication)')
    except Exception as exc:
        print(f'Erreur Claude {type(exc).__name__} (aucune publication)')


def main():
    path = Path('articles.json')
    if path.exists():
        try:
            articles = json.loads(path.read_text(encoding='utf-8'))
            print('Articles existants preserves :', len(articles))
        except (ValueError, OSError) as exc:
            print('Lecture articles.json impossible :', type(exc).__name__)
    found = collect()
    print('TOTAL TITRES CANDIDATS :', len(found))
    for item in found[:8]:
        print(item['zone'], '|', item['titre_source'], '|', item['source'], '|', item['url_rss'])
    # Aucune validation automatique : un titre RSS seul ne prouve pas un fait.
    # Les brouillons ne sont jamais publies et ne constituent pas une verification.
    if found:
        claude_preview(found[0])
    else:
        print('Aucun titre candidat pour le test Claude.')
    print('MODE TEST : AUCUN FICHIER MODIFIE. AUCUNE PUBLICATION.')


if __name__ == '__main__':
    main()
