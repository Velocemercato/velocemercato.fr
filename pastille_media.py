"""Rendu local et contrôles des médias Pastille, sans publication implicite."""
import json
import os
from pathlib import Path
import re
import subprocess

INTRO_SECONDS = 0.8
OUTRO_SECONDS = 5.0
GAP_SECONDS = 0.12
CDN_MAX_BYTES = 20_000_000
CDN_PACKAGE_BYTES = 150_000_000


def speech_rate():
    value = float(os.getenv('VM_SPEECH_RATE', '1.12'))
    if not 1.0 <= value <= 1.35:
        raise ValueError('VM_SPEECH_RATE doit être compris entre 1 et 1.35.')
    return value


def spoken_text(text):
    # Faciliter la lecture des sigles, sans modifier les faits ni les chiffres.
    names = {'PSG': 'Paris Saint-Germain', 'OM': 'Olympique de Marseille',
             'UEFA': 'U E F A', 'GTA': 'G T A', 'EA': 'E A'}
    text = re.sub(r'\b(?:PSG|OM|UEFA|GTA|EA)\b', lambda match: names[match.group()], text)
    return re.sub(r'\s+', ' ', text.replace('…', '. ').replace('’', "'")).strip()


def publication_enabled():
    return (os.getenv('VM_PUBLISH') == '1' and os.getenv('GITHUB_ACTIONS') == 'true'
            and os.getenv('GITHUB_REF') == 'refs/heads/main')


def video_profile():
    value = os.getenv('VM_VIDEO_PROFILE', 'auto')
    if value == 'auto':
        return 'cdn' if publication_enabled() else 'hd'
    if value not in ('cdn', 'hd'):
        raise ValueError('VM_VIDEO_PROFILE doit être auto, cdn ou hd.')
    if value == 'hd' and publication_enabled():
        raise RuntimeError('Le rendu HD long nécessite un hébergement vidéo connecté. Utiliser un aperçu HD sans publication.')
    return value


def encode_video(folder, output, total, music):
    """Conserve le profil CDN en production ; HD explicite pour les aperçus longs."""
    return _encode(folder, output, total, music, video_profile() == 'hd')


def encode_hd_master(folder, output, total, music):
    """Rendu local conservé pour YouTube/Twitch ; aucun envoi au transport CDN."""
    return _encode(folder, output, total, music, True)


def _encode(folder, output, total, music, hd):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        'ffmpeg', '-v', 'error', '-y', '-filter_complex_threads', '1',
        '-f', 'concat', '-safe', '0', '-i', str(folder / 'images.txt'),
        '-i', str(folder / 'voix.wav'), '-stream_loop', '-1', '-i', str(music),
        '-filter_complex',
        '[1:a]highpass=f=65,apad[v];[2:a]volume=0.035[m];'
        '[v][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=9[a]',
        '-map', '0:v', '-map', '[a]', '-t', f'{total:.3f}',
        '-r', '24' if hd else '12', '-c:v', 'libx264', '-threads', '2', '-preset', 'medium' if hd else 'veryfast',
        '-tune', 'stillimage', '-crf', '22' if hd else '31', '-maxrate', '1800k' if hd else '600k', '-bufsize', '3600k' if hd else '1200k',
        '-profile:v', 'high', '-level', '3.1', '-g', '48' if hd else '24', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '96k' if hd else '56k', '-ar', '48000', '-ac', '1',
        '-movflags', '+faststart', str(output)
    ], check=True)
    # La radio n'a pas besoin de télécharger la piste vidéo.
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(output), '-vn',
                    '-c:a', 'copy', '-movflags', '+faststart', str(output.with_suffix('.m4a'))], check=True)
    return probe(output)


def probe(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams',
                             '-of', 'json', str(path)], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def validate_cdn_files(files):
    for path in map(Path, files):
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f'Média absent ou vide : {path.name}')
        if path.stat().st_size >= CDN_MAX_BYTES:
            raise RuntimeError(f'{path.name} dépasse la limite jsDelivr de 20 Mo. '
                               'Utiliser un hébergeur vidéo adapté ; ne pas dégrader silencieusement la qualité.')


def validate_cdn_package(folder):
    total = sum(path.stat().st_size for path in Path(folder).rglob('*')
                if path.is_file() and '.git' not in path.relative_to(folder).parts)
    if total >= CDN_PACKAGE_BYTES:
        raise RuntimeError('Le lot de médias dépasse la limite GitHub/jsDelivr de 150 Mo. Utiliser un hébergeur vidéo adapté.')


def prune_cdn_package(folder, protected, keep=24):
    """Limiter le dernier instantané ; les versions précédentes restent dans l'historique Git."""
    folder = Path(folder)
    videos = sorted(folder.glob('*.mp4'), key=lambda path: path.name[-17:], reverse=True)
    for index, old in enumerate(videos):
        if old.name == protected:
            continue
        if index >= keep:
            for suffix in ('.mp4', '.jpg', '.m4a'):
                old.with_suffix(suffix).unlink(missing_ok=True)
    for old in reversed(videos):
        try:
            validate_cdn_package(folder)
            return
        except RuntimeError:
            if old.name != protected:
                for suffix in ('.mp4', '.jpg', '.m4a'):
                    old.with_suffix(suffix).unlink(missing_ok=True)
    validate_cdn_package(folder)
