"""Le Foot historique reste intact ; le portail et les pages sport sont séparés."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
def read(path):return (ROOT/path).read_text(encoding="utf-8")
SPORTS=("nba","nfl","f1","motogp","tennis","rugby","cyclisme","nhl","mlb","mma","ski")
class AccueilMultisportTests(unittest.TestCase):
 def test_foot_restored_with_robots(self):
  """Accueil = maquette VM Multisport (thème 08/11/2026, demande du propriétaire)."""
  home=read("index.html")
  self.assertEqual(home.count('<!-- VM_ACTUS_VISIBLES_START -->'),1)
  self.assertEqual(home.count('<!-- VM_ACTUS_VISIBLES_END -->'),1)
  self.assertIn('data-vmt="home"',home)
  self.assertIn('id="actu-jour"',home)
  self.assertIn('class="nav-tabs"',home)
  self.assertIn('href="/mangas/"',home)
  self.assertIn('href="/multisport/"',home)
  self.assertIn('href="/pronos/"',home)
  self.assertIn('href="/actus/"',home)
  self.assertIn('href="/vm-gaming/"',home)
  self.assertIn('href="/soutenir.html"',home)
  self.assertIn('href="https://vmunivers.fr/"',home)
  self.assertIn('/assets/vm-home.css',home)
  self.assertIn('/assets/hero-multisport.jpg',home)
  # Les 3 pages Facebook + les réseaux en couleur
  for fb in ("1CZ5mPjsaw","14vjnjB1vbZ","1FeRjn2vau"):
   self.assertIn(fb,home)
  self.assertIn('class="soc-fb"',home)
  self.assertIn('class="soc-yt"',home)
  self.assertNotIn('id="vm-wow-app"',home)
  self.assertNotIn('src="/assets/home-multisport-wow.js?v=1"',home)
 def test_portal_sport_pages(self):
  portal=read("multisport/index.html")
  self.assertIn('data-mode="portal"',portal)
  self.assertIn('VM MANGAS',portal)
  self.assertIn('id="recent-list"',portal)
  self.assertIn('id="news-list"',portal)
  self.assertIn('class="banner"',portal)
  for sport in SPORTS:
   content=read(f"multisport/{sport}/index.html")
   self.assertIn(f'data-current-sport="{sport}"',content)
   self.assertIn('data-mode="sport"',content)
   for section in ('actualites','france','europe','international','feminin','resultats','videos'):
    self.assertIn(f'id="{section}"',content)
   self.assertIn('href="/mangas/"',content)
 def test_mascots(self):
  for sport in ("foot","nba","nfl","f1","motogp","tennis","ski"):
   svg=read(f"assets/mascottes/vm-{sport}.svg")
   ET.fromstring(svg)
   self.assertIn('>87</text>',svg)
 def test_no_fabricated_videos_or_scores(self):
  js=read("multisport/univers.js")
  for path in ('/fil.json','/multisport/actualites.json','/studio/diffusions.json'):self.assertIn(path,js)
  self.assertIn("status==='published'",js)
  self.assertIn('textContent',js)
  self.assertIn('localStorage',js)
  self.assertNotIn('10:24',js)
if __name__=="__main__":unittest.main()
