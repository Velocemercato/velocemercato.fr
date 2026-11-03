#!/usr/bin/env python3
"""Vidéos promo verticales ORIGINALES VM (9:16, 1080x1920, 30 i/s, 15 s), en complément des publications.

Animation en 5 temps : logo couronné → titre → illustration VM ou personnage Véloce → 3 points → appel à l'action.
Uniquement des éléments du dépôt (logo VM, avatar Véloce, illustrations VM), couleurs noir / rouge néon / or / vert.
Piste audio silencieuse : aucune musique tierce. Le texte reste dans les zones sûres de TikTok, Reels et Shorts
(ni sous les boutons de droite, ni sous la légende du bas).

Ces vidéos ne sont PAS publiées automatiquement : elles ne figurent pas dans campagnes/calendrier.json.

  python tools/vm_videos_promo.py            # génère les vidéos et les aperçus
  python tools/vm_videos_promo.py --apercus  # aperçus seulement (rapide)
"""
import argparse
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.veloce_team_visuels import font, fit, avatar, BLACK, RED, GOLD, GREEN, WHITE  # noqa: E402

W, H, FPS, SECONDS = 1080, 1920, 30, 15
SAFE_TOP, SAFE_BOTTOM, SAFE_LEFT, SAFE_RIGHT = 260, 1560, 90, 930   # zones sûres (boutons à droite, légende en bas)
OUT = ROOT / 'assets/social/promo'
PREVIEWS = ROOT / 'docs/apercus/videos-promo'
ACCENT = {'vert': GREEN, 'or': GOLD, 'rouge': RED}

CONCEPTS = [
    {'id': 'veloce-team-intro', 'surtitre': 'Véloce Team', 'titre': 'DEUX UNIVERS', 'titre2': 'UNE PASSION',
     'illustration': '', 'couleur': 'or',
     'points': ['velocemercato.fr : foot et actu', 'Mangas, séries, multisport', 'vmunivers.fr : projets et services'],
     'cta': 'REJOINS LA TEAM', 'lien': 'velocemercato.fr · vmunivers.fr'},
    {'id': 'vm-mangas-teaser', 'surtitre': 'VM MANGAS', 'titre': 'NOTRE ENFANCE', 'titre2': 'EN DESSINS ANIMÉS',
     'illustration': 'img/vm-art/vm-mangas-hero.webp', 'couleur': 'rouge',
     'points': ['Olive et Tom, Dragon Ball', 'One Piece, Oggy, les Zinzins', 'Un toucher et ça démarre'],
     'cta': 'REGARDE SUR VM', 'lien': 'velocemercato.fr/mangas'},
    {'id': 'foot-amateur', 'surtitre': 'VM Foot amateur', 'titre': 'TON CLUB', 'titre2': 'TA RÉGION',
     'illustration': 'img/banniere-foot.webp', 'couleur': 'vert',
     'points': ['National 2, N3, Régional', 'District et Coupe de France', 'Les titres du jour'],
     'cta': 'TROUVE TON CLUB', 'lien': 'velocemercato.fr/foot-amateur'},
    {'id': 'question-team', 'surtitre': 'La question de la team', 'titre': 'TEAM FOOT', 'titre2': 'OU TEAM UNIVERS ?',
     'illustration': '', 'couleur': 'vert',
     'points': ['Team Foot : velocemercato.fr', 'Team Univers : vmunivers.fr', 'Les deux ? Bienvenue !'],
     'cta': 'RÉPONDS EN COMMENTAIRE', 'lien': 'Véloce Team'},
    {'id': 'veloce-arena', 'surtitre': 'VM Gaming', 'titre': 'VÉLOCE ARENA', 'titre2': 'ENTRE POTES',
     'illustration': 'vm-gaming/img/vm-show-840.webp', 'couleur': 'vert',
     'points': ['Ligues et coupes EA SPORTS FC', 'Défis gratuits', "L'actu jeux vidéo chaque jour"],
     'cta': 'REJOINS L’ARENA', 'lien': 'velocemercato.fr/gaming.html'},
]


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def phase(t, start, length):
    return ease((t - start) / length)


def background(accent):
    base = Image.new('RGBA', (W, H), BLACK)
    halo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([90, 420, 990, 1320], fill=(243, 39, 75, 70))
    base.alpha_composite(halo.filter(ImageFilter.GaussianBlur(110)))
    return base


def speed_lines(img, t, accent):
    """Traits de vitesse façon manga qui défilent en arrière-plan."""
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    color = Image.new('RGB', (1, 1), accent).getpixel((0, 0))
    for i in range(14):
        y = (i * 151 + int(t * 420)) % (H + 200) - 100
        x = (i * 97) % 400 - 200
        d.line([(x, y), (x + 520, y - 140)], fill=color + (38,), width=6)
    img.alpha_composite(layer)


def neon(img, pulse):
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([26, 26, W - 26, H - 26], 40, outline=RED, width=18)
    glow = glow.filter(ImageFilter.GaussianBlur(14 + 6 * pulse))
    img.alpha_composite(glow)
    ImageDraw.Draw(img).rounded_rectangle([26, 26, W - 26, H - 26], 40, outline=RED, width=5)


def text_center(draw, y, text, size, color, alpha=1.0, dx=0, stroke=3, width=SAFE_RIGHT - SAFE_LEFT):
    f = fit(draw, text, size, width)
    w = draw.textlength(text, font=f)
    x = SAFE_LEFT + (width - w) / 2 + dx
    c = Image.new('RGB', (1, 1), color).getpixel((0, 0))
    draw.text((x, y), text, font=f, fill=c + (int(255 * alpha),), stroke_width=stroke, stroke_fill=(5, 7, 13, int(255 * alpha)))
    return f.size


