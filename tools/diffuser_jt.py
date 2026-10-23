#!/usr/bin/env python3
"""Diffuser un vrai programme HD sur les comptes YouTube/Twitch autorisés.

Les sessions d'upload, jetons renouvelés et accusés restent chiffrés hors du site.
La préparation sans connexion ne contacte aucun compte et ne publie rien.
"""
import argparse
import base64
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pastille_media import probe
from tools.assembler_jt import assemble

UTC = dt.timezone.utc
HOSTS = {'oauth2.googleapis.com', 'www.googleapis.com', 'youtube.googleapis.com', 'id.twitch.tv', 'api.twitch.tv'}
PROVIDERS = {
    'youtube': ['YOUTUBE_CLIENT_ID', 'YOUTUBE_CLIENT_SECRET', 'YOUTUBE_REFRESH_TOKEN', 'YOUTUBE_CHANNEL_ID'],
    'twitch': ['TWITCH_CLIENT_ID', 'TWITCH_CLIENT_SECRET', 'TWITCH_REFRESH_TOKEN', 'TWITCH_BROADCASTER_ID'],
}


class DeliveryError(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None


class HTTP:
    def __init__(self):
        self.opener = urllib.request.build_opener(NoRedirect())

    def request(self, method, url, headers=None, data=None):
        target = urllib.parse.urlsplit(url)
        if target.scheme != 'https' or target.hostname not in HOSTS or target.username or target.password:
            raise DeliveryError('Destination API non autorisée.')
        request = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
        try:
            with self.opener.open(request, timeout=90) as response:
                return response.status, dict(response.headers.items()), response.read()
        except urllib.error.HTTPError as error:
            if error.code == 308:
                return 308, dict(error.headers.items()), error.read()
            # Le corps OAuth et les URL de session ne doivent pas apparaître dans les logs :
            # seul le code d'erreur normalisé (ex. invalid_client) est affiché.
            code = ''
            try:
                err = json.loads(error.read() or b'{}').get('error')
                err = err.get('status') if isinstance(err, dict) else err
                if isinstance(err, str) and re.fullmatch(r'[A-Za-z_]{3,40}', err):
                    code = ' (' + err + ')'
            except Exception:
                pass
            raise DeliveryError(f'API {target.hostname} : HTTP {error.code}{code}.') from None
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            raise DeliveryError(f'API {target.hostname} : connexion interrompue.') from None

    def json(self, method, url, token=None, body=None, form=None, headers=None):
        hdr = dict(headers or {})
        data = None
        if token:
            hdr['Authorization'] = 'Bearer ' + token
        if body is not None:
            data = json.dumps(body).encode()
            hdr['Content-Type'] = 'application/json'
        if form is not None:
            data = urllib.parse.urlencode(form).encode()
            hdr['Content-Type'] = 'application/x-www-form-urlencoded'
        _, _, raw = self.request(method, url, hdr, data)
        return json.loads(raw) if raw else {}


def state_key(raw):
    """Clé de 32 octets : base64 de 32 octets, ou phrase secrète d'au moins 24 caractères (dérivée en SHA-256)."""
    raw = (raw or '').strip()
    try:
        decoded = base64.urlsafe_b64decode(raw)
        if len(decoded) == 32:
            return decoded
    except Exception:
        pass
    if len(raw) >= 24:
        return hashlib.sha256(('VM-diffusion-key:' + raw).encode()).digest()
    raise ValueError('clé trop courte')


class State:
    """AES-GCM : le dépôt public ne reçoit jamais de jeton ni d'URL privée en clair."""
    def __init__(self, path, key, persist=None):
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        try:
            decoded = state_key(key)
        except Exception:
            raise DeliveryError('Clé VM_DIFFUSION_STATE_KEY absente ou invalide.') from None
        self.path, self.cipher, self.persist = Path(path), AESGCM(decoded), persist
        self.data = {'version': 1, 'tokens': {}, 'programmes': {}}
        if self.path.is_file():
            try:
                raw = self.path.read_bytes()
                self.data = json.loads(self.cipher.decrypt(raw[:12], raw[12:], b'VM-diffusion-v1'))
            except Exception:
                raise DeliveryError('État chiffré illisible : conserver la clé existante et ne pas réinitialiser les accusés.') from None

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        nonce = os.urandom(12)
        raw = nonce + self.cipher.encrypt(nonce, json.dumps(self.data).encode(), b'VM-diffusion-v1')
        temporary = self.path.with_suffix('.tmp')
        temporary.write_bytes(raw)
        temporary.chmod(0o600)
        temporary.replace(self.path)
        if self.persist:
            self.persist()


def git_save(path):
    def git(*args):
        subprocess.run(['git', '-c', 'credential.helper=!gh auth git-credential', *args],
                       cwd=Path(path).parent, check=True, capture_output=True)
    git('add', Path(path).name)
    git('-c', 'user.name=github-actions[bot]', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
        'commit', '--quiet', '-m', 'Accusés de diffusion chiffrés')
    git('push', '--quiet', 'origin', 'HEAD:broadcast-state')


def public_allowed():
    """Passage en public automatique seulement si le propriétaire l'a explicitement autorisé (VM_YOUTUBE_PUBLIC=true)."""
    return os.getenv('VM_YOUTUBE_PUBLIC') == 'true'


def enabled(provider):
    return os.getenv('VM_AUTO_' + provider.upper()) == 'true' and all(os.getenv(name, '').strip() for name in PROVIDERS[provider])


YOUTUBE_PUBLIC_CLIENT_ID = '143768939550-tfgsm898rp33c6rbs49t75hv7a9i1his.apps.googleusercontent.com'


def clean_credential(provider, kind, value):
    """Tolère un copier-coller imparfait depuis un téléphone (texte autour, JSON complet du Terrain de jeu OAuth)."""
    value = (value or '').strip()
    if provider == 'youtube' and kind == 'REFRESH_TOKEN':
        match = re.search(r'1//[A-Za-z0-9_\-]{20,}', value)
        return match.group(0) if match else value
    if provider == 'youtube' and kind == 'CLIENT_ID':
        match = re.search(r'\d{6,}-[a-z0-9]+\.apps\.googleusercontent\.com', value)
        return match.group(0) if match else YOUTUBE_PUBLIC_CLIENT_ID  # l'ID client est public
    return value


def access_token(provider, state, http):
    prefix = provider.upper()
    initial = clean_credential(provider, 'REFRESH_TOKEN', os.environ[prefix + '_REFRESH_TOKEN'])
    client = clean_credential(provider, 'CLIENT_ID', os.environ[prefix + '_CLIENT_ID'])
    fingerprint = hashlib.sha256((client + initial).encode()).hexdigest()
    stored = state.data['tokens'].get(provider, {})
    refresh = stored.get('refresh') if stored.get('fingerprint') == fingerprint else initial
    form = {'client_id': client, 'client_secret': os.environ[prefix + '_CLIENT_SECRET'].strip(),
            'grant_type': 'refresh_token', 'refresh_token': refresh}
    endpoint = 'https://oauth2.googleapis.com/token' if provider == 'youtube' else 'https://id.twitch.tv/oauth2/token'
    result = http.json('POST', endpoint, form=form)
    token = result.get('access_token')
    if not token:
        raise DeliveryError(f'{provider} : renouvellement OAuth non confirmé.')
    state.data['tokens'][provider] = {'refresh': result.get('refresh_token', refresh), 'fingerprint': fingerprint}
    state.save()  # Conserver immédiatement un éventuel refresh token renouvelé.
    return token


def youtube_metadata(manifest):
    names = {'matin': 'du matin', 'midi': 'du midi', 'soir': 'du soir'}
    date = dt.date.fromisoformat(manifest['date']).strftime('%d/%m/%Y')
    if manifest.get('format') in ('speciale', 'debat'):
        label = 'Spéciale avant-match' if manifest['format'] == 'speciale' else 'Le débat du soir'
        title = f'Véloce Mercato — {label} — {date}'
    else:
        title = f'VM Univers — Le grand JT {names[manifest["moment"]]} — {date}'
    def clock(seconds):
        seconds = int(seconds)
        return f'{seconds//3600:02}:{seconds//60%60:02}:{seconds%60:02}' if seconds >= 3600 else f'{seconds//60:02}:{seconds%60:02}'
    description = ('Programme enregistré et généré par IA, avec des personnages inventés.\n'
                   'Actualités issues des brèves sourcées des médias VM.\n\n' +
                   '\n'.join(clock(row['debut_secondes']) + ' ' + row['titre'] for row in manifest['chapitres']) +
                   '\n\nSources et articles :\nhttps://velocemercato.fr/\nhttps://velocemercato.fr/actus/\n'
                   'https://velocemercato.fr/vm-gaming/\nTous nos projets : https://vmunivers.fr/\n')
    return {'snippet': {'title': title[:100], 'description': description[:4900], 'categoryId': '25', 'defaultLanguage': 'fr'},
            'status': {'privacyStatus': 'private', 'selfDeclaredMadeForKids': False, 'containsSyntheticMedia': True}}


class YouTube:
    def __init__(self, http, state, token):
        self.http, self.state, self.token = http, state, token

    def verify_channel(self):
        result = self.http.json('GET', 'https://www.googleapis.com/youtube/v3/channels?part=id,snippet&mine=true', self.token)
        rows = result.get('items', [])
        found = re.search(r'UC[A-Za-z0-9_-]{22}', os.environ.get('YOUTUBE_CHANNEL_ID', ''))
        expected = found.group(0) if found else ''
        if expected not in [row['id'] for row in rows]:
            names = ', '.join(re.sub(r'[\x00-\x1f]', '', r.get('snippet', {}).get('title', '?'))[:60] + ' (' + r['id'] + ')' for r in rows) or 'aucune chaîne'
            # Identifiants de chaînes publics : affichés pour corriger la configuration.
            raise DeliveryError(f'YouTube : la chaîne autorisée est {names}, mais YOUTUBE_CHANNEL_ID indique {expected or "un texte sans UC…"}.')

    def upload(self, file, metadata, receipt, chunk_size=8*1024*1024):
        file = Path(file)
        total = file.stat().st_size
        if receipt.get('video_id'):
            return receipt['video_id']
        if not receipt.get('session'):
            if receipt.get('status') == 'uploading':
                raise DeliveryError('Session YouTube non confirmée : vérifier avant de créer une autre vidéo.')
            receipt['status'] = 'uploading'
            self.state.save()
            _, headers, _ = self.http.request('POST', 'https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',
                {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json',
                 'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(total)}, json.dumps(metadata).encode())
            session = next((v for k, v in headers.items() if k.lower() == 'location'), '')
            target = urllib.parse.urlsplit(session)
            if target.scheme != 'https' or target.hostname != 'www.googleapis.com' or target.username or target.password:
                raise DeliveryError('Session YouTube absente ou non autorisée.')
            receipt['session'] = session
            self.state.save()
        session = receipt['session']
        def accept(status, headers, body):
            if status in (200, 201):
                ident = json.loads(body).get('id', '')
                if not re.fullmatch(r'[A-Za-z0-9_-]{11}', ident):
                    raise DeliveryError('YouTube : identifiant vidéo absent de la confirmation.')
                receipt.update(video_id=ident, status='private')
                receipt.pop('session', None)
                self.state.save()
                return total, ident
            if status != 308:
                raise DeliveryError('YouTube : réponse de reprise inattendue.')
            received = next((v for k, v in headers.items() if k.lower() == 'range'), '')
            match = re.fullmatch(r'bytes=0-(\d+)', received)
            return (int(match.group(1)) + 1 if match else 0), None
        offset, ident = accept(*self.http.request('PUT', session,
            {'Authorization': 'Bearer ' + self.token, 'Content-Length': '0', 'Content-Range': f'bytes */{total}'}, b''))
        if ident:
            return ident
        failures = 0
        with file.open('rb') as stream:
            while offset < total:
                stream.seek(offset)
                chunk = stream.read(chunk_size)
                try:
                    result = self.http.request('PUT', session,
                        {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'video/mp4',
                         'Content-Range': f'bytes {offset}-{offset+len(chunk)-1}/{total}'}, chunk)
                    following, ident = accept(*result)
                    if ident:
                        return ident
                    if not offset < following <= total:
                        raise DeliveryError('YouTube : aucun progrès confirmé de l’upload.')
                    offset, failures = following, 0
                except DeliveryError:
                    failures += 1
                    if failures > 3:
                        raise
                    time.sleep(min(2**failures, 8))
                    offset, ident = accept(*self.http.request('PUT', session,
                        {'Authorization': 'Bearer ' + self.token, 'Content-Length': '0', 'Content-Range': f'bytes */{total}'}, b''))
                    if ident:
                        return ident
        raise DeliveryError('YouTube : fin de transfert non confirmée, conserver la session pour reprise.')

    def make_public(self, receipt, timeout=600):
        ident = receipt['video_id']
        deadline = time.monotonic() + timeout
        while True:
            data = self.http.json('GET', 'https://www.googleapis.com/youtube/v3/videos?part=status,processingDetails&id=' + ident, self.token)
            row = next(iter(data.get('items', [])), {})
            status = row.get('status', {})
            processing = row.get('processingDetails', {}).get('processingStatus')
            if status.get('uploadStatus') in ('failed', 'rejected', 'deleted') or processing in ('failed', 'terminated'):
                raise DeliveryError('YouTube : traitement refusé ; la vidéo ne sera pas annoncée publique.')
            if processing == 'succeeded':
                break
            if time.monotonic() >= deadline:
                raise DeliveryError('YouTube : traitement encore en cours ; la vidéo reste privée.')
            time.sleep(15)
        self.http.json('PUT', 'https://www.googleapis.com/youtube/v3/videos?part=status', self.token,
            body={'id': ident, 'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False, 'containsSyntheticMedia': True}})
        check = self.http.json('GET', 'https://www.googleapis.com/youtube/v3/videos?part=status&id=' + ident, self.token)
        if not any(row.get('id') == ident and row.get('status', {}).get('privacyStatus') == 'public' for row in check.get('items', [])):
            raise DeliveryError('YouTube : visibilité publique non confirmée.')
        receipt.update(status='published', url='https://www.youtube.com/watch?v=' + ident)
        self.state.save()


class Twitch:
    def __init__(self, http, state, token):
        self.http, self.state, self.token = http, state, token
        self.user = os.environ['TWITCH_BROADCASTER_ID']
        if not self.user.isdigit():
            raise DeliveryError('Identifiant Twitch invalide.')

    def api(self, method, path, body=None):
        return self.http.json(method, 'https://api.twitch.tv/helix/' + path, self.token,
                              body=body, headers={'Client-Id': os.environ['TWITCH_CLIENT_ID']})

    def stream(self, file, title, receipt, duration):
        if receipt.get('status') in ('starting', 'live', 'ended', 'skipped_live'):
            if receipt['status'] in ('starting', 'live'):
                raise DeliveryError('Twitch : diffusion précédente incertaine, vérifier la chaîne avant de reprendre.')
            return
        users = self.api('GET', 'users').get('data', [])
        user = next((u for u in users if u.get('id') == self.user), None)
        if not user:
            raise DeliveryError('Twitch : le compte connecté ne correspond pas à la chaîne autorisée.')
        if self.api('GET', 'streams?user_id=' + self.user).get('data'):
            receipt['status'] = 'skipped_live'
            self.state.save()
            return  # Préserver un direct déjà lancé par le propriétaire.
        self.api('PATCH', 'channels?broadcaster_id=' + self.user,
                 {'title': (title[:100] + ' · programme enregistré · IA')[:140], 'broadcaster_language': 'fr', 'game_id': '509658'})
        keys = self.api('GET', 'streams/key?broadcaster_id=' + self.user).get('data', [])
        key = next(iter(keys), {}).get('stream_key', '')
        if not re.fullmatch(r'[A-Za-z0-9_-]+', key):
            raise DeliveryError('Twitch : clé de diffusion non disponible.')
        destination = 'rtmp://live.twitch.tv/app/' + key
        receipt['status'] = 'starting'
        self.state.save()
        command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-re', '-i', str(file),
                   '-map', '0:v:0', '-map', '0:a:0', '-c:v', 'libx264', '-threads', '2', '-preset', 'veryfast',
                   '-pix_fmt', 'yuv420p', '-r', '30', '-b:v', '2500k', '-maxrate', '2500k', '-bufsize', '5000k',
                   '-g', '60', '-keyint_min', '60', '-sc_threshold', '0', '-c:a', 'aac', '-b:a', '128k',
                   '-ar', '48000', '-ac', '2', '-f', 'flv', '-flvflags', 'no_duration_filesize', destination]
        # Les erreurs ffmpeg peuvent contenir la destination et sa clé : ne jamais les journaliser.
        try:
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            raise DeliveryError('Twitch : outil de diffusion indisponible, aucun démarrage confirmé.') from None
        try:
            confirmed = False
            for _ in range(12):
                if process.poll() is not None:
                    break
                if self.api('GET', 'streams?user_id=' + self.user).get('data'):
                    confirmed = True
                    break
                time.sleep(5)
            if not confirmed:
                raise DeliveryError('Twitch : démarrage du direct non confirmé.')
            receipt.update(status='live', url='https://www.twitch.tv/' + user['login'])
            self.state.save()
            try:
                finished = process.wait(timeout=duration + 180)
            except subprocess.TimeoutExpired:
                raise DeliveryError('Twitch : délai de fin dépassé ; vérifier le canal avant toute reprise.') from None
            if finished != 0:
                raise DeliveryError('Twitch : flux interrompu avant sa fin.')
            receipt['status'] = 'ended'
            self.state.save()
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


def prepare(masters, output, now=None, expected_run=None):
    masters, output = Path(masters), Path(output)
    authorization = json.loads((masters / '_autorisation.json').read_text())
    now = now or dt.datetime.now(UTC)
    created = dt.datetime.fromisoformat(authorization['created'])
    if (authorization.get('publish') is not True or created.tzinfo is None
            or not dt.timedelta(0) <= now - created <= dt.timedelta(hours=3)
            or (expected_run and str(authorization.get('run_id')) != str(expected_run))):
        raise DeliveryError('Programme non autorisé, trop ancien ou provenant d’un autre lancement.')
    date, moment = authorization['date'], authorization['moment']
    if moment not in ('matin', 'midi', 'soir') or date != now.astimezone(ZoneInfo('Europe/Paris')).date().isoformat():
        raise DeliveryError('Créneau de diffusion invalide.')
    kind = authorization.get('format', 'edition')
    if kind in ('speciale', 'debat'):
        ident = authorization.get('unit', '')
        if not re.fullmatch(r'[a-z0-9-]+', ident):
            raise DeliveryError('Identifiant de spéciale/débat invalide.')
        row = json.loads((masters / (ident + '.json')).read_text())
        if row.get('id') != ident or row.get('format') != kind or row.get('univers') != 'foot' or row.get('date', '')[:10] != date:
            raise DeliveryError('Spéciale/débat non cohérent avec l’autorisation de production.')
        source = masters / (ident + '.mp4')
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, output)
        result = {'date':date, 'moment':moment, 'format':kind, 'universes':['foot'], 'id':ident,
                  'duree_mesuree':float(probe(output)['format']['duration']),
                  'chapitres':[{'debut_secondes':0, 'univers':'foot', 'titre':row['titre'], 'id':ident}]}
    elif kind == 'edition':
        result = assemble(ROOT, moment, date, output, masters)
        result.update(format='edition', universes=['foot','actus','gaming'], id='jt-' + date + '-' + moment)
    else:
        raise DeliveryError('Format de programme non autorisé.')
    info = probe(output)
    video = next(row for row in info['streams'] if row['codec_type'] == 'video')
    if video['codec_name'] != 'h264' or video['width'] < 1280 or video['height'] < 720 or video['avg_frame_rate'] not in ('24/1', '25/1', '30/1'):
        raise DeliveryError('Le programme long nécessite les vrais originaux HD ; aucun ancien fichier comprimé substitué.')
    return result


def publish(file, manifest, state, http=None):
    http = http or HTTP()
    receipts = state.data['programmes'].setdefault(manifest['id'], {})
    errors = []
    for provider in ('youtube', 'twitch'):
        if not enabled(provider):
            continue
        receipt = receipts.setdefault(provider, {})
        if receipt.get('status') in ('published', 'ended', 'skipped_live'):
            continue
        if provider == 'youtube' and receipt.get('status') == 'private_ready' and not public_allowed():
            continue
        try:
            token = access_token(provider, state, http)
            if provider == 'youtube':
                client = YouTube(http, state, token)
                client.verify_channel()
                client.upload(file, youtube_metadata(manifest), receipt)
                if public_allowed():
                    client.make_public(receipt)
                else:
                    # Accord du propriétaire requis : la vidéo reste PRIVÉE, visible seulement dans YouTube Studio.
                    receipt['status'] = 'private_ready'
                    state.save()
            else:
                Twitch(http, state, token).stream(file, youtube_metadata(manifest)['snippet']['title'], receipt, manifest['duree_mesuree'])
        except DeliveryError as error:
            errors.append(str(error))
    return receipts, errors


def public_index(path, manifest, receipts):
    path = Path(path)
    rows = json.loads(path.read_text()) if path.is_file() else []
    public = {}
    for provider, receipt in receipts.items():
        if receipt.get('status') in ('published', 'ended') and receipt.get('url'):
            public[provider] = {'url': receipt['url'], 'status': receipt['status']}
    if public:
        row = {'id': manifest['id'], 'date': manifest['date'], 'moment': manifest['moment'],
               'universes':manifest.get('universes', ['foot','actus','gaming']),
               'date_publication': dt.datetime.now(UTC).isoformat(timespec='seconds'),
               'titre': youtube_metadata(manifest)['snippet']['title'], 'plateformes': public}
        rows = [r for r in rows if r['id'] != row['id']] + [row]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(sorted(rows, key=lambda r: (r.get('date_publication', r.get('date','')), r['id']), reverse=True)[:90], ensure_ascii=False, indent=1) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--masters', type=Path)
    parser.add_argument('--state', type=Path)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--git-state', action='store_true')
    args = parser.parse_args()
    active = [provider for provider in PROVIDERS if enabled(provider)]
    if args.check:
        try:
            valid_key = len(state_key(os.getenv('VM_DIFFUSION_STATE_KEY', ''))) == 32
        except Exception:
            valid_key = False
        print(json.dumps({'ready': bool(active) and valid_key, 'providers': active}))
        return
    if not active:
        print('YouTube/Twitch : aucun compte autorisé configuré, aucune diffusion.')
        return
    if (os.getenv('GITHUB_ACTIONS') != 'true' or os.getenv('GITHUB_REF') != 'refs/heads/main'
            or not args.masters or not args.state or not args.git_state):
        raise DeliveryError('Diffusion disponible sur main avec les accusés persistants configurés.')
    output = ROOT / 'studio/tmp/diffusion/programme.mp4'
    manifest = prepare(args.masters, output, expected_run=os.getenv('SOURCE_RUN_ID'))
    state = State(args.state, os.getenv('VM_DIFFUSION_STATE_KEY', ''), lambda: git_save(args.state))
    receipts, errors = publish(output, manifest, state)
    public_index(ROOT / 'studio/diffusions.json', manifest, receipts)
    for provider, receipt in receipts.items():
        print(provider + ' : ' + receipt.get('status', 'non confirmé'))
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        raise DeliveryError('Au moins une diffusion reste non confirmée ; les accusés sont conservés.')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Les exceptions réseau/sous-processus peuvent inclure des secrets : message contrôlé seulement.
        print(str(error) if isinstance(error, DeliveryError) else 'Diffusion interrompue (' + type(error).__name__ + '). Aucun succès annoncé.', file=sys.stderr)
        sys.exit(1)
