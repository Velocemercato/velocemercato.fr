#!/usr/bin/env python3
"""Campagne quotidienne VÉLOCE TEAM : un thème par jour, préparé à l'avance.

Le calendrier `campagnes/calendrier.json` est la seule source : Heineguez peut y corriger un texte,
passer un jour en "statut": "pause", ou tout couper avec "actif": false. Les visuels sont originaux
(personnage Véloce, logo VM, illustrations VM existantes) et générés par ce script.

  python tools/campagne_quotidienne.py --visuels     # (re)génère les visuels des jours à venir
"""
import argparse
import json
import subprocess
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / 'campagnes/calendrier.json'
OUT = ROOT / 'assets/social/campagne'
import sys
sys.path.insert(0, str(ROOT))
from tools.veloce_team_visuels import font, fit, centered, neon_frame, avatar, BLACK, RED, GOLD, GREEN, WHITE  # noqa: E402

ACCENTS = {'vert': GREEN, 'or': GOLD, 'rouge': RED}


def load():
    return json.loads(CAL.read_text(encoding='utf-8'))


def art(name, width, height):
    """Illustration VM recadrée (couverture), ou None."""
    if not name:
        return None
    im = Image.open(ROOT / name).convert('RGB')
    scale = max(width / im.width, height / im.height)
    im = im.resize((int(im.width * scale) + 1, int(im.height * scale) + 1), Image.LANCZOS)
    x, y = (im.width - width) // 2, (im.height - height) // 2
    im = im.crop((x, y, x + width, y + height)).convert('RGBA')
    mask = Image.new('L', (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, width, height], 28, fill=255)
    im.putalpha(mask)
    return im


def poster(day, height, offset=None):
    story = height > 1350
    k = 1.2 if story else 1.0
    accent = ACCENTS.get(day.get('couleur'), GOLD)
    img = Image.new('RGBA', (1080, height), BLACK)
    halo = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([120, int(height * .1), 960, int(height * .1) + 820], fill=(243, 39, 75, 65))
    img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(90)))
    neon_frame(img)
    draw = ImageDraw.Draw(img)
    start = 280 if story else 58
    y = start + (offset or 0)
    logo = Image.open(ROOT / 'img/logo-vm-officiel.png').convert('RGBA')
    logo.thumbnail((int(120 * k), int(120 * k)))
    img.alpha_composite(logo, ((1080 - logo.width) // 2, y))
    y += logo.height + 4
    centered(draw, y, day['surtitre'].upper(), font(int(30 * k), True), accent)
    y += int(48 * k)
    centered(draw, y, day['titre'], fit(draw, day['titre'], int(92 * k), 920), WHITE, stroke=4)
    y += int(112 * k)
    centered(draw, y, day['accroche'], fit(draw, day['accroche'], int(42 * k), 940), GOLD, stroke=2)
    y += int(72 * k)
    visual = art(day.get('illustration'), 920, int(330 * k))
    if visual is not None:
        img.alpha_composite(visual, (80, y))
        ImageDraw.Draw(img).rounded_rectangle([80, y, 1000, y + visual.height], 28, outline=accent, width=5)
        y += visual.height + int(30 * k)
    else:
        av = avatar(int(300 * k))
        img.alpha_composite(av, ((1080 - av.width) // 2, y))
        y += av.height + int(26 * k)
    lf = font(int(36 * k), True)
    for line in day['points']:
        centered(draw, y, '• ' + line, fit(draw, '• ' + line, int(36 * k), 940), WHITE)
        y += int(54 * k)
    y += int(14 * k)
    bh = int(84 * k)
    draw.rounded_rectangle([110, y, 970, y + bh], bh // 2, fill=RED)
    label = day['lien'].replace('https://', '').rstrip('/').upper()
    bf = fit(draw, label, int(40 * k), 800)
    centered(draw, y + (bh - bf.size) // 2 - 4, label, bf, WHITE)
    y += bh + int(26 * k)
    centered(draw, y, 'VÉLOCE TEAM · velocemercato.fr · vmunivers.fr', font(int(26 * k), True), '#c9d0de')
    if offset is None:
        # Second rendu centré verticalement (en gardant les zones masquées par Instagram en story).
        bottom = height - (300 if story else 70)
        return poster(day, height, max(0, (bottom - (y + 40)) // 2))
    if y + 70 > height:
        raise ValueError(f"{day['date']} : texte trop long pour l'affiche ({y}px)")
    return img.convert('RGB')


def video(story_path, out_path, seconds=10):
    frames = seconds * 30
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-i', str(story_path),
                    '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100', '-filter_complex',
                    f"[0:v]scale=2160:3840,zoompan=z='min(zoom+0.0007,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=30,format=yuv420p[v]",
                    '-map', '[v]', '-map', '1:a', '-t', str(seconds), '-c:v', 'libx264', '-preset', 'medium',
                    '-crf', '26', '-c:a', 'aac', '-b:a', '48k', '-movflags', '+faststart', str(out_path)], check=True)


def files(day):
    base = 'assets/social/campagne/' + day['date']
    return {'post': base + '-post.jpg', 'story': base + '-story.jpg', 'video': base + '-reel.mp4'}


def render(day):
    OUT.mkdir(parents=True, exist_ok=True)
    f = files(day)
    poster(day, 1350).save(ROOT / f['post'], quality=88, optimize=True, progressive=True)
    poster(day, 1920).save(ROOT / f['story'], quality=88, optimize=True, progressive=True)
    if day.get('reel') or day.get('youtube_short'):
        video(ROOT / f['story'], ROOT / f['video'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--visuels', action='store_true')
    parser.add_argument('--depuis', default=date.today().isoformat())
    args = parser.parse_args()
    cal = load()
    for day in cal['jours']:
        if day['date'] >= args.depuis and args.visuels:
            render(day)
            print('visuels prêts :', day['date'], day['titre'])


if __name__ == '__main__':
    main()
