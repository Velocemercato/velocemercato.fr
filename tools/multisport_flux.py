#!/usr/bin/env python3
"""Fil multisport sourcé pour VM. RSS Google News, aucun article inventé.
Les liens et titres appartiennent aux éditeurs. Aucune copie de leurs articles.
"""
from __future__ import annotations
import datetime as dt
import email.utils
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'multisport'/'actualites.json'
UTC=dt.timezone.utc
SPORTS={
 'nba': 'NBA basket actualité -WNBA',
 'nfl': 'NFL football américain actualité',
 'f1': 'Formule 1 F1 Grand Prix actualité',
 'motogp': 'MotoGP moto Grand Prix actualité',
 'tennis': 'ATP WTA tennis résultats actualité',
 'rugby': 'Top 14 rugby XV international actualité',
 'cyclisme': 'cyclisme UCI Tour de France actualité',
 'nhl': 'NHL hockey sur glace résultats actualité',
 'mlb': 'MLB baseball World Series actualité',
 'mma': 'UFC MMA combat arts martiaux mixtes actualité',
}
# Écarter les résultats RSS hors sujet : être cité « comme la NBA » n'en fait pas une actu basket.
RELEVANCE={
 'nba': r'\bNBA\b|\bbasket(?:-ball)?\b|Wemb|LeBron|Curry|Embiid|Spurs|Lakers|Celtics|Warriors|Knicks|Sixers|Thunder|Nuggets|Grizzlies|Heat|Bulls|Bucks|Raptors|Mavericks|Timberwolves|Clippers|Pacers|Rockets',
 'nfl': r'\bNFL\b|football américain|Super Bowl|quarterback|touchdown|Ravens|Chiefs|Eagles|Patriots|Bills|Cowboys|Bears|Vikings|Broncos|Seahawks|49ers|Steelers|Dolphins|Lions|Bengals|Rams|Chargers',
 'f1': r'\bF1\b|Formule 1|Formula 1|Grand Prix|Verstappen|Leclerc|Antonelli|Hamilton|Norris|Russell|Piastri|McLaren|Ferrari',
 'motogp': r'MotoGP|Moto2|Moto3|Grand Prix moto|Márquez|Marquez|Bagnaia|Quartararo|Acosta|Bezzecchi|Sepang',
 'tennis': r'tennis|\bATP\b|\bWTA\b|Roland.Garros|Wimbledon|Alcaraz|Sinner|Djokovic|Swiatek|Sabalenka',
 'rugby': r'rugby|Top 14|XV de France|Six Nations|All Blacks|Stade Toulousain|Champions Cup',
 'cyclisme': r'cyclisme|\bUCI\b|Tour de France|Tour d.Italie|Tour d.Espagne|Giro|Vuelta|Pogacar|Vingegaard|Evenepoel',
 'nhl': r'\bNHL\b|hockey sur glace|Stanley Cup|Canadiens de Montréal|Maple Leafs|Bruins|Rangers|Red Wings|Oilers|Penguins',
 'mlb': r'\bMLB\b|baseball|World Series|Yankees|Dodgers|Mets|Astros|Phillies|Red Sox|Blue Jays',
 'mma': r'\bUFC\b|\bMMA\b|arts martiaux mixtes|octogone|Pereira|Makhachev|Jon Jones|Adesanya|McGregor',
}
NEGATIVE={
 'nba': r'Kardashian|OnlyFans|Tissot|Mbappé|Real Madrid|programme TV|TV-Programme|sneakers',
 'nfl': r'programme TV|sneakers|casquette',
 'f1': r'parfum|montre de luxe|jeu vidéo',
 'motogp': r'jeu vidéo|moto électrique.*prix',
}
def relevant(sport,title):
 return (bool(re.search(RELEVANCE[sport],title,re.IGNORECASE))
         and not bool(re.search(NEGATIVE.get(sport,r'(?!)'),title,re.IGNORECASE)))

