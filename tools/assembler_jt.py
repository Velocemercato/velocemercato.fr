#!/usr/bin/env python3
"""Assembler les trois JT frais en programme long, sans upload ni direct."""
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
from pastille_media import probe


def assemble(root, moment, date, output, master_dir=None):
    root,output=Path(root),Path(output)
    metadata_dir = Path(master_dir) if master_dir else root/'studio/tv'
    media_dir = Path(master_dir) if master_dir else root/'studio/tmp'
    parts=[]
    for universe in ['foot','actus','gaming']:
        choices=[]
        for metadata in metadata_dir.glob('*.json'):
            if metadata.name.startswith('_'):continue
            row=json.loads(metadata.read_text())
            if (row.get('univers')==universe and row.get('format')=='edition'
                    and row.get('moment')==moment and row.get('date','')[:10]==date):choices.append(row)
        if not choices:raise RuntimeError(f'JT {universe} du {date} ({moment}) absent : aucun programme complet inventé.')
        row=max(choices,key=lambda item:item['date'])
        if not re.fullmatch(r'[a-z0-9-]+\.mp4',row.get('fichier','')):raise ValueError('Fichier de JT invalide')
        file=media_dir/row['fichier']
        if not file.is_file():raise RuntimeError(f'Rendu local manquant : {file.name}. Générer les trois JT en aperçu avant assemblage.')
        info=probe(file);video=next(stream for stream in info['streams'] if stream['codec_type']=='video')
        audio=next(stream for stream in info['streams'] if stream['codec_type']=='audio')
        signature=(video['codec_name'],video['width'],video['height'],video['pix_fmt'],video['avg_frame_rate'],audio['codec_name'],audio['sample_rate'],audio['channels'])
        parts.append((row,file,float(info['format']['duration']),signature))
    if len({part[3] for part in parts})!=1:raise RuntimeError('Formats des JT incompatibles : ne pas dégrader les sources par une conversion implicite.')
    if output.resolve() in [part[1].resolve() for part in parts]:raise ValueError('Le programme ne doit pas écraser un JT source.')
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='pastille-programme-') as folder:
        listing=Path(folder)/'concat.txt'
        listing.write_text(''.join("file '"+str(file.resolve()).replace("'","'\\''")+"'\n" for _,file,_,_ in parts))
        subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),
                        '-c','copy','-movflags','+faststart',str(output)],check=True)
    offset=0;chapters=[]
    for row,_,duration,_ in parts:
        chapters.append({'debut_secondes':round(offset,3),'univers':row['univers'],'titre':row['titre'],'id':row['id']})
        offset+=duration
    data={'date':date,'moment':moment,'duree_mesuree':float(probe(output)['format']['duration']),
          'chapitres':chapters,'youtube':'préparation seulement','twitch':'préparation seulement','publie':False}
    output.with_suffix('.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    def clock(seconds):
        seconds=int(seconds);return f'{seconds//3600:02}:{seconds//60%60:02}:{seconds%60:02}' if seconds>=3600 else f'{seconds//60:02}:{seconds%60:02}'
    output.with_suffix('.txt').write_text('Programme enregistré, généré par IA avec des personnages inventés.\n\n'+
      '\n'.join(clock(item['debut_secondes'])+' '+item['titre'] for item in chapters)+'\n')
    return data


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--moment',choices=['matin','midi','soir'],required=True)
    parser.add_argument('--date',default=dt.datetime.now(ZoneInfo('Europe/Paris')).date().isoformat())
    parser.add_argument('--output',type=Path)
    parser.add_argument('--masters',type=Path,help='Répertoire des originaux HD et de leurs métadonnées')
    args=parser.parse_args()
    output=args.output or ROOT/'studio/tmp'/f'programme-{args.date}-{args.moment}.mp4'
    result=assemble(ROOT,args.moment,args.date,output,args.masters)
    print(f"Programme prêt en local : {output.name} · {round(result['duree_mesuree'])} s · aucune diffusion")
