"""Horaires locaux et matchs confirmés ; aucune requête réseau ni publication."""
import datetime as dt
import json
import os
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

PARIS = ZoneInfo('Europe/Paris')
JT_CRON = '0 6,7,10,11,18,19 * * *'
JT_PREP_CRON = '45 4,5,8,9,16,17 * * *'
MATCH_CRON = '15,45 10-22 * * *'
DEBATE_CRON = '45 20,21,22 * * *'
BUTS_CRON = '0 16,17 * * 0'
# Un déclenchement après l'heure couvre les articles jusqu'à l'heure annoncée.
# Les passages suivants rattrapent un retard sans produire deux fois le JT.
SEPARATE_CRON = '2,15,32,47 * * * *'
EDITION_HOURS = {'actus': (7, 13, 19), 'foot': (8, 12, 20, 23), 'gaming': (0, 10, 18)}
GRID_START = dt.date(2026, 11, 8)
DAILY_HOURS = {'actus': (7, 12, 19), 'foot': (8, 13, 20, 23), 'gaming': (9, 16, 22)}
# Créneaux mis en pause sans toucher à la grille (limite d'envois YouTube par jour).
# Variable VM_JT_PAUSE, ex. "actus:7,foot:23" ; vide = toute la grille.


def paused_slots():
    out = set()
    for part in os.environ.get('VM_JT_PAUSE', '').replace(' ', '').split(','):
        name, _, hour = part.partition(':')
        if name in EDITION_HOURS and hour.isdigit():
            out.add((name, int(hour)))
    return out


def active_hours(universe):
    """Heures réellement produites ; la pause ne vide jamais complètement un univers."""
    paused = paused_slots()
    hours = tuple(h for h in EDITION_HOURS[universe] if (universe, h) not in paused)
    return hours or EDITION_HOURS[universe]


def paris_slots(universe, day):
    if day < GRID_START:
        return [(h, 0, 'jt') for h in active_hours(universe)]
    slots = [(h, 0, 'jt') for h in DAILY_HOURS[universe]]
    if universe == 'foot':
        slots[-1] = (23, 0, 'semaine' if day.weekday() == 6 else 'debrief')
        slots.append((20, 15, 'match'))
        if day.weekday() == 4:
            slots.append((18, 0, 'semaine'))
    elif day.weekday() == 6:
        slots.append((23, 0, 'semaine'))
    return sorted(slots)


def edition_window(universe, target):
    """Bornes (précédente édition, édition courante], en heure de Paris."""
    if universe not in EDITION_HOURS or target.tzinfo is None:
        raise ValueError('Univers ou date de JT invalide.')
    target = target.astimezone(PARIS)
    day = target.date()
    if day < GRID_START:
        slots = [(h, 0, 'jt') for h in EDITION_HOURS[universe]]
    else:
        slots = paris_slots(universe, day)
    clock = (target.hour, target.minute)
    kind = next((kind for hour, minute, kind in slots if (hour, minute) == clock), '')
    if not kind or target.second or target.microsecond:
        raise ValueError('Heure hors de la grille des JT.')
    if day < GRID_START:
        hours = active_hours(universe)
        previous = [target.replace(hour=h) for h in hours if h < target.hour]
        start = max(previous) if previous else (target - dt.timedelta(days=1)).replace(hour=hours[-1])
    else:
        previous = [hour for hour in DAILY_HOURS[universe] if hour < target.hour]
        last = DAILY_HOURS[universe][-1]
        if day == GRID_START:
            last = active_hours(universe)[-1]
        start = target.replace(hour=previous[-1], minute=0) if previous else (target - dt.timedelta(days=1)).replace(hour=last, minute=0)
        midnight = target.replace(hour=0, minute=0)
        if kind == 'semaine':
            start = target - dt.timedelta(days=7) if day.weekday() == 4 else midnight - dt.timedelta(days=6)
        elif kind == 'debrief':
            start = midnight
        elif kind == 'match':
            start = target - dt.timedelta(hours=8)
    midi_end = 16 if day < GRID_START else 17
    moment = 'matin' if 5 <= target.hour < 12 else 'midi' if 12 <= target.hour < midi_end else 'soir'
    label = {'semaine': 'Récap de la semaine', 'debrief': 'Débrief sport du jour',
             'match': 'Point match 20 h 15'}.get(kind, f'JT {target:%H} h')
    if kind == 'jt' and universe == 'foot' and day >= GRID_START:
        label = f'JT multisport {target:%H} h'
    return {'univers': universe, 'edition_at': target.isoformat(), 'source_start': start.isoformat(),
            'source_end': target.isoformat(), 'moment': moment, 'label': label, 'kind': kind}


