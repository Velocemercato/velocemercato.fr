"""Voix françaises locales, sans API payante ni imitation d'une personne réelle."""
import os, sys, json, wave, re, subprocess
from pathlib import Path
ROOT=Path(os.environ.get('VM_WORKSPACE_ROOT', Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(ROOT/'tts-runtime'))
os.environ['ORT_DISABLE_TELEMETRY']='1'
import onnxruntime
# Synthèse locale : désactiver la télémétrie avant toute session de modèle.
onnxruntime.disable_telemetry_events()
from piper import PiperVoice, SynthesisConfig
BASE=ROOT/'vm-studio-2026'; OUT=BASE/'audio'; OUT.mkdir(parents=True,exist_ok=True)
pack=json.loads((BASE/'scriptpack.json').read_text())
models={n:PiperVoice.load(ROOT/f'voices/fr_FR-{n}-medium.onnx') for n in ('upmc','siwis')}
roles={'VM Pronos':('upmc',1,1.05),'Pablo':('upmc',1,.97),'Black':('upmc',1,1.12),'Scorpion':('upmc',1,1.00),'La créatrice':('siwis',None,1.03)}
def spoken(t):
    for a,b in [('NHL','ène ache elle'),('NBA','ène bé a'),('GTA','gé té a'),('VM','vé ème'),('UEFA','ou é fa'),('PS5','PlayStation cinq')]:
        t=re.sub(r'\b'+a+r'\b',b,t)
    return t
manifest={}
for fmt in ('reel','pastille','jt'):
    rows=[]
    if fmt=='jt':
        for title,plan,screen,sources,lines in pack['jt']:
            rows.extend((speaker,text,title,screen,sources) for speaker,text in lines)
    else:
        rows=[(speaker,text,'LA MINUTE VM' if fmt=='reel' else 'LA PASTILLE VM','16 NOVEMBRE 2026','') for speaker,text in pack[fmt]]
    records=[]
    for i,(speaker,text,title,screen,sources) in enumerate(rows):
        out=OUT/f'{fmt}-{i:03d}.wav'
        model,sid,pace=roles[speaker]
        if not out.exists():
            with wave.open(str(out),'wb') as w:
                models[model].synthesize_wav(spoken(text),w,SynthesisConfig(speaker_id=sid,length_scale=pace,noise_scale=.56,noise_w_scale=.72))
        with wave.open(str(out),'rb') as w: duration=w.getnframes()/w.getframerate()
        records.append(dict(speaker=speaker,text=text,title=title,screen=screen,sources=sources,audio=out.name,duration=duration))
        print(fmt,i,speaker,round(duration,2),flush=True)
    manifest[fmt]=records
    (BASE/'voice-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('VOIX TERMINEES',flush=True)
