"""Illustrated, captioned bulletin; no fake lip sync or time-stretched narration."""
import json,subprocess,sys,math
from pathlib import Path
B=Path(__file__).resolve().parent
name=sys.argv[1];D=B/name;M=json.loads((D/'manifest.json').read_text())
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
titles={'sport':'LE JT SPORT','actus':'LE JT ACTUS','gaming':'LE JT GAMING'}
colors={'sport':'0x9cd9ea','actus':'0xe6bd66','gaming':'0xc5adff'}
def run(a):subprocess.run(a,check=True)
def at(t):
 c=round(t*100);return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'
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
elapsed=0;chapters=[]
for i,r in enumerate(M):
 ass=head;chunks=[];cur=[]
 for word in r['boundaries']:
  if cur and (len(' '.join(w['text'] for w in cur+[word]))>34 or len(cur)>=6):chunks.append(cur);cur=[]
  cur.append(word)
 if cur:chunks.append(cur)
 for j,ch in enumerate(chunks):
  start=ch[0]['start'];end=chunks[j+1][0]['start']-.04 if j+1<len(chunks) else min(r['duration'],ch[-1]['start']+ch[-1]['duration']+.15)
  text=' '.join(w['text'] for w in ch).replace('{','').replace('}','')
  ass+=f'Dialogue: 0,{at(start)},{at(max(start+.15,end))},Default,,0,0,0,,{text}\n'
 cap=D/f'caption-{i:02}.ass';cap.write_text(ass)
 chapter=D/f'chapter-{i:02}.txt';chapter.write_text(r['chapter'])
 source=B.parent/'assets'/f"{r['portrait']}-presentateur.png"
 frame=D/f'frame-{i:02}.png'
 vf=f"scale=-2:1280,crop=720:1280,setsar=1,drawbox=x=0:y=0:w=720:h=220:color=0x08172a:t=fill,drawbox=x=0:y=1000:w=720:h=280:color=0x08172a@0.93:t=fill,drawtext=fontfile={BOLD}:text='VÉLOCE MERCATO':fontsize=23:fontcolor=0xe6bd66:x=(w-tw)/2:y=28,drawtext=fontfile={BOLD}:text='{titles[name]}':fontsize=45:fontcolor=white:x=(w-tw)/2:y=67,drawtext=fontfile={FONT}:text='ÉDITION DU 16 NOVEMBRE 2026':fontsize=21:fontcolor={colors[name]}:x=(w-tw)/2:y=128,drawtext=fontfile={BOLD}:textfile={chapter}:fontsize=25:fontcolor=white:x=(w-tw)/2:y=175,drawtext=fontfile={BOLD}:text='{r['speaker'].upper()}':fontsize=26:fontcolor=0xe6bd66:x=(w-tw)/2:y=1182,drawtext=fontfile={FONT}:text='MANGA ILLUSTRÉ · VOIX DE SYNTHÈSE':fontsize=17:fontcolor=0xa9b5c7:x=(w-tw)/2:y=1235"
 run(['ffmpeg','-y','-v','error','-filter_threads','1','-i',str(source),'-vf',vf,'-frames:v','1',str(frame)])
 output=D/f'part-{i:02}.mp4'
 run(['ffmpeg','-y','-v','error','-threads','2','-filter_threads','1','-loop','1','-framerate','25','-i',str(frame),'-i',str(D/r['audio']),'-vf',f'ass={cap}', '-af','loudnorm=I=-16:TP=-1.5:LRA=9','-t',str(r['duration']),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-threads','2','-preset','veryfast','-tune','stillimage','-crf','25','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-ar','48000','-ac','2','-movflags','+faststart',str(output)])
 chapters.append({'start_seconds':elapsed,'title':r['chapter'],'speaker':r['speaker'],'sources':r['sources']});elapsed+=math.ceil(r['duration']*25)/25
 print('RENDERED',name,i,flush=True)
(D/'chapters.json').write_text(json.dumps(chapters,ensure_ascii=False,indent=2))
(D/'concat.txt').write_text(''.join(f"file 'part-{i:02}.mp4'\n" for i in range(len(M))))
out=D/f'VM-JT-{name.title()}-2026-11-16.mp4'
run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(D/'concat.txt'),'-c','copy','-movflags','+faststart',str(out)])
print('DONE',out,flush=True)