def stamp(raw):
 try:
  x=email.utils.parsedate_to_datetime(raw)
  return x.astimezone(UTC) if x.tzinfo else None
 except (ValueError,TypeError,IndexError): return None
def clean(s,limit=180):
 return re.sub(r'\s+',' ',str(s or '')).strip()[:limit]
def fetch(sport,query,now):
 params=urllib.parse.urlencode({'q':query+' when:7d','hl':'fr','gl':'FR','ceid':'FR:fr'})
 req=urllib.request.Request('https://news.google.com/rss/search?'+params,headers={'User-Agent':'VM-Multisport/1.0 (editeur de liens; https://velocemercato.fr/multisport/)'})
 with urllib.request.urlopen(req,timeout=18) as response:
  if response.status!=200:raise ValueError('HTTP non 200')
  data=response.read(2_000_000)
  if not data or len(data)>=2_000_000:raise ValueError('flux absent ou trop volumineux')
 root=ET.fromstring(data)
 items=[]
 for item in root.findall('./channel/item'):
  title=clean(item.findtext('title'),210)
  url=clean(item.findtext('link'),1500)
  pub=stamp(item.findtext('pubDate'))
  source=item.find('source')
  source_name=clean(source.text if source is not None else '',100)
  if not(title and source_name and relevant(sport,title) and url.startswith('https://news.google.com/') and pub):
   continue
  age=now-pub
  if not dt.timedelta(0)<=age<=dt.timedelta(days=7):continue
  items.append({'id':sport+'-'+str(int(pub.timestamp()))+'-'+re.sub('[^a-z0-9]','',title.lower())[:28],
    'titre':title,'source':source_name,'url':url,'date':pub.isoformat(timespec='seconds')})
 seen=set();out=[]
 for row in sorted(items,key=lambda x:x['date'],reverse=True):
  key=(row['titre'].casefold(),row['source'].casefold())
  if key in seen:continue
  seen.add(key);out.append(row)
  if len(out)>=22:break
 return out

def main():
 now=dt.datetime.now(UTC)
 try:current=json.loads(OUT.read_text(encoding='utf-8')) if OUT.is_file() else {}
 except (ValueError,OSError):current={}
 old_data=current.get('sports') if isinstance(current.get('sports'),dict) else {}
 data={'misAJour':now.isoformat(timespec='seconds'),'fenetreJours':7,'source':'Google News RSS — liens vers les éditeurs originaux',
       'sports':{}}
 success=0
 for sport,query in SPORTS.items():
  try:
   items=fetch(sport,query,now)
   if items:success+=1
   else:print(f'::warning::{sport}: aucun titre récent renvoyé',flush=True)
  except (urllib.error.URLError,TimeoutError,ValueError,ET.ParseError,OverflowError) as error:
   items=[]
   print(f'::warning::{sport}: flux indisponible ({type(error).__name__})',flush=True)
  if not items:
   old=old_data.get(sport,[])
   # Réutilisation courte des éléments encore récents; jamais des archives comme « chaude de la semaine ».
   for row in old:
    try:age=now-dt.datetime.fromisoformat(row['date'])
    except (KeyError,ValueError,TypeError):continue
    if dt.timedelta(0)<=age<=dt.timedelta(days=7) and row.get('url','').startswith('https://news.google.com/') and relevant(sport,row.get('titre','')):
     items.append(row)
   items=items[:20]
  data['sports'][sport]=items
  time.sleep(0.8)
 if not success and not any(data['sports'].values()):
  print('::warning::Aucun flux récupéré. Pas de publication de faux articles.',flush=True)
  return 0 if OUT.is_file() else 1
 OUT.parent.mkdir(parents=True,exist_ok=True)
 content=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
 OUT.write_text(content,encoding='utf-8')
 print(f'::notice::Actus 7 jours par sport: '+', '.join(f'{k}={len(v)}' for k,v in data['sports'].items()),flush=True)
 return 0
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as error:
  print('::error::Récupération multisport: '+type(error).__name__)
  sys.exit(1)
