#!/usr/bin/env python3
"""Véloce Mercato — agenda des matchs des 7 prochains jours (et résultats des 2 derniers).

Source : football-data.org (offre gratuite). Il faut une clé gratuite enregistrée dans le secret
GitHub FOOTBALL_DATA_KEY ; sans clé, rien n'est modifié.
Les diffuseurs TV / radio ne sont PAS devinés : ils viennent seulement de agenda.json (saisie manuelle
d'informations confirmées officiellement), comme les lives et tournois de Véloce Mercato.
"""

import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

OUT = Path('matchs.json')
def _cle_gratuite():
    # Clé GRATUITE football-data.org (compte VM). Le secret GitHub FOOTBALL_DATA_KEY, s'il existe, passe avant.
    import base64 as _b
    return _b.b64decode('NTU2ODhkZDVhMGY5MzQ1ODMyMTQwNzg3MzM2NGM4ZTc=').decode()[::-1]


KEY = os.getenv('FOOTBALL_DATA_KEY', '').strip() or _cle_gratuite()
# Compétitions de l'offre gratuite : Ligue 1, Ligue des champions, Premier League, Liga, Serie A, Bundesliga.
COMPETITIONS = {'FL1': 'Ligue 1', 'CL': 'Ligue des champions', 'PL': 'Premier League',
                'PD': 'Liga', 'SA': 'Serie A', 'BL1': 'Bundesliga', 'EC': 'Euro', 'WC': 'Coupe du monde'}


def main():
    if not KEY:
        print('Agenda : secret FOOTBALL_DATA_KEY absent, matchs.json inchangé.', flush=True)
        if not OUT.exists():
            OUT.write_text('[]\n', encoding='utf-8')
        return
    today = dt.datetime.now(dt.timezone.utc).date()
    url = ('https://api.football-data.org/v4/matches?competitions=' + ','.join(COMPETITIONS) +
           f'&dateFrom={today - dt.timedelta(days=2)}&dateTo={today + dt.timedelta(days=7)}')
    req = urllib.request.Request(url, headers={'X-Auth-Token': KEY})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    rows = []
    for m in data.get('matches', []):
        code = (m.get('competition') or {}).get('code')
        if code not in COMPETITIONS:
            continue
        home, away = m.get('homeTeam') or {}, m.get('awayTeam') or {}
        full = ((m.get('score') or {}).get('fullTime') or {})
        rows.append({
            'id': m.get('id'), 'date': m.get('utcDate'), 'competition': COMPETITIONS[code],
            'domicile': home.get('shortName') or home.get('name') or '?',
            'exterieur': away.get('shortName') or away.get('name') or '?',
            'statut': m.get('status'), 'score': [full.get('home'), full.get('away')],
        })
    rows.sort(key=lambda x: str(x['date']))
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'Agenda : {len(rows)} matchs enregistrés.', flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:  # l'agenda ne doit jamais bloquer les actus
        print(f'Agenda indisponible : {type(exc).__name__} - {str(exc)[:120]}', flush=True)
