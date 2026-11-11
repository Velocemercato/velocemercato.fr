#!/usr/bin/env python3
"""Trois flashes originaux par bloc : articles sourcés, illustration VM, voix Piper et musique VM."""
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PARIS = ZoneInfo('Europe/Paris')
GENRES = {'foot': ('articles.json', 'VM FOOT', 'img/v2-mercato.webp'),
          'actus': ('actus/news.json', 'VM ACTUS', 'img/v2-actus.webp'),
          'gaming': ('vm-gaming/news.json', 'VM GAMING', 'vm-gaming/img/vm-gaming.webp')}


def read(path, default):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


def upcoming(now):
    local = now.astimezone(PARIS)
    for days in (0, 1):
        for hour in (9, 12, 20):
            target = (local + dt.timedelta(days=days)).replace(hour=hour, minute=0, second=0, microsecond=0)
            if target - local >= dt.timedelta(minutes=20):
                return target


def choose(rows, genre, known, now):
    used = {str(row.get('article_id')) for row in known if row.get('univers') == genre and row.get('article_id')}
    for row in sorted(rows, key=lambda r:str(r.get('publishedAt','')), reverse=True):
        try:
            stamp = dt.datetime.fromisoformat(str(row.get('publishedAt')).replace('Z','+00:00'))
        except (ValueError, TypeError):
            continue
        if stamp.tzinfo is None or not dt.timedelta(0) <= now - stamp <= dt.timedelta(hours=24):
            continue
        if not row.get('id') or str(row['id']) in used or not row.get('titre') or not row.get('resume'):
            continue
        sources = [s for s in row.get('sources',[]) if s.get('nom') and str(s.get('url','')).startswith('https://')]
        if not sources:
            continue
        if genre == 'gaming' and re.search(r'\b(chapitre|manga|one piece|dragon ball)\b',row['titre'],re.I) and not re.search(r'\b(jeu|gaming|console|playstation|xbox|switch)\b',row['titre'],re.I):
            continue
        return row, sources[0]
    return None


def lines(draw, text, font, width):
    result, current = [], ''
    for word in str(text).split():
        test = (current + ' ' + word).strip()
        if current and draw.textlength(test,font=font)>width:
            result.append(current)
            current=word
        else:
            current=test
    if current:
        result.append(current)
    return result


def poster(root, genre, row, source, output):
    from PIL import Image, ImageOps, ImageDraw, ImageFont
    image=ImageOps.fit(Image.open(root/GENRES[genre][2]).convert('RGB'),(1080,1920))
    shade=Image.new('RGBA',image.size,(0,0,0,0))
    d=ImageDraw.Draw(shade)
    for y in range(1920):
        alpha=int(220*max(0,1-y/800)) if y<800 else int(230*max(0,(y-1050)/870))
        d.line((0,y,1080,y),fill=(7,9,17,alpha))
    image=Image.alpha_composite(image.convert('RGBA'),shade)
    d=ImageDraw.Draw(image)
    bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    regular='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font=lambda size:ImageFont.truetype(bold,size)
    d.rounded_rectangle((58,70,530,155),radius=22,fill='#e9be70')
    d.text((85,82),GENRES[genre][1],font=font(48),fill='#100e13')
    size=64
    while size>40:
        wrapped=lines(d,row['titre'],font(size),960)
        if len(wrapped)<=5:break
        size-=2
    for index,line in enumerate(wrapped[:5]):
        d.text((58,210+index*(size+18)),line,font=font(size),fill='white',stroke_width=3,stroke_fill='#101017')
    d.rounded_rectangle((55,1450,1025,1785),radius=28,fill=(9,11,22,238),outline='#e9be70',width=3)
    d.text((85,1480),'UNE INFO · LA SOURCE · L’ESSENTIEL',font=font(28),fill='#e9be70')
    for index,line in enumerate(lines(d,row['resume'],ImageFont.truetype(regular,34),900)[:5]):
        d.text((85,1540+index*47),line,font=ImageFont.truetype(regular,34),fill='white')
    d.text((70,1818),('Source : '+source['nom'])[:65],font=font(25),fill='#f6d99e')
    d.text((70,1860),'velocemercato.fr · Voix et visuel IA',font=font(25),fill='white')
    image.convert('RGB').save(output,quality=93)


