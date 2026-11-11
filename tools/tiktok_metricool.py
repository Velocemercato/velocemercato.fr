#!/usr/bin/env python3
"""JT La Pastille TV → TikTok via l'API officielle Metricool (plan avec accès API requis).

Source : les versions verticales déjà produites par « VM - Kit réseaux des JT » (studio/reseaux.json).
Rien n'est modifié dans les robots existants : ce script lit leurs résultats.

Pour chaque JT retenu (univers autorisés, récent, pas encore traité) :
  1. télécharge la verticale, la convertit en 1080x1920 H.264/AAC 30 i/s, la contrôle (ffprobe, son présent) ;
  2. l'héberge sur la branche technique « tiktok » (lien jsDelivr figé par commit, comme le kit réseaux) ;
  3. crée la publication Metricool :
       --mode essai   → BROUILLON Metricool (draft), visibilité SELF_ONLY : rien n'est publié ;
       --mode publier → programmée à +15 min, publique, publication automatique par Metricool.
Garde-fous : un accusé chiffré (branche tiktok-state) est écrit AVANT l'envoi ; un JT déjà tenté n'est jamais
renvoyé ; recherche du même fichier parmi les publications Metricool programmées ; 1 JT par passage par défaut.
« programmé » ≠ « publié » : la confirmation de publication se fait dans Metricool / TikTok.
Secrets attendus (créés par Heineguez) : METRICOOL_USER_TOKEN, METRICOOL_USER_ID, METRICOOL_BLOG_ID.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.diffuser_jt import State, DeliveryError  # noqa: E402

REPO = 'Velocemercato/velocemercato.fr'
API = 'https://app.metricool.com/api'
LIST = ROOT / 'studio/reseaux.json'
JOURNAL = ROOT / 'studio/tiktok.json'
BRANCH, STATE_BRANCH, KEEP = 'tiktok', 'tiktok-state', 20
SOURCE = re.compile(r'^https://cdn\.jsdelivr\.net/gh/Velocemercato/velocemercato\.fr@[0-9a-f]{40}/[a-z0-9-]+-vertical\.mp4$')
PARIS = ZoneInfo('Europe/Paris')
KEY = 'tiktok_metricool'


def note(text):
    print('::notice::' + text, flush=True)


def caption(entry):
    """TikTok via l'API ne gère pas les retours à la ligne : texte sur une ligne, ≤ 2 000 caractères."""
    text = entry.get('texte_vertical') or entry.get('titre', '')
    text = re.sub(r'\s*\n+\s*', ' · ', text.strip())
    if 'velocemercato.fr' not in text:
        text += ' · velocemercato.fr'
    text += ' · JT généré par IA, présentateur virtuel'
    return text[:2000]


def candidates(rows, universes, now, hours=30):
    out = []
    for r in rows:
        if r.get('univers') not in universes or not SOURCE.fullmatch(r.get('verticale', '')):
            continue
        try:
            when = dt.datetime.fromisoformat(str(r.get('date')))
        except ValueError:
            continue
        if when.tzinfo is None:
            when = when.replace(tzinfo=PARIS)
        if dt.timedelta(0) <= now - when <= dt.timedelta(hours=hours):
            out.append(r)
    return sorted(out, key=lambda r: r['date'])


def convert(src, out):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-vf', 'scale=1080:1920:flags=lanczos,fps=30,format=yuv420p',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-profile:v', 'high', '-c:a', 'aac', '-b:a', '128k',
                    '-ar', '48000', '-movflags', '+faststart', str(out)], check=True)
    return check_video(out)


