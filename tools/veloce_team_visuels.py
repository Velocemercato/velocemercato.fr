#!/usr/bin/env python3
"""Visuels originaux de la campagne « VÉLOCE TEAM — Deux univers, une passion ».

Uniquement des éléments VM : personnage Véloce, logo couronné, couleurs noir / rouge néon / or / vert.
Produit assets/social/veloce-team-{post,story}.jpg et veloce-team-short.mp4 (vertical, sans son tiers).
"""
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/social'
BLACK, RED, GOLD, GREEN, WHITE = '#05070d', '#f3274b', '#f4cf55', '#91f770', '#ffffff'


def font(size, condensed=False):
    names = (['DejaVuSansCondensed-Bold.ttf', 'DejaVuSans-Bold.ttf'] if condensed
             else ['DejaVuSans-Bold.ttf', 'DejaVuSansCondensed-Bold.ttf'])
    for name in names:
        try:
            return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def centered(draw, y, text, f, fill, stroke=0, width=1080):
    w = draw.textlength(text, font=f)
    draw.text(((width - w) / 2, y), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=BLACK)


def neon_frame(img, inset=26, radius=38):
    glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.rounded_rectangle([inset, inset, img.width - inset, img.height - inset], radius, outline=RED, width=18)
    glow = glow.filter(ImageFilter.GaussianBlur(16))
    img.alpha_composite(glow)
    ImageDraw.Draw(img).rounded_rectangle([inset, inset, img.width - inset, img.height - inset], radius, outline=RED, width=5)


def avatar(size):
    src = Image.open(ROOT / 'img/avatar-veloce.webp').convert('RGBA')
    side = min(src.size)
    src = src.crop(((src.width - side) // 2, 0, (src.width + side) // 2, side)).resize((size, size), Image.LANCZOS)
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size, size], fill=255)
    disc = Image.new('RGBA', (size + 24, size + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(disc)
    d.ellipse([0, 0, size + 23, size + 23], fill=GOLD)
    d.ellipse([7, 7, size + 16, size + 16], fill=RED)
    disc.paste(src, (12, 12), mask)
    return disc


def fit(draw, text, size, width):
    while size > 12 and draw.textlength(text, font=font(size, True)) > width:
        size -= 1
    return font(size, True)


def card(draw, box, title, title_color, lines, k=1.0):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, 26, fill='#0f1424', outline=title_color, width=5)
    tf = fit(draw, title, int(44 * k), x1 - x0 - 40)
    w = draw.textlength(title, font=tf)
    draw.text((x0 + (x1 - x0 - w) / 2, y0 + int(26 * k)), title, font=tf, fill=title_color)
    lf = font(int(29 * k), True)
    y = y0 + int(96 * k)
    for line in lines:
        w = draw.textlength(line, font=lf)
        draw.text((x0 + (x1 - x0 - w) / 2, y), line, font=lf, fill=WHITE)
        y += int(44 * k)


def poster(height):
    img = Image.new('RGBA', (1080, height), BLACK)
    # Halo rouge discret en fond
    halo = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([140, int(height * .08), 940, int(height * .08) + 800], fill=(243, 39, 75, 70))
    img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(90)))
    neon_frame(img)
    draw = ImageDraw.Draw(img)
    story = height > 1350
    k = 1.22 if story else 1.0
    top = 290 if story else 62
    logo = Image.open(ROOT / 'img/logo-vm-officiel.png').convert('RGBA')
    logo.thumbnail((int(160 * k), int(160 * k)))
    img.alpha_composite(logo, ((1080 - logo.width) // 2, top))
    y = top + logo.height + 6
    centered(draw, y, 'VÉLOCE TEAM', fit(draw, 'VÉLOCE TEAM', int(108 * k), 900), GOLD, stroke=4)
    y += int(128 * k)
    centered(draw, y, 'Deux univers, une passion', font(int(48 * k), True), WHITE, stroke=2)
    y += int(80 * k)
    av = avatar(int(290 * k))
    img.alpha_composite(av, ((1080 - av.width) // 2, y))
    y += av.height + int(34 * k)
    ch = int(300 * k)
    card(draw, (64, y, 528, y + ch), 'VELOCEMERCATO.FR', GREEN,
         ['Foot pro, amateur', 'et régional', 'Actu · Multisport', 'Mangas · Séries'], k)
    card(draw, (552, y, 1016, y + ch), 'VMUNIVERS.FR', GOLD,
         ['Tous les projets VM', 'Services locaux', 'Pros · Communauté', 'Franche-Comté'], k)
    y += ch + int(34 * k)
    bh = int(84 * k)
    draw.rounded_rectangle([130, y, 950, y + bh], bh // 2, fill=RED)
    bf = font(int(42 * k), True)
    centered(draw, y + (bh - bf.size) // 2 - 4, 'REJOINS LA VÉLOCE TEAM', bf, WHITE)
    y += bh + int(30 * k)
    centered(draw, y, 'Médias, services et projets d’ici · Gratuit', font(int(27 * k), True), '#c9d0de')
    assert y + 60 < height, (height, y)
    return img.convert('RGB')


def video(story_path, out_path, seconds=12):
    """Lent zoom avant sur la story, 30 i/s, piste audio silencieuse (aucune musique tierce)."""
    frames = seconds * 30
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-i', str(story_path),
           '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
           '-filter_complex',
           f"[0:v]scale=2160:3840,zoompan=z='min(zoom+0.0006,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=30,format=yuv420p[v]",
           '-map', '[v]', '-map', '1:a', '-t', str(seconds), '-c:v', 'libx264', '-preset', 'medium', '-crf', '22',
           '-c:a', 'aac', '-b:a', '64k', '-movflags', '+faststart', str(out_path)]
    subprocess.run(cmd, check=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    post = OUT / 'veloce-team-post.jpg'
    story = OUT / 'veloce-team-story.jpg'
    poster(1350).save(post, quality=90, optimize=True, progressive=True)
    poster(1920).save(story, quality=90, optimize=True, progressive=True)
    if '--sans-video' not in sys.argv:
        video(story, OUT / 'veloce-team-short.mp4')
    print('Visuels VÉLOCE TEAM prêts dans', OUT)


if __name__ == '__main__':
    main()
