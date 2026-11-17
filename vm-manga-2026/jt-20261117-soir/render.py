"""Finish the accepted animated A-roll at natural speed, preserving attribution.

Run: python render.py
Inputs: presenter.mp4 and speech-aligned transcript.json in this directory.
The source contains a landscape picture inside a portrait canvas. This explicit
social-format conversion crops only to the original newsroom/presenter, and
copies the original HeyGen attribution into the output; it is never removed.
"""
import array
import json
import math
import subprocess
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

B = Path(__file__).resolve().parent
W,H = 720,1280
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
NAVY=(8,15,38); GOLD=(249,200,76); CYAN=(76,218,235)

def call(args):
    return subprocess.run(args,check=True,capture_output=True)

def centered(draw,text,y,size=44,color='white'):
    font=ImageFont.truetype(FONT,size)
    bounds=draw.textbbox((0,0),text,font=font,stroke_width=1)
    assert bounds[2]-bounds[0] < 600,text
    draw.text(((W-(bounds[2]-bounds[0]))/2-bounds[0],y),text,font=font,fill=color)

def card(name,title,rows):
    im=Image.new('RGB',(W,H),NAVY);d=ImageDraw.Draw(im)
    for y in range(0,H,18):
        for x in range(0,W,18):
            d.ellipse((x,y,x+2,y+2),fill=(18,31,58))
    d.polygon([(82,307),(610,281),(640,679),(96,705)],fill=(0,0,0))
    d.polygon([(70,295),(598,269),(628,667),(84,693)],fill=(20,36,63),outline=GOLD,width=4)
    centered(d,title,326,38,GOLD)
    for i,row in enumerate(rows):centered(d,row,421+i*74,42,CYAN if i==0 else 'white')
    im.save(B/(name+'.png'))

def ass_time(t):
    c=round(t*100);return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'

def captions(rows):
    words=[w for row in rows for w in row['words']]
    # Fix clear recognition/spelling errors against the accepted script.
    for w in words:
        w['word']=w['word'].replace("l'un", "l'Inde").replace("d'a", "a")
    chunks=[];cur=[]
    for word in words:
        candidate=' '.join(w['word'].strip() for w in cur+[word])
        if cur and (len(candidate)>35 or word['start']-cur[0]['start']>2.1):
            chunks.append(cur);cur=[]
        cur.append(word)
    if cur:chunks.append(cur)
    font=ImageFont.truetype(FONT,42)
    out='''[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,42,&H00FFFFFF,&H00FFFFFF,&H00260F08,&H00260F08,-1,0,0,0,100,100,0,0,1,4,1,5,144,144,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    srt=[]
    def stamp(t):return ass_time(t).replace('.',',').rjust(11,'0')+'0'
    cues=[]
    for i,ch in enumerate(chunks):
        start=ch[0]['start'];end=min(ch[-1]['end']+.10,chunks[i+1][0]['start'] if i+1<len(chunks) else ch[-1]['end'])
        lines=['']
        for w in ch:
            text=(lines[-1]+' '+w['word'].strip()).strip()
            if font.getlength(text)>420 and lines[-1]:lines.append(w['word'].strip())
            else:lines[-1]=text
        if len(lines)>2:raise ValueError('Subtitle needs regrouping: '+str(lines))
        text='\\N'.join(lines)
        out+=f'Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{{\\pos(360,780)}}{text}\n'
        srt.append(f'{i+1}\n{stamp(start)} --> {stamp(end)}\n'+ '\n'.join(lines)+'\n')
        cues.append({'start':start,'end':end,'text':' '.join(lines)})
    (B/'captions.ass').write_text(out)
    (B/'captions.srt').write_text('\n'.join(srt))
    (B/'caption-cues.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2))

def music(duration):
    sr=48000;result=array.array('h');beat=60/112
    progression=[(146.83,185.0,220.0),(130.81,164.81,196.0),(174.61,220.0,261.63),(164.81,196,246.94)]
    for n in range(math.ceil(duration*sr)):
        t=n/sr;ch=progression[int(t/(beat*4))%4];p=(t%beat)/beat
        pad=sum(math.sin(2*math.pi*f*t) for f in ch)/3*.045
        bass=math.sin(2*math.pi*ch[0]/2*t)*math.exp(-p*8)*.10
        kick=math.sin(2*math.pi*(48*t+10*(1-math.exp(-p*15))))*math.exp(-p*30)*.06
        fade=min(1,t/1.2,max(0,(duration-t)/1.2))
        v=int(32767*(pad+bass+kick)*fade)
        result.append(v);result.append(v)
    with wave.open(str(B/'music.wav'),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes(result.tobytes())

def main():
    rows=json.loads((B/'transcript.json').read_text())
    captions(rows)
    duration=float(call(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(B/'presenter.mp4')]).stdout)
    music(duration)
    card('sport','TURIN · RÉSULTATS',['FILS  4  6  6','JODAR  6  2  2'])
    card('climat','COP31 · COOPÉRATION',['RISQUES CÔTIERS','ÉCOSYSTÈMES','ÉNERGIE · FORMATION'])
    card('gaming','GTA VI · DATE ANNONCÉE',['19 NOVEMBRE','Préchargement ouvert','Sortie ≠ téléchargement'])
    filters='[0:v]split=2[news][brand];[news]crop=228:404:246:438,scale=720:1280,setsar=1,drawbox=x=0:y=0:w=720:h=185:color=0x080f26:t=fill,drawtext=fontfile='+FONT+":text='LE JOURNAL VM':fontsize=42:fontcolor=0xf9c84c:x=(w-tw)/2:y=88[base];[brand]crop=220:150:480:1120,format=rgba,colorkey=0xf7f8fc:0.018:0.004[mark];"
    filters+="[base][1:v]overlay=0:0:enable='between(t,8.0,10.6)'[v1];"
    filters+="[v1][2:v]overlay=0:0:enable='between(t,23.2,27.52)'[v2];"
    filters+="[v2][3:v]overlay=0:0:enable='between(t,33.6,35.2)'[v3];"
    filters+="[v3][mark]overlay=480:1120,ass="+str(B/'captions.ass')+"[v];"
    filters+='[0:a]aresample=48000,asplit=2[voice][key];[4:a]volume=0.24[bed];[bed][key]sidechaincompress=threshold=0.025:ratio=6:attack=15:release=220[duck];[voice][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-2:LRA=9[a]'
    args=['ffmpeg','-y','-v','error','-threads','2','-i',str(B/'presenter.mp4')]
    for name in ['sport','climat','gaming']:args+=['-loop','1','-i',str(B/(name+'.png'))]
    args+=['-i',str(B/'music.wav'),'-filter_complex_threads','2','-filter_complex',filters,'-map','[v]','-map','[a]','-t',str(duration),'-r','25','-c:v','libx264','-preset','fast','-crf','22','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(B/'VM-JT-Soir-20261117.mp4')]
    call(args)
    meta={'duration':duration,'source_video_id':'4b86a3d2cfec5ab56a7448501c7e9545','speech_speed':1.0,'listening_review':'not_performed','head_exclusion':[90,200,630,660],'caption_region':[144,720,576,832],'attribution':'Original HeyGen mark retained from source','format_note':'Portrait crop of the original newsroom picture; no claim of newly generated 3D characters'}
    (B/'production.json').write_text(json.dumps(meta,indent=2))
    print(json.dumps(meta))

if __name__=='__main__':main()
