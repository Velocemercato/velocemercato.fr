#!/usr/bin/env python3
"""Smoke-test navigateur VM sur trois sites clonés, tests réels de clic et mobile/desktop.
Les requêtes tierces sont coupées : vidéos, publicité, Stripe, météo et analytics
ne sont PAS considérés comme vérifiés par ce test local.
"""
from __future__ import annotations
from collections import Counter
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright,TimeoutError as BrowserTimeout

PAGES={
"foot":["/","/actus/","/pronos/","/vm-gaming/","/mangas/","/mangas/episodes/ecole-des-champions-01.html","/multisport/","/multisport/nba/","/multisport/f1/","/multisport/ski/","/notifications/","/scores/","/meteo/","/soutenir.html","/pub/","/investisseurs.html","/studio.html","/shop/","/services-web.html","/web-studio.html","/ou-regarder.html","/mentions-legales.html","/archives.html"],
"univers":["/","/decouvrir.html","/meteo/","/professionnels/","/telechargements/","/connect/"],
"papiers":["/","/outils.html","/accompagnement.html"]
}
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*_):pass
 def copyfile(self,source,out):
  try:super().copyfile(source,out)
  except (BrokenPipeError,ConnectionResetError):pass
def server(root):
 s=ThreadingHTTPServer(("127.0.0.1",0),partial(Handler,directory=str(root)))
 threading.Thread(target=s.serve_forever,daemon=True).start()
 return s,f"http://127.0.0.1:{s.server_port}"
