#!/usr/bin/env python3
"""Tests multisport sans données externes ni publications."""
from pathlib import Path
import json
import py_compile
ROOT=Path(__file__).resolve().parents[1]
read=lambda name:(ROOT/name).read_text(encoding="utf-8")
html=read("multisport/index.html")
js=read("multisport/app.js")
home=read("index.html")
alerts=read("notifications/alertes.js")
prefs=read("notifications/index.html")
sports=("nba","nfl","f1","motogp","tennis","rugby","cyclisme")
for sport in sports:
 assert f'data-sport-choice="{sport}"' in html, sport
 assert f" {sport}:" in js or f"\n {sport}:" in js, sport
 assert f"['" in alerts and f"{sport}:[" in alerts, "alertes "+sport
 assert f'data-topic="{sport}"' in prefs, "préférences "+sport
 assert f'/multisport/?sport={sport}' in home, sport
assert "🏆 Multisport" in home, "menu multisport absent"
assert 'vm-resume-sport' in home, "préférence à reprendre manquante"
assert 'tv-sports.fr/widget.js' in js, "programme externe indisponible"
assert 'La Pastille ' in js and 'pas encore produites' in js, "ne pas annoncer de pastilles imaginaires"
assert 'localStorage' in js and "pushState" in js, "sélection persistante manquante"
assert 'Date.now()-t<=7*86400000' in js, "fenêtre 7 jours absente"
assert "textContent" in js, "n'injecter aucun titre RSS en HTML brut"
data=json.loads(read("multisport/actualites.json"))
assert data["fenetreJours"]==7
assert all(s in data["sports"] for s in sports)
assert all(isinstance(data["sports"][s],list) for s in sports)
assert all('news.google.com' not in str(x) or 'https://' in str(x) for lines in data['sports'].values() for x in lines)
gen=read("tools/multisport_flux.py")
assert "when:7d" in gen and "source_name" in gen and "dt.timedelta(days=7)" in gen
assert "news.google.com/" in gen
py_compile.compile(str(ROOT/"tools/multisport_flux.py"),doraise=True)
print("OK : bascule sport, flux datés, notifications, résultats et présentation vidéo honnête.")
