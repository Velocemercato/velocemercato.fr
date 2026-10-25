#!/usr/bin/env python3
"""Facebook et Instagram automatiques pour Véloce Mercato (Page + Instagram pro reliés).

connecter : échange le jeton court (secret META_USER_TOKEN, 1 h) contre l'accès permanent de la Page,
            rangé dans l'état chiffré (branche broadcast-state). Rien n'est publié.
publier   : seulement si VM_AUTO_META=true (réglé par le propriétaire) :
            - les pastilles verticales récentes (studio/reseaux.json) en Reels Facebook + Instagram ;
            - un article foot sourcé par créneau (8 h, 12 h, 20 h) en publication Facebook avec lien.
Jamais deux fois le même contenu : un accusé est écrit AVANT chaque envoi.
Aucun jeton n'est affiché ; les erreurs Meta sont résumées.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, DeliveryError, git_save  # noqa: E402

GRAPH = 'https://graph.facebook.com/'
HOSTS = {'graph.facebook.com'}
PARIS = ZoneInfo('Europe/Paris')
UTC = dt.timezone.utc
SLOTS = {8: 'matin', 12: 'midi', 20: 'soir'}
IDENT = re.compile(r'[a-z0-9][a-z0-9-]{1,99}')
VIDEO = re.compile(r'https://cdn\.jsdelivr\.net/gh/Velocemercato/velocemercato\.fr@[0-9a-f]{40}/[A-Za-z0-9._-]+\.mp4')


class Graph:
    def call(self, method, path, params):
        url = GRAPH + path.lstrip('/')
        if urllib.parse.urlsplit(url).hostname not in HOSTS:
            raise DeliveryError('Destination Meta non autorisée.')
        data = urllib.parse.urlencode(params).encode()
        if method == 'GET':
            request = urllib.request.Request(url + '?' + data.decode(), method='GET')
        else:
            request = urllib.request.Request(url, data=data, method='POST')
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read() or b'{}')
        except urllib.error.HTTPError as error:
            try:
                info = json.loads(error.read()).get('error', {})
            except ValueError:
                info = {}
            message = re.sub(r'[A-Za-z0-9]{40,}', '…', str(info.get('message', '')))[:180]
            raise DeliveryError(f'Meta a refusé ({error.code}, code {info.get("code", "?")}) : {message}') from None


def connect(state, graph, app_id, app_secret, user_token):
    long = graph.call('GET', 'oauth/access_token', {'grant_type': 'fb_exchange_token', 'client_id': app_id,
                                                    'client_secret': app_secret, 'fb_exchange_token': user_token})
    token = long.get('access_token')
    if not token:
        raise DeliveryError('Meta : échange du jeton non confirmé (jeton expiré ? le refaire dans l’explorateur).')
    pages = graph.call('GET', 'me/accounts', {'fields': 'id,name,access_token,instagram_business_account{id,username}',
                                              'access_token': token}).get('data', [])
    pages = [p for p in pages if p.get('access_token')]
    if not pages:
        raise DeliveryError('Meta : aucune Page autorisée. Cocher la Page Véloce Mercato lors de « Generate Access Token ».')
    page = next((p for p in pages if 'veloce' in p.get('name', '').lower().replace('é', 'e')), pages[0])
    insta = page.get('instagram_business_account') or {}
    state.data.setdefault('tokens', {})['meta'] = {'page_id': str(page['id']), 'page_name': page.get('name', ''),
                                                   'page_token': page['access_token'], 'ig_id': str(insta.get('id', '')),
                                                   'ig_username': insta.get('username', '')}
    state.save()
    print(f'::notice::Meta connecté : Page « {page.get("name", "?")} »'
          + (f' + Instagram @{insta["username"]}' if insta.get('username') else ' (aucun Instagram pro relié à cette Page)')
          + '. Rien n’est publié tant que VM_AUTO_META n’est pas à true.', flush=True)
    return page


def read(path, default):
    path = Path(path)
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else default


def when(value):
    try:
        moment = dt.datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return moment if moment.tzinfo else None
    except ValueError:
        return None


def clean(value, limit=600):
    return re.sub(r'[ \t]+', ' ', str(value)).strip()[:limit]


def reels(root, now, hours=30):
    out = []
    for row in read(Path(root) / 'studio/reseaux.json', []):
        date = when(row.get('date'))
        if (IDENT.fullmatch(str(row.get('id', ''))) and VIDEO.fullmatch(str(row.get('verticale', '')))
                and date and dt.timedelta(0) <= now - date <= dt.timedelta(hours=hours)):
            out.append(row)
    return sorted(out, key=lambda r: r['date'])


def article(root, now, done, hours=12):
    rows = sorted(read(Path(root) / 'articles.json', []), key=lambda a: a.get('publishedAt', ''), reverse=True)
    for row in rows:
        ident = str(row.get('id', ''))
        source = next((s for s in row.get('sources', []) if s.get('nom') and str(s.get('url', '')).startswith('https://')), None)
        date = when(row.get('publishedAt'))
        if (IDENT.fullmatch(ident) and source and row.get('titre') and row.get('resume') and 'article/' + ident not in done
                and date and dt.timedelta(0) <= now - date <= dt.timedelta(hours=hours)
                and (Path(root) / 'a' / (ident + '.html')).is_file()):
            return row, source
    return None, None


def instagram_reel(graph, meta, row, wait=480, sleep=time.sleep):
    created = graph.call('POST', meta['ig_id'] + '/media', {'media_type': 'REELS', 'video_url': row['verticale'],
                                                           'caption': clean(row.get('texte_vertical') or row.get('titre'), 2100),
                                                           'share_to_feed': 'true', 'access_token': meta['page_token']})
    container = created.get('id')
    if not container:
        raise DeliveryError('Instagram : préparation du Reel non confirmée.')
    for _ in range(max(1, wait // 15)):
        status = graph.call('GET', container, {'fields': 'status_code', 'access_token': meta['page_token']}).get('status_code')
        if status == 'FINISHED':
            return graph.call('POST', meta['ig_id'] + '/media_publish', {'creation_id': container,
                                                                         'access_token': meta['page_token']}).get('id')
        if status in ('ERROR', 'EXPIRED'):
            raise DeliveryError('Instagram : la vidéo a été refusée au traitement.')
        sleep(15)
    raise DeliveryError('Instagram : traitement trop long, Reel non publié (sera ignoré pour éviter un doublon).')


def publish(state, graph, root=ROOT, now=None, limit=2, sleep=time.sleep):
    now = now or dt.datetime.now(UTC)
    meta = state.data.get('tokens', {}).get('meta')
    if not meta or not meta.get('page_token'):
        raise DeliveryError('Meta non connecté : lancer « Connecter Facebook et Instagram ».')
    done = state.data.setdefault('meta', {})
    errors, sent = [], 0

    def mark(key, status, **extra):
        done[key] = {'status': status, 'at': now.isoformat(timespec='seconds'), **extra}
        state.save()

    for row in reels(root, now):
        if sent >= limit:
            break
        attempted = False
        for network in ('facebook', 'instagram'):
            key = f'reel/{network}/{row["id"]}'
            if key in done or (network == 'instagram' and not meta.get('ig_id')):
                continue
            attempted = True
            mark(key, 'envoi')  # accusé AVANT l'envoi : jamais de doublon, même après une coupure
            try:
                if network == 'facebook':
                    result = graph.call('POST', meta['page_id'] + '/videos', {
                        'file_url': row['verticale'], 'description': clean(row.get('texte_vertical') or row.get('titre'), 2000),
                        'access_token': meta['page_token']}).get('id')
                else:
                    result = instagram_reel(graph, meta, row, sleep=sleep)
                mark(key, 'publie', post=str(result or ''))
                print(f'::notice::{network} : pastille {row["id"]} publiée')
            except DeliveryError as error:
                mark(key, 'echec')
                errors.append(f'{network} / {row["id"]} : {error}')
        sent += attempted

    local = now.astimezone(PARIS)
    slot = SLOTS.get(local.hour)
    slot_key = f'creneau/{local:%Y-%m-%d}/{slot}'
    if slot and slot_key not in done:
        row, source = article(root, now, done)
        if row:
            key = 'article/' + row['id']
            mark(slot_key, 'envoi', article=row['id'])
            mark(key, 'envoi')
            url = 'https://velocemercato.fr/a/' + row['id'] + '.html'
            message = (f'⚽ {clean(row["titre"], 200)}\n\n{clean(row["resume"], 500)}\n\n'
                       f'Selon {clean(source["nom"], 70)}\n👉 Toute l’info sur velocemercato.fr\n\n#foot #mercato #football #velocemercato')
            try:
                result = graph.call('POST', meta['page_id'] + '/feed', {'message': message, 'link': url,
                                                                        'access_token': meta['page_token']}).get('id')
                mark(key, 'publie', post=str(result or ''))
                mark(slot_key, 'publie', article=row['id'])
                print(f'::notice::facebook : article {row["id"]} publié ({slot})')
            except DeliveryError as error:
                mark(key, 'echec')
                errors.append(f'facebook / article {row["id"]} : {error}')
    for line in errors:
        print('::error::' + line.replace('\n', ' '))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['connecter', 'publier'])
    parser.add_argument('--state', type=Path, required=True)
    args = parser.parse_args()
    state = State(args.state, os.getenv('VM_DIFFUSION_STATE_KEY', ''), lambda: git_save(args.state))
    if args.action == 'connecter':
        values = [os.getenv(name, '').strip() for name in ('META_APP_ID', 'META_APP_SECRET', 'META_USER_TOKEN')]
        if not all(values):
            raise DeliveryError('Ajouter META_APP_ID, META_APP_SECRET et META_USER_TOKEN dans les secrets GitHub.')
        connect(state, Graph(), *values)
        return
    if os.getenv('VM_AUTO_META') != 'true':
        print('Facebook/Instagram : publication automatique non activée (VM_AUTO_META). Rien n’est publié.')
        return
    if publish(state, Graph()):
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:  # message contrôlé, sans jeton
        message = str(error) if isinstance(error, DeliveryError) else 'Interrompu (' + type(error).__name__ + ').'
        print('::error::' + message.replace('\n', ' '))
        sys.exit(1)
