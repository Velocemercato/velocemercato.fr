"""Grand reportage Alexia Depagne : visuels (baby-foot dessiné, aucune photo de la joueuse),
vidéo verticale muette sous-titrée, à partir de sources publiques citées sur la page.
Usage : python tools/reportage_alexia.py"""
import math
import random
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


# Chapitres du reportage long : uniquement des faits publics sourcés (liste des sources sur l'article).
CHAPITRES = [
    ('table', 'GRAND REPORTAGE', 'ALEXIA DEPAGNE', ['La Niçoise qui fait briller le baby-foot féminin.', 'Son parcours, étape par étape.']),
    ('table', 'CHAPITRE 1 · L’ENFANCE', 'LA FÊTE FORAINE', ['Tout commence avec ses parents, dans les fêtes foraines.', 'Son premier adversaire : son père.', 'Puis une petite table Smoby à la maison.']),
    ('nombre', 'CHAPITRE 2', '7 ANS', ['À l’école primaire, une table l’attend à la pause de midi.', 'Elle invente déjà ses propres stratégies.']),
    ('nombre', 'CHAPITRE 3 · LE DÉCLIC', '17 ANS', ['Dans son lycée niçois, il y a plusieurs tables.', 'Elle découvre un club à Nice et s’y inscrit.', 'Elle n’en est jamais repartie.']),
    ('table', 'CHAPITRE 4', 'LE PLAISIR D’ABORD', ['Jusqu’à 25 ans, elle joue surtout pour s’amuser,', 'avec quelques compétitions de club', 'pour retrouver ses amis.']),
    ('nombre', 'CHAPITRE 5 · PREMIER PODIUM OFFICIEL', '2015', ['3e du tournoi DYP du samedi au WCS Bonzini,', 'avec Daniel Kelovic.', 'Source : Fédération française de baby-foot.']),
    ('nombre', 'CHAPITRE 6 · LE SOMMET', '2017', ['Sélectionnée en équipe de France', 'pour la Coupe du monde multi-tables.', 'La France remporte le titre mondial par équipe.']),
    ('table', 'CHAPITRE 7 · SES ARMES', 'LA TÊTE ET LES NERFS', ['Le basket et le volley lui ont appris à analyser,', 'à décider vite et à jouer en équipe.', 'Gérer ses émotions : la clé, selon elle.']),
    ('table', 'CHAPITRE 8 · AU SERVICE DU CLUB', 'DIRIGEANTE', ['Secrétaire, puis trésorière,', 'puis présidente de son club.']),
    ('nombre', 'CHAPITRE 9 · MARS 2026', '1re', ['Victoire en double féminin à l’Open national', 'd’Avesnes-les-Aubert, avec Marie Chatillon.', 'Et 2e du simple féminin.']),
    ('nombre', 'CHAPITRE 10 · MAI 2026', '2e', ['Vice-championne de France en double mixte,', 'avec Tom Droit.', 'Source : Fédération française de baby-foot.']),
    ('table', 'CHAPITRE 11 · WORLD SERIES 2026', 'DEUX FOIS 2e', ['2e par équipe avec la France, 2e en simple dames,', 'après seulement deux entraînements :', 'elle avait pris du recul pour d’autres projets.']),
    ('stat', 'CHAPITRE 12 · LE CONSTAT', '- de 100', ['licenciées en France,', 'pour plus de 2 000 pratiquants.', 'Elle se bat pour que ça change.']),
    ('citation', 'CE QU’ELLE PROPOSE', '« Les clubs devraient désigner des personnes référentes pour accompagner les nouvelles joueuses. »', ['Alexia Depagne, Women Sports, juillet 2026']),
    ('table', 'CHAPITRE 13 · SON ASSOCIATION', 'PLACE AUX FEMMES', ['Aider les joueuses à aller en compétition,', 'organiser des initiations,', 'et trouver partenaires et sponsors.']),
    ('citation', 'SA DEVISE', '« Nous sommes des sportifs avec une préparation, une alimentation adaptée et une vraie concentration. »', ['Alexia Depagne, Women Sports, juillet 2026']),
    ('nombre', 'OBJECTIF', '2028', ['La Coupe du monde avec l’équipe de France.', '« J’espère voir toujours plus de femmes', 'autour des tables de baby-foot. »']),
    ('fin', 'VÉLOCE MERCATO', 'MERCI ALEXIA', ['Le reportage complet et les sources', 'sur velocemercato.fr']),
]


