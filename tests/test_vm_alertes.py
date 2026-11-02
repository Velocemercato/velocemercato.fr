#!/usr/bin/env python3
"""Checks statiques sans réseau et sans publication."""
import json
from pathlib import Path
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
def read(path):return (ROOT/path).read_text(encoding="utf-8")
def check(ok,msg):
    if not ok:raise AssertionError(msg)
episodes=json.loads(read("notifications/episodes.json"))
check(isinstance(episodes,list) and len(episodes)>=8,"Catalogue alertes mangas vide")
for episode in episodes:
    check(all(episode.get(k) for k in ("id","title","url","date")),"Métadonnées épisode incomplètes")
    check(episode["url"].startswith("/mangas/episodes/"),"Chemin épisode externe interdit")
    check((ROOT/episode["url"].lstrip("/")).is_file(),"Page épisode absente : "+episode["id"])
notification_html=read("notifications/index.html")
for key in ("foot","actus","gaming","pronos","mangas"):
    check('data-topic="'+key+'"' in notification_html,"Sujet manquant : "+key)
check("navigateur est fermé" in notification_html,"Informer de l'absence de push de fond")
check("localStorage" in read("notifications/alertes.js"),"Préférences locales manquantes")
for path in ("index.html","actus/index.html","vm-gaming/index.html","pronos/index.html","mangas/index.html"):
    html=read(path)
    check("/notifications/alertes.js" in html,"Lien JS notifications manquant : "+path)
    check("/notifications/alertes.css" in html,"Lien CSS notifications manquant : "+path)
manga=read("mangas/index.html")
check('vm-manga-hero' in manga and 'vm-featured' in manga and 'vm-strip' in manga,"Habillage Manga incomplet")
check("VM MANGAS 87" not in manga,"Ne pas mettre 87 dans le nom du site")
check("vm-87.svg" in read("mangas/assets/neon-v2.css"),"Mascotte manquante")
check("87" in read("mangas/assets/vm-87.svg"),"Le numéro 87 doit rester sur le maillot")
links=json.loads(read("liens.json"))
check(str(links.get("soutien_media","")).startswith("https://buy.stripe.com/"),"Lien media Stripe manquant ou invalide")
check(not links.get("soutien_pro"),"Le soutien pro doit rester désactivé sans lien vérifié")
print("OK : catalogue, notifications opt-in, accès sites, décor manga, configuration des liens de soutien.")
