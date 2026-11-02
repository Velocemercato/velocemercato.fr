#!/usr/bin/env python3
"""VM Foot amateur : les titres du foot amateur et régional, région par région.

Gratuit (aucune IA) : comme VM Belfort, on reprend seulement le titre, le média, l'heure
et le lien vers l'article d'origine. Sources : Google Actualités (presse régionale,
recherche par région), Ouest-France Foot Amateur et Foot National (N2/N3).
Rien de la veille : chaque matin à 5 h, le fil repart à neuf (vm_fraicheur).
"""

import datetime as dt
import email.utils
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import vm_fraicheur

OUT = Path('foot-amateur/actus.json')
KEEP_PAR_REGION = 30
UA = 'VM-FootAmateur/1.0 (editeur de liens; https://velocemercato.fr/foot-amateur/)'

# code : (nom affiché, termes de recherche presse régionale)
REGIONS = {
    'ARA': ('Auvergne-Rhône-Alpes', '"Auvergne-Rhône-Alpes" OR Lyon OR Grenoble OR Clermont OR "Saint-Étienne" OR Annecy'),
    'BFC': ('Bourgogne-Franche-Comté', '"Bourgogne-Franche-Comté" OR Belfort OR Besançon OR Dijon OR Montbéliard OR Vesoul OR Auxerre'),
    'BRE': ('Bretagne', 'Bretagne OR Rennes OR Brest OR Lorient OR Vannes OR "Saint-Brieuc" OR Quimper'),
    'CVL': ('Centre-Val de Loire', '"Centre-Val de Loire" OR Tours OR Orléans OR Bourges OR Chartres OR Blois'),
    'COR': ('Corse', 'Corse OR Ajaccio OR Bastia'),
    'GES': ('Grand Est', '"Grand Est" OR Strasbourg OR Metz OR Nancy OR Reims OR Mulhouse OR Troyes OR Colmar'),
    'HDF': ('Hauts-de-France', '"Hauts-de-France" OR Lille OR Lens OR Amiens OR Valenciennes OR Dunkerque OR Beauvais'),
    'IDF': ('Île-de-France', '"Île-de-France" OR "Seine-Saint-Denis" OR "Val-de-Marne" OR Essonne OR Yvelines OR "Hauts-de-Seine" OR "Val-d\'Oise" OR "Seine-et-Marne"'),
    'NOR': ('Normandie', 'Normandie OR Caen OR Rouen OR "Le Havre" OR Cherbourg OR Évreux'),
    'NAQ': ('Nouvelle-Aquitaine', '"Nouvelle-Aquitaine" OR Bordeaux OR Limoges OR Poitiers OR Pau OR "La Rochelle" OR Bayonne'),
    'OCC': ('Occitanie', 'Occitanie OR Toulouse OR Montpellier OR Nîmes OR Perpignan OR Béziers OR Rodez'),
    'PDL': ('Pays de la Loire', '"Pays de la Loire" OR Nantes OR Angers OR "Le Mans" OR "La Roche-sur-Yon" OR Laval OR Cholet'),
    'PAC': ("Provence-Alpes-Côte d'Azur", 'Provence OR Marseille OR Nice OR Toulon OR Avignon OR Cannes OR "Aix-en-Provence"'),
    'OM': ('Outre-mer', 'Guadeloupe OR Martinique OR Guyane OR "La Réunion" OR Mayotte OR "Nouvelle-Calédonie" OR Tahiti'),
}
NIVEAUX = '"National 3" OR N3 OR "Régional 1" OR R1 OR R2 OR R3 OR district OR "foot amateur" OR "Coupe de France"'

# Flux directs (presse spécialisée du foot amateur) : rangés par région d'après les villes citées.
FLUX = [
    ('Ouest-France Foot Amateur', 'https://footamateur.ouest-france.fr/feed/'),
    ('Ouest-France Foot Amateur', 'https://footamateur.ouest-france.fr/categories/nationaux/feed'),
    ('Foot National', 'https://www.foot-national.com/rss/national-2.html'),
    ('Foot National', 'https://www.foot-national.com/rss/national-3.html'),
]

FOOT = re.compile(r'foot|football|futsal|coupe de france|\bN[23]\b|national [23]|\bR[123]\b|régional [123]|district|\bU1[3-9]\b|\bD[1-5]\b', re.I)
# Le foot professionnel a déjà sa place à l'accueil ; ici, place aux clubs amateurs.
PRO = re.compile(r"\b(ligue 1|ligue 2|ligue des champions|ligue europa|premier league|liga|serie a|bundesliga|psg|mbapp[ée]|"
                 r"paris sportifs?|pronostics?|cotes?|casino|horoscope|programme t[ée]l[ée])\b", re.I)
AUTRES_SPORTS = re.compile(r'\b(rugby|handball|basket|volley|hockey|football américain|NFL)\b', re.I)


