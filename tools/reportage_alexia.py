"""Grand reportage Alexia Depagne : visuels (baby-foot dessiné, aucune photo de la joueuse),
vidéo verticale muette sous-titrée, à partir de sources publiques citées sur la page.
Usage : python tools/reportage_alexia.py"""
import math
import random
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'img/reportages/alexia-depagne'
BOLD = str(ROOT / 'studio/assets/Poppins-Bold.ttf')
MED = str(ROOT / 'studio/assets/Poppins-Medium.ttf')
GOLD, NIGHT, BLUE, RED, WHITE = (244, 207, 85), (6, 10, 28), (40, 90, 220), (225, 36, 58), (255, 255, 255)


def font(path, size):
    return ImageFont.truetype(path, size)


def table(w, h, seed=1, tint=(18, 120, 60)):
    """Table de baby-foot vue de dessus, éclairage de salle de compétition."""
    rnd = random.Random(seed)
    img = Image.new('RGB', (w, h), NIGHT)
    d = ImageDraw.Draw(img)
    # halo de projecteur
    glow = Image.new('L', (w, h), 0)
    ImageDraw.Draw(glow).ellipse((-w * .2, -h * .1, w * 1.2, h * 1.1), fill=150)
    glow = glow.filter(ImageFilter.GaussianBlur(min(w, h) // 5))
    img = Image.composite(Image.new('RGB', (w, h), (40, 46, 80)), img, glow)
    d = ImageDraw.Draw(img)
    m = int(min(w, h) * .08)
    fx0, fy0, fx1, fy1 = m, int(h * .1), w - m, int(h * .9)
    d.rounded_rectangle((fx0 - 26, fy0 - 26, fx1 + 26, fy1 + 26), 30, fill=(70, 38, 18))      # bois
    d.rounded_rectangle((fx0 - 12, fy0 - 12, fx1 + 12, fy1 + 12), 18, fill=(110, 62, 28))
    d.rectangle((fx0, fy0, fx1, fy1), fill=tint)                                               # terrain
    for i in range(8):                                                                         # bandes de tonte
        if i % 2:
            y0 = fy0 + (fy1 - fy0) * i / 8
            d.rectangle((fx0, y0, fx1, y0 + (fy1 - fy0) / 8), fill=tuple(min(255, c + 12) for c in tint))
    lw = max(3, w // 300)
    d.rectangle((fx0 + 10, fy0 + 10, fx1 - 10, fy1 - 10), outline=WHITE, width=lw)
    cy = (fy0 + fy1) // 2
    d.line((fx0 + 10, cy, fx1 - 10, cy), fill=WHITE, width=lw)
    r = (fx1 - fx0) * .14
    d.ellipse(((fx0 + fx1) / 2 - r, cy - r, (fx0 + fx1) / 2 + r, cy + r), outline=WHITE, width=lw)
    gw = (fx1 - fx0) * .3
    for gy in (fy0, fy1):
        d.rectangle(((fx0 + fx1) / 2 - gw / 2, gy - 18, (fx0 + fx1) / 2 + gw / 2, gy), fill=(20, 20, 24)) if gy == fy0 else \
            d.rectangle(((fx0 + fx1) / 2 - gw / 2, gy, (fx0 + fx1) / 2 + gw / 2, gy + 18), fill=(20, 20, 24))
    # barres et joueurs : 8 barres, 1-2-5-3 de chaque côté
    counts = [1, 2, 3, 5, 5, 3, 2, 1]
    for i, n in enumerate(counts):
        y = fy0 + (fy1 - fy0) * (i + .5) / 8
        d.rectangle((fx0 - 60, y - 6, fx1 + 60, y + 6), fill=(190, 196, 210))
        d.rectangle((fx0 - 60, y - 2, fx1 + 60, y), fill=(240, 244, 255))
        for side in (fx0 - 90, fx1 + 50):
            d.rounded_rectangle((side, y - 16, side + 40, y + 16), 10, fill=(20, 20, 26))
        col = BLUE if i in (0, 1, 3, 5) else RED
        off = rnd.uniform(-.06, .06) * (fx1 - fx0)
        for k in range(n):
            x = fx0 + (fx1 - fx0) * (k + 1) / (n + 1) + off
            pw, ph = (fx1 - fx0) * .045, (fy1 - fy0) * .05
            d.rounded_rectangle((x - pw / 2, y - ph / 2, x + pw / 2, y + ph / 2), int(pw / 3), fill=col, outline=(10, 10, 14), width=2)
            d.ellipse((x - pw * .32, y - pw * .32, x + pw * .32, y + pw * .32), fill=(250, 214, 170))
    bx, by = fx0 + (fx1 - fx0) * rnd.uniform(.3, .7), fy0 + (fy1 - fy0) * rnd.uniform(.3, .7)
    br = (fx1 - fx0) * .022
    d.ellipse((bx - br, by - br, bx + br, by + br), fill=(255, 255, 250), outline=(30, 30, 30), width=2)
    # vignette + reflet doré
    vig = Image.new('L', (w, h), 0)
    ImageDraw.Draw(vig).rectangle((0, 0, w, h), fill=255)
    ImageDraw.Draw(vig).ellipse((w * .05, h * .05, w * .95, h * .95), fill=0)
    vig = vig.filter(ImageFilter.GaussianBlur(min(w, h) // 6))
    img = Image.composite(Image.new('RGB', (w, h), (2, 3, 10)), img, vig)
    return img


def shade(img, top=.15, bottom=.92):
    """Dégradé sombre pour lire le texte."""
    w, h = img.size
    g = Image.new('L', (1, h))
    for y in range(h):
        t = y / h
        a = 0 if t < top else min(1, (t - top) / (bottom - top)) ** 1.2
        g.putpixel((0, y), int(235 * a))
    g = g.resize((w, h))
    return Image.composite(Image.new('RGB', (w, h), NIGHT), img, g)


def wrap(d, text, f, maxw):
    lines, cur = [], ''
    for word in text.split():
        test = (cur + ' ' + word).strip()
        if d.textlength(test, font=f) <= maxw:
            cur = test
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


SLIDES = [
    ('GRAND REPORTAGE', 'ALEXIA DEPAGNE', 'La Niçoise qui fait briller le baby-foot féminin', 1, (18, 120, 60)),
    ('L’ENFANCE', 'LA FÊTE FORAINE', 'Tout commence en défiant son père. Puis une petite table Smoby à la maison.', 2, (24, 110, 70)),
    ('À 7 ANS', 'DÉJÀ STRATÈGE', 'À l’école, elle invente des tactiques pendant la pause de midi.', 3, (20, 100, 90)),
    ('À 17 ANS', 'LE CLUB DE NICE', 'Au lycée, elle découvre un club niçois… et n’en repart jamais.', 4, (30, 90, 120)),
    ('2017', 'CHAMPIONNE DU MONDE', 'Avec l’équipe de France, titre mondial par équipe à la Coupe du monde multi-tables.', 5, (120, 90, 20)),
    ('AU CLUB', 'DIRIGEANTE', 'Secrétaire, trésorière, puis présidente de son club.', 6, (60, 60, 130)),
    ('2026', 'SUR LE PODIUM', 'Vice-championne de France en double mixte. 2e par équipe et 2e en simple aux World Series.', 7, (130, 40, 60)),
    ('SON COMBAT', 'PLACE AUX FEMMES', 'Moins de 100 licenciées pour plus de 2 000 pratiquants. Elle crée une association pour les aider.', 8, (90, 30, 110)),
    ('OBJECTIF 2028', 'LA COUPE DU MONDE', '« J’espère voir toujours plus de femmes autour des tables de baby-foot. »', 9, (18, 120, 60)),
]


def text_layer(w, h, eye, title, body, last=False):
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, maxw = 80, w - 160
    fe, ft, fb = font(BOLD, 44), font(BOLD, 112), font(MED, 56)
    tl = wrap(d, title, ft, maxw)
    bl = wrap(d, body, fb, maxw)
    y = h - 260 - len(bl) * 74 - len(tl) * 118 - 90
    ew = d.textlength(eye, font=fe)
    d.rounded_rectangle((x, y, x + ew + 48, y + 72), 36, fill=GOLD)
    d.text((x + 24, y + 10), eye, font=fe, fill=(11, 21, 51))
    y += 100
    for line in tl:
        d.text((x, y), line, font=ft, fill=WHITE, stroke_width=5, stroke_fill=(0, 0, 0))
        y += 118
    y += 14
    for line in bl:
        d.text((x, y), line, font=fb, fill=(235, 238, 248))
        y += 74
    foot = 'Le reportage complet sur velocemercato.fr' if last else 'VÉLOCE MERCATO · GRAND REPORTAGE'
    ff = font(BOLD, 40)
    d.text((x, h - 150), foot, font=ff, fill=GOLD)
    d.line((x, h - 175, w - x, h - 175), fill=(255, 40, 60), width=5)
    return layer


def video(path_mp4, poster):
    W, H, FPS, SEC = 1080, 1920, 24, 6.0
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        n = 0
        for i, (eye, title, body, seed, tint) in enumerate(SLIDES):
            bg = shade(table(1240, 2200, seed, tint), .25, .85)
            txt = text_layer(W, H, eye, title, body, last=i == len(SLIDES) - 1)
            frames = int(SEC * FPS)
            for f in range(frames):
                t = f / (frames - 1)
                z = 1 + .1 * t
                cw, ch = int(1240 / z), int(2200 / z)
                ox = int((1240 - cw) * (.5 + .3 * math.sin(i + t)))
                oy = int((2200 - ch) * (.4 + .2 * t))
                fr = bg.crop((ox, oy, ox + cw, oy + ch)).resize((W, H), Image.BILINEAR).convert('RGBA')
                a = min(1, t * 4) if i else 1
                if a < 1:
                    tl = txt.copy()
                    tl.putalpha(tl.getchannel('A').point(lambda v: int(v * a)))
                    fr.alpha_composite(tl)
                else:
                    fr.alpha_composite(txt)
                fr.convert('RGB').save(tmp / f'f{n:05d}.jpg', quality=88)
                if i == 0 and f == frames // 2:
                    fr.convert('RGB').save(poster, quality=86)
                n += 1
        # Vidéo muette (choix de Romain : pas de musique fabriquée), piste audio silencieuse pour Instagram.
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', str(tmp / 'f%05d.jpg'),
                        '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-shortest',
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '24', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-b:a', '64k', '-movflags', '+faststart', str(path_mp4)], check=True)


def hero():
    w, h = 1600, 900
    img = shade(table(w, h, 1), .1, .95)
    img.save(OUT / 'hero.webp', quality=82)
    og = img.resize((1200, 675)).crop((0, 22, 1200, 652))
    d = ImageDraw.Draw(og)
    d.rounded_rectangle((60, 300, 470, 352), 26, fill=GOLD)
    d.text((82, 306), 'GRAND REPORTAGE', font=font(BOLD, 32), fill=(11, 21, 51))
    d.text((60, 370), 'ALEXIA DEPAGNE', font=font(BOLD, 86), fill=WHITE, stroke_width=4, stroke_fill=(0, 0, 0))
    d.text((60, 478), 'De la fête foraine au titre mondial', font=font(MED, 40), fill=(235, 238, 248))
    d.text((60, 560), 'VÉLOCE MERCATO', font=font(BOLD, 34), fill=GOLD)
    og.save(OUT / 'partage.jpg', quality=86)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    hero()
    video(OUT / 'reportage-vertical.mp4', OUT / 'reportage-vertical.jpg')
    print('ok', *sorted(p.name for p in OUT.iterdir()))