def long_delivery(edition):
    """Répartir les mises en ligne YouTube. Toutes les éditions ont aussi un rendu site."""
    target = dt.datetime.fromisoformat(edition['edition_at'])
    if target.date() < GRID_START:
        return True
    hour, weekday = target.hour, target.weekday()
    return (hour in (7, 8, 9, 23)
            or (weekday != 6 and (edition['kind'] == 'match'
                                 or (hour == 18 if weekday == 4 else hour == 19))))


def edition_recorded(root, edition):
    """Un original déjà transmis reste à reprendre en diffusion, sans le recréer."""
    for path in (Path(root) / 'studio/tv').glob('*.json'):
        if path.name.startswith('_'):
            continue
        row = json.loads(path.read_text())
        if (row.get('univers') == edition['univers'] and row.get('format') == 'edition'
                and row.get('edition_at') == edition['edition_at']
                and (row.get('publie') is True or row.get('hebergement') == 'en_attente' or row.get('diffusion') == 'youtube')):
            return True
    return False


def due_edition(root, now, universe=None, extra_scores=()):
    """Dernier créneau échu depuis moins de 3 h (GitHub saute parfois des déclenchements) ; jamais une édition future."""
    local = now.astimezone(PARIS)
    candidates = []
    for name in EDITION_HOURS:
        if universe and name != universe:
            continue
        for day in (local.date(), local.date() - dt.timedelta(days=1)):
            for hour, minute, kind in paris_slots(name, day):
                target = dt.datetime.combine(day, dt.time(hour, minute), PARIS)
                age = now.astimezone(dt.timezone.utc) - target.astimezone(dt.timezone.utc)
                if not dt.timedelta(0) <= age < dt.timedelta(minutes=35 if kind == 'match' else 180):
                    continue
                if kind == 'match' and not edition_fixtures(root, target, kind, extra_scores):
                    continue
                candidates.append(edition_window(name, target))
    for edition in sorted(candidates, key=lambda e: (e['edition_at'], e['univers'] == 'foot'), reverse=True):
        if not edition_recorded(root, edition):
            return edition
    return None


def edition_fixtures(root, target, kind, extra_scores=()):
    """Instantané sourcé des affiches du soir ou des résultats du jour."""
    path = Path(root) / 'scores.json'
    if kind not in ('match', 'debrief', 'semaine'):
        return []
    data = json.loads(path.read_text()) if path.is_file() else {}
    covered = {row['comp'] for row in extra_scores}
    matches = list(extra_scores) + [row for row in data.get('matchs', []) if row.get('comp') not in covered]
    rows = []
    for match in matches:
        try:
            kick = dt.datetime.fromisoformat(match['date'].replace('Z', '+00:00'))
            if not kick.tzinfo or kick.astimezone(PARIS).date() != target.date():
                continue
            status = match['statut']
            if kind == 'match':
                if not -dt.timedelta(minutes=20) <= kick - target <= dt.timedelta(minutes=95):
                    continue
                if status not in ('SCHEDULED', 'TIMED', 'IN_PLAY', 'PAUSED'):
                    continue
            elif kick > target or status not in ('FINISHED', 'IN_PLAY', 'PAUSED'):
                continue
            if not all(match.get(k) for k in ('id', 'comp', 'dom', 'ext')):
                continue
            keys = ('id', 'date', 'comp', 'dom', 'ext', 'statut', 'source', 'league')
            row = {k: match[k] for k in keys if k in match}
            if status in ('FINISHED', 'IN_PLAY', 'PAUSED') and None not in match.get('score', [None]):
                row['score'] = match['score']
            rows.append(row)
        except (KeyError, ValueError, TypeError):
            continue
    major = {'Ligue 1', 'Ligue des champions', 'Ligue Europa', 'Ligue Conférence', 'Coupe de France'}
    return sorted(rows, key=lambda row: (row['comp'] not in major, row['date']))[:12]


SUNDAY_SHOW_HOUR = 11  # Le mag du dimanche (format 'buts'), comme Téléfoot


def sunday_show_due(root, now):
    """Dimanche entre 11 h et 13 h 59 (rattrapages compris), une seule fois par dimanche."""
    local = now.astimezone(PARIS)
    if local.date() >= GRID_START or local.weekday() != 6 or not SUNDAY_SHOW_HOUR <= local.hour < SUNDAY_SHOW_HOUR + 3:
        return False
    return not already_published(root, 'foot', 'buts', 'soir', now)


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
