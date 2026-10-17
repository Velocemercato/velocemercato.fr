#!/usr/bin/env python3
"""Collecte prudente de liens d'actualités football, sans inventer d'articles."""
import datetime as dt, email.utils, hashlib, html, json, pathlib, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parent
QUERIES={
 'FRANCE':'mercato football Ligue 1 Ligue 2 transfert',
 'NATIONAL':'football mercato National 1 transfert club',
 'N2_N3':'football mercato National 2 National 3 recrutement',
 'FEMININ':'football féminin transfert Première Ligue Seconde Ligue',
 'AMATEUR':'football amateur régional recrutement mutation club',
 'INTERNATIONAL':'football transfer mercato Premier League Liga Serie A Bundesliga',
}
HEADERS={'User-Agent':'VeloceMercatoNewsBot/1.0 (+https://velocemercato.fr/)'}
def read_json(name):
 try:
  x=json.loads((ROOT/name).read_text(encoding='utf-8'))
  return x if isinstance(x,list) else []
 except (OSError,ValueError): return []
def clean(s): return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s or ''))).strip()
def collect(zone,query):
 params=urllib.parse.urlencode({'q':query,'hl':'fr','gl':'FR','ceid':'FR:fr'})
 req=urllib.request.Request('https://news.google.com/rss/search?'+params,headers=HEADERS)
 with urllib.request.urlopen(req,timeout=18) as response: data=response.read(1500000)
 root=ET.fromstring(data)
 for item in root.findall('./channel/item')[:12]:
  title=clean(item.findtext('title')); link=item.findtext('link','').strip()
  pub=item.findtext('pubDate','')
  try: date=email.utils.parsedate_to_datetime(pub).astimezone(dt.timezone.utc)
  except (TypeError,ValueError,OverflowError): continue
  if not title or not link.startswith('https://'): continue
  if date < dt.datetime.now(dt.timezone.utc)-dt.timedelta(hours=36): continue
  source=item.find('source'); source_name=clean(source.text if source is not None else '') or 'Google Actualités'
  digest=hashlib.sha256((title.casefold()+'|'+source_name.casefold()).encode()).hexdigest()[:16]
  yield {'id':'rss-'+digest,'publishedAt':date.isoformat(timespec='seconds').replace('+00:00','Z'),
   'titre':title[:180], 'resume':'Actualité signalée par '+source_name+'. Consultez la source pour les détails.',
   'texte':'Une nouvelle information concernant le football a été repérée dans les sources suivies. Les détails restent à consulter dans l’article d’origine. Aucun transfert n’est présenté ici comme confirmé sans vérification.',
   'zone':zone,'tag':'MERCATO','sources':[{'nom':source_name,'url':link}], 'format':'veille'}
def main():
 existing=read_json('articles.json'); ids={str(a.get('id')) for a in existing}; additions=[]
 for zone,query in QUERIES.items():
  try:
   for a in collect(zone,query):
    if a['id'] not in ids: additions.append(a);ids.add(a['id'])
  except Exception as exc: print('Source indisponible',zone,str(exc)[:150])
 if not additions: print('Aucune nouvelle entrée');return
 all_articles=sorted(existing+additions,key=lambda a:a.get('publishedAt',''),reverse=True)[:200]
 (ROOT/'articles.json').write_text(json.dumps(all_articles,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(len(additions),'nouvelles entrées de veille ajoutées')
if __name__=='__main__':main()
