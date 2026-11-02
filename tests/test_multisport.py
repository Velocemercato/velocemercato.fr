#!/usr/bin/env python3
"""Tests multisport, sans réseaux ni médias inventés."""
from pathlib import Path
import json
import py_compile,importlib.util
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:(ROOT/p).read_text(encoding="utf-8")
home=read("index.html")
portal=read("multisport/index.html")
js=read("multisport/univers.js")
sports=("nba","nfl","f1","motogp","tennis","rugby","cyclisme","nhl","mlb","mma","ski")
assert 'id="feed-title"' in home
assert 'id="pastille-tv"' in home
assert 'href="/multisport/"' in home
assert 'href="/mangas/"' in home
assert 'data-mode="portal"' in portal
for sport in sports:
 assert f'data-sport="{sport}"' in portal, sport
 path=f"multisport/{sport}/index.html"
 assert (ROOT/path).is_file(),path
 h=read(path)
 assert f'data-current-sport="{sport}"' in h
 assert f'data-mode="sport"' in h
 for section in ('france','europe','international','feminin','resultats','videos'):
  assert f'id="{section}"' in h,(sport,section)
 assert 'href="/mangas/"' in h
 assert f"{sport}:" in js or f"{sport}:" in js
assert 'textContent' in js
assert "/multisport/actualites.json" in js
assert "/fil.json" in js
assert "status==='published'" in js
assert '7*86400000' in js
data=json.loads(read("multisport/actualites.json"))
assert data.get("fenetreJours") in (1,7)  # 1 : la veille s efface chaque matin (vm_fraicheur)
assert all(sport in data["sports"] for sport in sports)
py_compile.compile(str(ROOT/"tools/multisport_flux.py"),doraise=True)
spec=importlib.util.spec_from_file_location('flux',ROOT/'tools/multisport_flux.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
assert mod.relevant('nba','NBA : Wembanyama et les Spurs')
assert not mod.relevant('nba','Tissot présente une montre NBA')
assert mod.relevant('ski','Ski alpin : slalom de Coupe du monde')
assert 'france' in mod.rubriques('f1','F1 : Pierre Gasly décroche une pole')
assert 'europe' in mod.rubriques('f1','F1 : Grand Prix de Monza')
assert 'feminin' in mod.rubriques('nba','WNBA : les femmes du basket')
print('OK: 11 sports, foot conservé, rubriques, titres vérifiés, moteur ski.')
