#!/usr/bin/env python3
"""Fonds vidéo originaux VM (à placer derrière soi dans CapCut, TikTok, OBS…).

Dessinés entièrement par ce script, plus le logo VM : aucun élément tiers.
Le centre et le bas restent sobres pour la personne filmée ; logo discret en haut à gauche.

  python tools/vm_fonds_video.py   → assets/social/fonds/<nom>-vertical.jpg et -horizontal.jpg
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/social/fonds'
BLACK, RED, GOLD, GREEN = (5, 7, 13), (243, 39, 75), (244, 207, 85), (145, 247, 112)
SIZES = {'vertical': (1080, 1920), 'horizontal': (1920, 1080)}


def glow(size, shapes, blur):
    layer = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for kind, box, color, width in shapes:
        getattr(d, kind)(box, **({'fill': color} if width is None else {'outline': color, 'width': width}))
    return layer.filter(ImageFilter.GaussianBlur(blur))


def logo(img, scale=0.11, alpha=230):
    w, h = img.size
    m = Image.open(ROOT / 'img/logo-vm-officiel.png').convert('RGBA')
    side = int(min(w, h) * scale * 1.6)
    m.thumbnail((side, side))
    m.putalpha(m.getchannel('A').point(lambda a: a * alpha // 255))
    img.alpha_composite(m, (int(w * 0.04), int(h * 0.03)))


def studio_neon(w, h):
    img = Image.new('RGBA', (w, h), BLACK + (255,))
    img.alpha_composite(glow((w, h), [('ellipse', [w * .1, h * .05, w * .9, h * .7], RED + (90,), None)], min(w, h) * .18))
    # Cadres néon en profondeur (couloir lumineux)
    for i, k in enumerate((0.92, 0.72, 0.52)):
        bx = [w * (1 - k) / 2, h * (1 - k) / 2 - h * .06, w * (1 + k) / 2, h * (1 + k) / 2 - h * .06]
        col = (RED if i != 1 else GOLD) + (255,)
        img.alpha_composite(glow((w, h), [('rounded_rectangle', bx, col, 14)], 18))
        ImageDraw.Draw(img).rounded_rectangle(bx, 30, outline=col, width=4)
    # Sol brillant
    floor = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(floor)
    for i in range(12):
        y = h * .78 + i * i * h * .0016
        d.line([(0, y), (w, y)], fill=RED + (60,), width=2)
    for i in range(-8, 9):
        d.line([(w / 2 + i * w * .02, h * .78), (w / 2 + i * w * .16, h)], fill=RED + (45,), width=2)
    img.alpha_composite(floor)
    logo(img)
    return img


def plateau(w, h):
    img = Image.new('RGBA', (w, h), (8, 10, 24, 255))
    d = ImageDraw.Draw(img)
    for y in range(h):  # dégradé bleu nuit → noir
        t = y / h
        d.line([(0, y), (w, y)], fill=(int(14 - 9 * t), int(18 - 11 * t), int(48 - 35 * t)))
    # Écrans géants en arrière-plan
    for i, x in enumerate((0.06, 0.38, 0.70)):
        bx = [w * x, h * .12, w * (x + .24), h * .12 + w * .24 * 9 / 16]
        img.alpha_composite(glow((w, h), [('rectangle', bx, (60, 110, 220, 160), None)], 30))
        ImageDraw.Draw(img).rectangle(bx, fill=(16, 28, 70), outline=GOLD if i == 1 else (90, 140, 255), width=4)
    # Bandeaux dorés du plateau
    img.alpha_composite(glow((w, h), [('rectangle', [0, h * .62, w, h * .635], GOLD + (220,), None)], 12))
    d = ImageDraw.Draw(img)
    d.rectangle([0, h * .62, w, h * .628], fill=GOLD)
    d.rectangle([0, h * .80, w, h * .806], fill=RED)
    logo(img)
    return img


def stade(w, h):
    img = Image.new('RGBA', (w, h), BLACK + (255,))
    d = ImageDraw.Draw(img)
    for y in range(int(h * .62)):  # ciel de nuit
        t = y / (h * .62)
        d.line([(0, y), (w, y)], fill=(int(6 + 14 * t), int(9 + 18 * t), int(24 + 40 * t)))
    # Projecteurs avec faisceaux
    for cx in ((0.24, 0.88) if w > h else (0.12, 0.88)):
        x, y = w * cx, h * .12
        beams = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        bd = ImageDraw.Draw(beams)
        for a in range(-3, 4):
            ang = math.radians(90 + (25 if cx < .5 else -25) + a * 6)
            bd.polygon([(x, y), (x + math.cos(ang - .05) * h, y + math.sin(ang - .05) * h),
                        (x + math.cos(ang + .05) * h, y + math.sin(ang + .05) * h)], fill=(255, 250, 220, 18))
        img.alpha_composite(beams.filter(ImageFilter.GaussianBlur(20)))
        img.alpha_composite(glow((w, h), [('ellipse', [x - w * .05, y - w * .05, x + w * .05, y + w * .05], (255, 245, 200, 255), None)], 25))
        ImageDraw.Draw(img).ellipse([x - w * .018, y - w * .018, x + w * .018, y + w * .018], fill=(255, 255, 240))
    # Pelouse en perspective
    d = ImageDraw.Draw(img)
    for i in range(10):
        y0 = h * .62 + (h * .38) * (i / 10) ** 1.3
        y1 = h * .62 + (h * .38) * ((i + 1) / 10) ** 1.3
        d.rectangle([0, y0, w, y1], fill=(22, 110, 48) if i % 2 else (28, 128, 56))
    d.line([(0, h * .62), (w, h * .62)], fill=(240, 240, 240), width=4)
    d.ellipse([w * .3, h * .7, w * .7, h * .82], outline=(240, 240, 240), width=4)
    img.alpha_composite(glow((w, h), [('rectangle', [0, h * .6, w, h * .64], RED + (120,), None)], 30))
    logo(img)
    return img


def univers(w, h):
    img = Image.new('RGBA', (w, h), BLACK + (255,))
    img.alpha_composite(glow((w, h), [('ellipse', [w * .15, h * .05, w * .85, h * .6], GOLD + (70,), None)], min(w, h) * .15))
    rnd = random.Random(87)
    dots = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(dots)
    for _ in range(260):  # particules dorées
        x, y, r = rnd.random() * w, rnd.random() * h * .85, rnd.random() * 3 + 1
        d.ellipse([x - r, y - r, x + r, y + r], fill=GOLD + (rnd.randint(60, 200),))
    img.alpha_composite(dots)
    big = Image.open(ROOT / 'img/logo-vm-officiel.png').convert('RGBA')
    side = int(min(w, h) * .55)
    big.thumbnail((side, side))
    big.putalpha(big.getchannel('A').point(lambda a: a * 40 // 255))  # filigrane très discret
    img.alpha_composite(big, ((w - big.width) // 2, int(h * .08)))
    ImageDraw.Draw(img).rectangle([0, h * .9, w, h * .905], fill=GOLD)
    logo(img)
    return img


def manga(w, h):
    img = Image.new('RGBA', (w, h), BLACK + (255,))
    cx, cy = w / 2, h * .42
    rays = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(rays)
    rnd = random.Random(7)
    for i in range(140):  # traits de vitesse façon manga
        a = rnd.random() * math.tau
        r0, r1 = min(w, h) * (.22 + rnd.random() * .15), max(w, h) * 1.2
        col = (RED if i % 3 else GOLD) + (rnd.randint(60, 150),)
        d.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * r1, cy + math.sin(a) * r1)],
               fill=col, width=rnd.randint(2, 7))
    img.alpha_composite(rays.filter(ImageFilter.GaussianBlur(1)))
    img.alpha_composite(glow((w, h), [('ellipse', [cx - w * .3, cy - w * .3, cx + w * .3, cy + w * .3], BLACK + (255,), None)], 60))
    logo(img)
    return img


FONDS = {'studio-neon': studio_neon, 'plateau-pastille': plateau, 'stade-nuit': stade, 'vm-univers': univers, 'manga-vitesse': manga}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, draw in FONDS.items():
        for kind, (w, h) in SIZES.items():
            draw(w, h).convert('RGB').save(OUT / f'{name}-{kind}.jpg', quality=92, optimize=True)
        print('fond prêt :', name)


if __name__ == '__main__':
    main()
