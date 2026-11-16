"""Free local editing pipeline. No paid generation and no stored credentials."""
import asyncio,json,os,sys,subprocess,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B.parents[2]/'voice-neural-runtime'))
import edge_tts
from edge_tts import voices,communicate
if os.getenv('SSL_CERT_FILE'):
 for m in (voices,communicate):m._SSL_CTX.load_verify_locations(cafile=os.environ['SSL_CERT_FILE'])
VOICES={'Heineguez':'fr-FR-HenriNeural','Pablo':'fr-BE-GerardNeural','Black':'fr-FR-RemyMultilingualNeural','Scorpions':'fr-CH-FabriceNeural'}
def probe(p):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)]))
async def main(name):
 d=B/name;d.mkdir(exist_ok=True);sem=asyncio.Semaphore(2)
 rows=[]
 for block in (B/f'{name}.txt').read_text().strip().split('\n\n'):
  header,text=block.split('\n',1);speaker,chapter,sources=header.split('|')
  rows.append(dict(speaker=speaker,voice=VOICES[speaker],portrait=speaker.lower(),chapter=chapter,text=text,sources=sources.split(',')))
 async def make(i,r):
  f=d/f'voice-{i:02}.mp3';j=f.with_suffix('.json');key=hashlib.sha256((r['voice']+r['text']).encode()).hexdigest()
  if f.exists() and j.exists() and json.loads(j.read_text()).get('key')==key:
   data=json.loads(j.read_text());r.update(audio=f.name,duration=probe(f),boundaries=data['boundaries']);return
  async with sem:
   for attempt in range(3):
    try:
     boundaries=[];c=edge_tts.Communicate(r['text'],voice=r['voice'],rate='+0%',pitch='+0Hz',boundary='WordBoundary',proxy=os.getenv('HTTPS_PROXY'))
     with f.open('wb') as o:
      async for x in c.stream():
       if x['type']=='audio':o.write(x['data'])
       elif x['type']=='WordBoundary':boundaries.append({'start':x['offset']/1e7,'duration':x['duration']/1e7,'text':x['text']})
     duration=probe(f);assert duration>1 and boundaries
     j.write_text(json.dumps({'key':key,'boundaries':boundaries},ensure_ascii=False))
     r.update(audio=f.name,duration=duration,boundaries=boundaries)
     print(name,i,r['speaker'],round(duration,2),flush=True);break
    except Exception:
     if attempt==2:raise
     await asyncio.sleep(2)
 await asyncio.gather(*(make(i,r) for i,r in enumerate(rows)))
 (d/'manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 print('TOTAL',name,round(sum(r['duration'] for r in rows),3),flush=True)
asyncio.run(main(sys.argv[1]))
