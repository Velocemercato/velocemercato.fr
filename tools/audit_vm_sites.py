#!/usr/bin/env python3
"""Audit statique de tous les liens et documents VM (sans altérer les sites).
Balaye chaque fichier HTML, CSS, manifest et sitemap dans les dépôts publiés.
Les URL externes non vérifiées sont déclarées séparément.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse, unquote
import xml.etree.ElementTree as ET

SKIP_DIRS={"node_modules",".git","__pycache__",".venv","venv","site-packages"}
HOSTS={"velocemercato.fr":"foot","www.velocemercato.fr":"foot","vmunivers.fr":"univers",
       "www.vmunivers.fr":"univers","velocemercato.github.io":"github"}
CORE={
 "foot":{"index.html","mangas/index.html","multisport/index.html","actus/index.html",
 "pronos/index.html","vm-gaming/index.html","soutenir.html","pub/index.html",
 "investisseurs.html","notifications/index.html","mentions-legales.html"},
 "univers":{"index.html","decouvrir.html","telechargements/index.html","professionnels/index.html"},
 "papiers":{"index.html","outils.html","accompagnement.html"}
}
class Parser(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True)
  self.urls=[];self.ids=[];self.alt_missing=[];self.title=0;self.h1=0;self.canonical=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if d.get("id"):self.ids.append(d["id"])
  if tag=="title":self.title+=1
  if tag=="h1":self.h1+=1
  if tag=="img" and "alt" not in d:self.alt_missing.append(d.get("src",""))
  for field in ("href","src","poster","data-src","action"):
   if d.get(field):self.urls.append((field,d[field]))
  if d.get("srcset"):
   for piece in d["srcset"].split(","):
    if piece.strip():self.urls.append(("srcset",piece.strip().split(" ")[0]))
  if tag=="link" and d.get("rel","").lower()=="canonical":self.canonical.append(d.get("href"))
 def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)
def is_ignored(s):
 return (not s or s.startswith(("#","mailto:","tel:","sms:","data:","blob:","about:","intent:","whatsapp:"))
 or any(t in s for t in ("{{","}}","<%",">%", "${", "{ref}", "javascript:void(0)")))
def resolve(current,ref,roots,domain,github_root):
 if is_ignored(ref):return "skip",None
 if ref.startswith("javascript:"):return "unsafe",None
 if ref.startswith("//"):ref="https:"+ref
 base=("https://velocemercato.github.io/Papiers-sans-galere/" if domain=="velocemercato.github.io" else "https://"+domain+"/")+current.relative_to(roots).as_posix()
 try:p=urlparse(urljoin(base,ref))
 except ValueError:return "invalid",None
 if p.scheme not in ("http","https"):return "skip",None
 host=(p.hostname or "").lower()
 if host not in HOSTS:return "external",p.geturl()
 if host=="velocemercato.github.io":
  if p.path.startswith("/Papiers-sans-galere/"):target=github_root
  else:return "external",p.geturl()
  path=p.path.removeprefix("/Papiers-sans-galere/")
 else:
  target=domain_map[HOSTS[host]]
  path=p.path.lstrip("/")
 if target is None:return "unknown_host",p.geturl()
 decoded=unquote(path)
 if any(part in ("..",) for part in decoded.split("/")):return "skip",p.geturl()
 rel=Path(decoded)
 files=[target/rel]
 if not rel.suffix or decoded.endswith("/"):
  files=[target/rel/"index.html",target/rel/"index.htm",target/rel]
 elif rel.suffix==".html":
  files.append(target/rel.parent/rel.stem/"index.html")
 elif rel.suffix==".php":
  return "dynamic",p.geturl()
 ok=next((f for f in files if f.is_file()),None)
 if ok:return "ok",(ok,p.fragment)
 # Static hosting GitHub Pages may add extensionless .html
 if not rel.suffix and (target/(decoded.rstrip("/")+".html")).is_file():
  return "ok",(target/(decoded.rstrip("/")+".html"),p.fragment)
 return "missing",p.geturl()
domain_map={}
def run(roots:dict[str,Path]):
 global domain_map
 domain_map=roots
 incidents=[];summary={}
 expected_hosts={"foot":"velocemercato.fr","univers":"vmunivers.fr","papiers":"velocemercato.github.io"}
 seenhtml={}
 for name,root in roots.items():
  if root is None or not root.is_dir():continue
  htmls=sorted(x for x in root.rglob("*.html") if not any(y in SKIP_DIRS for y in x.parts))
  csss=sorted(x for x in root.rglob("*.css") if not any(y in SKIP_DIRS for y in x.parts))
  jsons=sorted(x for x in root.rglob("*.json") if not any(y in SKIP_DIRS for y in x.parts))
  manifests=sorted(root.rglob("*.webmanifest"))
  stats=Counter()
  for file in htmls:
   rel=file.relative_to(root).as_posix()
   try:
    source=file.read_text("utf-8")
    parser=Parser();parser.feed(source)
   except (UnicodeError,OSError,ValueError) as e:
    incidents.append(("HIGH",name,rel,"html_parse",type(e).__name__))
    continue
   seenhtml[name,rel]=parser
   stats["html_scanned"]+=1
   duplicates=[i for i,c in Counter(parser.ids).items() if c>1]
   if duplicates:
    stats["duplicate_ids"]+=len(duplicates)
    incidents.append(("MEDIUM",name,rel,"duplicate_id",", ".join(duplicates[:6])))
   if not parser.title and rel in CORE.get(name,set()):
    incidents.append(("MEDIUM",name,rel,"title_missing",""))
   for field,href in parser.urls:
    status,extra=resolve(file,href,root,expected_hosts[name],roots.get("papiers"))
    if status=="missing":
     stats["internal_missing"]+=1
     severity="HIGH" if rel in CORE.get(name,set()) else "MEDIUM"
     incidents.append((severity,name,rel,field+"_missing",str(extra)[:225]))
    elif status=="unsafe":
     stats["unsafe_js_links"]+=1
     incidents.append(("MEDIUM",name,rel,"unsafe_javascript",href[:120]))
    elif status=="external":stats["external_links_unverified"]+=1
    elif status=="unknown_host":stats["unknown_vm_domain"]+=1
    elif status=="ok" and field=="href" and isinstance(extra,tuple) and extra[1]:
     target,frag=extra
     # Only check local, exact fragment targets; dynamic IDs have false positives.
     if target==file and frag and frag not in parser.ids and frag not in ("top",""):
      stats["own_missing_anchor"]+=1
      if stats["own_missing_anchor"]<=20:incidents.append(("LOW",name,rel,"anchor_missing",frag[:120]))
   if parser.alt_missing and rel in CORE.get(name,set()):
    incidents.append(("LOW",name,rel,"image_missing_alt",str(parser.alt_missing[:3])[:150]))
   if rel in CORE.get(name,set()) and not parser.canonical:
    incidents.append(("LOW",name,rel,"canonical_missing",""))
  for file in csss:
   stats["css_scanned"]+=1
   try:source=file.read_text("utf-8")
   except (OSError,UnicodeError):continue
   for url in re.findall(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)",source,flags=re.I):
    if not url.startswith(("/","./","../")):continue
    status,extra=resolve(file,url,root,expected_hosts[name],roots.get("papiers"))
    if status=="missing":
     stats["css_assets_missing"]+=1
     incidents.append(("HIGH" if file.name in ("style.css","univers.css","portal.css") else "MEDIUM",
      name,file.relative_to(root).as_posix(),"css_asset_missing",str(extra)[:225]))
  for file in jsons+manifests:
   try:json.loads(file.read_text("utf-8"));stats["json_valid"]+=1
   except (OSError,UnicodeError,ValueError) as e:
    stats["json_invalid"]+=1
    incidents.append(("HIGH",name,file.relative_to(root).as_posix(),"json_invalid",str(e)[:180]))
  sitemap=root/"sitemap.xml"
  if sitemap.is_file():
   try:
    doc=ET.fromstring(sitemap.read_text("utf-8"))
    urls=[x.text.strip() for x in doc.findall(".//{*}loc") if x.text and x.text.strip()]
    stats["sitemap_urls"]=len(urls)
    for u in urls:
     st,ex=resolve(root/"index.html",u,root,expected_hosts[name],roots.get("papiers"))
     if st=="missing":
      stats["sitemap_missing"]+=1
      incidents.append(("HIGH",name,"sitemap.xml","sitemap_missing",str(ex)[:200]))
   except (OSError,ValueError,ET.ParseError) as e:
    incidents.append(("HIGH",name,"sitemap.xml","sitemap_invalid",str(e)[:200]))
  summary[name]=dict(stats)
 # Noise: counts by defect signature; full incidents remain in report JSON, report MD includes grouped examples
 signature=Counter((i[1],i[3],i[4]) for i in incidents)
 grouped=Counter((i[1],i[3]) for i in incidents)
 most=sorted(incidents,key=lambda i:({"HIGH":0,"MEDIUM":1,"LOW":2}.get(i[0],3),i[1],i[2],i[3]))
 return {"summary":summary,"total_issues":len(incidents),"by_issue":{f"{a}:{b}":n for (a,b),n in grouped.items()},
  "incidents":[{"severity":a,"project":b,"file":c,"kind":d,"detail":e} for a,b,c,d,e in most]}
def markdown(report):
 lines=["# Audit technique VM — liens et fichiers statiques","","Contrôle depuis le code GitHub, non équivalent à un audit navigateur ou à un test du fournisseur de paiement.","",
 "| Projet | HTML | CSS | JSON valides | Liens manquants | Liens externes non testés |",
 "|---|---:|---:|---:|---:|---:|"]
 for name,s in report["summary"].items():
  lines.append(f"| {name} | {s.get('html_scanned',0)} | {s.get('css_scanned',0)} | {s.get('json_valid',0)} | {s.get('internal_missing',0)+s.get('css_assets_missing',0)} | {s.get('external_links_unverified',0)} |")
 lines+=["",f"**Anomalies au total : {report['total_issues']}.**","",
  "## Par type",""]
 for key,count in sorted(report["by_issue"].items(),key=lambda x:-x[1]):
  lines.append(f"- {key} : {count}")
 lines+=["","## Exemples prioritaires (100 au maximum)","",
  "| Sévérité | Projet | Page | Catégorie | Détail |","|---|---|---|---|---|"]
 for x in report["incidents"][:100]:
  clean=lambda s:str(s).replace("|","/").replace("\n"," ")[:130]
  lines.append("| "+" | ".join(clean(x[v]) for v in ("severity","project","file","kind","detail"))+" |")
 lines+=["","## Limites","","- Les sites externes, le comportement réel des boutons JavaScript et les comptes partenaires ne sont pas validés par ce balayage.",
 "- Les liens de vidéos YouTube peuvent être retirés ou bloqués par leurs ayants droit.",
 "- Les liens d'ancres calculés à l'exécution peuvent apparaître comme absents.",
 "- Tester également la version mobile, les lecteurs, le paiement et la publication sociale en situation réelle.",""]
 return "\n".join(lines)
def main():
 a=argparse.ArgumentParser();a.add_argument("--foot",type=Path,required=True);a.add_argument("--univers",type=Path,required=True);a.add_argument("--papiers",type=Path,required=True);a.add_argument("--out",type=Path,default=Path("audit-report"));args=a.parse_args()
 report=run({"foot":args.foot.resolve(),"univers":args.univers.resolve(),"papiers":args.papiers.resolve()})
 args.out.mkdir(parents=True,exist_ok=True)
 (args.out/"liens.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
 (args.out/"rapport.md").write_text(markdown(report),encoding="utf-8")
 print(markdown(report)[:14500])
 return 0
if __name__=="__main__":raise SystemExit(main())
