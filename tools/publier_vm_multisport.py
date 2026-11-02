#!/usr/bin/env python3
"""Campagne UNIQUE, authentifiée, pour VM Multisport — Facebook, Instagram, Story.
Illustrations originales VM. Aucune publicité payante et aucun extrait tiers.
Un reçu est mémorisé AVANT l'envoi pour éviter les doublons à l'échec.
"""
import argparse
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.diffuser_jt import State, DeliveryError, git_save
from tools.publier_meta import Graph, instagram_image, ensure_meta_targets

IMG="https://velocemercato.fr/assets/social/vm-multisport-lancement-portrait.jpg"
URL="https://velocemercato.fr/multisport/"
CAPTION=(
 "⚽🏀🏈🏎️ VÉLOCE MERCATO : TON SPORT, TON UNIVERS ! 🔥\n\n"
 "Le média Foot garde son site historique, et le nouveau VM MULTISPORT t'ouvre les portes "
 "des actus NBA, NFL, F1, MotoGP, tennis, rugby, cyclisme, NHL, MLB, MMA et ski.\n\n"
 "📺 Et les nostalgiques retrouveront aussi VM MANGAS ❤️\n"
 "🏆 Choisis ta discipline, retrouve les actus sourcées et personnalise tes alertes.\n"
 "👉 "+URL+"\n"
 "Quel sport veux-tu suivre en premier ? 👇\n"
 "#VeloceMercato #VMMultisport #VMmangas #NBA #NFL #F1 #MotoGP #Sports"
)
IG=CAPTION.replace("👉 "+URL,"👉 Retrouve VM Multisport à velocemercato.fr/multisport/")
EXPECTED={'meta':'1384363904759072','meta_univers':'1349998758205153'}

def media_public():
    for i in range(10):
        try:
            req=urllib.request.Request(IMG,method='HEAD',headers={'User-Agent':'Veloce-VM-Promo/1.0'})
            with urllib.request.urlopen(req,timeout=13) as res:
                if res.status==200 and 'image/' in res.headers.get('Content-Type',''):
                    print("::notice::Affiche VM Multisport accessible",flush=True)
                    return
        except Exception:pass
        time.sleep(10)
    raise DeliveryError('Affiche VM Multisport non accessible ; aucun post envoyé')

def done_once(state,identifier,func):
    seen=state.data.setdefault('vm_multisport_launch_v1',{})
    if identifier in seen:
        print("::notice::Campagne déjà tentée pour "+identifier,flush=True)
        return
    seen[identifier]={'status':'envoi'}
    state.save()
    try:
        post_id=func()
        if not post_id:raise DeliveryError('Graph Meta : aucun ID de publication reçu')
        seen[identifier]={'status':'publie','id':str(post_id)}
        state.save()
        print("::notice::PUBLIÉ "+identifier+" id="+str(post_id),flush=True)
    except Exception as ex:
        seen[identifier]={'status':'echec'}
        state.save()
        print("::error::Échec "+identifier+" : "+(str(ex) if isinstance(ex,DeliveryError) else type(ex).__name__)[:160],flush=True)

def instagram_story(g,meta):
    r=g.call('POST',meta['ig_id']+'/media',{'media_type':'STORIES','image_url':IMG,'access_token':meta['page_token']})
    cid=r.get('id')
    if not cid:raise DeliveryError('Story : conteneur non créé')
    for i in range(25):
        data=g.call('GET',cid,{'fields':'status_code','access_token':meta['page_token']})
        code=data.get('status_code')
        if code in (None,'FINISHED'):break
        if code in ('ERROR','EXPIRED'):raise DeliveryError('Story rejetée')
        time.sleep(5)
    else:raise DeliveryError('Story non terminée')
    return g.call('POST',meta['ig_id']+'/media_publish',{'creation_id':cid,'access_token':meta['page_token']}).get('id')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--state',required=True,type=Path)
    args=parser.parse_args()
    media_public()
    state=State(args.state,os.getenv('VM_DIFFUSION_STATE_KEY',''),lambda:git_save(args.state))
    ensure_meta_targets(state)
    graph=Graph()
    for account in ('meta','meta_univers'):
        info=state.data.get('tokens',{}).get(account) or {}
        if not info.get('page_token'):
            print('::notice::Pas de connexion Meta pour '+account)
            continue
        if str(info.get('page_id'))!=EXPECTED[account]:
            raise DeliveryError('ID page Meta inattendu : '+account)
        done_once(state,account+'/facebook/photo',lambda m=info:graph.call('POST',m['page_id']+'/photos',{'url':IMG,'caption':CAPTION,'access_token':m['page_token']}).get('id'))
        if info.get('ig_id'):
            done_once(state,account+'/instagram/photo',lambda m=info:instagram_image(graph,m,IMG,IG))
            done_once(state,account+'/instagram/story',lambda m=info:instagram_story(graph,m))
if __name__=='__main__':
    try:main()
    except Exception as ex:
        print('::error::Campagne VM Multisport : '+str(ex)[:180],flush=True)
        sys.exit(1)
