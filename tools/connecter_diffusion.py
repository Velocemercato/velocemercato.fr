#!/usr/bin/env python3
"""À lancer sur votre ordinateur pour autoriser vos comptes, puis configurer GitHub.

Aucun mot de passe, code OAuth ou jeton n'est affiché ni enregistré dans le dépôt.
YouTube : client OAuth Google de type Application pour ordinateur.
Twitch : application avec redirection http://localhost:8765/callback.
"""
import argparse
import base64
import datetime as dt
import getpass
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import urllib.parse
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import HTTP, DeliveryError

YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.readonly']
TWITCH_SCOPES = ['channel:manage:broadcast', 'channel:read:stream_key']


def authorize(provider, client_id, port=8765, timeout=600):
    state = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(64)
    host = '127.0.0.1' if provider == 'youtube' else 'localhost'
    redirect = f'http://{host}:{port}/callback'
    result = {}
    class Callback(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass  # Ne jamais écrire le code OAuth dans un journal HTTP.

        def do_GET(self):
            parsed = urllib.parse.urlsplit(self.path)
            data = urllib.parse.parse_qs(parsed.query)
            if parsed.path != '/callback' or data.get('state', [''])[0] != state:
                self.send_error(400, 'Retour non reconnu')
                return
            result.update(code=data.get('code', [''])[0], error=bool(data.get('error')))
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('Autorisation reçue. Retournez dans le terminal pour terminer la connexion.'.encode())
    params = {'client_id': client_id, 'redirect_uri': redirect, 'response_type': 'code', 'state': state}
    if provider == 'youtube':
        endpoint = 'https://accounts.google.com/o/oauth2/v2/auth'
        params.update(scope=' '.join(YOUTUBE_SCOPES), access_type='offline', prompt='consent',
                      code_challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('='),
                      code_challenge_method='S256')
    else:
        endpoint = 'https://id.twitch.tv/oauth2/authorize'
        params.update(scope=' '.join(TWITCH_SCOPES), force_verify='true')
    url = endpoint + '?' + urllib.parse.urlencode(params)
    with HTTPServer(('127.0.0.1', port), Callback) as server:
        server.timeout = 1
        print('Autorisez votre compte dans le navigateur. Cette étape est nécessaire une fois pour ce raccordement.')
        print('Si le navigateur ne s’ouvre pas, utilisez ce lien sur le même ordinateur :\n' + url)
        webbrowser.open(url)
        deadline = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=timeout)
        while not result and dt.datetime.now(dt.timezone.utc) < deadline:
            server.handle_request()
    if result.get('error') or not result.get('code'):
        raise DeliveryError('Autorisation refusée ou expirée ; aucun calendrier activé.')
    return result['code'], redirect, verifier


