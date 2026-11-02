#!/usr/bin/env python3
"""Fraîcheur du site : chaque matin à 5 h (heure de Paris), ce qui date de la veille s'efface.

Une seule règle pour tous les robots, pour que le site ne sature jamais :
la « journée VM » commence à HEURE_BASCULE heure de Paris. Tout contenu mis en ligne
avant ce début de journée est retiré des fils, des pages d'articles et du sitemap.
La nuit, les actus de la soirée restent donc visibles jusqu'à 5 h.

Lancé seul (`python vm_fraicheur.py`), le script fait le ménage du matin dans tous les fils.
Les calendriers et résultats (matchs.json, scores.json, agenda.json) ne sont pas concernés :
ils ont leurs propres robots et contiennent des matchs à venir.
"""

import datetime as dt
import json
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

PARIS = ZoneInfo('Europe/Paris')
HEURE_BASCULE = 5
MEMOIRE_JOURS = 4  # liens déjà publiés gardés en mémoire pour ne pas les republier après le ménage

# (fichier, clef de la liste dans le JSON ou None si le fichier est une liste, clefs de date)
FILS = [
    ('articles.json', None, ('createdAt', 'publishedAt')),
    ('flash.json', None, ('publishedAt',)),
    ('actus/news.json', None, ('createdAt', 'publishedAt')),
    ('actus/flash.json', None, ('publishedAt',)),
    ('psg/news.json', None, ('createdAt', 'publishedAt')),
    ('psg/flash.json', None, ('publishedAt',)),
    ('vm-gaming/news.json', None, ('createdAt', 'publishedAt')),
    ('vm-gaming/flash.json', None, ('publishedAt',)),
    ('videos.json', None, ('publishedAt',)),
    ('fil.json', 'titres', ('d',)),
    ('belfort/actus.json', 'titres', ('d',)),
    ('foot-amateur/actus.json', 'titres', ('d',)),
]
# Fils d'articles rédigés : leurs liens sources sont mémorisés avant d'être effacés.
ARTICLES = {'articles.json', 'actus/news.json', 'psg/news.json', 'vm-gaming/news.json'}


def maintenant():
    forced = os.getenv('VM_MAINTENANT', '').strip()  # pour les tests uniquement
    if forced:
        return dt.datetime.fromisoformat(forced.replace('Z', '+00:00'))
    return dt.datetime.now(dt.timezone.utc)


def debut_journee(now=None):
    """Début de la journée VM en cours (datetime avec fuseau)."""
    paris = (now or maintenant()).astimezone(PARIS)
    jour = paris.date() if paris.hour >= HEURE_BASCULE else paris.date() - dt.timedelta(days=1)
    return dt.datetime.combine(jour, dt.time(HEURE_BASCULE), PARIS)


def lire_date(valeur):
    try:
        d = dt.datetime.fromisoformat(str(valeur).strip().replace('Z', '+00:00'))
    except (TypeError, ValueError):
        return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def date_de(row, cles):
    """Date de mise en ligne : la plus récente des clefs disponibles (createdAt, publishedAt…)."""
    dates = [d for k in cles if isinstance(row, dict) and (d := lire_date(row.get(k)))]
    return max(dates) if dates else None


def du_jour(rows, cles=('publishedAt',), now=None):
    """Garde seulement ce qui a été mis en ligne depuis le début de la journée VM.
    Une ligne sans date lisible est retirée : sinon elle ne s'effacerait jamais."""
    limite = debut_journee(now)
    return [r for r in rows if (d := date_de(r, cles)) and d >= limite]


def memoire_path(fichier):
    return Path(fichier).with_name('deja-publies.json')


def lire_memoire(fichier):
    try:
        rows = json.loads(memoire_path(fichier).read_text(encoding='utf-8'))
        return [r for r in rows if isinstance(r, dict)] if isinstance(rows, list) else []
    except (OSError, ValueError):
        return []


def memoriser(fichier, retires, now=None):
    """Garde les liens, identifiants et titres des brèves effacées pendant quelques jours."""
    now = now or maintenant()
    limite = (now - dt.timedelta(days=MEMOIRE_JOURS)).isoformat(timespec='seconds')
    garde = [r for r in lire_memoire(fichier) if str(r.get('le', '')) >= limite]
    connus = {r.get('id') for r in garde}
    for a in retires:
        if a.get('id') in connus:
            continue
        garde.append({'id': a.get('id'), 'le': now.isoformat(timespec='seconds'),
                      'urls': [s.get('url', '').split('?')[0] for s in a.get('sources', []) if isinstance(s, dict) and s.get('url')],
                      'titres': [t for t in (a.get('titre'), a.get('titreSource')) if isinstance(t, str) and t]})
    ecrire(memoire_path(fichier), garde)


def ecrire(path, data):
    """Écriture atomique : un fichier à moitié écrit ne peut jamais être publié."""
    path = Path(path)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    json.loads(tmp.read_text(encoding='utf-8'))
    tmp.replace(path)


def menage(racine='.', now=None):
    """Retire de chaque fil ce qui date d'avant la journée VM en cours. Renvoie le total retiré."""
    now = now or maintenant()
    total = 0
    for nom, cle, cles in FILS:
        path = Path(racine) / nom
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except ValueError as exc:
            # Fichier illisible : on ne le remplace pas à l'aveugle.
            print(f'::warning::{nom} illisible, laissé tel quel ({exc})', flush=True)
            continue
        rows = data.get(cle) if cle and isinstance(data, dict) else data
        if not isinstance(rows, list):
            print(f'::warning::{nom} : format inattendu, laissé tel quel', flush=True)
            continue
        garde = du_jour(rows, cles, now)
        retires = [r for r in rows if r not in garde]
        if not retires:
            print(f'{nom} : rien à effacer ({len(rows)} éléments du jour).', flush=True)
            continue
        if nom in ARTICLES:
            memoriser(path, retires, now)
        if cle:
            data[cle] = garde
        else:
            data = garde
        ecrire(path, data)
        total += len(retires)
        print(f'{nom} : {len(retires)} éléments de la veille effacés, {len(garde)} gardés.', flush=True)
    sport = Path(racine) / 'multisport/actualites.json'
    if sport.is_file():
        try:
            data = json.loads(sport.read_text(encoding='utf-8'))
            avant = sum(len(v) for v in data.get('sports', {}).values())
            data['sports'] = {k: du_jour(v, ('date',), now) for k, v in data.get('sports', {}).items()}
            apres = sum(len(v) for v in data['sports'].values())
            if apres != avant:
                data['fenetreJours'] = 1
                ecrire(sport, data)
                total += avant - apres
            print(f'multisport/actualites.json : {avant - apres} éléments de la veille effacés, {apres} gardés.', flush=True)
        except (ValueError, AttributeError) as exc:
            print(f'::warning::multisport/actualites.json laissé tel quel ({exc})', flush=True)
    return total


if __name__ == '__main__':
    n = menage()
    print(f'Ménage du matin terminé : {n} éléments de la veille effacés '
          f'(journée VM depuis {debut_journee():%d/%m %H:%M}, heure de Paris).', flush=True)
    sys.exit(0)
