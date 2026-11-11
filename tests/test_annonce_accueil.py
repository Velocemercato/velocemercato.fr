import importlib.util
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest

class Error(Exception):pass

def load():
 spec=importlib.util.spec_from_file_location('annonce_under_test',Path(__file__).resolve().parents[1]/'tools/annoncer_nouvel_accueil.py');module=importlib.util.module_from_spec(spec)
 fake=SimpleNamespace(Graph=None,State=None,git_save=None,ensure_meta_targets=lambda state:None,DeliveryError=Error)
 original=sys.modules.get('tools.publier_meta');sys.modules['tools.publier_meta']=fake
 try:spec.loader.exec_module(module)
 finally:
  if original is None:sys.modules.pop('tools.publier_meta',None)
  else:sys.modules['tools.publier_meta']=original
 return module

class State:
 def __init__(self,expected):self.data={'tokens':{k:{'page_id':v,'page_token':'test'} for k,v in expected.items()}};self.saved=0;self.fail=False
 def save(self):
  self.saved+=1
  if self.fail:raise Error('persistance interrompue')
class Graph:
 def __init__(self):self.posts=[];self.empty=False
 def call(self,method,path,params):
  if method=='POST':self.posts.append(path);return {} if self.empty else {'post_id':path.split('/')[0]+'_123'}
  if 'fields' in params and params['fields']=='permalink_url':return {'permalink_url':'https://www.facebook.com/'+path}
  return {'id':path,'name':'Page test'}
class Tests(unittest.TestCase):
 def setUp(self):self.m=load();self.state=State(self.m.EXPECTED);self.graph=Graph();self.tmp=tempfile.TemporaryDirectory();self.report=Path(self.tmp.name)/'bilan.json';self.url='https://raw.githubusercontent.com/Velocemercato/velocemercato.fr/'+'a'*40+'/campagnes/avis-nouvel-accueil-2026-11-11.jpg'
 def tearDown(self):self.tmp.cleanup()
 def publish(self):return self.m.publish(self.state,self.graph,'Votre avis ? https://velocemercato.fr/',self.url,self.report)
 def test_three_exact_pages_and_no_duplicates(self):
  self.assertEqual(len(self.publish()),3);self.assertEqual(len(self.graph.posts),3);self.publish();self.assertEqual(len(self.graph.posts),3)
 def test_failed_reservation_prevents_post(self):
  self.state.fail=True
  with self.assertRaises(Error):self.publish()
  self.assertEqual(self.graph.posts,[])
 def test_unconfirmed_response_never_retried(self):
  self.graph.empty=True;self.publish();self.assertEqual(len(self.graph.posts),3);self.publish();self.assertEqual(len(self.graph.posts),3)
 def test_wrong_page_not_published(self):
  self.state.data['tokens']['meta']['page_id']='999';self.publish();self.assertNotIn('999/photos',self.graph.posts);self.assertNotIn('1384363904759072/photos',self.graph.posts)
if __name__=='__main__':unittest.main()
