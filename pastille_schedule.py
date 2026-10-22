"""Horaires locaux et matchs confirmés ; aucune requête réseau ni publication."""
import datetime as dt
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

PARIS = ZoneInfo('Europe/Paris')
JT_CRON = '0 5,6,10,11,18,19 * * *'
MATCH_CRON = '15,45 10-22 * * *'
DEBATE_CRON = '30 21,22 * * *'


def slot(now, cron):
    local = now.astimezone(PARIS)
    if cron == JT_CRON and local.minute < 30:
        return {7:'matin',12:'midi',20:'soir'}.get(local.hour, '')
    if cron == MATCH_CRON:
        return 'speciale'
    if cron == DEBATE_CRON and local.hour == 23 and local.minute >= 30:
        return 'debat'
    return ''


def confirmed_matches(root, now, finished=False):
    path = Path(root) / 'scores.json'
    if not path.is_file():
        return []
    data = json.loads(path.read_text())
    try:
        updated = dt.datetime.fromisoformat(data['maj'].replace('Z','+00:00'))
        if not dt.timedelta(0) <= now - updated <= dt.timedelta(hours=2):
            return []
    except (ValueError,KeyError,TypeError):
        return []
    result = []
    for match in data.get('matchs', []):
        try:
            kick = dt.datetime.fromisoformat(match['date'].replace('Z','+00:00'))
            if kick.astimezone(PARIS).date() != now.astimezone(PARIS).date():
                continue
            if finished:
                allowed = match.get('statut') == 'FINISHED'
            else:
                allowed = match.get('statut') in ['SCHEDULED','TIMED'] and dt.timedelta(minutes=35) <= kick-now <= dt.timedelta(minutes=80)
            if allowed:
                result.append(match)
        except (ValueError,KeyError,TypeError):
            continue
    return result


def already_published(root, univers, fmt, moment, now):
    for path in (Path(root) / 'studio/tv').glob('*.json'):
        if path.name.startswith('_'):
            continue
        row = json.loads(path.read_text())
        if (row.get('publie') is True and row.get('univers') == univers and row.get('format') == fmt
                and row.get('moment') == moment and row.get('date','')[:10] == now.astimezone(PARIS).date().isoformat()):
            return True
    return False


if __name__ == '__main__':
    now = dt.datetime.now(dt.timezone.utc)
    plan = slot(now, sys.argv[1] if len(sys.argv)>1 else '')
    if plan in ('speciale','debat') and not confirmed_matches(Path(__file__).parent, now, finished=plan == 'debat'):
        print('Pas de match confirmé par les données disponibles : spéciale/débat non déclenché.', file=sys.stderr)
        plan = ''
    print(plan)
