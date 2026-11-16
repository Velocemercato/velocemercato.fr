import json,subprocess,math,wave,array,sys
from pathlib import Path
B=Path(__file__).resolve().parent
M=json.loads((B/'manifest.json').read_text())
W,H,FPS=720,1280,25
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def run(args):subprocess.run(args,check=True)
def ass_time(t):
 cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
head='''[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,36,&H00FFFFFF,&H00FFFFFF,&H00201708,&H00201708,-1,0,0,0,100,100,0,0,1,3,0,2,45,45,150,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
for i,r in enumerate(M):
 if "--intro-only" in sys.argv and i!=0:continue
 ass=head; words=r['boundaries'];chunks=[];cur=[]
 for word in words:
  if cur and (len(' '.join(w['text'] for w in cur+[word]))>34 or len(cur)>=6):chunks.append(cur);cur=[]
  cur.append(word)
 if cur:chunks.append(cur)
 for j,ch in enumerate(chunks):
  start=ch[0]['start'];end=(chunks[j+1][0]['start']-.04) if j+1<len(chunks) else min(r['duration'],ch[-1]['start']+ch[-1]['duration']+.15)
  text=' '.join(w['text'] for w in ch)
  ass+=f'Dialogue: 0,{ass_time(start)},{ass_time(max(start+.15,end))},Default,,0,0,0,,{text}\n'
 (B/f'caption-{i}.ass').write_text(ass)
 use_video=i==0 and (B/'heineguez-intro.mp4').exists()
 source=B/'heineguez-intro.mp4' if use_video else B.parent/'assets'/f"{r['portrait']}-presentateur.png"
 args=['ffmpeg','-y','-v','error','-threads','2']
 if not use_video:args+=['-loop','1']
 args+=['-i',str(source),'-i',str(B/r['audio'])]
 # Preserve faces in the central crop; the header/footer are local to the social version.
 vf=f"scale=-2:1280,crop=720:1280,setsar=1,fps=25,drawbox=x=0:y=0:w=720:h=200:color=0x08172a:t=fill,drawbox=x=0:y=1000:w=720:h=280:color=0x08172a@0.93:t=fill,drawtext=fontfile={BOLD}:text='VÉLOCE MERCATO':fontsize=24:fontcolor=0xe6bd66:x=(w-tw)/2:y=35,drawtext=fontfile={BOLD}:text='LA MINUTE VM':fontsize=46:fontcolor=white:x=(w-tw)/2:y=82,drawtext=fontfile={FONT}:text='16 NOVEMBRE 2026':fontsize=22:fontcolor=0x9cd9ea:x=(w-tw)/2:y=153,drawtext=fontfile={BOLD}:text='{r['speaker'].upper()}':fontsize=26:fontcolor=0xe6bd66:x=(w-tw)/2:y=1182,drawtext=fontfile={FONT}:text='MANGA ILLUSTRÉ · VOIX DE SYNTHÈSE':fontsize=17:fontcolor=0xa9b5c7:x=(w-tw)/2:y=1235,ass={B/f'caption-{i}.ass'}"
 args+=['-vf',vf,'-af','loudnorm=I=-16:TP=-1.5:LRA=9','-t',str(r['duration']),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','25','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-ar','48000','-ac','2','-movflags','+faststart',str(B/f'part-{i}.mp4')]
 run(args);print('RENDERED',i,flush=True)
(B/'concat.txt').write_text(''.join(f"file 'part-{i}.mp4'\n" for i in range(len(M))))
run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(B/'concat.txt'),'-c','copy','-movflags','+faststart',str(B/'VM-Minute-Manga.mp4')])
run(['ffmpeg','-y','-v','error','-ss','20','-i',str(B/'VM-Minute-Manga.mp4'),'-frames:v','1',str(B/'review.jpg')])
print('DONE',flush=True)
