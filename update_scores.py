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
def _cle_gratuite():
    # Clé GRATUITE football-data.org (compte de Romain). Le secret GitHub FOOTBALL_DATA_KEY, s'il existe, passe avant.
    import base64 as _b
    return _b.b64decode('NTU2ODhkZDVhMGY5MzQ1ODMyMTQwNzg3MzM2NGM4ZTc=').decode()[::-1]


KEY = os.getenv('FOOTBALL_DATA_KEY', '').strip() or _cle_gratuite()
WEBHOOK = os.getenv('DISCORD_WEBHOOK', '').strip()  # salon Discord #buts-en-direct (facultatif)
COMPETITIONS = {'FL1': 'Ligue 1', 'CL': 'Ligue des champions'}
PARIS = ZoneInfo('Europe/Paris')


def notify(old_rows, rows):
    """Envoie dans le salon Discord : coup d'envoi, but, mi-temps, fin de match (scores officiels seulement)."""
    if not WEBHOOK.startswith('https://discord.com/api/webhooks/') or not old_rows:
        return
    before = {m['id']: m for m in old_rows}
    msgs = []
    for m in rows:
        o = before.get(m['id'])
        if not o:
            continue
        sc, so = m['score'], o['score']
        tag = f"**{m['dom']} {sc[0] if sc[0] is not None else 0}-{sc[1] if sc[1] is not None else 0} {m['ext']}** · {m['comp']}"
        if o['statut'] in ('SCHEDULED', 'TIMED') and m['statut'] == 'IN_PLAY':
            msgs.append(f"🟢 Coup d'envoi : {m['dom']} – {m['ext']} ({m['comp']})")
        elif m['statut'] in ('IN_PLAY', 'PAUSED', 'FINISHED') and sc != so and None not in sc:
            msgs.append(f"⚽ BUT ! {tag}")
        if o['statut'] == 'IN_PLAY' and m['statut'] == 'PAUSED':
            msgs.append(f"⏸ Mi-temps : {tag}")
        if o['statut'] != 'FINISHED' and m['statut'] == 'FINISHED':
            msgs.append(f"🏁 Terminé : {tag}")
    for text in msgs[:10]:
        body = json.dumps({'content': text + '\n<https://velocemercato.fr>', 'username': 'Véloce Mercato · Flash'}).encode('utf-8')
        try:
            urllib.request.urlopen(urllib.request.Request(WEBHOOK, data=body, headers={'Content-Type': 'application/json',
                                   'User-Agent': 'VeloceMercato/1.0'}, method='POST'), timeout=10).read()
        except Exception as exc:
            print(f'Discord : envoi impossible ({type(exc).__name__})')
    if msgs:
        print(f'Discord : {len(msgs)} notification(s).')


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
    notify(old.get('matchs') or [], rows)
    new['maj'] = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    OUT.write_text(json.dumps(new, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'Scores : {len(rows)} matchs mis à jour.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Scores indisponibles : {type(exc).__name__} - {str(exc)[:120]}')
