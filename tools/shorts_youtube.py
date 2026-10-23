#!/usr/bin/env python3
"""Publier les versions verticales des JT en Shorts YouTube.

Réutilise la connexion et les accusés chiffrés de tools/diffuser_jt.py :
aucun jeton dans le dépôt, aucun envoi en double (un accusé par Short).
Quota YouTube : chaque envoi coûte environ 1 600 points sur 10 000 par jour,
partagés avec les JT longs. D'où une limite quotidienne (VM_SHORTS_PAR_JOUR, 1 par défaut)
et un seul moment par jour (VM_SHORTS_MOMENT, « midi » par défaut).
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import (HTTP, DeliveryError, State, YouTube, access_token, enabled,  # noqa: E402
                               public_allowed)
import subprocess  # noqa: E402

BRANCH = 'shorts-state'  # registre séparé : jamais de conflit avec la diffusion des JT longs


def git_save(path):
    def git(*args):
        subprocess.run(['git', '-c', 'credential.helper=!gh auth git-credential', *args],
                       cwd=Path(path).parent, check=True, capture_output=True)
    git('add', Path(path).name)
    git('-c', 'user.name=github-actions[bot]', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
        'commit', '--quiet', '-m', 'Accusés des Shorts chiffrés')
    git('push', '--quiet', 'origin', 'HEAD:' + BRANCH)

PARIS = ZoneInfo('Europe/Paris')
LIST = ROOT / 'studio/reseaux.json'
EMISSIONS = ROOT / 'studio/emissions.json'
PUBLIC_LIST = ROOT / 'studio/shorts.json'
CATEGORIES = {'foot': '17', 'gaming': '20', 'actus': '25'}
NAMES = {'foot': 'Véloce Mercato', 'actus': 'VM Actus', 'gaming': 'VM Gaming'}


def metadata(row):
    title = (row.get('titre') or NAMES.get(row.get('univers'), 'VM')).strip()
    title = (title[:88].rstrip() + ' #Shorts') if '#shorts' not in title.lower() else title[:100]
    description = (row.get('texte_vertical') or row.get('texte') or '').strip() + (
        '\n\nProgramme généré par IA, avec des personnages inventés. Actualités issues des brèves sourcées des médias VM.\n'
        'Le JT complet : https://velocemercato.fr/studio.html#tv\nTous nos projets : https://vmunivers.fr/\n#Shorts')
    return {'snippet': {'title': title, 'description': description[:4900], 'categoryId': CATEGORIES.get(row.get('univers'), '25'),
                        'defaultLanguage': 'fr', 'tags': ['VM', 'Véloce Mercato', 'La Pastille', 'Shorts']},
            'status': {'privacyStatus': 'public' if public_allowed() else 'private',
                       'selfDeclaredMadeForKids': False, 'containsSyntheticMedia': True}}


def candidates(today, moment):
    rows = json.loads(LIST.read_text(encoding='utf-8')) if LIST.is_file() else []
    moments = {e['id']: e.get('moment') for e in json.loads(EMISSIONS.read_text(encoding='utf-8'))} if EMISSIONS.is_file() else {}
    keep = []
    for r in rows:
        when = dt.datetime.fromisoformat(r['date']).astimezone(PARIS).date() if r.get('date') else None
        if when == today and r.get('verticale') and (not moment or moments.get(r['id'], r.get('moment')) == moment):
            keep.append(r)
    # Un seul Short par univers et par jour : le JT le plus récent (la liste est du plus récent au plus ancien).
    seen, unique = set(), []
    for r in keep:
        if r.get('univers') not in seen:
            seen.add(r.get('univers'))
            unique.append(r)
    order = {'foot': 0, 'actus': 1, 'gaming': 2}
    return sorted(unique, key=lambda r: order.get(r.get('univers'), 9))


def download(url, path):
    if not url.startswith('https://cdn.jsdelivr.net/gh/Velocemercato/'):
        raise DeliveryError('Source de la vidéo verticale non autorisée.')
    req = urllib.request.Request(url, headers={'User-Agent': 'VM-shorts/1.0'})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, 'wb') as f:
        shutil.copyfileobj(r, f)


def save_public(rows):
    old = json.loads(PUBLIC_LIST.read_text(encoding='utf-8')) if PUBLIC_LIST.is_file() else []
    merged = {r['id']: r for r in old}
    merged.update({r['id']: r for r in rows})
    PUBLIC_LIST.write_text(json.dumps(sorted(merged.values(), key=lambda r: r['date_publication'], reverse=True)[:60],
                                      ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--state', type=Path, required=True)
    p.add_argument('--git-state', action='store_true')
    a = p.parse_args()
    if not enabled('youtube'):
        print('YouTube non configuré ou désactivé (VM_AUTO_YOUTUBE) : aucun Short envoyé.')
        return
    limit = max(0, int(os.getenv('VM_SHORTS_PAR_JOUR', '1') or 1))
    moment = os.getenv('VM_SHORTS_MOMENT', 'midi').strip()
    today = dt.datetime.now(PARIS).date()
    state = State(a.state, os.getenv('VM_DIFFUSION_STATE_KEY', ''), (lambda: git_save(a.state)) if a.git_state else None)
    shorts = state.data.setdefault('shorts', {})
    sent_today = sum(1 for r in shorts.values() if r.get('jour') == today.isoformat() and r.get('video_id'))
    done_univers = {r.get('univers') for r in shorts.values() if r.get('jour') == today.isoformat() and r.get('video_id')}
    # La liste publique fait aussi foi : un JT déjà publié en Short n'est jamais renvoyé, même si le registre est neuf.
    public = json.loads(PUBLIC_LIST.read_text(encoding='utf-8')) if PUBLIC_LIST.is_file() else []
    public_today = [r for r in public if dt.datetime.fromisoformat(r['date_publication']).astimezone(PARIS).date() == today]
    already = {r['id'] for r in public}
    done_univers |= {r.get('univers') for r in public_today}
    sent_today = max(sent_today, len(public_today))
    todo = [r for r in candidates(today, moment)
            if r['id'] not in already and r.get('univers') not in done_univers and shorts.get(r['id'], {}).get('status') != 'published'][:max(0, limit - sent_today)]
    if not todo:
        print(f'Aucun Short à envoyer ({sent_today}/{limit} aujourd’hui).')
        return
    http = HTTP()
    client = YouTube(http, state, access_token('youtube', state, http))
    client.verify_channel()
    published, errors = [], []
    for r in todo:
        receipt = shorts.setdefault(r['id'], {'jour': today.isoformat(), 'univers': r.get('univers')})
        try:
            with tempfile.TemporaryDirectory() as tmp:
                file = Path(tmp) / (r['id'] + '-vertical.mp4')
                if not receipt.get('video_id'):
                    download(r['verticale'], file)
                client.upload(file, metadata(r), receipt)
            if public_allowed():
                client.make_public(receipt, timeout=1200)
            else:
                receipt['status'] = 'private_ready'
                state.save()
            if receipt.get('status') == 'published':
                url = 'https://www.youtube.com/shorts/' + receipt['video_id']
                published.append({'id': r['id'], 'univers': r.get('univers'), 'titre': r.get('titre'), 'url': url,
                                  'date_publication': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')})
                print('::notice::Short publié · ' + url)
        except DeliveryError as error:
            # Aucune session ouverte = aucune vidéo créée : on peut réessayer au prochain passage.
            if not receipt.get('session') and not receipt.get('video_id'):
                shorts.pop(r['id'], None)
                state.save()
            errors.append(f"{r['id']} : {error}")
            if 'quota' in str(error).lower() or 'Limit' in str(error):
                break  # Inutile d'insister : le quota repart le lendemain.
    if published:
        save_public(published)
    for e in errors:
        print('::error::' + e.replace('\n', ' '))
    if errors and not published:
        raise DeliveryError('Aucun Short confirmé ; les accusés sont conservés.')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        message = str(error) if isinstance(error, DeliveryError) else 'Shorts interrompus (' + type(error).__name__ + '). Aucun succès annoncé.'
        print('::error::' + message.replace('\n', ' '))
        sys.exit(1)
