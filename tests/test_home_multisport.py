"""Tests du nouveau portail d'accueil VM, sans publication et sans réseau."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
read=lambda p:(ROOT/p).read_text(encoding="utf-8")
class AccueilMultisportTests(unittest.TestCase):
 def test_site_preserve_football_and_robots(self):
  h=read("index.html")
  self.assertEqual(h.count('id="vm-wow-app"'),1)
  self.assertEqual(h.count('<!-- VM_ACTUS_VISIBLES_START -->'),1)
  self.assertEqual(h.count('<!-- VM_ACTUS_VISIBLES_END -->'),1)
  self.assertIn('id="pastille-tv"',h)
  self.assertIn('id="feed"',h)
  self.assertIn('id="feed-title"',h)
  self.assertIn('id="vitrine"',h)
  self.assertIn('id="vm-wow-expanded"',h)
  self.assertIn('src="/assets/home-multisport-wow.js?v=1"',h)
 def test_accessible_real_sports(self):
  h=read("index.html")
  for sport in ('foot','nba','nfl','f1','motogp','tennis','rugby','cyclisme','nhl','mlb','mma'):
   self.assertIn('data-wow-sport="'+sport+'"',h)
  for group in ('wow-france','wow-europe','wow-world'):
   self.assertIn('id="'+group+'"',h)
  self.assertNotIn('VM MULTISPORT 87',h)
  self.assertNotIn('ÉPISODE DU JOUR :',h) # Pas de vidéo de tous les sports inventée
 def test_original_mascot_assets(self):
  h=read("index.html")
  for sport in ('foot','nba','nfl','f1','motogp','tennis'):
   path="assets/mascottes/vm-"+sport+".svg"
   self.assertTrue((ROOT/path).is_file())
   svg=read(path)
   ET.fromstring(svg)
   self.assertIn('>87</text>',svg) # Numéro sur le maillot, pas dans le nom du site
   self.assertIn('VM MULTISPORT',svg)
  for sport in ('foot','nba','nfl','f1','tennis'):
   self.assertIn('/assets/mascottes/vm-'+sport+'.svg',h)
 def test_real_source_data_no_invented_headlines(self):
  js=read("assets/home-multisport-wow.js")
  self.assertIn("fetchJSON('/fil.json')",js)
  self.assertIn("fetchJSON('/multisport/actualites.json')",js)
  self.assertIn("fetchJSON('/studio/diffusions.json')",js)
  self.assertIn("status==='published'",js)
  self.assertIn('textContent',js)
  self.assertIn('localStorage',js)
  self.assertIn("pushState",js)
  self.assertIn("home-main",read("assets/home-multisport-wow.css"))
if __name__=='__main__':unittest.main()
