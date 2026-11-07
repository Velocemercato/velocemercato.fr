"""Calendriers, compositions publiées et buts issus du flux public ESPN."""
from concurrent.futures import ThreadPoolExecutor
import json
import urllib.request

API = 'https://site.api.espn.com/apis/site/v2/sports/soccer/'
COMPETITIONS = {
    'fra.1': 'Ligue 1', 'uefa.champions': 'Ligue des champions',
    'uefa.europa': 'Ligue Europa', 'uefa.europa.conf': 'Ligue Conférence',
    'fra.coupe_de_france': 'Coupe de France', 'fra.2': 'Ligue 2',
    'eng.1': 'Premier League', 'esp.1': 'Liga', 'ita.1': 'Serie A', 'ger.1': 'Bundesliga',
}


def fetch(path):
    try:
        with urllib.request.urlopen(API + path, timeout=6) as response:
            return json.load(response)
    except (OSError, ValueError):
        return {}


def scoreboard(league, day):
    rows = []
    for event in fetch(f'{league}/scoreboard?dates={day:%Y%m%d}').get('events', []):
        try:
            competition = event['competitions'][0]
            teams = {team['homeAway']: team for team in competition['competitors']}
            status = competition['status']['type']
            if any(word in status['name'] for word in ('POSTPONED', 'CANCEL', 'SUSPENDED', 'ABANDON')):
                continue
            phase = {'pre': 'SCHEDULED', 'in': 'IN_PLAY'}.get(status['state'])
            if status['completed']:
                phase = 'FINISHED'
            ident = str(event['id'])
            if not phase or not ident.isdigit():
                continue
            home, away = teams['home'], teams['away']
            row = {'id': ident, 'date': event['date'], 'comp': COMPETITIONS[league],
                   'dom': home['team']['shortDisplayName'], 'ext': away['team']['shortDisplayName'],
                   'statut': phase, 'league': league,
                   'source': f'https://www.espn.com/soccer/match/_/gameId/{ident}'}
            scores = [str(team.get('score', '')) for team in (home, away)]
            if phase != 'SCHEDULED' and all(score.isdigit() for score in scores):
                row['score'] = list(map(int, scores))
            rows.append(row)
        except (KeyError, IndexError, TypeError):
            continue
    return rows


def fixtures(day):
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = pool.map(lambda league: scoreboard(league, day), COMPETITIONS)
        return [row for matches in results for row in matches]


def details(row):
    league, ident = row.get('league'), str(row.get('id', ''))
    if league not in COMPETITIONS or not ident.isdigit():
        return row
    data = fetch(f'{league}/summary?event={ident}')
    for side in data.get('rosters', []):
        starters = [(player.get('athlete') or {}).get('displayName') for player in side.get('roster', [])
                    if player.get('starter') is True]
        if len(starters) == 11 and all(starters) and side.get('homeAway') in ('home', 'away'):
            row.setdefault('compositions_publiées_ESPN', {})[side['homeAway']] = starters
    if row['statut'] != 'SCHEDULED':
        goals = [{'minute': (event.get('clock') or {}).get('displayValue'), 'description_en': event.get('text')}
                 for event in data.get('keyEvents', [])
                 if event.get('scoringPlay') is True and not event.get('shootout')]
        if goals:
            row['buts_confirmés_ESPN'] = goals[:12]
    return row
