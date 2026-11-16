"""Offline checks for the authorized destinations and duplicate protection."""
import hashlib,importlib.util,json,sys,tempfile,types,unittest
from pathlib import Path
class DeliveryError(Exception):pass
shared={};calls=[];uncertain=False
class State:
 def __init__(self,*args):self.data=shared
 def save(self):pass
class Graph:
 def call(self,method,path,params):
  global uncertain
  if method=='GET':
   if path in ['1384363904759072','1349998758205153','112294796981981']:return {'id':path}
   if path=='ig1':return {'id':path,'username':'veloce.mercato'}
   if path=='ig2':return {'id':path,'username':'vmunivers.fr'}
   if path.startswith('container'):return {'status_code':'FINISHED'}
   return {'id':path,'permalink':'https://www.instagram.com/reel/'+path,'permalink_url':'https://www.facebook.com/reel/'+path,'status':{'video_status':'ready'}}
  calls.append((method,path))
  if path.endswith('/media'):return {'id':'container'+str(len(calls))}
  if uncertain and path=='ig1/media_publish':
   uncertain=False;raise TimeoutError('uncertain external response')
  return {'id':'media'+str(len(calls))}
class Response:
 content=b'reviewed-video';status_code=200
 def raise_for_status(self):pass
 def json(self):return {'id':'fb'+str(len(calls))}
def post(url,**kwargs):calls.append(('POST',url));return Response()
reqmod=types.ModuleType('requests');reqmod.get=lambda *a,**k:Response();reqmod.post=post
sys.modules['requests']=reqmod
meta=types.ModuleType('tools.publier_meta');meta.Graph=Graph;meta.ensure_meta_targets=lambda s:None
state=types.ModuleType('tools.diffuser_jt');state.State=State;state.DeliveryError=DeliveryError;state.git_save=lambda x:None
sys.modules['tools.publier_meta']=meta;sys.modules['tools.diffuser_jt']=state
spec=importlib.util.spec_from_file_location('publisher',Path(__file__).with_name('publish.py'));p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
p.time.sleep=lambda _:None
class PublishChecks(unittest.TestCase):
 def setUp(self):
  global shared,calls,uncertain
  shared={'tokens':{'meta':{'page_id':'1384363904759072','page_token':'fake','ig_id':'ig1'},'meta_univers':{'page_id':'1349998758205153','page_token':'fake','ig_id':'ig2'},'meta_pronos':{'page_id':'112294796981981','page_token':'fake'}}};calls=[];uncertain=False
  self.tmp=tempfile.TemporaryDirectory();root=Path(self.tmp.name);(root/'.github').mkdir();p.ROOT=p.BASE=root
  import os
  os.environ['RUNNER_TEMP']=str(root)
  req={'id':'vm-jt-manga-free-20261116-v1','edition_date':'2026-11-16','publish':True,'editions':[{'slug':n,'duration_seconds':600,'caption':n,'media_url':'https://resource2.heygen.ai/example.mp4','sha256':hashlib.sha256(Response.content).hexdigest()} for n in ['actus','sport','gaming']]}
  (root/'.github/vm-jt-manga-free-20261116.json').write_text(json.dumps(req))
 def tearDown(self):self.tmp.cleanup()
 def test_all_destinations_and_no_duplicate(self):
  p.run();count=len(calls);p.run();self.assertEqual(len(calls),count)
  rows=shared['manga_jt_publications']['vm-jt-manga-free-20261116-v1'];self.assertEqual(len(rows),15);self.assertTrue(all(r['status']=='published' for r in rows.values()))
  self.assertEqual(sum('/videos' in path for _,path in calls),9);self.assertEqual(sum('/media_publish' in path for _,path in calls),6)
 def test_uncertain_publish_is_never_repeated(self):
  global uncertain
  uncertain=True
  with self.assertRaises(SystemExit):p.run()
  count=len(calls)
  with self.assertRaises(SystemExit):p.run()
  self.assertEqual(len(calls),count)
  self.assertEqual(shared['manga_jt_publications']['vm-jt-manga-free-20261116-v1']['actus/instagram/meta']['status'],'verification_required')
if __name__=='__main__':unittest.main()
