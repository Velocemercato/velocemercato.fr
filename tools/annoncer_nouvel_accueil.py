#!/usr/bin/env python3
"""Annonce unique demandée par Romain sur les trois Pages Facebook, sans programmation récurrente."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.publier_meta import Graph,State,git_save,ensure_meta_targets,DeliveryError
EXPECTED={'meta':'1384363904759072','meta_pronos':'112294796981981','meta_univers':'1349998758205153'}
CAMPAIGN='avis-nouvel-accueil-2026-11-11'
REPORT=ROOT/'studio'/(CAMPAIGN+'.json')

def save_report(rows,path=REPORT):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps({'campaign':CAMPAIGN,'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'results':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def publish(state,graph,caption,image_url,report=REPORT):
 ensure_meta_targets(state)
 if not caption.strip() or 'https://velocemercato.fr/' not in caption:raise DeliveryError('Texte de campagne invalide.')
 if not re.fullmatch(r'https://raw\.githubusercontent\.com/Velocemercato/velocemercato\.fr/[0-9a-f]{40}/campagnes/avis-nouvel-accueil-2026-11-11\.jpg',image_url):raise DeliveryError('Image de campagne non conforme.')
 receipts=state.data.setdefault('annonces_accueil',{});rows=[]
 for account,expected in EXPECTED.items():
  key=CAMPAIGN+'/'+account+'/facebook'
  previous=receipts.get(key)
  if previous:
   rows.append(dict(previous,account=account,page_id=expected,skipped=True));save_report(rows,report);continue
  meta=state.data.get('tokens',{}).get(account) or {}
  if str(meta.get('page_id'))!=expected or not meta.get('page_token'):
   rows.append({'account':account,'page_id':expected,'status':'bloque','reason':'Connexion de cette Page absente.'});save_report(rows,report);continue
  try:identity=graph.call('GET',expected,{'fields':'id,name','access_token':meta['page_token']})
  except DeliveryError:
   rows.append({'account':account,'page_id':expected,'status':'bloque','reason':'Identité de Page non vérifiée.'});save_report(rows,report);continue
  if str(identity.get('id'))!=expected:raise DeliveryError('Identité Meta inattendue. Aucun envoi vers cette destination.')
  receipts[key]={'status':'envoi','reserved_at':dt.datetime.now(dt.timezone.utc).isoformat()}
  state.save() # Refus de persistance = aucun POST. Même clé jamais renvoyée, même après erreur réseau.
  try:
   result=graph.call('POST',expected+'/photos',{'url':image_url,'caption':caption,'published':'true','access_token':meta['page_token']})
   ident=result.get('post_id') or result.get('id')
   if not ident:raise DeliveryError('Publication non confirmée : identifiant absent.')
  except Exception as error:
   receipts[key]={'status':'incertain','reason':type(error).__name__,'date':dt.datetime.now(dt.timezone.utc).isoformat()}
   rows.append(dict(receipts[key],account=account,page_id=expected));save_report(rows,report);state.save();continue
  url=''
  try:url=graph.call('GET',str(ident),{'fields':'permalink_url','access_token':meta['page_token']}).get('permalink_url','')
  except DeliveryError:pass
  if not re.fullmatch(r'https://(?:www\.)?facebook\.com/[^\s<>]+',url or ''):url='https://www.facebook.com/'+str(ident)
  receipt={'status':'publie','post_id':str(ident),'url':url,'date':dt.datetime.now(dt.timezone.utc).isoformat()}
  rows.append(dict(receipt,account=account,page_id=expected));save_report(rows,report)
  receipts[key]=receipt;state.save()
  print('::notice::Annonce accueil publiée : '+account+' → '+url,flush=True)
 return rows

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--state',required=True,type=Path);args=parser.parse_args()
 sha=os.environ.get('GITHUB_SHA','')
 if not re.fullmatch('[0-9a-f]{40}',sha):raise DeliveryError('Version GitHub non vérifiée.')
 caption=(ROOT/'campagnes'/(CAMPAIGN+'.txt')).read_text(encoding='utf-8')
 state=State(args.state,os.environ.get('VM_DIFFUSION_STATE_KEY',''),lambda:git_save(args.state))
 rows=publish(state,Graph(),caption,'https://raw.githubusercontent.com/Velocemercato/velocemercato.fr/'+sha+'/campagnes/'+CAMPAIGN+'.jpg')
 if any(r.get('status')!='publie' for r in rows):raise DeliveryError('Certaines Pages ne confirment pas la publication. Lire le bilan ; ne pas relancer aveuglément.')

if __name__=='__main__':
 try:main()
 except Exception as error:
  print('::error::Annonce interrompue ('+type(error).__name__+'). Les accusés existants sont conservés.',flush=True);sys.exit(1)
