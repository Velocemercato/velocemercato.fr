#!/usr/bin/env python3
"""Affiches originales VM Multisport pour publication sur les réseaux.
Aucun extrait de match, personnage de série tiers, métrique ou score inventé.
"""
from pathlib import Path
from io import BytesIO
import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/"assets"
OUT=ASSETS/"social"
OUT.mkdir(parents=True,exist_ok=True)
SPORTS=["foot","nba","nfl","f1","motogp","tennis"]
BADGES=["⚽ FOOT","🏀 NBA","🏈 NFL","🏎️ F1","🏍️ MOTOGP","🎾 TENNIS"]

def font(n,condensed=False):
    files=[
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ] if condensed else [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
    ]
    for p in files:
        try:return ImageFont.truetype(p,n)
        except OSError:pass
    return ImageFont.load_default()

def mascot(slug,w,h):
    svg=ASSETS/"mascottes"/("vm-"+slug+".svg")
    assert svg.is_file(),slug
    data=cairosvg.svg2png(url=str(svg),output_width=w,output_height=h)
    return Image.open(BytesIO(data)).convert("RGB")

def gradients(img):
    w,h=img.size
    dr=ImageDraw.Draw(img)
    for y in range(h):
        t=y/max(1,h-1)
        dr.line((0,y,w,y),fill=(int(8+22*t),int(9+6*t),int(23+21*t)))
    return dr

def palette_art(img,y,h,sports):
    dr=ImageDraw.Draw(img)
    w=img.width
    cell=(w-48)//len(sports)
    for i,sport in enumerate(sports):
        left=24+i*cell
        art=mascot(sport,530,400)
        crop=art.crop((100,0,415,380)).resize((cell-8,h),Image.Resampling.LANCZOS)
        img.paste(crop,(left,y))
        dr.rectangle((left,y,left+cell-8,y+h),outline=("#ff4164" if i%2==0 else "#6bb7ff"),width=5)
        dr.text((left+9,y+h-40),sport.upper(),font=font(22,True),fill="white",stroke_width=2,stroke_fill="#05060e")

def draw_badges(draw,labels,start_x,y,wide,fontsize):
    n=len(labels);gap=9
    cell=(wide-gap*(n-1))//n
    for i,label in enumerate(labels):
        x=start_x+i*(cell+gap)
        draw.rounded_rectangle((x,y,x+cell,y+50),radius=12,fill="#112344",outline="#ff405f",width=3)
        # Avoid unsupported emoji font glyphs; text names only.
        name=label.split(" ",1)[-1]
        draw.text((x+10,y+12),name,font=font(fontsize,True),fill="#fff")

def portrait():
    im=Image.new("RGB",(1080,1350));d=gradients(im)
    palette_art(im,20,670,SPORTS[:4])
    d=ImageDraw.Draw(im)
    d.rectangle((0,690,1080,1350),fill="#080e1f")
    d.rectangle((0,690,1080,707),fill="#f12c4b")
    d.text((53,736),"VÉLOCE",font=font(94,True),fill="white",stroke_width=3,stroke_fill="#000")
    d.text((53,850),"MULTISPORT",font=font(108,True),fill="#ffe278",stroke_width=3,stroke_fill="#000")
    d.text((55,982),"TON SPORT. TON UNIVERS.",font=font(45,True),fill="white")
    draw_badges(d,["FOOT","NBA","NFL","F1","MOTOGP","SKI"],52,1052,976,24)
    d.rounded_rectangle((50,1155,1030,1252),radius=18,fill="#ed2d4b",outline="#ffa7b2",width=4)
    d.text((76,1188),"VELOCEMERCATO.FR/MULTISPORT/",font=font(39,True),fill="white")
    d.text((53,1295),"Actualités sourcées • Pages par sport • VM MANGAS",font=font(25),fill="#d6e9ff")
    out=OUT/"vm-multisport-lancement-portrait.jpg"
    im.save(out,"JPEG",quality=89,optimize=True,subsampling=0);print(out.name,out.stat().st_size)

def landscape():
    im=Image.new("RGB",(1200,630));d=gradients(im)
    palette_art(im,20,350,SPORTS[:5])
    d=ImageDraw.Draw(im);d.rectangle((0,370,1200,630),fill="#070b18");d.rectangle((0,370,1200,383),fill="#ff395c")
    d.text((34,403),"VM MULTISPORT",font=font(96,True),fill="#ffdc6b",stroke_width=3,stroke_fill="#06070d")
    d.text((36,518),"FOOT • NBA • NFL • F1 • MOTOGP • TENNIS • SKI",font=font(33,True),fill="#fff")
    d.text((38,575),"velocemercato.fr/multisport/   |   VM MANGAS",font=font(25),fill="#c9d6f2")
    out=OUT/"vm-multisport-lancement-paysage.jpg"
    im.save(out,"JPEG",quality=88,optimize=True,subsampling=0);print(out.name,out.stat().st_size)
if __name__=="__main__":
    portrait()
    landscape()
