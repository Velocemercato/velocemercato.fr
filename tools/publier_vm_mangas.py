#!/usr/bin/env python3
"""Campagne UNIQUE VM MANGAS n°87 : posts Meta + IG Stories/Reels + YouTube Short original.
N'utilise JAMAIS les vidéos de mangas : seul l'art original 87 est posté.
Chaque action porte un accusé chiffré avant l'envoi ; aucun doublon en cas de réexécution.
"""
import argparse
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.diffuser_jt import HTTP, State, YouTube, DeliveryError, access_token, git_save, public_allowed
from tools.publier_meta import Graph, instagram_image, instagram_reel, ensure_meta_targets

PHOTO="https://velocemercato.fr/mangas/assets/vm-mangas-reseaux.jpg"
STORY="https://velocemercato.fr/mangas/assets/vm-mangas-story.jpg"
VIDEO="https://velocemercato.fr/mangas/assets/vm-mangas-short.mp4"
URL="https://velocemercato.fr/mangas/"
CAPTION=(
    "📺👑 VM MANGAS 87 : LE GRAND RETOUR DE NOTRE ENFANCE ! ⚽🐉\n\n"
    "Olive et Tom, L'École des champions, Dragon Ball Z : redécouvre les séries cultes "
    "dans notre nouveau club sur Véloce Mercato. "
    "Épisodes publiés par leurs chaînes YouTube officielles, souvenirs et débats !\n\n"
    "👉 "+URL+"\n"
    "Quel dessin animé regardais-tu après l'école ? ❤️\n"
    "#VMMangas #VeloceMercato #OliveEtTom #EcoleDesChampions #DragonBallZ #Nostalgie")
IG_CAPTION=CAPTION.replace("👉 "+URL,"👉 Lien vers velocemercato.fr/mangas dans le profil")
EXPECTED={'meta':'1384363904759072','meta_univers':'1349998758205153'}

def confirm_media():
    for link, expected in ((PHOTO,'image/'),(STORY,'image/'),(VIDEO,'video/')):
        for attempt in range(16):
            try:
                req=urllib.request.Request(link,method='HEAD',headers={'User-Agent':'VM-MANGAS87-launch/1'})
                with urllib.request.urlopen(req,timeout=12) as resp:
                    if resp.status==200 and (resp.headers.get('Content-Type') or '').startswith(expected):
                        print('::notice::Visuel public prêt : '+link.rsplit('/',1)[-1],flush=True)
                        break
            except Exception:
                pass
            if attempt==15: raise DeliveryError('Fichier média public indisponible : '+link.rsplit('/',1)[-1])
            time.sleep(10)

def action(state,key,callback):
    done=state.data.setdefault('vm_mangas_87',{})
    if key in done:
        print('::notice::Déjà traité, pas de doublon : '+key,flush=True)
        return False
    done[key]={'status':'envoi'}
    state.save()
    try:
        ident=callback()
        if not ident: raise DeliveryError('Aucun identifiant de publication retourné')
        done[key]={'status':'publie','id':str(ident)}
        state.save()
        print('::notice::PUBLIÉ : '+key+' id='+str(ident),flush=True)
        return True
    except Exception as ex:
        done[key]={'status':'echec'}
        state.save()
        print('::error::Échec '+key+' : '+(str(ex) if isinstance(ex,DeliveryError) else type(ex).__name__)[:170],flush=True)
        return False

def ig_story(graph,meta):
    result=graph.call('POST',meta['ig_id']+'/media',{'media_type':'STORIES','image_url':STORY,'access_token':meta['page_token']})
    container=result.get('id')
    if not container:raise DeliveryError('Story : préparation non confirmée')
    for _ in range(24):
        status=graph.call('GET',container,{'fields':'status_code','access_token':meta['page_token']}).get('status_code')
        if status in (None,'FINISHED'):break
        if status in ('ERROR','EXPIRED'):raise DeliveryError('Story refusée par Instagram')
        time.sleep(5)
    else:raise DeliveryError('Story encore en traitement')
    return graph.call('POST',meta['ig_id']+'/media_publish',{'creation_id':container,'access_token':meta['page_token']}).get('id')

def publish_meta(state):
    ensure_meta_targets(state)
    g=Graph()
    for account in ('meta','meta_univers'):
        meta=state.data.get('tokens',{}).get(account) or {}
        if not meta.get('page_token'):
            print('::notice::Destination non connectée, ignorée : '+account)
            continue
        if str(meta.get('page_id'))!=EXPECTED[account]:
            raise DeliveryError('Page Meta non conforme : '+account)
        page=meta['page_id']
        action(state,account+'/facebook/photo',lambda m=meta,p=page:g.call('POST',p+'/photos',
            {'url':PHOTO,'caption':CAPTION,'access_token':m['page_token']}).get('id'))
        if meta.get('ig_id'):
            action(state,account+'/instagram/photo',lambda m=meta:instagram_image(g,m,PHOTO,IG_CAPTION))
            action(state,account+'/instagram/story',lambda m=meta:ig_story(g,m))
            action(state,account+'/instagram/reel',lambda m=meta:instagram_reel(g,m,
                {'verticale':VIDEO,'texte_vertical':IG_CAPTION}))
        action(state,account+'/facebook/video',lambda m=meta,p=page:g.call('POST',p+'/videos',
            {'file_url':VIDEO,'description':CAPTION,'access_token':m['page_token']}).get('id'))

def publish_youtube(state):
    if os.getenv('VM_AUTO_YOUTUBE')!='true':
        print('::notice::YouTube non activé; aucune vidéo envoyée')
        return
    key='youtube/short'
    if key in state.data.setdefault('vm_mangas_87',{}):
        print('::notice::Short déjà tenté, aucun nouvel envoi')
        return
    path=ROOT/'mangas/assets/vm-mangas-short.mp4'
    if not path.is_file(): raise DeliveryError('Short absent dans le dépôt')
    http=HTTP()
    client=YouTube(http,state,access_token('youtube',state,http))
    client.verify_channel()
    metadata={'snippet':{'title':'VM MANGAS 87 👑 Les dessins animés de notre enfance #Shorts',
        'description':'Le club nostalgie de Véloce Mercato ! 🐉⚽\n'
          'Olive et Tom, L’École des champions, Dragon Ball Z (lecteurs officiels).\n'
          '👉 https://velocemercato.fr/mangas/\nVisuel et montage originaux VM MANGAS, réalisés avec l’aide de l’IA.',
        'categoryId':'24','defaultLanguage':'fr','tags':['VM Mangas','Véloce Mercato','Olive et Tom','nostalgie','mangas']},
        'status':{'privacyStatus':'private','selfDeclaredMadeForKids':False,'containsSyntheticMedia':True}}
    def send():
        receipt=state.data.setdefault('promos',{}).setdefault('vm-mangas-87-short',{})
        client.upload(path,metadata,receipt)
        if public_allowed():client.make_public(receipt)
        else:receipt['status']='private_ready';state.save()
        return receipt.get('youtube_id') or receipt.get('id') or 'video_envoyee'
    action(state,key,send)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--state',required=True,type=Path)
    args=parser.parse_args()
    state=State(args.state,os.getenv('VM_DIFFUSION_STATE_KEY',''),lambda:git_save(args.state))
    confirm_media()
    publish_meta(state)
    publish_youtube(state)

if __name__=='__main__':
    try:main()
    except Exception as ex:
        print('::error::Campagne VM MANGAS : '+(str(ex) if isinstance(ex,DeliveryError) else type(ex).__name__)[:170])
        sys.exit(1)
