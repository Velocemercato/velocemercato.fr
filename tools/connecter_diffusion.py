#!/usr/bin/env python3
"""Autoriser vos comptes sur ordinateur ou depuis Chrome avec GitHub Codespaces.

Aucun mot de passe, code OAuth ou jeton n'est affiché ni enregistré dans le dépôt.
YouTube : client OAuth Google de type Application pour ordinateur.
Twitch : application avec redirection locale, ou HTTPS dans Codespaces.
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

# videos.insert accepte upload ; videos.update (passage du privé au public)
# exige youtube.force-ssl. Les anciens jetons doivent être reconnectés une fois.
YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.readonly',
                  'https://www.googleapis.com/auth/youtube.force-ssl']
TWITCH_SCOPES = ['channel:manage:broadcast', 'channel:read:stream_key']


def codespace_redirect(port=8765):
    name = os.getenv('CODESPACE_NAME', '')
    if not re.fullmatch(r'[a-z0-9-]{3,100}', name) or not 1 <= port <= 65535:
        raise DeliveryError('Ouvrir ce dépôt dans votre GitHub Codespace avant d’utiliser le mode Android.')
    return f'https://{name}-{port}.app.github.dev/callback'


def authorize(provider, client_id, port=8765, timeout=600, redirect_uri=None):
    state = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(64)
    host = '127.0.0.1' if provider == 'youtube' else 'localhost'
    redirect = redirect_uri or f'http://{host}:{port}/callback'
    if redirect_uri:
        target = urllib.parse.urlsplit(redirect_uri)
        if (target.scheme != 'https' or not re.fullmatch(r'[a-z0-9-]+\.app\.github\.dev', target.netloc)
                or target.path != '/callback' or target.query or target.fragment or target.username):
            raise DeliveryError('Le retour distant doit être l’adresse HTTPS de votre Codespace.')
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
    with HTTPServer(('0.0.0.0' if redirect_uri else '127.0.0.1', port), Callback) as server:
        server.timeout = 1
        print('Autorisez votre compte dans le navigateur. Cette étape est nécessaire une fois pour ce raccordement.')
        print('Ouvrez ce lien dans Chrome :\n' + url)
        if not redirect_uri:
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
    if provider == 'youtube':
        # Par défaut : envois en PRIVÉ uniquement. Le passage public demande l'accord du propriétaire.
        variables = {row['name'] for row in json.loads(gh('variable', 'list', '--repo', repo, '--json', 'name'))}
        if 'VM_YOUTUBE_PUBLIC' not in variables:
            gh('variable', 'set', 'VM_YOUTUBE_PUBLIC', '--repo', repo, '--body', 'false')
    # Activer seulement après le succès de toutes les écritures de secrets.
    gh('variable', 'set', 'VM_AUTO_' + provider.upper(), '--repo', repo, '--body', 'true')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('provider', choices=['youtube', 'twitch'])
    parser.add_argument('--client-json', type=Path, help='Fichier OAuth Google téléchargé, conservé hors du dépôt')
    parser.add_argument('--client-id', help='Identifiant public de votre application Google ou Twitch')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--codespaces', action='store_true', help='Connexion HTTPS depuis Chrome, y compris Android')
    parser.add_argument('--adresse', action='store_true', help='Afficher uniquement l’adresse de retour à enregistrer')
    parser.add_argument('--repo', default='Velocemercato/velocemercato.fr')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', args.repo):
        raise DeliveryError('Nom du dépôt GitHub invalide.')
    redirect_uri = codespace_redirect(args.port) if args.codespaces else None
    if args.adresse:
        if not redirect_uri:
            raise DeliveryError('Utiliser --codespaces --adresse depuis votre espace GitHub.')
        print(redirect_uri)
        return
    # Vérifier l'accès (y compris le droit d'écrire les secrets) avant d'ouvrir une autorisation de compte inutile.
    gh('repo', 'view', args.repo, '--json', 'nameWithOwner')
    try:
        gh('secret', 'list', '--repo', args.repo, '--json', 'name')
    except DeliveryError:
        raise DeliveryError('GitHub refuse la gestion des secrets. Dans le terminal, taper : unset GITHUB_TOKEN puis gh auth login '
                            '(compte Velocemercato), puis relancer cette commande. Aucun secret affiché.') from None
    http = HTTP()
    if args.provider == 'youtube':
        if args.client_json:
            document = json.loads(args.client_json.read_text())
            client = document.get('web' if args.codespaces else 'installed', {})
            client_id, client_secret = client.get('client_id'), client.get('client_secret')
            if args.codespaces and redirect_uri not in client.get('redirect_uris', []):
                raise DeliveryError('Enregistrer l’adresse de retour Codespaces dans le client Web Google et télécharger le JSON actualisé.')
        elif args.codespaces and args.client_id:
            client_id = args.client_id
            client_secret = getpass.getpass('Secret du client Web Google (saisie masquée) : ')
        else:
            raise DeliveryError('Sur ordinateur : --client-json. Dans Codespaces/Android : --codespaces --client-id avec un client Web Google.')
        if not client_id or not client_secret:
            raise DeliveryError('Client OAuth Google incomplet ; un compte de service ne convient pas.')
    else:
        client_id = args.client_id
        if not client_id:
            raise DeliveryError('Indiquer le Client ID public Twitch avec --client-id.')
        client_secret = getpass.getpass('Secret de votre application Twitch (saisie masquée) : ')
        if not client_secret:
            raise DeliveryError('Secret Twitch absent.')
    code, redirect, verifier = authorize(args.provider, client_id, args.port, redirect_uri=redirect_uri)
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
    if args.provider == 'youtube':
        print('Les vidéos seront envoyées en PRIVÉ : rien n’est publié sans votre accord (variable VM_YOUTUBE_PUBLIC).')
    print('Les journaux et accusés confirmeront les envois ; cette connexion seule ne constitue pas une publication.')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(str(error) if isinstance(error, DeliveryError) else 'Connexion interrompue (' + type(error).__name__ + '). Aucun secret affiché.', file=sys.stderr)
        sys.exit(1)
