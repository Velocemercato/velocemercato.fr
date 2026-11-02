#!/usr/bin/env python3
"""Vérification HTTPS en lecture seule des pages publiées (pas des comptes ni des paiements).
Les statuts 403/429/502 peuvent refléter des restrictions réseau du runner.
"""
import concurrent.futures
import json
from pathlib import Path
import ssl
import urllib.error
import urllib.request
import time

URLS=[
"https://velocemercato.fr/","https://velocemercato.fr/actus/","https://velocemercato.fr/pronos/",
"https://velocemercato.fr/vm-gaming/","https://velocemercato.fr/mangas/",
"https://velocemercato.fr/mangas/episodes/ecole-des-champions-01.html",
"https://velocemercato.fr/multisport/","https://velocemercato.fr/multisport/nba/",
"https://velocemercato.fr/multisport/f1/","https://velocemercato.fr/multisport/ski/",
"https://velocemercato.fr/notifications/","https://velocemercato.fr/scores/",
"https://velocemercato.fr/meteo/","https://velocemercato.fr/pub/",
"https://velocemercato.fr/investisseurs.html","https://velocemercato.fr/soutenir.html",
"https://velocemercato.fr/mentions-legales.html","https://velocemercato.fr/studio.html",
"https://velocemercato.fr/img/logo-vm-192.png","https://velocemercato.fr/mangas/assets/vm-87.svg",
"https://velocemercato.fr/sitemap.xml",
"https://vmunivers.fr/","https://vmunivers.fr/meteo/","https://vmunivers.fr/decouvrir.html",
"https://vmunivers.fr/professionnels/","https://vmunivers.fr/connect/",
"https://vmunivers.fr/sitemap.xml",
"https://velocemercato.github.io/Papiers-sans-galere/",
"https://velocemercato.github.io/Papiers-sans-galere/outils.html",
"https://velocemercato.github.io/Papiers-sans-galere/accompagnement.html",
]
def probe(url):
 start=time.monotonic()
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"VM-Audit-Public/1.0 (+https://velocemercato.fr/)","Accept":"text/html,application/json,image/*,*/*;q=0.5"})
  with urllib.request.urlopen(req,timeout=10) as res:
   content=res.read(128_000)
   code=res.status
   typ=(res.headers.get("Content-Type") or "").split(";")[0]
   final=res.geturl()
   if code==200 and typ=="text/html" and len(content)<200:
    state="suspect"
   elif code==200:state="ok"
   else:state="http_error"
   return {"url":url,"status":state,"http":code,"mime":typ,"final":final,"bytes_sample":len(content),"elapsed_ms":round(1000*(time.monotonic()-start))}
 except urllib.error.HTTPError as e:return {"url":url,"status":"http_error","http":e.code,"detail":str(e.reason)[:100]}
 except Exception as e:return {"url":url,"status":"unreachable","detail":type(e).__name__+": "+str(e)[:100]}
def main():
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  data=list(pool.map(probe,URLS))
 Path("audit-live").mkdir(exist_ok=True)
 Path("audit-live/urls.json").write_text(json.dumps({"tested_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"checks":data},ensure_ascii=False,indent=2))
 for row in data:print(f"{row['status']:12} HTTP={str(row.get('http','---')):>3} {row['url']} {row.get('detail','')}")
 return 0
if __name__=="__main__":raise SystemExit(main())
