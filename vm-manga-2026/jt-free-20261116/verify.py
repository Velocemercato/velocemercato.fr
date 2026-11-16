import hashlib,json,subprocess,sys,re
from pathlib import Path
B=Path(__file__).resolve().parent;name=sys.argv[1];D=B/name
p=D/f'VM-JT-{name.title()}-2026-11-16.mp4'
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
duration=float(meta['format']['duration']);assert 580<=duration<=620
v=next(s for s in meta['streams'] if s['codec_type']=='video');a=next(s for s in meta['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['codec_name'],v['pix_fmt'])==(720,1280,'h264','yuv420p')
assert a['codec_name']=='aac' and a['sample_rate']=='48000'
subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(p),'-map','0:v','-map','0:a','-f','null','-'],check=True)
z=subprocess.run(['ffmpeg','-v','info','-i',str(p),'-vn','-af','volumedetect','-f','null','-'],capture_output=True,text=True,check=True)
peak=float(re.search(r'max_volume: ([-\d.]+) dB',z.stderr).group(1));assert peak<0
rows=json.loads((D/'manifest.json').read_text())
assert {r['speaker'] for r in rows}=={'Heineguez','Pablo','Black','Scorpions'}
for r in rows:
 assert r['boundaries'] and r['boundaries'][-1]['start']<r['duration']
assert abs(duration-sum(r['duration'] for r in rows))<2
report={'edition':name,'file':str(p),'duration_seconds':duration,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size_bytes':p.stat().st_size,'video':'H.264 720x1280 25 fps','audio':'AAC 48kHz stereo','peak_dbfs':peak,'full_decode':'passed','cast':'Heineguez, Pablo, Black, Scorpions','format':'Portraits manga illustrés, voix de synthèse, sous-titres synchronisés','visual_review':'Representative frames reviewed; illustration, no lip sync','audio_review':'Technical decode and peak measurements only; no claim of human listening'}
(D/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False),flush=True)
