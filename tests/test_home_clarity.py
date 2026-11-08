"""L'accueil VM Multisport reste lisible et complet : sections clés et liens vivants."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class HomeClarityTests(unittest.TestCase):
 def test_home_has_all_key_sections(self):
  home=(ROOT/"index.html").read_text(encoding="utf-8")
  for marker in (
   'class="livebar"',
   'class="nav-tabs"',
   'id="actu-jour"',
   'id="pronos"',
   'class="press-grid"',
   'id="agenda"',
   'class="geo-grid"',
   'class="social-row"',
   'class="vm-banner"',
   'class="footer"',
   '<!-- VM_ACTUS_VISIBLES_START -->',
   '<!-- VM_ACTUS_VISIBLES_END -->',
  ):
   self.assertIn(marker,home)
 def test_home_links_resolve_locally(self):
  home=(ROOT/"index.html").read_text(encoding="utf-8")
  import re
  for href in re.findall(r'href="(/[\w./-]+)"',home):
   rel=href.lstrip('/')
   if href.endswith('/'):
    self.assertTrue((ROOT/rel/"index.html").exists(),f"{href} introuvable")
   else:
    self.assertTrue((ROOT/rel).is_file(),f"{href} introuvable")

if __name__=="__main__":
 unittest.main()