def check_video(path):
    info = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                      'stream=codec_type,codec_name,width,height:format=duration', '-of', 'json', str(path)],
                                     check=True, capture_output=True, text=True).stdout)
    v = next((s for s in info['streams'] if s['codec_type'] == 'video'), {})
    a = next((s for s in info['streams'] if s['codec_type'] == 'audio'), {})
    dur = float(info['format']['duration'])
    problems = []
    if (v.get('codec_name'), v.get('width'), v.get('height')) != ('h264', 1080, 1920):
        problems.append('vidéo non conforme')
    if a.get('codec_name') != 'aac':
        problems.append('son AAC absent')
    if not 3 <= dur <= 600:
        problems.append(f'durée {dur:.0f} s hors limites')
    vol = subprocess.run(['ffmpeg', '-i', str(path), '-af', 'volumedetect', '-vn', '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = re.search(r'max_volume: (-?[0-9.]+) dB', vol)
    if not m or float(m.group(1)) < -60:
        problems.append('son muet')
    if problems:
        raise DeliveryError('Vidéo refusée : ' + ', '.join(problems))
    return round(dur)


class Metricool:
    def __init__(self, token, user_id, blog_id, opener=urllib.request.urlopen):
        if not (token and re.fullmatch(r'\d+', user_id or '') and re.fullmatch(r'\d+', blog_id or '')):
            raise DeliveryError('Metricool non configuré : secrets METRICOOL_USER_TOKEN, METRICOOL_USER_ID, METRICOOL_BLOG_ID requis')
        self.token, self.user, self.blog, self.open = token, user_id, blog_id, opener

    def call(self, method, path, query, body=None):
        url = f'{API}{path}?' + urllib.parse.urlencode(dict(query, userId=self.user, integrationSource='MCP'))
        req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                     headers={'X-Mc-Auth': self.token, 'Content-Type': 'application/json'})
        try:
            with self.open(req, timeout=60) as resp:
                return json.loads(resp.read() or b'{}')
        except urllib.error.HTTPError as err:
            detail = re.sub(r'[A-Za-z0-9_-]{32,}', '…', err.read().decode('utf-8', 'replace'))[:200]
            raise DeliveryError(f'Metricool a refusé (HTTP {err.code}) : {detail}') from None

    def tiktok_connected(self):
        brands = self.call('GET', '/v2/settings/brands', {}).get('data', [])
        brand = next((b for b in brands if str(b.get('id')) == self.blog), None)
        if not brand:
            raise DeliveryError('Marque Metricool introuvable pour METRICOOL_BLOG_ID')
        if 'tiktok' not in json.dumps(brand.get('networksData') or {}).lower():
            raise DeliveryError('TikTok n’est pas connecté à cette marque Metricool')
        return brand.get('label', '?'), brand.get('timezone') or 'Europe/Paris'

    def already_scheduled(self, media_url, timezone):
        today = dt.date.today()
        q = {'blogId': self.blog, 'start': f'{today - dt.timedelta(days=2)}T00:00:00', 'end': f'{today + dt.timedelta(days=7)}T23:59:59',
             'timezone': timezone, 'extendedRange': 'true'}
        return media_url in json.dumps(self.call('GET', '/v2/scheduler/posts', q))

    def schedule(self, text, media_url, when, timezone, draft):
        body = {'autoPublish': not draft, 'draft': draft, 'descendants': [], 'firstCommentText': '', 'hasNotReadNotes': False,
                'media': [media_url], 'mediaAltText': [], 'providers': [{'network': 'tiktok'}],
                'publicationDate': {'dateTime': when.strftime('%Y-%m-%dT%H:%M:%S'), 'timezone': timezone},
                'shortener': False, 'smartLinkData': {'ids': []}, 'text': text,
                'tiktokData': {'disableComment': False, 'disableDuet': False, 'disableStitch': False,
                               'privacyOption': 'SELF_ONLY' if draft else 'PUBLIC_TO_EVERYONE',
                               'commercialContentThirdParty': False, 'commercialContentOwnBrand': False,
                               'title': '', 'autoAddMusic': False, 'photoCoverIndex': 0}}
        result = self.call('POST', '/v2/scheduler/posts', {'blogId': self.blog}, body)
        data = result.get('data', result) if isinstance(result, dict) else {}
        ident = data.get('id') or data.get('uuid') if isinstance(data, dict) else None
        if not ident:
            raise DeliveryError('Metricool n’a renvoyé aucun identifiant de publication')
        return str(ident)


def git(*args, cwd=None):
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def remote():
    token = os.getenv('GITHUB_TOKEN', '')
    return f'https://x-access-token:{token}@github.com/{REPO}.git' if token else f'https://github.com/{REPO}.git'


def host(path):
    """Range la vidéo TikTok sur la branche technique « tiktok » et renvoie son lien jsDelivr figé."""
    with tempfile.TemporaryDirectory(prefix='tiktok-') as folder:
        work = Path(folder) / 'r'
        try:
            git('clone', '--quiet', '--depth', '1', '--branch', BRANCH, remote(), str(work))
        except subprocess.CalledProcessError:
            work.mkdir()
            git('init', '--quiet', cwd=work)
            git('checkout', '--quiet', '--orphan', BRANCH, cwd=work)
            git('remote', 'add', 'origin', remote(), cwd=work)
            (work / 'README.md').write_text('Versions TikTok 1080x1920 des JT. Branche technique gérée par tools/tiktok_metricool.py.\n')
        (work / path.name).write_bytes(path.read_bytes())
        for old in sorted(work.glob('*.mp4'), key=lambda p: p.name, reverse=True)[KEEP:]:
            old.unlink()
        git('add', '-A', cwd=work)
        if git('status', '--porcelain', cwd=work):
            git('-c', 'user.name=github-actions[bot]', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
                'commit', '--quiet', '-m', 'TikTok : version 1080x1920 d’un JT', cwd=work)
            git('push', '--quiet', 'origin', f'HEAD:{BRANCH}', cwd=work)
        return f'https://cdn.jsdelivr.net/gh/{REPO}@{git("rev-parse", "HEAD", cwd=work)}/{path.name}'


def state_saver(path):
    def save():
        folder = path.parent
        git('add', path.name, cwd=folder)
        git('-c', 'user.name=github-actions[bot]', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
            'commit', '--quiet', '--allow-empty', '-m', 'Accusés TikTok chiffrés', cwd=folder)
        git('push', '--quiet', 'origin', f'HEAD:{STATE_BRANCH}', cwd=folder)
    return save


def wait_public(url, attempts=30):
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'VM-TikTok/1'}), timeout=20) as r:
                if r.status == 200 and (r.headers.get('Content-Type') or '').startswith('video/'):
                    return
        except Exception:
            pass
        time.sleep(10)
    raise DeliveryError('Vidéo TikTok non accessible publiquement sur jsDelivr')


