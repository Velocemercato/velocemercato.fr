#!/usr/bin/env python3
"""Envoie les vidéos de présentation VM (media/promos) sur YouTube, en PRIVÉ.

- 2 vidéos maximum par passage (quota YouTube API : ~6 envois par jour, les JT restent prioritaires).
- Jamais deux fois la même vidéo : les accusés sont chiffrés dans l'état de diffusion (branche broadcast-state).
- Passage en public UNIQUEMENT si VM_YOUTUBE_PUBLIC=true (accord du propriétaire).
"""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import clean_credential, HTTP, State, YouTube, DeliveryError, access_token, enabled, git_save, public_allowed

PROMOS = [
    ('veloce-foot', 'Véloce Mercato — le média foot', 'https://velocemercato.fr/'),
    ('vm-univers', 'VM Univers — tous les projets VM', 'https://vmunivers.fr/'),
    ('vm-studio', 'La Pastille TV — les JT foot, actu et gaming', 'https://velocemercato.fr/studio.html'),
    ('vm-actus', "VM Actus — l'actu en brèves sourcées", 'https://velocemercato.fr/actus/'),
    ('vm-gaming', 'VM Gaming — jeux vidéo et communauté', 'https://velocemercato.fr/vm-gaming/'),
    ('vm-bureaux', 'Véloce Web Studio — votre site internet', 'https://velocemercato.fr/web-studio.html'),
]
FORMATS = [('vertical', ' #Shorts'), ('paysage', '')]


def queue():
    for fmt, suffix in FORMATS:          # d'abord les Shorts verticaux, puis les versions paysage
        for key, title, url in PROMOS:
            path = ROOT / 'media/promos' / f'{key}-{fmt}.mp4'
            if path.is_file():
                yield f'{key}-{fmt}', path, title + suffix, url


def metadata(title, url):
    return {'snippet': {'title': title[:100], 'categoryId': '22', 'defaultLanguage': 'fr',
                        'description': f'{title}\n\n👉 {url}\nTous les projets VM : https://vmunivers.fr/\n\n'
                                       'Vidéo de présentation réalisée avec l’aide de l’IA (visuels et montage).',
                        'tags': ['VM Univers', 'Véloce Mercato', 'VM']},
            'status': {'privacyStatus': 'private', 'selfDeclaredMadeForKids': False, 'containsSyntheticMedia': True}}


def run(state, http, limit=2):
    done = state.data.setdefault('promos', {})
    sent = 0
    token = None
    for ident, path, title, url in queue():
        receipt = done.setdefault(ident, {})
        if receipt.get('status') in ('private_ready', 'published') and not (receipt['status'] == 'private_ready' and public_allowed()):
            continue
        if sent >= limit:
            break
        token = token or access_token('youtube', state, http)
        client = YouTube(http, state, token)
        client.verify_channel()
        client.upload(path, metadata(title, url), receipt)
        if public_allowed():
            client.make_public(receipt)
        else:
            receipt['status'] = 'private_ready'
            state.save()
        print(f'::notice::{ident} : {receipt["status"]}')
        sent += 1
    left = sum(1 for ident, *_ in queue() if done.get(ident, {}).get('status') not in ('private_ready', 'published'))
    print(f'::notice::Envoyées ce passage : {sent} · restantes : {left}')
    return sent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--limit', type=int, default=2)
    args = parser.parse_args()
    cid = clean_credential('youtube', 'CLIENT_ID', os.getenv('YOUTUBE_CLIENT_ID', ''))
    sec = os.getenv('YOUTUBE_CLIENT_SECRET', '').strip()
    ref = clean_credential('youtube', 'REFRESH_TOKEN', os.getenv('YOUTUBE_REFRESH_TOKEN', ''))
    # Contrôle sans divulgation : l'ID client est public ; du secret on ne montre que les 4 derniers caractères,
    # comme la console Google (****xxxx), pour comparer.
    print(f'::notice::Contrôle : ID client longueur {len(cid)}, commence par 143768939550- : {cid.startswith("143768939550-")}, finit par .apps.googleusercontent.com : {cid.endswith(".apps.googleusercontent.com")} · secret commence par GOCSPX- : {sec.startswith("GOCSPX-")} · '
          f'longueur secret {len(sec)} · fin du secret ****{sec[-4:] if len(sec) > 8 else "?"} · '
          f'jeton commence par 1// : {ref.startswith("1//")} (longueur {len(ref)}) · chaîne commence par UC : '
          f'{os.getenv("YOUTUBE_CHANNEL_ID", "").strip().startswith("UC")}')
    if not enabled('youtube'):
        print('YouTube non connecté : aucun envoi.')
        return
    state = State(args.state, os.getenv('VM_DIFFUSION_STATE_KEY', ''), lambda: git_save(args.state))
    run(state, HTTP(), max(1, min(args.limit, 3)))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:  # message visible dans les annotations GitHub, sans secret
        msg = str(error) if isinstance(error, DeliveryError) else type(error).__name__ + ' : ' + str(error)[:200]
        print('::error::' + msg.replace('\n', ' '))
        sys.exit(1)
