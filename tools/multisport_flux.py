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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import vm_fraicheur  # noqa: E402

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
 'ski': 'ski alpin ski nordique biathlon coupe du monde sports hiver actualité',
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
 'ski': r'\bski\b|ski alpin|ski de fond|biathlon|descente|slalom|super.G|sports d.hiver|Coupe du monde FIS|Odermatt|Shiffrin|Pinturault|Fourcade|Boe',
}
NEGATIVE={
 'nba': r'Kardashian|OnlyFans|Tissot|Mbappé|Real Madrid|programme TV|TV-Programme|sneakers',
 'nfl': r'programme TV|sneakers|casquette',
 'f1': r'parfum|montre de luxe|jeu vidéo',
 'motogp': r'jeu vidéo|moto électrique.*prix',
}
GAMING_CONTENT = '\\b(?:gta(?:\\s*(?:vi|[56]))?|grand theft auto|playstation|xbox|nintendo|fortnite|minecraft|roblox|esports?|e-sports?|nba\\s*2k\\w*|madden|ea\\s*(?:sports\\s*)?fc|fifa\\s*2[0-9]|jeux? vid[eé]o|gaming|steam|ubisoft|activision|call of duty)\\b'

def relevant(sport,title):
 return (sport in RELEVANCE and not re.search(GAMING_CONTENT,title,re.IGNORECASE)
         and bool(re.search(RELEVANCE[sport],title,re.IGNORECASE))
         and not bool(re.search(NEGATIVE.get(sport,r'(?!)'),title,re.IGNORECASE)))

# Rubriques éditoriales : elles concernent les personnes, équipes et compétitions citées,
# pas nécessairement le pays où un match ou une course se déroule.
FRANCE_HINTS={
 'nba': r'Wembanyama|Wemby|Gobert|Risacher|Sarr|Coulibaly|Batum|Yabusele|français|France',
 'nfl': r'français|française|France|Paris|équipe de France',
 'f1': r'Gasly|Ocon|Hadjar|Alpine|écurie française|pilote français|Grand Prix de France',
 'motogp': r'Quartararo|Zarco|pilote français|Grand Prix de France|Le Mans|français',
 'tennis': r'Alcaraz(?: contre | face à )Fils|Arthur Fils|Humbert|Moutet|Monfils|Mannarino|Cazaux|Gaston|Garcia|français|française|France',
 'rugby': r'Top 14|XV de France|Toulouse|La Rochelle|Racing 92|Stade Français|Bordeaux.Bègles|Bayonne|Castres|Pau|Toulon|Montpellier|France|français',
 'cyclisme': r'Alaphilippe|Gaudu|Laporte|Madouas|Vauquelin|France|français|française|Arkéa|Decathlon AG2R',
 'nhl': r'Alexandre Texier|Bellemare|français|France|hockey français',
 'mlb': r'français|France|baseball français',
 'mma': r'Ciryl Gane|Beno[iî]t Saint.Denis|Imavov|Manon Fiorot|français|française|France',
 'ski': r'Pinturault|Clément Noël|Julia Simon|Justine Braisaz|France|français|française|Le Grand Bornand|Val d.Isère|Courchevel',
}
EUROPE_HINTS={
 'nba': r'Europe|européen|européenne|EuroLeague|Euroligue|Joki[cć]|Don[cč]i[cć]|Giannis|Antetokounmpo|Porzingis|Wembanyama|Wemby',
 'nfl': r'Europe|européen|européenne|Allemagne|Berlin|Madrid|Londres|London|Dublin|Irlande',
 'f1': r'Europe|européen|européenne|Monaco|Monza|Silverstone|Spa.Francorchamps|Barcelone|Imola|Zandvoort|Belgique|Italie|Espagne',
 'motogp': r'Europe|européen|européenne|Le Mans|Misano|Assen|Mugello|Jerez|Aragon|Catalogne',
 'tennis': r'Europe|européen|européenne|Wimbledon|Roland.Garros|Paris|Madrid|Rome|Bercy|Vienne|Bâle|Monte.Carlo',
 'rugby': r'Europe|européen|européenne|Champions Cup|Six Nations|Tournoi des Six Nations|Angleterre|Italie|Écosse|Irlande|Pays de Galles|Top 14',
 'cyclisme': r'Europe|européen|européenne|Tour de France|Giro|Vuelta|Paris.Roubaix|Liège.Bastogne|Flandres|Milan.Sanremo',
 'nhl': r'Europe|européen|européenne|Finlande|Suède|République tchèque|Slovaquie|Suisse',
 'mlb': r'Europe|européen|européenne|Londres|London|Paris|Allemagne',
 'mma': r'Europe|européen|européenne|Paris|Londres|London|Dublin|Angleterre|France',
 'ski': r'Europe|européen|européenne|Alpes|Autriche|Suisse|Italie|Val d.Isère|Courchevel|Bormio|Kitzbühel|Oslo|Norvège',
}
def rubriques(sport,title):
    categories=['international']  # édition globale : articles vérifiés de cette discipline
    if re.search(FRANCE_HINTS[sport],title,re.IGNORECASE):categories.append('france')
    if re.search(EUROPE_HINTS[sport],title,re.IGNORECASE):categories.append('europe')
    # Les compétitions féminines ne sont classées que si le titre le précise.
    if re.search(r"\bféminin(?:e|es|s)?\b|\bfemmes\b|\bdames\b|\bWTA\b|\bWNBA\b|\bPWHL\b|Women's|\bF1 Academy\b|\bUFC Women\b",title,re.IGNORECASE):
        categories.append('feminin')
    return categories

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
    'titre':title,'source':source_name,'url':url,'date':pub.isoformat(timespec='seconds'),'rubriques':rubriques(sport,title)})
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
 data={'misAJour':now.isoformat(timespec='seconds'),'fenetreJours':1,'source':'Google News RSS — liens vers les éditeurs originaux',
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
     items.append({**row,'rubriques':rubriques(sport,row.get('titre',''))})
   items=items[:20]
  data['sports'][sport]=vm_fraicheur.du_jour(items,('date',))  # rien de la veille
  time.sleep(0.8)
 if not success and not any(data['sports'].values()):
  print('::warning::Aucun flux récupéré. Pas de publication de faux articles.',flush=True)
  return 0 if OUT.is_file() else 1
 OUT.parent.mkdir(parents=True,exist_ok=True)
 content=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
 OUT.write_text(content,encoding='utf-8')
 print(f'::notice::Actus du jour par sport: '+', '.join(f'{k}={len(v)}' for k,v in data['sports'].items()),flush=True)
 return 0
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as error:
  print('::error::Récupération multisport: '+type(error).__name__)
  sys.exit(1)