def scan(rootdirs,out):
 out.mkdir(parents=True,exist_ok=True)
 reports=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
  for name,root in rootdirs.items():
   srv,base=server(root)
   try:
    for path in PAGES[name]:
     rel=path.lstrip("/")
     if not (root/rel).is_file() and not (root/rel/"index.html").is_file():
      # Skip unavailable endpoints, but record them.
      reports.append({"project":name,"page":path,"issue":"route_absent","width":0,"detail":"Route absente du dépôt"})
      continue
     for width in (390,1440):
      ctx=browser.new_context(viewport={"width":width,"height":844 if width==390 else 900},service_workers="block")
      ctx.route("**/*",lambda route:route.continue_() if route.request.url.startswith(base+"/") else route.abort())
      page=ctx.new_page()
      errors=[];broken=[]
      page.on("pageerror",lambda error:errors.append(str(error)))
      page.on("response",lambda res:broken.append(res.url[len(base):]) if res.status>=400 and res.url.startswith(base+"/") else None)
      try:
       page.goto(base+path,wait_until="domcontentloaded",timeout=15000)
       page.wait_for_timeout(650)
       title=page.title()
       if not title.strip():reports.append({"project":name,"page":path,"width":width,"issue":"title_vide","detail":""})
       maxwidth=page.evaluate("document.documentElement.scrollWidth")
       if maxwidth>width+24:
        reports.append({"project":name,"page":path,"width":width,"issue":"overflow_horizontal","detail":f"{maxwidth}px pour viewport {width}px"})
       if path=="/" and name=="foot":
        if page.locator("#feed-title").count()!=1:reports.append({"project":name,"page":path,"width":width,"issue":"fil_foot_absent","detail":""})
        if page.locator("#vm-cinema-home").count()!=1:reports.append({"project":name,"page":path,"width":width,"issue":"banniere_vm_absente","detail":""})
        if page.locator('a[href="/mangas/"]').count()==0:reports.append({"project":name,"page":path,"width":width,"issue":"lien_manga_absent","detail":""})
       if path=="/multisport/" and name=="foot":
        if page.locator('a[href="/multisport/nba/"]').count()<1:reports.append({"project":name,"page":path,"width":width,"issue":"selection_nba_absente","detail":""})
       if path=="/mangas/":
        if page.locator("a[href*='episodes/ecole-des-champions-01.html']").count()<1:reports.append({"project":name,"page":path,"width":width,"issue":"episodes_absents","detail":""})
       if name=="foot" and path=="/":
        cat=page.locator('#cats button[data-cat="LIGUE_1"]').first
        if cat.count():
         cat.click(timeout=6500)
         if cat.get_attribute("aria-pressed")!="true":
          reports.append({"project":name,"page":path,"width":width,"issue":"filtre_foot_inactif","detail":"Clic Ligue 1 ne sélectionne pas le filtre"})
       if name=="foot" and path=="/multisport/":
        a=page.locator('a[data-sport="nba"]').first
        if a.count():
         a.click(timeout=6500)
         if not page.url.endswith("/multisport/nba/"):
          reports.append({"project":name,"page":path,"width":width,"issue":"choix_nba_inactif","detail":"Le clic NBA ne navigue pas sur la page dédiée"})
       if name=="foot" and path=="/mangas/":
        a=page.locator('a[href="/mangas/episodes/ecole-des-champions-01.html"]').first
        if a.count():
         a.click(timeout=6500)
         if "/mangas/episodes/ecole-des-champions-01.html" not in page.url:
          reports.append({"project":name,"page":path,"width":width,"issue":"navigation_manga_inactive","detail":"La carte épisode n'ouvre pas sa page"})
       if name=="foot" and path=="/mangas/episodes/ecole-des-champions-01.html":
        a=page.locator('.video button').first
        if a.count():
         a.click(timeout=6000)
         iframe=page.locator('iframe[src*="youtube-nocookie.com/embed/"]').first
         if not iframe.count():
          reports.append({"project":name,"page":path,"width":width,"issue":"lecteur_manga_inactif","detail":"Clic charger lecteur sans iframe officielle"})
       if name=="foot" and path=="/notifications/":
        checkbox=page.locator('[data-topic="mangas"]').first
        if checkbox.count() and page.locator('#vm-alert-enable').count():
         checkbox.check(timeout=4500)
         page.locator('#vm-alert-enable').click(timeout=4500)
         page.wait_for_timeout(450)
         status=page.locator('#vm-alert-status').inner_text().lower()
         if "activ" not in status:
          reports.append({"project":name,"page":path,"width":width,"issue":"notifications_inactives","detail":status[:190]})
       if name=="foot" and path=="/notifications/":
        if page.locator('[data-topic="mangas"]').count()!=1:reports.append({"project":name,"page":path,"width":width,"issue":"preferences_mangas_absentes","detail":""})
      except Exception as exc:
       reports.append({"project":name,"page":path,"width":width,"issue":"navigation_echec","detail":str(exc)[:200]})
      for err in errors[:7]:reports.append({"project":name,"page":path,"width":width,"issue":"javascript_error","detail":err[:200]})
      for url in list(dict.fromkeys(broken))[:10]:
       reports.append({"project":name,"page":path,"width":width,"issue":"asset_http_error","detail":url[:220]})
      ctx.close()
   finally:srv.shutdown();srv.server_close()
  browser.close()
 counts=Counter((p["project"],p["issue"]) for p in reports)
 report={"total_pages":sum(len(v) for v in PAGES.values()),"viewports":2,
         "problems":len(reports),"counts":{f"{k[0]}:{k[1]}":v for k,v in counts.items()},"incidents":reports}
 (out/"browser.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
 print("Pages visitées :",report["total_pages"],"× 2 résolutions")
 print("Anomalies détectées:",len(reports))
 for name,count in sorted(report["counts"].items(),key=lambda kv:-kv[1]):print(f"  {name}: {count}")
 for incident in reports[:100]:print("  "+str(incident)[:350])
 return 0
if __name__=="__main__":
 import argparse
 parser=argparse.ArgumentParser()
 for k in ("foot","univers","papiers"):parser.add_argument("--"+k,type=Path,required=True)
 parser.add_argument("--out",type=Path,default=Path("audit-resultats"))
 a=parser.parse_args()
 raise SystemExit(scan({k:getattr(a,k).resolve() for k in ("foot","univers","papiers")},a.out))
