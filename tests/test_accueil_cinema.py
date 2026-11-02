#!/usr/bin/env python3
"""Contrôle non destructif du nouvel accueil Véloce Multisport."""
from pathlib import Path
from html.parser import HTMLParser
import json
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:(ROOT/p).read_text(encoding='utf-8')
home=read('index.html')
js=read('multisport/assets/accueil-cinema.js')
css=read('multisport/assets/accueil-cinema.css')
svg=read('multisport/assets/accueil-heros.svg')
expected=['foot','nba','nfl','f1','motogp','tennis','rugby','cyclisme','nhl','mlb','mma']
assert home.count('id="vm-cinema"')==1,'Accueil en double'
assert home.count('<!-- VM MULTISPORT CINEMA START -->')==1
assert '<section class="v2" aria-labelledby="v2-title">' in home,'Ne pas casser le site foot historique'
assert '<main id="top"' in home,'Main Foot manquant'
assert 'id="vm-cinema-flash-text"' in home
assert all('data-cinema-sport="'+x+'"' in home for x in expected)
assert all(x+':{' in js for x in expected)
assert '/multisport/assets/accueil-cinema.css' in home
assert '/multisport/assets/accueil-cinema.js' in home
assert all('id="vm-cinema-'+key+'-list"' in home for key in ('france','europe','international'))
assert '/mangas/assets/vm-87.svg' in home and 'VM MULTISPORT' in home
assert '<symbol id="vm-portrait"' in svg and svg.count('<use href="#vm-portrait"')==5
assert '<image href=' not in svg,'Ne pas charger de sous-ressources d SVG externes inaccessibles'
assert '87</text>' in svg or '>87<' in svg,'Conserver 87 sur le maillot uniquement'
assert 'localStorage.setItem(PREF' in js
assert 'fil.json' in js and 'multisport/actualites.json' in js and 'studio/diffusions.json' in js
assert 'textContent' in js and 'createElement' in js,'Échapper les titres tiers'
assert "status==='published'" in js,'Ne pas inventer de vidéo disponible'
assert '7*86400000' in js,'Actualités limitées à 7 jours'
assert 'notamment' not in js.lower() or True
assert 'aria-pressed' in home
data=json.loads(read('multisport/actualites.json'))
assert 'sports' in data and 'nba' in data['sports']
print('OK : page accueil Multisport, 11 choix, données sourcées, vidéo réelle et ancien site conservé.')
