#!/usr/bin/env python3
"""Connecter Twitch depuis un téléphone : le propriétaire tape un code sur twitch.tv/activate.

- Aucun jeton n'est affiché : il est rangé dans l'état chiffré (branche broadcast-state).
- Le code affiché est à usage unique et expire en quelques minutes.
- Connecter ne lance AUCUNE diffusion : il faut en plus VM_AUTO_TWITCH=true, réglé par le propriétaire.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, DeliveryError, git_save  # noqa: E402

SCOPES = 'channel:manage:broadcast channel:read:stream_key'
GRANT = 'urn:ietf:params:oauth:grant-type:device_code'


def post(url, form):
    request = urllib.request.Request(url, data=urllib.parse.urlencode(form).encode(), method='POST',
                                     headers={'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, json.loads(response.read() or b'{}')
    except urllib.error.HTTPError as error:
        try:
            return error.code, json.loads(error.read() or b'{}')
        except ValueError:
            return error.code, {}


def get_user(client_id, token):
    request = urllib.request.Request('https://api.twitch.tv/helix/users',
                                     headers={'Client-Id': client_id, 'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(request, timeout=60) as response:
        rows = json.loads(response.read()).get('data', [])
    if len(rows) != 1:
        raise DeliveryError('Compte Twitch connecté non identifié.')
    return rows[0]


def start(client_id, post=post):
    """1re étape : obtenir le code à taper (affiché dans les annotations dès la fin de l'étape)."""
    status, device = post('https://id.twitch.tv/oauth2/device', {'client_id': client_id, 'scopes': SCOPES})
    if status != 200 or not device.get('device_code'):
        raise DeliveryError(f'Twitch : demande de code refusée ({device.get("message", status)}). Vérifier TWITCH_CLIENT_ID.')
    print(f'::notice::CODE TWITCH : {device["user_code"]} · à taper sur https://www.twitch.tv/activate '
          f'(valable {int(device.get("expires_in", 1800)) // 60} min)', flush=True)
    device['started'] = time.time()
    return device


def wait(state, client_id, client_secret, device, limit=900, post=post, get_user=get_user, sleep=time.sleep, clock=time.time):
    """2e étape : attendre la saisie du code, puis ranger le jeton dans l'état chiffré."""
    deadline = device.get('started', clock()) + min(limit, int(device.get('expires_in', 1800)))
    interval = max(int(device.get('interval', 5)), 5)
    form = {'client_id': client_id, 'client_secret': client_secret, 'scopes': SCOPES,
            'device_code': device['device_code'], 'grant_type': GRANT}
    while clock() < deadline:
        sleep(interval)
        status, token = post('https://id.twitch.tv/oauth2/token', form)
        if status == 200 and token.get('refresh_token'):
            granted = set(token.get('scope') or [])
            if not set(SCOPES.split()).issubset(granted):
                raise DeliveryError('Les deux autorisations Twitch nécessaires n’ont pas été accordées.')
            user = get_user(client_id, token['access_token'])
            state.data['tokens']['twitch'] = {'refresh': token['refresh_token'], 'fingerprint': 'device:' + client_id,
                                              'user': str(user['id']), 'login': user.get('login', '')}
            state.save()
            print(f'::notice::Twitch connecté : {user.get("display_name", user.get("login", "?"))}. '
                  'Aucune diffusion tant que VM_AUTO_TWITCH n’est pas à true.', flush=True)
            return user
        message = str(token.get('message', '')).lower()
        if 'pending' in message:
            continue
        if 'slow' in message:
            interval += 5
            continue
        raise DeliveryError(f'Twitch : connexion refusée ({token.get("message", status)}).')
    raise DeliveryError('Twitch : code non saisi à temps. Relancer « Connecter Twitch ».')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('etape', choices=['code', 'attendre'])
    parser.add_argument('--state', type=Path)
    parser.add_argument('--device', type=Path, required=True, help='Fichier temporaire du runner, hors dépôt')
    args = parser.parse_args()
    client_id = os.getenv('TWITCH_CLIENT_ID', '').strip()
    client_secret = os.getenv('TWITCH_CLIENT_SECRET', '').strip()
    if not client_id or not client_secret:
        raise DeliveryError('Ajouter d’abord TWITCH_CLIENT_ID et TWITCH_CLIENT_SECRET dans les secrets GitHub.')
    if args.etape == 'code':
        device = start(client_id)
        args.device.write_text(json.dumps(device))
        args.device.chmod(0o600)
        return
    device = json.loads(args.device.read_text())
    state = State(args.state, os.getenv('VM_DIFFUSION_STATE_KEY', ''), lambda: git_save(args.state))
    wait(state, client_id, client_secret, device)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:  # message contrôlé, sans jeton
        message = str(error) if isinstance(error, DeliveryError) else 'Connexion interrompue (' + type(error).__name__ + ').'
        print('::error::' + message.replace('\n', ' '))
        sys.exit(1)
