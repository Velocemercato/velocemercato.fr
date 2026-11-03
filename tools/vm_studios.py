#!/usr/bin/env python3
"""Studios et habillages VM : gaming (stream PS5) et médias Véloce Mercato / VM Univers.

Dessinés par ce script avec uniquement les logos VM (aucune marque tierce, aucun logo de console).

Fonds (assets/social/fonds/, JPG) :
  gaming-studio-{vertical,horizontal}, plateau-veloce-mercato-{…}, plateau-vm-univers-{…}
Habillages transparents (assets/social/habillages/, PNG 1920x1080 sauf mention) :
  stream-vm-gaming          : jeu plein écran + cadre caméra + bandeaux (zones transparentes)
  stream-ecran-debut / -pause / -fin : écrans « Le live commence », « On revient vite », « Merci d'avoir regardé »
  bandeau-veloce-mercato / bandeau-vm-univers (+ -vertical 1080x1920) : bandeau bas vide pour le nom ou le sujet
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONDS, HAB = ROOT / 'assets/social/fonds', ROOT / 'assets/social/habillages'
BLACK, RED, GOLD, GREEN, WHITE = (5, 7, 13), (243, 39, 75), (244, 207, 85), (145, 247, 112), (255, 255, 255)
PURPLE, CYAN = (150, 70, 255), (60, 200, 255)


def font(size, oblique=False):
    for name in (['DejaVuSans-BoldOblique.ttf'] if oblique else []) + ['DejaVuSansCondensed-Bold.ttf', 'DejaVuSans-Bold.ttf']:
        try:
            return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def blurred(size, draw_fn, blur):
    layer = Image.new('RGBA', size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    return layer.filter(ImageFilter.GaussianBlur(blur))


def crown(img, x, y, side, alpha=255):
    m = Image.open(ROOT / 'img/logo-vm-officiel.png').convert('RGBA')
    m.thumbnail((side, side))
    if alpha < 255:
        m.putalpha(m.getchannel('A').point(lambda a: a * alpha // 255))
    img.alpha_composite(m, (int(x), int(y)))
    return m.size


def text(draw, xy, s, size, fill, anchor='la', oblique=False, stroke=0):
    draw.text(xy, s, font=font(size, oblique), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=BLACK)


def gaming_logo(height):
    lg = Image.open(ROOT / 'vm-gaming/img/logo-vm-gaming.webp').convert('RGBA')
    lg = lg.resize((int(lg.width * height / lg.height), height), Image.LANCZOS)
    mask = Image.new('L', lg.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, lg.width, lg.height], height // 6, fill=255)
    lg.putalpha(mask)
    return lg


# ---------- Fonds ----------

def gaming_studio(w, h):
    img = Image.new('RGBA', (w, h), (6, 6, 16, 255))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=(int(14 - 8 * t), int(8 - 4 * t), int(30 - 18 * t)))
    # Panneaux hexagonaux lumineux au mur
    r = min(w, h) * .055
    hexes = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hexes)
    rnd = random.Random(5)
    for row in range(int(h * .62 / (r * 1.6))):
        for col in range(int(w / (r * 1.8)) + 1):
            if rnd.random() < .45:
                continue
            cx, cy = col * r * 1.8 + (r * .9 if row % 2 else 0), r * 1.2 + row * r * 1.55
            pts = [(cx + r * .8 * math.cos(math.radians(60 * k + 30)), cy + r * .8 * math.sin(math.radians(60 * k + 30))) for k in range(6)]
            col_ = rnd.choice([RED, PURPLE, CYAN, GREEN])
            hd.polygon(pts, outline=col_ + (230,), width=4, fill=col_ + (25,))
    img.alpha_composite(hexes.filter(ImageFilter.GaussianBlur(9)))
    img.alpha_composite(hexes)
    # Bandes LED et bureau
    img.alpha_composite(blurred((w, h), lambda dd: dd.rectangle([0, h * .70, w, h * .715], fill=PURPLE + (255,)), 18))
    d = ImageDraw.Draw(img)
    d.rectangle([0, h * .70, w, h * .708], fill=(190, 140, 255))
    d.rectangle([0, h * .72, w, h], fill=(10, 10, 20))
    img.alpha_composite(blurred((w, h), lambda dd: dd.ellipse([w * .2, h * .74, w * .8, h * .95], fill=RED + (60,)), 60))
    crown(img, w * .04, h * .03, int(min(w, h) * .16))
    return img


def plateau_media(w, h, univers=False):
    accent = GOLD if univers else RED
    img = Image.new('RGBA', (w, h), BLACK + (255,))
    img.alpha_composite(blurred((w, h), lambda dd: dd.ellipse([w * .05, h * .15, w * .95, h * .85], fill=accent + (70,)), min(w, h) * .16))
    d = ImageDraw.Draw(img)
    # Lignes de perspective du plateau
    for i in range(-10, 11):
        d.line([(w / 2 + i * w * .03, h * .55), (w / 2 + i * w * .25, h)], fill=accent + (55,), width=2)
    for i in range(8):
        y = h * .55 + (h * .45) * (i / 8) ** 1.6
        d.line([(0, y), (w, y)], fill=accent + (40,), width=2)
    # Bandeau titre en haut
    band_h = int(min(w, h) * .12)
    top = int(h * .05)
    d.rectangle([0, top, w, top + band_h], fill=(12, 14, 26))
    d.rectangle([0, top + band_h, w, top + band_h + 6], fill=accent)
    side = int(band_h * .9)
    cw, _ = crown(img, w * .03, top + band_h * .05, side)
    title = 'VM UNIVERS' if univers else 'VÉLOCE MERCATO'
    sub = 'MÉDIAS · SERVICES · PROJETS' if univers else 'FOOT · ACTU · MERCATO'
    tx = w * .03 + cw + band_h * .25
    text(d, (tx, top + band_h * .12), title, int(band_h * .46), GOLD if univers else WHITE, oblique=True)
    text(d, (tx, top + band_h * .64), sub, int(band_h * .22), accent if not univers else (220, 225, 240))
    # Logo filigrane derrière la personne
    big = int(min(w, h) * .5)
    crown(img, (w - big) / 2, h * .26, big, alpha=28)
    return img


# ---------- Habillages transparents ----------

def stream_overlay():
    w, h = 1920, 1080
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Cadre néon autour du jeu
    img.alpha_composite(blurred((w, h), lambda dd: dd.rectangle([6, 6, w - 6, h - 6], outline=PURPLE + (255,), width=10), 8))
    d.rectangle([4, 4, w - 4, h - 4], outline=(190, 140, 255), width=3)
    # Logo VM Gaming en haut à gauche, pastille EN DIRECT
    lg = gaming_logo(78)
    img.alpha_composite(lg, (30, 26))
    x = 30 + lg.width + 18
    d.rounded_rectangle([x, 44, x + 196, 92], 24, fill=RED)
    d.ellipse([x + 16, 60, x + 32, 76], fill=WHITE)
    text(d, (x + 44, 52), 'EN DIRECT', 30, WHITE)
    # Cadre caméra en bas à droite (zone transparente)
    cx0, cy0, cx1, cy1 = w - 30 - 480, h - 30 - 60 - 270, w - 30, h - 30 - 60
    img.alpha_composite(blurred((w, h), lambda dd: dd.rounded_rectangle([cx0, cy0, cx1, cy1], 22, outline=RED + (255,), width=12), 10))
    d.rounded_rectangle([cx0, cy0, cx1, cy1], 22, outline=RED, width=5)
    d.rounded_rectangle([cx0, cy1 - 4, cx1, cy1 + 52], 16, fill=(12, 10, 24, 235))
    text(d, ((cx0 + cx1) / 2, cy1 + 24), 'VÉLOCE TEAM', 30, GOLD, anchor='mm')
    # Bandeau bas : réseaux
    d.rounded_rectangle([30, h - 78, cx0 - 24, h - 28], 18, fill=(12, 10, 24, 225))
    text(d, (54, h - 53), 'twitch.tv/velocemercato  ·  YouTube @VeloceMercato  ·  velocemercato.fr/vm-gaming', 27, WHITE, anchor='lm')
    return img


def stream_screen(title, subtitle):
    w, h = 1920, 1080
    img = gaming_studio(w, h)
    img.alpha_composite(Image.new('RGBA', (w, h), (0, 0, 0, 120)))
    d = ImageDraw.Draw(img)
    lg = gaming_logo(150)
    img.alpha_composite(lg, ((w - lg.width) // 2, 250))
    text(d, (w / 2, 560), title, 120, WHITE, anchor='mm', oblique=True, stroke=5)
    text(d, (w / 2, 680), subtitle, 46, GOLD, anchor='mm', stroke=2)
    text(d, (w / 2, 930), 'twitch.tv/velocemercato  ·  YouTube @VeloceMercato', 36, (220, 220, 240), anchor='mm')
    return img


def lower_third(w, h, univers=False):
    accent = GOLD if univers else RED
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    vertical = h > w
    x0, bw = (40, w - 80) if vertical else (70, int(w * .48))
    y0 = int(h * (.70 if vertical else .74))
    bh = int(min(w, h) * (.11 if vertical else .12))
    img.alpha_composite(blurred((w, h), lambda dd: dd.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], 18, fill=accent + (160,)), 18))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], 18, fill=(12, 14, 26, 240), outline=accent, width=4)
    side = int(bh * .78)
    crown(img, x0 + 14, y0 + (bh - side) / 2, side)
    d.rounded_rectangle([x0 + side + 34, y0 + bh - 16, x0 + bw - 24, y0 + bh - 10], 3, fill=accent)
    d.rounded_rectangle([x0, y0 + bh + 10, x0 + int(bw * .62), y0 + bh + 10 + int(bh * .42)], 12, fill=accent + (235,))
    label = 'VM UNIVERS' if univers else 'VÉLOCE MERCATO'
    text(d, (x0 + 18, y0 + bh + 10 + int(bh * .21)), label, int(bh * .26), BLACK if univers else WHITE, anchor='lm')
    return img


def main():
    FONDS.mkdir(parents=True, exist_ok=True)
    HAB.mkdir(parents=True, exist_ok=True)
    for kind, size in (('vertical', (1080, 1920)), ('horizontal', (1920, 1080))):
        gaming_studio(*size).convert('RGB').save(FONDS / f'gaming-studio-{kind}.jpg', quality=92)
        plateau_media(*size).convert('RGB').save(FONDS / f'plateau-veloce-mercato-{kind}.jpg', quality=92)
        plateau_media(*size, univers=True).convert('RGB').save(FONDS / f'plateau-vm-univers-{kind}.jpg', quality=92)
    stream_overlay().save(HAB / 'stream-vm-gaming.png', optimize=True)
    for name, t, s in (('debut', 'LE LIVE COMMENCE', 'Installe-toi, on arrive !'),
                       ('pause', 'ON REVIENT VITE', 'Pause rapide, reste avec la team'),
                       ('fin', "MERCI D'AVOIR REGARDÉ", 'Abonne-toi pour le prochain live')):
        stream_screen(t, s).convert('RGB').save(HAB / f'stream-ecran-{name}.jpg', quality=92)
    for univers, label in ((False, 'veloce-mercato'), (True, 'vm-univers')):
        lower_third(1920, 1080, univers).save(HAB / f'bandeau-{label}.png', optimize=True)
        lower_third(1080, 1920, univers).save(HAB / f'bandeau-{label}-vertical.png', optimize=True)
    print('Studios et habillages prêts')


if __name__ == '__main__':
    main()
