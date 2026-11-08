"""Validation des trois thèmes cinéma : les liens et contenus sportifs restent authentiques."""
import unittest
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
def read(path):return (ROOT/path).read_text(encoding='utf-8')
class Parser(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.ids=[];self.links=[];self.script=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id'in d:self.ids.append(d['id'])
  if tag=='a':self.links.append(d.get('href',''))
  if tag=='script':self.script.append(d.get('src',''))
class CinemaTests(unittest.TestCase):
 def test_foot_and_old_feed_retained(self):
  h=read('index.html');p=Parser();p.feed(h)
  for id in ('accueil-title','univers-vm','actualites-du-jour','videos','pastille-tv'):
   self.assertIn(id,p.ids)
  self.assertEqual(h.count('<!-- VM_ACTUS_VISIBLES_START -->'),1)
  self.assertEqual(h.count('<!-- VM_ACTUS_VISIBLES_END -->'),1)
  self.assertIn('/mangas/',p.links)
  self.assertIn('/multisport/',p.links)
  self.assertIn('/assets/vm-editorial.js',p.script)
  self.assertIn('/assets/broadcast-feed.js',p.script)
 def test_all_sport_pages_have_cinema_and_manga(self):
  for sport in ('', 'nba/','nfl/','f1/','motogp/','tennis/','rugby/','cyclisme/','nhl/','mlb/','mma/','ski/'):
   with self.subTest(sport=sport):
    p=Parser();p.feed(read('multisport/'+sport+'index.html'))
    self.assertIn('/mangas/',p.links)
    self.assertIn('haut',p.ids)
    self.assertIn('/multisport/cinema-v2.css',read('multisport/'+sport+'index.html'))
    self.assertIn('/multisport/univers.js',p.script)
 def test_manga_episodes_still_published_only_from_official_hosts(self):
  p=Parser();h=read('mangas/index.html');p.feed(h)
  self.assertIn('/mangas/assets/cinema-v3.css',h)
  self.assertIn('catalogue',p.ids)
  self.assertIn('/multisport/',p.links)
  for name in ('ecole-des-champions-01','olive-et-tom-01','dragon-ball-z-01'):
   self.assertTrue((ROOT/'mangas/episodes'/ (name+'.html')).exists())
 def test_scripts_use_only_real_data(self):
  s=read('assets/vm-cinema-foot.js')
  self.assertIn("/fil.json",s);self.assertIn("/studio/diffusions.json",s)
  self.assertIn("status==='published'",s)
  self.assertIn("textContent",s)
  self.assertNotIn("600 000",s)
if __name__=='__main__': unittest.main()
