#!/usr/bin/env python3
"""Recompose l'ancien reportage Alexia Depagne en Reel studio au format Loic Tanzi.

- Réutilise uniquement le film original déjà publié sur Véloce Mercato.
- Préserve la voix et l'ordre des images, sans fabriquer de propos attribués à Alexia.
- Habillage 9:16 bleu nuit / or, lumières de plateau, terrain vert.
- Sortie H264/AAC compatible Reel Instagram.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import subprocess
import sys
import math

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "img/reportages/alexia-depagne/reportage-voix.mp4"
OUT = ROOT / "media/reportages/Reportage_Alexia_Depagne_instagram.mp4"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H = 540, 960


def font(size, bold=True):
    p = FONT if bold else FONT_REG
    return ImageFont.truetype(p, size=size)


def centered(draw, txt, top, size, color, bold=True, stroke=0):
    f = font(size, bold)
    bx = draw.textbbox((0, 0), txt, font=f, stroke_width=stroke)
    width = bx[2] - bx[0]
    draw.text(((W - width) / 2, top), txt, font=f, fill=color,
              stroke_width=stroke, stroke_fill="#030714" if stroke else None)


def make_plateau(path):
    im = Image.new("RGB", (W, H))
    pix = im.load()
    for y in range(H):
        t = min(1, y / 580)
        if y < 595:
            base = (7 + int(5*t), 10 + int(7*t), 30 + int(16*t))
            for x in range(W):
                halo = max(0, 1 - abs(x-410)/380) * max(0, 1 - y/600)
                pix[x, y] = (int(base[0] + 12*halo), int(base[1] + 17*halo), int(base[2] + 32*halo))
        else:
            for x in range(W):
                alpha = min(1, (y-595)/360)
                pix[x, y] = (int(9+7*alpha), int(67-30*alpha), int(32-9*alpha))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 592, W, 597], fill="#F8D95A")
    # Zone terrain avec lignes courbes façon plateau du reportage Loïc Tanzi
    for off in [0, 75, 150, 225]:
        yy = 615 + off
        d.line((0, yy, W, yy), fill=(28, 107, 65), width=2)
    d.arc((-95, 675, 635, 975), 190, 350, fill="#247C59", width=3)
    d.line((W//2, 595, W//2, H), fill="#267A50", width=2)
    # Deux batteries de projecteurs du plateau
    for right in (False, True):
        ox = 24 if not right else 448
        for row in range(3):
            for col in range(4):
                xx, yy = ox + col * 18, 77 + row * 20
                d.ellipse((xx-6, yy-6, xx+6, yy+6), fill="#e0e7f5")
                d.ellipse((xx-2, yy-2, xx+2, yy+2), fill="white")
    # Ornementation du plateau dans les marges
    confetti = ["#50b9ef", "#ffe17b", "#ff6583", "#b0eaeb"]
    for i in range(70):
        x = (i*151+41) % W
        y = 180 + ((i*79) % 480)
        if x < 30 or x > 510 or y < 275:
            d.ellipse((x,y,x+2+(i%2),y+2+(i%2)),fill=confetti[i%4])
    # Identité visuelle
    fbrand = font(17)
    d.text((345, 19), "VÉLOCE MERCATO", font=fbrand, fill="#FFD762")
    badge = (152, 77, 388, 110)
    d.rounded_rectangle(badge, radius=15, fill="#FFD356")
    centered(d, "GRAND REPORTAGE", 82, 18, "#0A0D23")
    centered(d, "ALEXIA DEPAGNE", 124, 38, "#FFFFFF", stroke=2)
    centered(d, "BABY-FOOT · ÉQUIPE DE FRANCE", 175, 17, "#FFE37D")
    d.line((31, 218, 509, 218), fill="#243D79", width=2)
    # Studio vertical, vidéo centrale plein cadre
    d.rounded_rectangle((34, 227, 506, 914), radius=19, fill="#060D1F", outline="#C0A14F", width=3)
    d.rectangle((39, 231, 501, 911), outline="#FFFFFF", width=1)
    # De petites touches de marque restent visibles sous la vidéo
    centered(d, "VÉLOCE MERCATO • REPORTAGE INDÉPENDANT", 923, 13, "#F2F6FF")
    im.save(path, format="PNG")


def main():
    if not SRC.exists() or SRC.stat().st_size < 1_000_000:
        raise RuntimeError("La vidéo narrée d'Alexia Depagne est absente ou incomplète.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    cover = OUT.with_suffix(".plateau.png")
    make_plateau(cover)
    # Respecter l'intégralité de l'image et de la bande-son d'origine.
    # Fenêtre 456×678 ; pas de recadrage destructif, seulement des marges.
    filt = (
        "[0:v]fps=25,scale=456:678:force_original_aspect_ratio=decrease,"
        "pad=456:678:(ow-iw)/2:(oh-ih)/2:color=0x060d1f,setsar=1[v];"
        "[1:v][v]overlay=x=42:y=232:shortest=1:format=auto,"
        "format=yuv420p[out]"
    )
    args = [
        "ffmpeg", "-hide_banner", "-nostdin", "-y",
        "-i", str(SRC),
        "-loop", "1", "-framerate", "25", "-i", str(cover),
        "-filter_complex", filt,
        "-map", "[out]", "-map", "0:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
        "-r", "25", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "96k", "-ar", "44100",
        "-movflags", "+faststart", "-shortest",
        str(OUT),
    ]
    print("Recomposition de la vidéo Alexia au format Reel...", flush=True)
    subprocess.run(args, check=True)
    cover.unlink(missing_ok=True)
    if OUT.stat().st_size < 100_000:
        raise RuntimeError("Échec du rendu Instagram : MP4 trop petit.")
    print(f"::notice::REEL ALEXIA PRÊT : {OUT.relative_to(ROOT)} ; {OUT.stat().st_size} octets")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("::error::REEL ALEXIA : " + str(e)[:190])
        sys.exit(1)
