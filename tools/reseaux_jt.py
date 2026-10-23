#!/usr/bin/env python3
"""Kit réseaux sociaux des JT : version verticale courte + texte prêt à coller.

Après chaque émission publiée, ce robot :
- télécharge le JT horizontal déjà publié ;
- fabrique une version verticale 9:16 de moins d'une minute (TikTok, Reels, Shorts) ;
- rédige le texte de publication (sans appel IA, à partir du titre et de l'accroche) ;
- range les vidéos verticales sur la branche technique « reseaux » ;
- met à jour studio/reseaux.json, lu par la page studio/reseaux.html.

Usage local (sans publication) : python tools/reseaux_jt.py --local DOSSIER --sortie DOSSIER
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REPO = 'Velocemercato/velocemercato.fr'
BRANCH = 'reseaux'
LIST = ROOT / 'studio/reseaux.json'
EMISSIONS = ROOT / 'studio/emissions.json'
FONT_BOLD = ROOT / 'studio/assets/Poppins-BoldItalic.ttf'
FONT_TEXT = ROOT / 'studio/assets/Poppins-Medium.ttf'
W, H = 720, 1280
MAX_SECONDS = 58
KEEP_VIDEOS = 12
KEEP_ENTRIES = 30

UNIVERS = {
    'foot': {'nom': 'La Pastille Foot', 'couleur': (244, 207, 85), 'emoji': '⚽', 'lien': 'velocemercato.fr',
             'tags': '#foot #football #mercato #ligue1 #actufoot #velocemercato',
             'questions': ['Dis-moi en commentaire ton match à ne pas rater 👇', 'Ton pronostic pour ce week-end ? 👇',
                           'Le transfert qui te fait rêver en ce moment ? 👇', 'Tu valides ou pas ? Dis-le en commentaire 👇']},
    'actus': {'nom': 'La Pastille Actus', 'couleur': (255, 90, 110), 'emoji': '📰', 'lien': 'velocemercato.fr/actus',
              'tags': '#actualite #info #journal #france #monde #vmactus',
              'questions': ['Partage à quelqu’un qui n’a pas eu le temps de suivre l’actu 🙏', 'Quelle info t’a le plus marqué aujourd’hui ? 👇',
                            'Abonne-toi pour ne rater aucun JT 🔔', 'Ton avis en commentaire 👇']},
    'gaming': {'nom': 'La Pastille Gaming', 'couleur': (214, 255, 110), 'emoji': '🎮', 'lien': 'velocemercato.fr/vm-gaming',
               'tags': '#gaming #jeuxvideo #gamer #playstation #xbox #nintendo #vmgaming',
               'questions': ['Tu joues à quoi en ce moment ? 👇', 'Le jeu que tu attends le plus ? 👇',
                             'Team PlayStation, Xbox ou Switch ? 👇', 'Dis-moi ce que tu en penses en commentaire 👇']},
}
ACCROCHES = {'matin': 'Bien réveillé ? Le JT du matin est là', 'midi': 'Le JT du midi est là', 'soir': 'Le JT du soir est là',
             'express': 'JT express'}


def pick(options, key):
    return options[int(hashlib.sha1(key.encode()).hexdigest(), 16) % len(options)]


def caption(entry):
    """Texte prêt à coller : un ton perso, une question pour faire réagir, le lien et les hashtags."""
    u = UNIVERS.get(entry.get('univers'), UNIVERS['actus'])
    intro = ACCROCHES.get(entry.get('moment'), 'Le nouveau JT est là')
    minutes = max(1, round(int(entry.get('duree') or 0) / 60))
    question = pick(u['questions'], entry['id'])
    long = (f"{intro} {u['emoji']}⚡\n{entry.get('accroche', '').strip()}\n\n"
            f"En {minutes} minute{'s' if minutes > 1 else ''}, t’es à jour 💪\n{question}\n\n"
            f"Toute l’actu sur {u['lien']}\n\n{u['tags']}")
    court = (f"{intro} {u['emoji']}⚡\n{entry.get('accroche', '').strip()}\n\n"
             f"Le JT complet ({minutes} min) est sur {u['lien']} 🔗 lien en bio\n{question}\n\n{u['tags']}")
    return long, court


def font(path, size):
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()


def overlay(entry, path):
    """Bandeau du haut (émission + titre) et bas (lien), dessinés sur un calque transparent."""
    u = UNIVERS.get(entry.get('univers'), UNIVERS['actus'])
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    badge = font(FONT_BOLD, 34)
    label = u['nom'].upper()
    bw = d.textlength(label, font=badge) + 40
    d.rounded_rectangle((36, 70, 36 + bw, 128), radius=14, fill=u['couleur'] + (255,), outline=(0, 0, 0, 255), width=4)
    d.text((56, 76), label, font=badge, fill=(4, 6, 15, 255))
    date = entry.get('label', '') + ' · ' + str(entry.get('date', ''))[8:10] + '/' + str(entry.get('date', ''))[5:7]
    d.text((38, 146), date, font=font(FONT_TEXT, 28), fill=(255, 255, 255, 230))
    # Le titre doit tenir entre le badge et la vidéo (y 200 à 470) : on réduit la taille si besoin.
    for size, width in ((52, 22), (44, 26), (38, 30)):
        lines = textwrap.wrap(entry.get('titre', ''), width=width)
        if len(lines) * (size + 14) <= 260:
            break
    title = font(FONT_BOLD, size)
    y = 205
    for line in lines[:6]:
        d.text((36, y), line, font=title, fill=(255, 255, 255, 255), stroke_width=5, stroke_fill=(0, 0, 0, 255))
        y += size + 14
    d.rounded_rectangle((36, H - 210, W - 36, H - 120), radius=22, fill=(4, 6, 15, 235), outline=u['couleur'] + (255,), width=4)
    msg, size = 'JT complet sur ' + u['lien'], 36
    while size > 20 and d.textlength(msg, font=font(FONT_BOLD, size)) > W - 120:
        size -= 2
    foot = font(FONT_BOLD, size)
    d.text(((W - d.textlength(msg, font=foot)) / 2, H - 165 - size / 2 - 6), msg, font=foot, fill=u['couleur'] + (255,))
    img.save(path)


def vertical(src, entry, out):
    """9:16, fond flou de l'image elle-même, vidéo au centre, bandeaux par-dessus, moins d'une minute."""
    with tempfile.TemporaryDirectory() as tmp:
        layer = Path(tmp) / 'calque.png'
        overlay(entry, layer)
        probe = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(src)],
                               check=True, capture_output=True, text=True).stdout.strip()
        dur = min(MAX_SECONDS, float(probe or MAX_SECONDS))
        fade = max(0.0, dur - 1.5)
        graph = (f'[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=24:2,eq=brightness=-0.18[bg];'
                 f'[0:v]scale={W}:-2[fg];[bg][fg]overlay=0:(H-h)/2+60[v1];[v1][1:v]overlay=0:0,'
                 f'fade=t=out:st={fade:.2f}:d=1.5,format=yuv420p[v]')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-t', f'{dur:.2f}', '-i', str(src), '-i', str(layer),
                        '-filter_complex', graph, '-map', '[v]', '-map', '0:a?', '-af', f'afade=t=out:st={fade:.2f}:d=1.5',
                        '-t', f'{dur:.2f}', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '26', '-r', '30',
                        '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(out)], check=True)
    return round(dur)


def download(url, path):
    req = urllib.request.Request(url, headers={'User-Agent': 'VM-reseaux/1.0'})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, 'wb') as f:
        shutil.copyfileobj(r, f)


def source_urls(entry):
    name = entry['fichier']
    sha = entry.get('media_sha')
    # Le dépôt brut d'abord (pas de limite de taille), puis le CDN.
    return [f'https://raw.githubusercontent.com/{REPO}/{sha}/{name}', f'https://cdn.jsdelivr.net/gh/{REPO}@{sha}/{name}'] if sha else []


def git(*args, cwd=None):
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def push_branch(files):
    """Ranger les vidéos verticales sur la branche « reseaux » en gardant les plus récentes."""
    token = os.getenv('GITHUB_TOKEN', '')
    url = f'https://x-access-token:{token}@github.com/{REPO}.git' if token else f'https://github.com/{REPO}.git'
    with tempfile.TemporaryDirectory(prefix='reseaux-') as folder:
        work = Path(folder) / 'r'
        try:
            git('clone', '--quiet', '--depth', '1', '--branch', BRANCH, url, str(work))
        except subprocess.CalledProcessError:
            work.mkdir()
            git('init', '--quiet', cwd=work)
            git('checkout', '--quiet', '--orphan', BRANCH, cwd=work)
            git('remote', 'add', 'origin', url, cwd=work)
            (work / 'README.md').write_text('Vidéos verticales des JT pour les réseaux. Branche technique gérée par tools/reseaux_jt.py.\n')
        for f in files:
            shutil.copyfile(f, work / f.name)
        videos = sorted(work.glob('*.mp4'), key=lambda p: p.name.split('-', 2)[-1], reverse=True)
        for old in videos[KEEP_VIDEOS:]:
            old.unlink()
        git('add', '-A', cwd=work)
        git('-c', 'user.name=github-actions[bot]', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
            'commit', '--quiet', '-m', 'Réseaux : vidéos verticales des JT', cwd=work)
        git('push', '--quiet', 'origin', f'HEAD:{BRANCH}', cwd=work)
        return git('rev-parse', 'HEAD', cwd=work)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--limit', type=int, default=3, help='JT à traiter au maximum par passage')
    p.add_argument('--local', help='Dossier contenant déjà les MP4 (test, sans téléchargement)')
    p.add_argument('--sortie', help='Dossier où écrire les vidéos sans publier (test)')
    a = p.parse_args()
    emissions = json.loads(EMISSIONS.read_text(encoding='utf-8'))
    done = json.loads(LIST.read_text(encoding='utf-8')) if LIST.is_file() else []
    known = {e['id'] for e in done}
    todo = [e for e in emissions if e.get('publie') in (True, 'True') and e.get('fichier') and e['id'] not in known][:a.limit]
    if not todo:
        print('Aucun nouveau JT à préparer pour les réseaux.')
        return
    out_dir = Path(a.sortie) if a.sortie else Path(tempfile.mkdtemp(prefix='reseaux-out-'))
    out_dir.mkdir(parents=True, exist_ok=True)
    made, rows = [], []
    for e in todo:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(a.local) / e['fichier'] if a.local else Path(tmp) / e['fichier']
            if not a.local:
                for url in source_urls(e):
                    try:
                        download(url, src)
                        break
                    except Exception as exc:  # Essayer la source suivante.
                        print(f"{e['id']} : téléchargement impossible depuis {url.split('/')[2]} ({type(exc).__name__}).")
            if not src.is_file():
                print(f"{e['id']} : vidéo introuvable, ignorée.")
                continue
            out = out_dir / (e['id'] + '-vertical.mp4')
            secs = vertical(src, e, out)
        long, court = caption(e)
        made.append(out)
        rows.append({'id': e['id'], 'univers': e.get('univers'), 'titre': e.get('titre'), 'date': e.get('date'),
                     'poster': e.get('poster', ''), 'horizontale': e.get('video', ''), 'duree': e.get('duree'),
                     'verticale_fichier': out.name, 'duree_verticale': secs, 'texte': long, 'texte_vertical': court})
        print(f"{e['id']} : version verticale de {secs} s prête.")
    if not rows:
        return
    if a.sortie:
        (out_dir / 'reseaux.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        print(f'Test : {len(rows)} kit(s) écrits dans {out_dir}, rien n’est publié.')
        return
    sha = push_branch(made)
    for r in rows:
        r['verticale'] = f"https://cdn.jsdelivr.net/gh/{REPO}@{sha}/{r.pop('verticale_fichier')}"
        r['prepare_le'] = dt.datetime.now(dt.timezone.utc).isoformat(timespec='minutes')
    LIST.write_text(json.dumps((rows + done)[:KEEP_ENTRIES], ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'{len(rows)} kit(s) réseaux publiés.')


if __name__ == '__main__':
    main()
