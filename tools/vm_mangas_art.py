#!/usr/bin/env python3
"""Create shareable original VM MANGAS art from our own SVG (not anime footage)."""
from pathlib import Path
import io
import cairosvg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/"mangas"/"assets"
svg=folder/"vm-87.svg"
assert svg.is_file()
png=folder/"vm-87.png"
cairosvg.svg2png(url=str(svg),write_to=str(png),output_width=1200,output_height=900)
src=Image.open(png).convert("RGB")
W,H=1080,1350
im=Image.new("RGB",(W,H),(8,9,20))
d=ImageDraw.Draw(im)
for y in range(H):
    t=y/H
    d.line((0,y,W,y),fill=(int(10+30*t),int(8+5*t),int(25+10*t)))
# Source illustration is original and already contains the number 87.
art=src.resize((1080,810),Image.Resampling.LANCZOS)
im.paste(art,(0,0))
d=ImageDraw.Draw(im)
d.rectangle((0,800,W,1350),fill=(9,14,31))
d.rectangle((0,802,W,827),fill=(236,36,74))
try:
    bold=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",74)
    sub=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",39)
    small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",29)
except OSError:
    bold=sub=small=ImageFont.load_default()
d.text((58,867),"VM MANGAS 87",font=bold,fill="#ffe275",stroke_width=3,stroke_fill="#000000")
d.text((60,990),"LE CLUB NOSTALGIE",font=sub,fill="white")
d.text((60,1060),"ÉPISODES OFFICIELS • FOOT & MANGAS",font=small,fill="#efcfb8")
d.rounded_rectangle((45,1130,1035,1258),radius=18,fill="#de1d42",outline="#ffbc9f",width=3)
d.text((73,1172),"VELOCEMERCATO.FR/MANGAS",font=sub,fill="#fff7ee")
out=folder/"vm-mangas-reseaux.jpg"
im.save(out,"JPEG",quality=89,optimize=True,subsampling=0)
print(png, png.stat().st_size, out, out.stat().st_size)
