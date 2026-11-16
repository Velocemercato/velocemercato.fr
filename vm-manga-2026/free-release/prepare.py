import asyncio,json,os,sys,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B.parents[2]/'voice-neural-runtime'))
import edge_tts
from edge_tts import voices,communicate
if os.getenv('SSL_CERT_FILE'):
 for m in (voices,communicate):m._SSL_CTX.load_verify_locations(cafile=os.environ['SSL_CERT_FILE'])
ROWS=[
 ('Heineguez','fr-FR-HenriNeural','heineguez','Les Bleus qualifiés, le rugby français sur le podium mondial, et Grand Theft Auto six cette semaine : voici la minute Véloce Mercato du seize novembre. Je suis Heineguez. Nouveau plateau manga, même envie de comprendre le sport et le gaming.'),
 ('Pablo','fr-BE-GerardNeural','pablo','Moi, c’est Pablo. Oui, toujours chauve ! La France a battu la Turquie deux à un à Bordeaux et rejoint les quarts de finale de la Ligue des nations. Le tirage est prévu vendredi vingt novembre.'),
 ('Black','fr-FR-RemyMultilingualNeural','black','Côté rugby, la France retrouve la troisième place mondiale après sa victoire vingt et un à dix-neuf contre l’Afrique du Sud. Une belle progression, sans oublier que le prochain match reste à jouer.'),
 ('Scorpions','fr-CH-FabriceNeural','scorpions','Et moi, c’est Scorpions. Pour le gaming, Rockstar annonce Grand Theft Auto six le dix-neuf novembre. Le préchargement est déjà ouvert. Une date annoncée, pas encore un test du jeu !'),
 ('Heineguez','fr-FR-HenriNeural','heineguez','Les sources sont dans la description. Dites-nous quel sujet vous voulez voir développé dans le prochain journal !')]
async def main():
 rows=[]
 for i,(name,voice,portrait,text) in enumerate(ROWS):
  f=B/f'voice-{i}.mp3';boundaries=[]
  c=edge_tts.Communicate(text,voice=voice,rate='+0%',pitch='+0Hz',boundary='WordBoundary',proxy=os.getenv('HTTPS_PROXY'))
  with f.open('wb') as o:
   async for x in c.stream():
    if x['type']=='audio':o.write(x['data'])
    elif x['type']=='WordBoundary':boundaries.append({'start':x['offset']/1e7,'duration':x['duration']/1e7,'text':x['text']})
  dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(f)]))
  rows.append(dict(speaker=name,voice=voice,portrait=portrait,text=text,audio=f.name,duration=dur,boundaries=boundaries))
  print(name,round(dur,2),flush=True)
 (B/'manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 print('TOTAL',sum(r['duration'] for r in rows))
asyncio.run(main())
