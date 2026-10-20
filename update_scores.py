#!/usr/bin/env python3
"""Résultats en direct : Ligue 1 et Ligue des champions (hier, aujourd'hui, demain).

Source officielle de données : football-data.org (offre gratuite, secret GitHub FOOTBALL_DATA_KEY).
Sans clé, rien n'est publié : aucun score n'est jamais deviné ni écrit par l'IA.
"""

import datetime as dt
import json
import os
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

OUT = Path('scores.json')
KEY = os.getenv('FOOTBALL_DATA_KEY', '').strip()
COMPETITIONS = {'FL1': 'Ligue 1', 'CL': 'Ligue des champions'}
PARIS = ZoneInfo('Europe/Paris')


def main():
    if not KEY:
        print('Scores : secret FOOTBALL_DATA_KEY absent, rien à publier.')
        return
    today = dt.datetime.now(PARIS).date()
    url = (f"https://api.football-data.org/v4/matches?competitions={','.join(COMPETITIONS)}"
           f'&dateFrom={today - dt.timedelta(days=1)}&dateTo={today + dt.timedelta(days=1)}')
    with urllib.request.urlopen(urllib.request.Request(url, headers={'X-Auth-Token': KEY}), timeout=20) as r:
        data = json.load(r)
    rows = []
    for m in data.get('matches', []):
        code = (m.get('competition') or {}).get('code')
        if code not in COMPETITIONS:
            continue
        home, away = m.get('homeTeam') or {}, m.get('awayTeam') or {}
        full = (m.get('score') or {}).get('fullTime') or {}
        rows.append({'id': m.get('id'), 'date': m.get('utcDate'), 'comp': COMPETITIONS[code],
                     'dom': home.get('shortName') or home.get('name') or '?', 'ext': away.get('shortName') or away.get('name') or '?',
                     'statut': m.get('status'), 'score': [full.get('home'), full.get('away')]})
    rows.sort(key=lambda x: (str(x['date']), x['comp']))
    new = {'matchs': rows}
    old = json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else {}
    if old.get('matchs') == rows:
        print('Scores inchangés.')
        return
    new['maj'] = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    OUT.write_text(json.dumps(new, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'Scores : {len(rows)} matchs mis à jour.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Scores indisponibles : {type(exc).__name__} - {str(exc)[:120]}')
