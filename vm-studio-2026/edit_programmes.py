"""Montage exact des trois programmes : plateau 3D, voix, musique et sous-titres."""
import json, os, subprocess, math, textwrap
from pathlib import Path
ROOT=Path(os.environ.get('VM_WORKSPACE_ROOT',Path(__file__).resolve().parents[1]))
BASE=ROOT/'vm-studio-2026'; OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
REND=BASE/'renders'; CACHE=BASE/'edit'; CACHE.mkdir(exist_ok=True)
manifest=json.loads((BASE/'voice-manifest.json').read_text())
ROLES={'VM Pronos':'vm','Pablo':'pablo','Black':'black','Scorpion':'scorpion','La créatrice':'creatrice'}
COLORS={'VM Pronos':'&H0069B9D6&','Pablo':'&H00D9E5EB&','Black':'&H00D2C12F&','Scorpion':'&H0069B9D6&','La créatrice':'&H00D2C12F&'}
def run(cmd):
    subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
def ff(*args):run(['ffmpeg','-y','-hide_banner','-loglevel','error',*map(str,args)])
def stamp(t):return f'{int(t//3600)}:{int(t//60)%60:02}:{t%60:05.2f}'
def esc(t):return t.replace('{','').replace('}','').replace('\n',r'\N')
def header(W,H):
    vert=H>W
    sizes=[38,62,37,27,25] if vert else [24,42,27,22,16]
    names=['Brand','Title','Caption','Role','Small']
    styles=''
    for name,size in zip(names,sizes):
        styles+=f'Style: {name},DejaVu Sans,{size},&H00FFFFFF,&H000000FF,&H00160F07,&H90000000,-1,0,0,0,100,100,0,0,1,2,0,5,30,30,0,1\n'
    return f'''[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{styles}
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def make(fmt,target,W,H):
    rows=manifest[fmt]; vert=H>W; intro=3 if vert else 4; outro=3 if vert else 4
    gap=4/24 if vert else 6/24
    speech_target=target-intro-outro-gap*(len(rows)-1)-1.5
    tempo=sum(r['duration'] for r in rows)/speech_target
    clock=float(intro); audio=[]; video=[]; subtitles=[]; timeline=[]
    folder=CACHE/fmt;folder.mkdir(exist_ok=True)
    def line(a,b,style,value,x,y,tags='',layer=1):
        subtitles.append(f'Dialogue: {layer},{stamp(a)},{stamp(b)},{style},,0,0,0,,{{\\pos({x},{y}){tags}}}{esc(value)}')
    def box(a,b,x,y,w,h,color='&H00160F07&',alpha='&H30&'):
        line(a,b,'Small',f'm 0 0 l {w} 0 l {w} {h} l 0 {h}',x,y,rf'\an7\p1\bord0\c{color}\alpha{alpha}',0)
    def prepare(shot):
        p=CACHE/(shot+('-v' if vert else '-h')+'.mp4')
        if p.exists():
            try:
                duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)]))
                if duration<3.95:p.unlink()
            except Exception:p.unlink(missing_ok=True)
        if not p.exists():
            src=REND/(shot+'.mp4')
            crop='crop=w=trunc(ih*9/16/2)*2:h=ih,' if vert else ''
            filters=crop+f'minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},tpad=stop_mode=clone:stop_duration=0.2'
            ff('-stream_loop','-1','-i',src,'-vf',filters,'-t','4','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-g','24',p)
        return p
    def segment(shot,dur,index):
        p=folder/f'v-{index:03d}.mp4'
        ff('-stream_loop','-1','-i',prepare(shot),'-frames:v',round(dur*24),'-an','-c:v','libx264','-preset','ultrafast','-crf','18','-pix_fmt','yuv420p',p)
        video.append(p)
    def silence(dur,index):
        p=folder/f'silence-{index}.wav';ff('-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t',dur,p);audio.append(p)
    opening='portrait' if vert else 'wide'
    segment(opening,intro,0);silence(intro,'intro')
    box(0,target,0,0,W,118 if vert else 56)
    line(0,target,'Brand','VÉLOCE MERCATO',W//2,66 if vert else 29,r'\fsp4\c&H0069B9D6&')
    box(0,intro,50 if vert else 250,220 if vert else 80,W-100 if vert else W-500,210 if vert else 140,alpha='&H20&')
    line(0,intro,'Title','LA MINUTE VM' if vert else ('LE JOURNAL VM' if fmt=='jt' else 'LA PASTILLE VM'),W//2,290 if vert else 125,r'\fad(250,200)')
    line(0,intro,'Small','16 NOVEMBRE 2026  /  ÉDITION DU MATIN',W//2,374 if vert else 183,r'\c&H0069B9D6&')
    for i,row in enumerate(rows):
        p=folder/f'a-{i:03d}.wav'
        pitch={'VM Pronos':1.00,'Pablo':1.10,'Black':.88,'Scorpion':.95,'La créatrice':1.04}[row['speaker']]
        ff('-i',BASE/'audio'/row['audio'],'-af',f'asetrate=22050*{pitch},aresample=24000,atempo={tempo/pitch:.8f},apad=pad_dur=0.05','-ac','1',p)
        # La durée des plans est quantifiée aux images, l'audio est calé au même pas.
        dur=math.ceil(row['duration']/tempo*24)/24
        # Distribuer le petit écart uniquement au dernier plan.
        if i==len(rows)-1:dur=target-outro-clock
        fit=folder/f'af-{i:03d}.wav'
        ff('-i',p,'-af','apad','-t',f'{dur:.6f}',fit);audio.append(fit)
        shot=('portrait' if row['speaker'] in ('VM Pronos','Pablo') else ROLES[row['speaker']]) if vert else ROLES[row['speaker']]
        if fmt=='jt' and i%8==0:shot='wide'
        segment(shot,dur,i+1)
        a,b=clock,clock+dur; timeline.append(dict(start=a,end=b,**row))
        title=row['title']
        if vert:
            titles=['LES BLEUS EN QUARTS','FRANCE 2 – 1 TURQUIE','VANCOUVER 6 – 3 VEGAS','McDAVID : 22 MATCHS','GTA VI • 19 NOVEMBRE','PABLO EST LÀ !','À DEMAIN, LA TEAM']
            title=titles[i]
        title_lines='\n'.join(textwrap.wrap(title.upper(),26 if vert else 54))
        box(a,b,45 if vert else 40,155 if vert else 76,W-90 if vert else W-80,180 if vert else 100,alpha='&H28&')
        line(a,b,'Title',title_lines,W//2,244 if vert else 127,r'\fad(120,100)'+('' if vert else r'\fs34'))
        capY=1510 if vert else 626
        box(a,b,45 if vert else 40,1340 if vert else 555,W-90 if vert else W-80,300 if vert else 130,alpha='&H20&')
        line(a,b,'Role',row['speaker'].upper(),W//2,1388 if vert else 579,r'\c'+COLORS[row['speaker']]+r'\fsp2')
        words=row['text'].split(); chunks=[]; chunk=[]
        maxchars=64 if vert else 110
        for word in words:
            if chunk and len(' '.join(chunk+[word]))>maxchars:chunks.append(chunk);chunk=[]
            chunk.append(word)
        if chunk:chunks.append(chunk)
        for j in range(len(chunks)-1):
            if chunks[j][-1].lower() in {'de','à','du','des','et','le','la','les','un','une','en','pour','avec','sur','au','aux','sa'}:
                chunks[j+1].insert(0,chunks[j].pop())
        c=a
        for ch in chunks:
            d=dur*len(ch)/len(words)
            wrapped='\n'.join(textwrap.wrap(' '.join(ch),40 if vert else 61))
            line(c,min(b,c+d),'Caption',wrapped,W//2,capY,r'\fad(65,65)')
            c+=d
        source='ÉDITION DU 16/11 • FFF / UEFA / NHL / NBA / ATP / ROCKSTAR'
        line(a,b,'Small',source,W//2,1735 if vert else 704,('\\fs18' if vert else '\\fs12')+r'\c&H00D3C5B8&')
        clock=b
        if i<len(rows)-1:
            silence(gap,i);segment(shot,gap,100+i);clock+=gap
    segment(opening,outro,999);silence(outro,'outro')
    box(target-outro,target,45 if vert else 240,180 if vert else 95,W-90 if vert else W-480,270 if vert else 150,alpha='&H20&')
    line(target-outro,target,'Title','LA TEAM VM',W//2,265 if vert else 145,r'\fad(150,300)')
    line(target-outro,target,'Small','PABLO • BLACK • SCORPION • LA CRÉATRICE',W//2,365 if vert else 205,'\\fs'+('23' if vert else '19'))
    line(0,target,'Small','Personnages fictifs • Voix de synthèse',W//2,1810 if vert else 44,('\\fs20' if vert else '\\fs10')+r'\c&H00B4B4B4&')
    ass=folder/'titres.ass';ass.write_text(header(W,H)+'\n'.join(subtitles)+'\n')
    for name,paths in [('audio',audio),('video',video)]:
        (folder/f'{name}.txt').write_text(''.join("file '"+str(p.resolve()).replace("'","'\\''")+"'\n" for p in paths))
    speech=folder/'voix.wav';ff('-f','concat','-safe','0','-i',folder/'audio.txt','-af','highpass=f=65,loudnorm=I=-16:TP=-1.8:LRA=10','-ar','48000','-ac','2',speech)
    filename={'jt':'VM-Journal-3D-16-novembre-2026.mp4','reel':'VM-Reel-3D-16-novembre-2026.mp4','pastille':'VM-Pastille-3D-16-novembre-2026.mp4'}[fmt]
    dest=OUT/filename
    music=ROOT/'reel3d/musique-originale.wav'
    filter_audio=f"[1:a]apad,atrim=0:{target}[voice];[2:a]atrim=0:{target},asetpts=PTS-STARTPTS,volume='if(lt(t,{intro}),0.50,if(gt(t,{target-outro}),0.50,0.10))':eval=frame,afade=t=out:st={target-1}:d=1[music];[voice][music]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.88[a]"
    ff('-f','concat','-safe','0','-i',folder/'video.txt','-i',speech,'-stream_loop','-1','-i',music,'-filter_complex',filter_audio,'-vf',f'ass={ass}','-map','0:v','-map','[a]','-t',target,'-r','24','-c:v','libx264','-preset','fast','-crf','21','-maxrate','1000k' if fmt=='jt' else '3500k','-bufsize','5M','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',dest)
    (folder/'timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2))
    print('TERMINE',fmt,dest,flush=True)
if __name__=='__main__':
    import sys
    wanted=sys.argv[1:] or ['reel','pastille','jt']
    for fmt in wanted:
        if fmt=='reel':make(fmt,60,1080,1920)
        elif fmt=='pastille':make(fmt,150,1280,720)
        elif fmt=='jt':make(fmt,600,1280,720)
