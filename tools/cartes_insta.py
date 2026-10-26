#!/usr/bin/env python3
"""Cartes Instagram (1080x1350) pour les articles VM : décor BD de l'univers, titre, source, site.

Les cartes sont rangées sur la branche technique « cartes » (les 60 plus récentes) et servies
par raw.githubusercontent.com, adresse publique lue par Instagram au moment de la publication.
"""
from pathlib import Path
import subprocess
import tempfile
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REPO = 'Velocemercato/velocemercato.fr'
BRANCH = 'cartes'
KEEP = 60
W, H = 1080, 1350
DECORS = {'foot': 'img/v2-mercato.webp', 'actus': 'img/v2-actus.webp', 'gaming': 'vm-gaming/img/vm-gaming.webp'}
LABELS = {'foot': ('⚽', 'VÉLOCE MERCATO', (244, 207, 85)), 'actus': ('📰', 'VM ACTUS', (255, 90, 110)),
          'gaming': ('🎮', 'VM GAMING', (214, 255, 110))}
FONT = ROOT / 'studio/assets/Poppins-Bold.ttf'
FONT_MED = ROOT / 'studio/assets/Poppins-Medium.ttf'


def font(path, size):
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()


def make_card(univers, title, source, output, root=ROOT):
    """Fabrique la carte JPEG ; aucun visage réel, aucun logo de club : seulement le décor BD du site."""
    decor = Path(root) / DECORS[univers]
    if decor.is_file():
        bg = Image.open(decor).convert('RGB')
        scale = max(W / bg.width, H / bg.height)
        bg = bg.resize((int(bg.width * scale) + 1, int(bg.height * scale) + 1), Image.LANCZOS)
        left, top = (bg.width - W) // 2, (bg.height - H) // 2
        bg = bg.crop((left, top, left + W, top + H))
    else:
        bg = Image.new('RGB', (W, H), (11, 21, 51))
    bg = bg.filter(ImageFilter.GaussianBlur(3))
    shade = Image.new('L', (W, H))
    draw = ImageDraw.Draw(shade)
    for y in range(H):  # bas assombri pour lire le titre
        draw.line((0, y, W, y), fill=int(95 + 150 * max(0, (y - H * 0.2) / (H * 0.8))))
    card = Image.composite(Image.new('RGB', (W, H), (5, 9, 23)), bg, shade)
    d = ImageDraw.Draw(card)
    _emoji, label, color = LABELS[univers]
    d.rounded_rectangle((60, 70, 60 + font(FONT, 44).getbbox(label)[2] + 60, 150), radius=40, fill=color)
    d.text((90, 82), label, font=font(FONT, 44), fill=(11, 21, 51))
    size = 74
    lines = textwrap.wrap(title, 24)
    while len(lines) > 6 and size > 50:
        size -= 6
        lines = textwrap.wrap(title, int(24 * 74 / size))
    lines = lines[:7]
    big = font(FONT, size)
    y = H - 330 - len(lines) * int(size * 1.18)
    for line in lines:
        d.text((60, y), line, font=big, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))
        y += int(size * 1.18)
    d.text((60, H - 250), 'Selon ' + source[:40], font=font(FONT_MED, 40), fill=(225, 230, 245))
    d.line((60, H - 175, W - 60, H - 175), fill=color, width=4)
    d.text((60, H - 150), 'velocemercato.fr', font=font(FONT, 48), fill=color)
    d.text((60, H - 85), 'Lien en bio · infos sourcées', font=font(FONT_MED, 32), fill=(200, 205, 225))
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    card.save(output, 'JPEG', quality=88, optimize=True)
    return output


def git(*args, cwd=None):
    helper = ['-c', 'credential.helper=!gh auth git-credential']
    return subprocess.run(['git', *helper, *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def push_card(path):
    """Range la carte sur la branche « cartes » et renvoie son adresse publique figée (par commit)."""
    url = f'https://github.com/{REPO}.git'
    with tempfile.TemporaryDirectory(prefix='cartes-') as folder:
        work = Path(folder) / 'c'
        try:
            git('clone', '--quiet', '--depth', '1', '--branch', BRANCH, url, str(work))
        except subprocess.CalledProcessError:
            work.mkdir()
            git('init', '--quiet', '-b', BRANCH, cwd=work)
            git('remote', 'add', 'origin', url, cwd=work)
            (work / 'README.md').write_text('Cartes Instagram des articles VM. Branche technique gérée par tools/cartes_insta.py.\n')
        (work / Path(path).name).write_bytes(Path(path).read_bytes())
        for old in sorted(work.glob('*.jpg'), key=lambda p: p.stat().st_mtime, reverse=True)[KEEP:]:
            old.unlink()
        git('add', '-A', cwd=work)
        git('-c', 'user.name=github-actions[bot]', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
            'commit', '--quiet', '-m', 'Cartes Instagram', cwd=work)
        git('push', '--quiet', 'origin', f'HEAD:{BRANCH}', cwd=work)
        sha = git('rev-parse', 'HEAD', cwd=work)
    return f'https://raw.githubusercontent.com/{REPO}/{sha}/{Path(path).name}'


def make_projet_card(name, icon, pitch, output, root=ROOT):
    """Carte « projet VM du jour » : l'icône de l'appli VM en grand, le nom et une phrase."""
    card = Image.new('RGB', (W, H), (8, 12, 40))
    path = Path(root) / 'app' / f'{icon}-512.png'
    if path.is_file():
        art = Image.open(path).convert('RGB')
        glow = art.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(60))
        card = Image.blend(card, glow, 0.55)
        card.paste(art.resize((620, 620), Image.LANCZOS), ((W - 620) // 2, 150))
    d = ImageDraw.Draw(card)
    d.text((60, 60), 'LE PROJET VM DU JOUR', font=font(FONT, 46), fill=(244, 207, 85))
    title = font(FONT, 78 if len(name) < 18 else 60)
    d.text(((W - title.getbbox(name)[2]) // 2, 820), name, font=title, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))
    y = 940
    for line in textwrap.wrap(pitch, 30)[:3]:
        f = font(FONT_MED, 46)
        d.text(((W - f.getbbox(line)[2]) // 2, y), line, font=f, fill=(225, 230, 245))
        y += 62
    d.line((60, H - 150, W - 60, H - 150), fill=(255, 40, 60), width=4)
    f = font(FONT, 52)
    d.text(((W - f.getbbox('vmunivers.fr')[2]) // 2, H - 125), 'vmunivers.fr', font=f, fill=(244, 207, 85))
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    card.save(output, 'JPEG', quality=88, optimize=True)
    return output