def illustration(name, width, height):
    if not name:
        return None
    im = Image.open(ROOT / name).convert('RGB')
    if im.width / im.height > width / height:
        # Bandeau large (logo écrit dedans) : affiché en entier, jamais coupé sur les côtés.
        scale = width / im.width
        im = im.resize((width, max(1, int(im.height * scale))), Image.LANCZOS).convert('RGBA')
        height = im.height
    else:
        scale = max(width / im.width, height / im.height)
        im = im.resize((int(im.width * scale) + 1, int(im.height * scale) + 1), Image.LANCZOS)
        x, y = (im.width - width) // 2, (im.height - height) // 2
        im = im.crop((x, y, x + width, y + height)).convert('RGBA')
    mask = Image.new('L', (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, width, height], 30, fill=255)
    im.putalpha(mask)
    return im


class Concept:
    def __init__(self, c):
        self.c = c
        self.accent = ACCENT[c['couleur']]
        self.bg = background(self.accent)
        logo = Image.open(ROOT / 'img/logo-vm-officiel.png').convert('RGBA')
        logo.thumbnail((170, 170))
        self.logo = logo
        self.visual = illustration(c['illustration'], SAFE_RIGHT - SAFE_LEFT, 380) or avatar(350)

    def frame(self, t):
        c, accent = self.c, self.accent
        img = self.bg.copy()
        speed_lines(img, t, accent)
        neon(img, 0.5 + 0.5 * math.sin(t * 4))
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        # 1. Logo : apparition avec rebond (0 → 1,2 s), puis reste en haut.
        k = phase(t, 0, 1.2)
        size = max(1, int(self.logo.width * (0.4 + 0.6 * k)))
        logo = self.logo.resize((size, size), Image.LANCZOS)
        logo.putalpha(logo.getchannel('A').point(lambda a: int(a * k)))
        layer.alpha_composite(logo, ((W - size) // 2, SAFE_TOP + (170 - size) // 2))
        y = SAFE_TOP + 190
        # 2. Surtitre + titre sur deux lignes (1 → 3 s), glissement vers le haut.
        a = phase(t, 1.0, 0.6)
        text_center(draw, y + int(30 * (1 - a)), c['surtitre'].upper(), 40, accent, a, stroke=2)
        y += 70
        for i, line in enumerate((c['titre'], c['titre2'])):
            a = phase(t, 1.4 + 0.5 * i, 0.6)
            text_center(draw, y + int(60 * (1 - a)), line, 96, WHITE if i == 0 else GOLD, a, stroke=5)
            y += 112
        y += 20
        # 3. Illustration ou personnage Véloce (3 → 4 s), léger zoom continu.
        a = phase(t, 3.0, 0.8)
        if a > 0:
            zoom = 0.9 + 0.1 * a + 0.02 * math.sin(t * 2)
            vis = self.visual.resize((int(self.visual.width * zoom), int(self.visual.height * zoom)), Image.LANCZOS)
            vis.putalpha(vis.getchannel('A').point(lambda v: int(v * a)))
            layer.alpha_composite(vis, ((SAFE_LEFT + SAFE_RIGHT) // 2 - vis.width // 2, y + (380 - vis.height) // 2))
        y += 400
        # 4. Trois points, l'un après l'autre (6 → 9 s), glissement depuis la gauche.
        for i, point in enumerate(c['points']):
            a = phase(t, 6.0 + 1.0 * i, 0.6)
            if a > 0:
                text_center(draw, y, '• ' + point, 46, WHITE, a, dx=int(-120 * (1 - a)), stroke=2)
            y += 62
        y += 24
        # 5. Appel à l'action (10 → 15 s) qui pulse doucement.
        a = phase(t, 10.0, 0.7)
        if a > 0:
            pulse = 1 + 0.04 * math.sin((t - 10) * 6)
            bw, bh = int(780 * pulse), int(110 * pulse)
            x0 = (SAFE_LEFT + SAFE_RIGHT) // 2 - bw // 2
            rgb = Image.new('RGB', (1, 1), RED).getpixel((0, 0))
            draw.rounded_rectangle([x0, y, x0 + bw, y + bh], bh // 2, fill=rgb + (int(255 * a),))
            text_center(draw, y + (bh - 50) // 2 - 4, c['cta'], 50, WHITE, a, stroke=0, width=SAFE_RIGHT - SAFE_LEFT - 60)
            text_center(draw, y + bh + 26, c['lien'], 36, GOLD, a, stroke=2)
        img.alpha_composite(layer)
        assert y + 200 <= SAFE_BOTTOM + 60, (c['id'], y)
        return img.convert('RGB')


def render_video(concept, out):
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
           '-map', '0:v', '-map', '1:a', '-t', str(SECONDS), '-c:v', 'libx264', '-preset', 'medium', '-crf', '24',
           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '48k', '-movflags', '+faststart', str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    c = Concept(concept)
    for n in range(SECONDS * FPS):
        proc.stdin.write(c.frame(n / FPS).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError('ffmpeg a échoué pour ' + concept['id'])


def preview(concept, out):
    c = Concept(concept)
    shots = [c.frame(t) for t in (1.0, 3.5, 8.5, 13.0)]
    sheet = Image.new('RGB', (4 * 270 + 30, 480), 'white')
    for i, s in enumerate(shots):
        s.thumbnail((270, 480))
        sheet.paste(s, (i * 280, 0))
    sheet.save(out, quality=85)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apercus', action='store_true')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    for concept in CONCEPTS:
        preview(concept, PREVIEWS / (concept['id'] + '.jpg'))
        if not args.apercus:
            render_video(concept, OUT / (concept['id'] + '.mp4'))
        print('prêt :', concept['id'])


if __name__ == '__main__':
    main()