def fond(kind, i, w, h):
    if kind == 'table':
        return shade(table(int(w * 1.15), int(h * 1.15), i + 1, [(18, 120, 60), (24, 110, 70), (30, 90, 120), (90, 30, 110), (130, 40, 60)][i % 5]), .25, .85)
    img = Image.new('RGB', (int(w * 1.15), int(h * 1.15)), NIGHT)
    d = ImageDraw.Draw(img)
    W2, H2 = img.size
    for y in range(H2):
        t = y / H2
        d.line((0, y, W2, y), fill=(int(6 + 70 * t), int(10 + 8 * t), int(28 + 40 * (1 - t))))
    for k in range(14):
        a = k / 14 * math.tau
        d.polygon([(W2 / 2, H2 * .38), (W2 / 2 + math.cos(a) * W2 * 1.5, H2 * .38 + math.sin(a) * W2 * 1.5),
                   (W2 / 2 + math.cos(a + .1) * W2 * 1.5, H2 * .38 + math.sin(a + .1) * W2 * 1.5)], fill=(30, 26, 40))
    return img


def calque(kind, w, h, eye, title, lines, n_visibles, last=False):
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, maxw = 80, w - 160
    fe, fb = font(BOLD, 44), font(MED, 54)
    body = []
    for line in lines:
        body += wrap(d, line, fb, maxw)
    centre = kind in ('nombre', 'stat')
    if centre:
        big = font(BOLD, 330 if len(title) <= 4 else 230)
        tw = d.textlength(title, font=big)
        ew = d.textlength(eye, font=fe)
        d.rounded_rectangle(((w - ew) / 2 - 24, h * .2 - 110, (w + ew) / 2 + 24, h * .2 - 38), 36, fill=GOLD)
        d.text(((w - ew) / 2, h * .2 - 100), eye, font=fe, fill=(11, 21, 51))
        d.text(((w - tw) / 2, h * .2), title, font=big, fill=GOLD, stroke_width=8, stroke_fill=(0, 0, 0))
        y = h * .2 + 440
    else:
        ft = font(BOLD, 78 if kind == 'citation' else 112)
        step = 96 if kind == 'citation' else 118
        tl = wrap(d, title, ft, maxw)
        y = h * .22 if kind == 'citation' else h - 260 - len(body) * 72 - len(tl) * step - 110
        ew = d.textlength(eye, font=fe)
        d.rounded_rectangle((x, y, x + ew + 48, y + 72), 36, fill=GOLD)
        d.text((x + 24, y + 10), eye, font=fe, fill=(11, 21, 51))
        y += 100
        for line in tl:
            d.text((x, y), line, font=ft, fill=WHITE, stroke_width=5, stroke_fill=(0, 0, 0))
            y += step
        y += 24
    for k, line in enumerate(body[:n_visibles]):
        col = GOLD if kind == 'citation' else (235, 238, 248)
        lx = (w - d.textlength(line, font=fb)) / 2 if centre else x
        d.text((lx, y), line, font=fb, fill=col, stroke_width=2, stroke_fill=(0, 0, 0))
        y += 72
    d.line((x, h - 175, w - x, h - 175), fill=(255, 40, 60), width=5)
    d.text((x, h - 150), 'velocemercato.fr' if last else 'VÉLOCE MERCATO · GRAND REPORTAGE', font=font(BOLD, 40), fill=GOLD)
    return layer, len(body)


def video(path_mp4, poster):
    """Reportage long, muet et sous-titré : les lignes apparaissent au rythme de lecture."""
    W, H, FPS, PER = 1080, 1920, 24, 2.8
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        n = 0
        for i, (kind, eye, title, lines) in enumerate(CHAPITRES):
            bg = fond(kind, i, W, H)
            _, total = calque(kind, W, H, eye, title, lines, 99)
            layers = [calque(kind, W, H, eye, title, lines, k, last=i == len(CHAPITRES) - 1)[0] for k in range(total + 1)]
            frames = int((3.0 + PER * total + (3 if kind == 'citation' else 1.5)) * FPS)
            BW, BH = bg.size
            for f in range(frames):
                t = f / (frames - 1)
                z = 1 + .12 * t
                cw, ch = int(BW / z), int(BH / z)
                ox = int((BW - cw) * (.5 + .35 * math.sin(i * 1.7 + t)))
                oy = int((BH - ch) * (.35 + .3 * t))
                fr = bg.crop((ox, oy, ox + cw, oy + ch)).resize((W, H), Image.BILINEAR).convert('RGBA')
                secs = f / FPS
                fr.alpha_composite(layers[min(total, int((secs - 1.5) / PER) + 1) if secs > 1.5 else 0])
                if f < 8:
                    fr = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), fr, f / 8)
                fr.convert('RGB').save(tmp / f'f{n:05d}.jpg', quality=85)
                if i == 0 and f == frames - 10:
                    fr.convert('RGB').save(poster, quality=86)
                n += 1
        # Vidéo muette (choix de Romain : pas de musique fabriquée), piste silencieuse pour Instagram.
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', str(tmp / 'f%05d.jpg'),
                        '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-shortest',
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '26', '-tune', 'stillimage', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-b:a', '48k', '-movflags', '+faststart', str(path_mp4)], check=True)


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