def planned_block(now):
    local = now.astimezone(PARIS)
    for hour in (9, 12, 20):
        target = local.replace(hour=hour, minute=0, second=0, microsecond=0)
        if dt.timedelta(minutes=5) <= target - local <= dt.timedelta(minutes=90):
            return target
    return None


def process(state, rows, mode, universes, limit, client_factory, download, convert_fn=convert, host_fn=host,
            wait_fn=wait_public, now=None, planned_at=None):
    now = now or dt.datetime.now(PARIS)
    done = state.data.setdefault(KEY, {})
    journal = []
    def open_(r):
        prev = done.get(r['id'])
        return prev is None or (prev.get('status') == 'echec_avant_envoi' and prev.get('essais', 0) < 3)
    todo = [r for r in candidates(rows, universes, now) if open_(r)][:limit]
    if planned_at:
        # Un nouveau contenu par genre et par bloc ; pas de rediffusion d'un vieux JT.
        available = [r for r in reversed(candidates(rows, universes, now)) if open_(r)]
        todo = []
        for universe in ('foot', 'actus', 'gaming'):
            slot = f'__slot/{planned_at:%Y-%m-%d}/{planned_at.hour:02d}/{universe}'
            if slot in done:
                continue
            row = next((r for r in available if r.get('univers') == universe), None)
            if row:
                todo.append(row)
        todo = todo[:limit]
    if not todo:
        note('Aucun nouveau JT à envoyer vers TikTok.')
        return journal
    client = client_factory()
    label, timezone = client.tiktok_connected()
    note(f'Metricool joignable, TikTok connecté à la marque « {label} »')
    for r in todo:
        key = r['id']
        essais = done.get(key, {}).get('essais', 0) + 1
        done[key] = {'status': 'preparation', 'mode': mode, 'essais': essais}
        state.save()
        sent = False
        try:
            with tempfile.TemporaryDirectory() as tmp:
                src, out = Path(tmp) / 'source.mp4', Path(tmp) / (key + '-tiktok.mp4')
                download(r['verticale'], src)
                secs = convert_fn(src, out)
                media = host_fn(out)
            wait_fn(media)
            draft = mode != 'publier'
            when = planned_at + dt.timedelta(minutes=3 * ('foot','actus','gaming').index(r['univers'])) if planned_at else now + dt.timedelta(minutes=15)
            done[key] = {'status': 'envoi', 'mode': mode, 'essais': essais, 'media': media}  # accusé AVANT l'envoi
            state.save()
            sent = True
            if planned_at:
                done[f'__slot/{planned_at:%Y-%m-%d}/{planned_at.hour:02d}/{r["univers"]}'] = {'status':'envoi','source':key,'heure':when.isoformat()}
                state.save()
            if client.already_scheduled(media, timezone):
                raise DeliveryError('déjà présent dans la programmation Metricool')
            ident = client.schedule(caption(r), media, when, timezone, draft)
            status = 'brouillon' if draft else 'programme'
            done[key] = {'status': status, 'metricool_id': ident, 'media': media, 'duree': secs, 'mode': mode, 'heure': when.isoformat()}
            state.save()
            journal.append({'id': key, 'statut': status, 'metricool_id': ident, 'media': media,
                            'heure': when.isoformat(timespec='minutes')})
            note(('BROUILLON Metricool créé (non publié)' if draft else 'PROGRAMMÉ sur Metricool (publication TikTok à confirmer)')
                 + f' : {key} · id {ident} · {secs} s')
        except Exception as ex:
            reason = (str(ex) if isinstance(ex, DeliveryError) else type(ex).__name__)[:200]
            # Avant l'envoi à Metricool : nouvel essai possible (3 au plus). Après : jamais, pour éviter un doublon.
            done[key] = {'status': 'echec' if sent else 'echec_avant_envoi', 'raison': reason, 'mode': mode, 'essais': essais}
            state.save()
            journal.append({'id': key, 'statut': 'echec', 'raison': reason})
            print(f'::error::TikTok {key} : {reason}', flush=True)
    return journal