def niveau(titre):
    t = titre.lower()
    if re.search(r'coupe de france|coupe gambardella|coupe de la ligue', t):
        return 'COUPE'
    if re.search(r'f[ée]minin|f[ée]minine|\bd[1-3] arkema|\bseconde ligue\b', t):
        return 'FEMININ'
    if re.search(r'futsal', t):
        return 'FUTSAL'
    if re.search(r'\bu1[3-9]\b|jeunes|gambardella|\bu2[01]\b', t):
        return 'JEUNES'
    if re.search(r'\bn2\b|national 2|\bn3\b|national 3', t):
        return 'NATIONAL'
    if re.search(r'\br[123]\b|r[ée]gional [123]|ligue r[ée]gionale', t):
        return 'REGIONAL'
    if re.search(r'district|\bd[1-5]\b|départemental', t):
        return 'DISTRICT'
    return 'AMATEUR'


# Région déduite des villes citées (flux directs, qui couvrent toute la France).
VILLES = {code: re.compile(r'\b(' + '|'.join(re.escape(v.strip('"')) for v in termes.split(' OR ')) + r')\b', re.I)
          for code, (_, termes) in REGIONS.items()}


def region_de(texte):
    for code, motif in VILLES.items():
        if motif.search(texte):
            return code
    return 'FR'


def nettoie(s, limite=180):
    return re.sub(r'\s+', ' ', str(s or '')).strip()[:limite]


def date_rss(brut):
    try:
        d = email.utils.parsedate_to_datetime(brut)
        return d.astimezone(dt.timezone.utc) if d.tzinfo else None
    except (TypeError, ValueError, IndexError):
        return None


def lire_flux(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=18) as r:
        data = r.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError('flux trop volumineux')
    root = ET.fromstring(data)
    for item in root.findall('./channel/item'):
        source = item.find('source')
        yield {'t': nettoie(item.findtext('title'), 210), 'u': nettoie(item.findtext('link'), 1500),
               'd': date_rss(item.findtext('pubDate')),
               's': nettoie(source.text if source is not None else '', 100)}


def garder(row):
    t = row['t']
    return bool(t and row['u'].startswith('https://') and row['d'] and FOOT.search(t)
                and not PRO.search(t) and not AUTRES_SPORTS.search(t))


def ligne(row, region, source):
    titre, media = row['t'], row['s']
    if media and titre.endswith(' - ' + media):  # Google Actualités ajoute « - Média » au titre
        titre = titre[:-len(media) - 3]
    return {'l': region, 'n': niveau(titre), 't': nettoie(titre), 'u': row['u'], 's': media or source,
            'd': row['d'].isoformat(timespec='seconds').replace('+00:00', 'Z')}


def main():
    rows, muets = [], 0
    for code, (nom, termes) in REGIONS.items():
        q = f'football ({NIVEAUX}) ({termes}) when:1d'
        url = 'https://news.google.com/rss/search?' + urllib.parse.urlencode({'q': q, 'hl': 'fr', 'gl': 'FR', 'ceid': 'FR:fr'})
        try:
            items = [ligne(r, code, 'Presse régionale') for r in lire_flux(url) if garder(r)]
            print(f'{nom} : {len(items)} titres', flush=True)
            rows.extend(items)
        except Exception as exc:
            muets += 1
            print(f'::warning::{nom} : flux muet ({type(exc).__name__})', flush=True)
        time.sleep(0.8)
    for source, url in FLUX:
        try:
            items = [ligne(r, region_de(r['t']), source) for r in lire_flux(url) if garder(r)]
            print(f'{source} : {len(items)} titres', flush=True)
            rows.extend(items)
        except Exception as exc:
            print(f'::warning::{source} ({url}) : flux muet ({type(exc).__name__})', flush=True)
    rows = vm_fraicheur.du_jour(rows, ('d',))  # rien de la veille
    if not rows and muets == len(REGIONS):
        print('Aucun flux joignable : fichier inchangé.')
        return
    vus, out, compte = set(), [], {}
    for r in sorted(rows, key=lambda r: r['d'], reverse=True):
        cle = re.sub(r'[^a-z0-9]', '', r['t'].lower())[:70]
        if cle in vus or r['u'] in vus or compte.get(r['l'], 0) >= KEEP_PAR_REGION:
            continue
        vus.update((cle, r['u']))
        compte[r['l']] = compte.get(r['l'], 0) + 1
        out.append(r)
    OUT.parent.mkdir(exist_ok=True)
    vm_fraicheur.ecrire(OUT, {'maj': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
                              'regions': {k: v[0] for k, v in REGIONS.items()}, 'titres': out})
    print('Foot amateur : ' + ', '.join(f'{k} {v}' for k, v in sorted(compte.items())) + f' — {len(out)} titres')


if __name__ == '__main__':
    main()
