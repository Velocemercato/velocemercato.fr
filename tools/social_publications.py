#!/usr/bin/env python3
"""Préparer deux sélections sourcées ; publier sur Discord seulement avec un accès configuré.

Aucun appel IA, aucune statistique de visiteurs, aucune clé dans les exports.
Les accusés sont conservés hors du site, sur la branche technique social-state.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
PARIS = ZoneInfo('Europe/Paris')
UTC = dt.timezone.utc
SLOTS = {7: 'matin', 12: 'midi', 20: 'soir'}
WEBHOOK = re.compile(r'https://discord\.com/api/webhooks/[0-9]+/[A-Za-z0-9_.-]+')
IDENT = re.compile(r'[a-z0-9][a-z0-9-]{1,99}')


def discord_access():
    configured = os.getenv('DISCORD_WEBHOOK', '').strip()
    if configured:
        return configured
    # Réutiliser le salon déjà configuré dans le robot de scores, sans recopier son accès.
    import update_scores
    return update_scores.WEBHOOK.strip()


def read(path, default):
    return json.loads(Path(path).read_text(encoding='utf-8')) if Path(path).is_file() else default


def timestamp(value):
    try:
        value = dt.datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return value if value.tzinfo else None
    except ValueError:
        return None


def fresh(value, now, hours=24):
    when = timestamp(value)
    return when is not None and dt.timedelta(0) <= now - when <= dt.timedelta(hours=hours)


def clean(value, limit=220):
    return re.sub(r'\s+', ' ', str(value)).replace('@', '＠').replace('`', "'").strip()[:limit]


def eligible_slot(now):
    local = now.astimezone(PARIS)
    return SLOTS.get(local.hour, '') if local.minute < 45 else ''


def prepare(root, now, moment, state=None):
    """Réutilise uniquement les contenus datés présents sur les sites, sans en inventer."""
    root = Path(root)
    state = state or {'receipts': {}}
    receipts = state.get('receipts', {})
    used = {}
    for receipt in receipts.values():
        # Une livraison ambiguë reste exclue jusqu'à vérification manuelle du salon.
        if receipt.get('status') in ('sending', 'uncertain', 'sent'):
            used.setdefault(receipt['brand'], set()).update(receipt.get('items', []))
    rows = []
    configurations = [
        ('velocemercato', 'Véloce Mercato', 'https://velocemercato.fr/', ['foot']),
        ('vmunivers', 'VM Univers', 'https://vmunivers.fr/', ['actus', 'gaming']),
    ]
    paths = {'foot': 'articles.json', 'actus': 'actus/news.json', 'gaming': 'vm-gaming/news.json'}
    labels = {'foot': 'Football', 'actus': 'VM Actus', 'gaming': 'VM Gaming'}
    for brand, title, portal, universes in configurations:
        edition = 'sélection du moment' if moment == 'maintenant' else 'sélection du ' + moment
        parts = [f'{title} · {edition} · {now.astimezone(PARIS):%d/%m/%Y}']
        items, sources = [], []
        excluded = used.get(brand, set())
        for universe in universes:
            news = sorted(read(root / paths[universe], []), key=lambda row: row.get('publishedAt', ''), reverse=True)
            for article in news:
                ident = str(article.get('id', ''))
                key = universe + '/' + ident
                source = next((s for s in article.get('sources', []) if s.get('nom') and str(s.get('url', '')).startswith('https://')), None)
                if (not IDENT.fullmatch(ident) or key in excluded or not source
                        or not article.get('titre') or not fresh(article.get('publishedAt'), now)):
                    continue
                if universe == 'foot':
                    if not (root / 'a' / (ident + '.html')).is_file():
                        continue
                    url = 'https://velocemercato.fr/a/' + ident + '.html'
                else:
                    route = 'actus/' if universe == 'actus' else 'vm-gaming/'
                    url = 'https://velocemercato.fr/' + route + '#a=' + ident
                parts.append(f'{labels[universe]} : {clean(article["titre"])}\nSelon {clean(source["nom"], 70)}\n{url}')
                items.append(key)
                sources.append({'id': key, 'publishedAt': article['publishedAt'], 'media': clean(source['nom'], 70), 'url': source['url']})
                break
        episodes = sorted(read(root / 'studio/emissions.json', []), key=lambda row: row.get('date', ''), reverse=True)
        for episode in episodes:
            key = 'video/' + str(episode.get('id', ''))
            if (episode.get('publie') is True and episode.get('univers') in universes and IDENT.fullmatch(str(episode.get('id', '')))
                    and key not in excluded and fresh(episode.get('date'), now)
                    and (root / 'studio/episodes' / (episode['id'] + '.html')).is_file()):
                url = 'https://velocemercato.fr/studio/episodes/' + episode['id'] + '.html'
                parts.append('JT · programme enregistré, généré par IA : ' + clean(episode.get('titre', 'La Pastille')) + '\n' + url)
                items.append(key)
                break
        if brand == 'velocemercato':
            quiz = read(root / 'quiz.json', {})
            key = 'quiz/' + str(quiz.get('id', ''))
            if (quiz.get('questions') and key not in excluded and fresh(quiz.get('date'), now)
                    and timestamp(quiz['date']).astimezone(PARIS).date() == now.astimezone(PARIS).date()):
                parts.append('Le quiz du jour : avez-vous suivi l’actualité ?\nhttps://velocemercato.fr/#quiz')
                items.append(key)
        if not items:
            continue
        parts.append('Retrouvez nos projets et contenus : ' + portal)
        content = '\n\n'.join(parts)
        if len(content) > 1950:
            raise ValueError('Sélection trop longue pour Discord')
        # L'identité dépend des contenus ; un même lot ne repart pas sous un autre créneau.
        ident = brand + '-' + hashlib.sha256(json.dumps(items, sort_keys=True).encode()).hexdigest()[:20]
        rows.append({'id': ident, 'brand': brand, 'name': title, 'moment': moment,
                     'date': now.isoformat(timespec='seconds'), 'content': content, 'items': items, 'sources': sources})
    return rows


def save_state(path, state, persist=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)
    if persist:
        persist()  # Un envoi est interdit si l'intention n'a pas été enregistrée à distance.


def persist_git(path):
    folder = Path(path).parent
    def git(*args):
        subprocess.run(['git', '-c', 'credential.helper=!gh auth git-credential', *args], cwd=folder,
                       check=True, capture_output=True, text=True)
    git('add', Path(path).name)
    git('-c', 'user.name=github-actions[bot]', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
        'commit', '--quiet', '-m', 'État des publications sociales')
    git('push', '--quiet', 'origin', 'HEAD:social-state')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None


def deliver(posts, state_path, webhook, persist=None, opener=None):
    if not WEBHOOK.fullmatch(webhook):
        raise ValueError('Accès Discord absent ou invalide ; aucun envoi.')
    opener = opener or urllib.request.build_opener(NoRedirect()).open
    state = read(state_path, {'version': 1, 'receipts': {}})
    results = []
    for post in posts:
        existing = state['receipts'].get(post['id'])
        if existing:
            results.append({'id': post['id'], 'status': existing['status'], 'attempted': False})
            continue
        receipt = {'brand': post['brand'], 'items': post['items'], 'status': 'sending',
                   'updated': dt.datetime.now(UTC).isoformat(timespec='seconds')}
        state['receipts'][post['id']] = receipt
        save_state(state_path, state, persist)
        payload = {'content': post['content'], 'username': post['name'], 'allowed_mentions': {'parse': []}}
        request = urllib.request.Request(webhook + '?wait=true', data=json.dumps(payload).encode(),
                                         headers={'Content-Type': 'application/json', 'User-Agent': 'VM-Communication/1.0'}, method='POST')
        try:
            with opener(request, timeout=25) as response:
                data = json.loads(response.read())
            if not str(data.get('id', '')).isdigit():
                raise ValueError('Accusé sans identifiant')
            receipt.update(status='sent', message_id=str(data['id']))
        except urllib.error.HTTPError as error:
            receipt.update(status='rejected' if 400 <= error.code < 500 else 'uncertain', http_status=error.code)
        except Exception:
            receipt['status'] = 'uncertain'
        save_state(state_path, state, persist)
        results.append({'id': post['id'], 'status': receipt['status'], 'attempted': True})
        if receipt['status'] != 'sent':
            break  # Pas de réessai aveugle après une réponse ambiguë.
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--moment', choices=['auto', 'maintenant', 'matin', 'midi', 'soir'], default='auto')
    parser.add_argument('--output', type=Path, default=ROOT / 'studio/tmp/social')
    parser.add_argument('--state', type=Path)
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--git-state', action='store_true')
    args = parser.parse_args()
    now = dt.datetime.now(UTC)
    moment = eligible_slot(now) if args.moment == 'auto' else args.moment
    args.output.mkdir(parents=True, exist_ok=True)
    if not moment:
        print('Hors créneau Paris ; aucun contenu envoyé.')
        return
    state = read(args.state, {'receipts': {}}) if args.state else None
    posts = prepare(ROOT, now, moment, state)
    (args.output / 'publications.json').write_text(json.dumps(posts, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (args.output / 'publications.txt').write_text('\n\n-----\n\n'.join(p['content'] for p in posts) + '\n', encoding='utf-8')
    print(f'{len(posts)} sélection(s) préparée(s), uniquement à partir des contenus datés existants.')
    if not args.publish:
        return
    if os.getenv('GITHUB_ACTIONS') != 'true' or os.getenv('GITHUB_REF') != 'refs/heads/main' or not args.state:
        raise RuntimeError('Envoi disponible uniquement sur main, avec un état persistant.')
    webhook = discord_access()
    if not webhook:
        print('DISCORD_WEBHOOK non disponible dans ce workflow : exports prêts, aucune publication sociale effectuée.')
        (args.output / 'resultats.json').write_text(json.dumps({'provider': 'discord', 'status': 'non_connecte', 'published': 0}) + '\n')
        return
    results = deliver(posts, args.state, webhook, persist=(lambda: persist_git(args.state)) if args.git_state else None)
    (args.output / 'resultats.json').write_text(json.dumps(results, indent=2) + '\n')
    for result in results:
        print(result['id'] + ' : ' + result['status'])
    if any(result['status'] != 'sent' for result in results):
        raise RuntimeError('Livraison interrompue ; vérifier le salon et l’état avant tout réessai.')


if __name__ == '__main__':
    main()
