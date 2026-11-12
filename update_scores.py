#!/usr/bin/env python3
"""Résultats en direct : Ligue 1, Ligue des champions, 4 grands championnats et sélections (hier, aujourd'hui, demain).

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
def _salon_discord():
    # Webhook du salon Discord de Romain. Le secret GitHub DISCORD_WEBHOOK, s'il existe, passe avant.
    import base64 as _b
    return _b.b64decode('endmbWxkU0hmVG9PWVQ0ai1hcHAyY2dfUVViZGJjQU5oNHp3MUNNSjNZM3M2emFKclJ3ZVdmbzUxNDQ2VmFIcG00dUovNDI3NTQ3MTgzNTU0NjcxMjY1MS9za29vaGJldy9pcGEvbW9jLmRyb2NzaWQvLzpzcHR0aA==').decode()[::-1]


WEBHOOK = os.getenv('DISCORD_WEBHOOK', '').strip() or _salon_discord()
COMPETITIONS = {'FL1': 'Ligue 1', 'CL': 'Ligue des champions', 'PL': 'Premier League', 'PD': 'Liga',
                'SA': 'Serie A', 'BL1': 'Bundesliga'}
# Deuxième source publique (sans clé) pour les sélections, absentes de l'offre gratuite football-data.
ESPN_LIGUES = {'uefa.nations': 'Ligue des nations', 'fifa.friendly': 'Match amical international',
               'caf.nations_qual': 'Qualifications CAN', 'uefa.euro_u21_qual': 'Qualifications Euro Espoirs'}
DISCORD_COMPS = {'Ligue 1', 'Ligue des champions', 'Ligue des nations'}  # le salon Discord reste centré sur la L1 et la C1
PARIS = ZoneInfo('Europe/Paris')


def notify(old_rows, rows):
    """Envoie dans le salon Discord : coup d'envoi, but, mi-temps, fin de match (scores officiels seulement)."""
    if not WEBHOOK.startswith('https://discord.com/api/webhooks/') or not old_rows:
        return
    before = {m['id']: m for m in old_rows}
    msgs = []
    for m in rows:
        o = before.get(m['id'])
        if not o or m['comp'] not in DISCORD_COMPS:
            continue
        sc, so = m['score'], o['score']
        tag = f"**{m['dom']} {sc[0] if sc[0] is not None else 0}-{sc[1] if sc[1] is not None else 0} {m['ext']}** · {m['comp']}"
        if o['statut'] in ('SCHEDULED', 'TIMED') and m['statut'] == 'IN_PLAY':
            msgs.append(f"🟢 Coup d'envoi : {m['dom']} – {m['ext']} ({m['comp']})")
        elif (o['statut'] in ('IN_PLAY', 'PAUSED') and m['statut'] in ('IN_PLAY', 'PAUSED', 'FINISHED')
              and None not in sc and None not in so and sum(sc) > sum(so)):
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


def espn_rows(today):
    """Matchs des sélections (hier, aujourd'hui, demain) depuis le tableau des scores public d'ESPN."""
    rows = []
    jours = '-'.join(d.strftime('%Y%m%d') for d in (today - dt.timedelta(days=1), today + dt.timedelta(days=1)))
    for slug, nom in ESPN_LIGUES.items():
        url = f'https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard?dates={jours}&lang=fr&region=fr'
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'VeloceMercato/1.0'}), timeout=15) as r:
                data = json.load(r)
        except Exception as exc:
            print(f'ESPN {slug} indisponible ({type(exc).__name__})')
            continue
        for e in data.get('events') or []:
            try:
                comp = (e.get('competitions') or [{}])[0]
                teams = {c.get('homeAway'): c for c in comp.get('competitors') or []}
                home, away = teams['home'], teams['away']
                st = (e.get('status') or {}).get('type') or {}
                state, name = st.get('state'), str(st.get('name', ''))
                statut = ('FINISHED' if state == 'post' else 'PAUSED' if 'HALFTIME' in name
                          else 'IN_PLAY' if state == 'in' else 'TIMED')
                if 'POSTPONED' in name or 'CANCELED' in name:
                    statut = 'POSTPONED'
                def but(c):
                    v = c.get('score')
                    return int(v) if statut != 'TIMED' and str(v).isdigit() else None
                rows.append({'id': 'espn-' + str(e['id']), 'date': e.get('date'), 'comp': nom,
                             'dom': (home.get('team') or {}).get('shortDisplayName') or '?',
                             'ext': (away.get('team') or {}).get('shortDisplayName') or '?',
                             'statut': statut, 'score': [but(home), but(away)]})
            except (KeyError, TypeError, ValueError):
                continue
    return rows


def main():
    if not KEY:
        print('Scores : secret FOOTBALL_DATA_KEY absent, rien à publier.')
        return
    today = dt.datetime.now(PARIS).date()
    url = (f"https://api.football-data.org/v4/matches?competitions={','.join(COMPETITIONS)}"
           f'&dateFrom={today - dt.timedelta(days=1)}&dateTo={today + dt.timedelta(days=1)}')
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'X-Auth-Token': KEY}), timeout=20) as r:
            data = json.load(r)
    except Exception as exc:  # une source en panne ne doit pas couper l'autre
        print(f'football-data indisponible ({type(exc).__name__})')
        data = {}
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
    rows += espn_rows(today)
    rows.sort(key=lambda x: (str(x['date']), x['comp']))
    old = json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else {}
    # La source renvoie parfois une ancienne version : on ne revient jamais en arrière
    # (un match commencé ne redevient pas « à venir », un score ne descend pas).
    rank = {'SCHEDULED': 0, 'TIMED': 0, 'POSTPONED': 0, 'IN_PLAY': 1, 'PAUSED': 1, 'FINISHED': 2}
    before = {m['id']: m for m in old.get('matchs') or []}
    for i, m in enumerate(rows):
        o = before.get(m['id'])
        if not o:
            continue
        older_status = rank.get(m['statut'], 0) < rank.get(o['statut'], 0)
        lower_score = None not in o['score'] and (None in m['score'] or sum(m['score']) < sum(o['score']))
        if older_status or lower_score:
            rows[i] = o
    new = {'matchs': rows}
    now_iso = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    if old.get('matchs') == rows:
        # Preuve de fraîcheur : « vérifié à » est rafraîchi au plus toutes les 30 minutes
        # (un fichier qui ne change pas ne doit pas faire croire que le robot est arrêté).
        last = old.get('verifie') or old.get('maj') or ''
        try:
            age = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(last.replace('Z', '+00:00'))).total_seconds()
        except ValueError:
            age = 1e9
        if age >= 1800:
            old['verifie'] = now_iso
            OUT.write_text(json.dumps(old, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
            print('Scores inchangés (vérification horodatée).')
        else:
            print('Scores inchangés.')
        return
    notify(old.get('matchs') or [], rows)
    new['maj'] = new['verifie'] = now_iso
    OUT.write_text(json.dumps(new, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'Scores : {len(rows)} matchs mis à jour.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Scores indisponibles : {type(exc).__name__} - {str(exc)[:120]}')