def gh(*args, input_value=None):
    try:
        return subprocess.run(['gh', *args], input=input_value, check=True, capture_output=True, text=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise DeliveryError('Configuration GitHub impossible : vérifier gh, les accès au dépôt et le réseau. Aucun secret affiché.') from None


def store(repo, provider, values):
    if not all(values.values()):
        raise DeliveryError('Connexion incomplète ; un identifiant autorisé est absent.')
    names = {row['name'] for row in json.loads(gh('secret', 'list', '--repo', repo, '--json', 'name'))}
    gh('variable', 'set', 'VM_AUTO_' + provider.upper(), '--repo', repo, '--body', 'false')
    if 'VM_DIFFUSION_STATE_KEY' not in names:
        key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        gh('secret', 'set', 'VM_DIFFUSION_STATE_KEY', '--repo', repo, input_value=key)
    for name, value in values.items():
        gh('secret', 'set', name, '--repo', repo, input_value=value)
    # Activer seulement après le succès de toutes les écritures de secrets.
    gh('variable', 'set', 'VM_AUTO_' + provider.upper(), '--repo', repo, '--body', 'true')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('provider', choices=['youtube', 'twitch'])
    parser.add_argument('--client-json', type=Path, help='Fichier OAuth Google téléchargé, conservé hors du dépôt')
    parser.add_argument('--client-id', help='Identifiant public de votre application Twitch')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--repo', default='Velocemercato/velocemercato.fr')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', args.repo):
        raise DeliveryError('Nom du dépôt GitHub invalide.')
    # Vérifier l'accès avant d'ouvrir une autorisation de compte inutile.
    gh('repo', 'view', args.repo, '--json', 'nameWithOwner')
    http = HTTP()
    if args.provider == 'youtube':
        if not args.client_json:
            raise DeliveryError('Indiquer le fichier client Google avec --client-json ; ne pas le déposer dans GitHub.')
        installed = json.loads(args.client_json.read_text()).get('installed', {})
        client_id, client_secret = installed.get('client_id'), installed.get('client_secret')
        if not client_id or not client_secret:
            raise DeliveryError('Un client OAuth Google de type Application pour ordinateur est nécessaire ; un compte de service ne convient pas.')
    else:
        client_id = args.client_id
        if not client_id:
            raise DeliveryError('Indiquer le Client ID public Twitch avec --client-id.')
        client_secret = getpass.getpass('Secret de votre application Twitch (saisie masquée) : ')
        if not client_secret:
            raise DeliveryError('Secret Twitch absent.')
    code, redirect, verifier = authorize(args.provider, client_id, args.port)
    form = {'client_id': client_id, 'client_secret': client_secret, 'code': code,
            'grant_type': 'authorization_code', 'redirect_uri': redirect}
    if args.provider == 'youtube':
        form['code_verifier'] = verifier
        token = http.json('POST', 'https://oauth2.googleapis.com/token', form=form)
        channels = http.json('GET', 'https://www.googleapis.com/youtube/v3/channels?part=id,snippet&mine=true', token.get('access_token')).get('items', [])
        if len(channels) != 1:
            raise DeliveryError('Sélectionner un seul compte de chaîne YouTube dans le parcours Google, puis recommencer.')
        ident, name = channels[0]['id'], channels[0]['snippet']['title']
        values = {'YOUTUBE_CLIENT_ID': client_id, 'YOUTUBE_CLIENT_SECRET': client_secret,
                  'YOUTUBE_REFRESH_TOKEN': token.get('refresh_token'), 'YOUTUBE_CHANNEL_ID': ident}
    else:
        token = http.json('POST', 'https://id.twitch.tv/oauth2/token', form=form)
        if not set(TWITCH_SCOPES).issubset(set(token.get('scope', []))):
            raise DeliveryError('Les deux autorisations Twitch nécessaires n’ont pas été accordées.')
        users = http.json('GET', 'https://api.twitch.tv/helix/users', token.get('access_token'), headers={'Client-Id': client_id}).get('data', [])
        if len(users) != 1:
            raise DeliveryError('Compte Twitch connecté non identifié.')
        ident, name = users[0]['id'], users[0]['display_name']
        values = {'TWITCH_CLIENT_ID': client_id, 'TWITCH_CLIENT_SECRET': client_secret,
                  'TWITCH_REFRESH_TOKEN': token.get('refresh_token'), 'TWITCH_BROADCASTER_ID': ident}
    safe_name = re.sub(r'[\x00-\x1f\x7f]', '', str(name))[:100]
    print('Compte autorisé : ' + safe_name)
    store(args.repo, args.provider, values)
    print('Connexion enregistrée dans les secrets GitHub. Le prochain programme complet pourra utiliser cette plateforme.')
    print('Les journaux et accusés confirmeront les envois ; cette connexion seule ne constitue pas une publication.')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(str(error) if isinstance(error, DeliveryError) else 'Connexion interrompue (' + type(error).__name__ + '). Aucun secret affiché.', file=sys.stderr)
        sys.exit(1)