def save_journal(rows):
    data = json.loads(JOURNAL.read_text(encoding='utf-8')) if JOURNAL.exists() else []
    seen = {(r['id'], r['statut']) for r in data}
    data = [r for r in rows if (r['id'], r['statut']) not in seen] + data
    JOURNAL.write_text(json.dumps(data[:200], ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def fetch(url, path):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'VM-TikTok/1'}), timeout=120) as r:
        path.write_bytes(r.read())


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--state', required=True, type=Path)
    p.add_argument('--mode', choices=['essai', 'publier'], default='essai')
    p.add_argument('--univers', default=os.getenv('VM_TIKTOK_UNIVERS', 'foot'))
    p.add_argument('--limite', type=int, default=int(os.getenv('VM_TIKTOK_PAR_PASSAGE', '1')))
    a = p.parse_args()
    if a.mode == 'publier' and os.getenv('VM_AUTO_TIKTOK') != 'true':
        raise DeliveryError('Publication TikTok non activée (variable VM_AUTO_TIKTOK) : utiliser le mode essai')
    block = None
    if os.getenv('VM_TIKTOK_PLAN_VM') == 'true' and a.mode == 'publier':
        block = planned_block(dt.datetime.now(PARIS))
        if block is None:
            note('Prochains blocs TikTok : 9 h, 12 h et 20 h Paris. Aucun envoi hors créneau.')
            return
    state = State(a.state, os.getenv('VM_DIFFUSION_STATE_KEY', ''), state_saver(a.state))
    rows = json.loads(LIST.read_text(encoding='utf-8'))
    factory = lambda: Metricool(os.getenv('METRICOOL_USER_TOKEN', ''), os.getenv('METRICOOL_USER_ID', ''), os.getenv('METRICOOL_BLOG_ID', ''))
    journal = process(state, rows, a.mode, set(a.univers.split(',')), max(1, min(a.limite, 3)), factory, fetch, planned_at=block)
    if journal:
        save_journal(journal)
    if any(r['statut'] == 'echec' for r in journal):
        raise DeliveryError('Au moins un envoi TikTok a échoué (voir les erreurs)')


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print('::error::TikTok Metricool : ' + (str(ex) if isinstance(ex, DeliveryError) else type(ex).__name__)[:200], flush=True)
        sys.exit(1)
