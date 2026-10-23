"""Horaires locaux et matchs confirmés ; aucune requête réseau ni publication."""
import datetime as dt
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

PARIS = ZoneInfo('Europe/Paris')
JT_CRON = '0 6,7,10,11,18,19 * * *'
JT_PREP_CRON = '45 4,5,8,9,16,17 * * *'
MATCH_CRON = '15,45 10-22 * * *'
DEBATE_CRON = '45 20,21,22 * * *'
BUTS_CRON = '0 16,17 * * 0'


def slot(now, cron):
    local = now.astimezone(PARIS)
    if cron == JT_PREP_CRON:
        minute = local.hour * 60 + local.minute
        for hour, moment in [(8, 'matin'), (12, 'midi'), (20, 'soir')]:
            # Préparation 75 minutes avant ; accepter un déclenchement tardif
            # jusqu'à la fin de l'heure cible, sans inventer une ponctualité.
            if hour * 60 - 75 <= minute < hour * 60 + 60:
                return moment
    if cron == JT_CRON:
        return {8:'matin',12:'midi',20:'soir'}.get(local.hour, '')
    if cron == MATCH_CRON:
        return 'speciale'
    if cron == DEBATE_CRON and local.hour in (22, 23) and local.minute >= 30:
        return 'debat'  # 22 h 45 si le match est terminé, sinon rattrapage à 23 h 45 (une seule fois par jour)
    if cron == BUTS_CRON and local.hour == 18 and local.weekday() == 6:
        return 'buts'   # dimanche 18 h : les buts de la semaine
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


def plan(root, now, cron):
    """Un rattrapage ne déclenche aucun travail si les trois JT existent déjà."""
    result = slot(now, cron)
    if result in ('matin', 'midi', 'soir'):
        if all(already_published(root, universe, 'edition', result, now)
               for universe in ('foot', 'actus', 'gaming')):
            return ''
    if result in ('speciale', 'debat') and not confirmed_matches(root, now, finished=result == 'debat'):
        return ''
    return result


if __name__ == '__main__':
    now = dt.datetime.now(dt.timezone.utc)
    print(plan(Path(__file__).parent, now, sys.argv[1] if len(sys.argv)>1 else ''))