def render(root, genre, row, source, out):
    import update_debat as D
    from tools.tiktok_metricool import check_video
    with tempfile.TemporaryDirectory() as folder:
        folder=Path(folder)
        image,voice=folder/'plan.jpg',folder/'voix.wav'
        poster(root,genre,row,source,image)
        text=f"{GENRES[genre][1]}. {row['titre']}. {row['resume']}. Selon {source['nom']}. Retrouve les infos sur Véloce Mercato point F R."
        engine=D.speak(text,'PRESENTATEUR',voice,True)
        duration=D.duration(voice)+1.8
        if engine!='piper' or not 10<=duration<=58:
            raise RuntimeError('Voix ou durée hors format : aucun flash publié.')
        music=root/'studio/assets/beat.m4a'
        # Zoom léger, musique VM en fond et texte lisible en permanence.
        filters=(f"[0:v]zoompan=z='min(zoom+0.00012,1.012)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps=30,format=yuv420p[v];"
                 f"[1:a]loudnorm=I=-17:TP=-2:LRA=7,apad=pad_dur=2[a];[2:a]volume=0.055[m];[a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95,afade=t=out:st={duration-1:.2f}:d=1[aout]")
        subprocess.run(['ffmpeg','-v','error','-y','-loop','1','-framerate','30','-i',str(image),'-i',str(voice),'-stream_loop','-1','-i',str(music),'-filter_complex',filters,'-map','[v]','-map','[aout]','-t',f'{duration:.2f}','-c:v','libx264','-preset','veryfast','-crf','25','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(out)],check=True)
        check_video(out)
        return round(duration)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prochain',action='store_true',help='Préparer le prochain bloc même en avance.')
    args=parser.parse_args()
    now=dt.datetime.now(dt.timezone.utc)
    target=upcoming(now)
    if not args.prochain and target-now>dt.timedelta(hours=2):
        print('Aucun bloc à préparer maintenant.')
        return
    from tools.reseaux_jt import push_branch
    kit_path=ROOT/'studio/reseaux.json'
    known=read(kit_path,[])
    made,entries=[],[]
    with tempfile.TemporaryDirectory() as folder:
        for genre,(file,label,_) in GENRES.items():
            ident=f'{genre}-teaser-{target:%Y%m%d-%H%M}'
            if any(row.get('id')==ident for row in known):continue
            choice=choose(read(ROOT/file,[]),genre,known,now)
            if not choice:
                print(f'::notice::{genre} : aucune brève inédite et sourcée, aucun flash inventé.')
                continue
            row,source=choice
            out=Path(folder)/(ident+'-vertical.mp4')
            duration=render(ROOT,genre,row,source,out)
            made.append(out)
            caption=f"{row['titre']}\n\n{row['resume']}\n\nSource : {source['nom']}\n{source['url']}\n\nToute l’info : https://velocemercato.fr/\nFlash original VM, voix et visuel générés par IA. #VeloceMercato #VMUnivers"
            entries.append({'id':ident,'univers':genre,'titre':row['titre'],'article_id':row['id'],'date':now.isoformat(),'planned_for':target.isoformat(),'duree':duration,'duree_verticale':duration,'texte':caption,'texte_vertical':caption,'format':'teaser-original','sources':[source]})
        if not made:return
        sha=push_branch(made)
        for row,path in zip(entries,made):row['verticale']=f'https://cdn.jsdelivr.net/gh/Velocemercato/velocemercato.fr@{sha}/{path.name}'
        kit_path.write_text(json.dumps((entries+known)[:150],ensure_ascii=False,indent=1)+'\n')
        (ROOT/'studio/teasers.json').write_text(json.dumps({'prepared_at':now.isoformat(),'planned_for':target.isoformat(),'videos':entries},ensure_ascii=False,indent=2)+'\n')
        print(f'{len(entries)} nouveaux flashes originaux prêts pour le bloc {target:%H:%M}. Aucune publication sociale dans ce rendu.')


if __name__=='__main__':
    main()
