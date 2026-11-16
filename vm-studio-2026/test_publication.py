"""Tests hors réseau du routage et de l'absence de doublon."""
import contextlib, importlib.util, io, json, os, sys, tempfile, types, unittest
from pathlib import Path
class Error(RuntimeError):pass
class FakeState:
    data={}
    def __init__(self,*a,**k):pass
    def save(self):pass
class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.base=self.root/'vm-studio-2026';self.base.mkdir()
        self.meta=types.ModuleType('tools.publier_meta');self.diff=types.ModuleType('tools.diffuser_jt')
        self.calls=[];outer=self
        class Graph:
            def call(self,method,path,params):
                if path in ('1384363904759072','1349998758205153','112294796981981'):return {'id':path}
                if path in ('ig-main','ig-univers'):return {'id':path,'username':'veloce.mercato' if path=='ig-main' else 'vmunivers.fr'}
                return {'id':path,'permalink_url':'https://www.facebook.com/video/'+path,'status':{'video_status':'ready'},'permalink':'https://www.instagram.com/p/'+path}
        self.meta.Graph=Graph;self.meta.ensure_meta_targets=lambda s:None
        def insta(graph,meta,row,**k):outer.calls.append(('instagram',meta['page_id']));return 'ig-post-'+str(len(outer.calls))
        self.meta.instagram_reel=insta
        self.diff.State=FakeState;self.diff.DeliveryError=Error;self.diff.git_save=lambda *a:None;self.diff.HTTP=lambda:None;self.diff.access_token=lambda *a:'test-only'
        class YouTube:
            def __init__(self,*a):pass
            def verify_channel(self):return {}
            def upload(self,file,meta,receipt):outer.calls.append(('youtube',None));receipt['video_id']='test-only-id'
            def make_public(self,receipt,**k):receipt.update(status='published',url='https://www.youtube.com/watch?v=test-only-id')
        self.diff.YouTube=YouTube
        self.oldmods={k:sys.modules.get(k) for k in ('tools','tools.publier_meta','tools.diffuser_jt')}
        sys.modules.update({'tools':types.ModuleType('tools'),'tools.publier_meta':self.meta,'tools.diffuser_jt':self.diff})
        spec=importlib.util.spec_from_file_location('vm_studio_publish_test',Path(__file__).with_name('publish_direct.py'));self.mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.mod)
        self.mod.ROOT=self.root;self.mod.BASE=self.base
        self.mod.facebook_file=lambda meta,*args:(self.calls.append(('facebook',meta['page_id'])) or 'fb-post-'+str(len(self.calls)))
        req={'publish':True,'id':'vm-jt3d-2026-11-16-v1'};(self.base/'diffusion.json').write_text(json.dumps(req))
        media={'reel':{'url':'https://cdn.jsdelivr.net/gh/Velocemercato/velocemercato.fr@'+'a'*40+'/VM-Reel-3D-16-novembre-2026.mp4','sha256':'a'*64},'jt':{'sha256':'b'*64}}
        (self.base/'published-media.json').write_text(json.dumps(media));(self.base/'scriptpack.json').write_text('{"sources":[]}')
        FakeState.data={'tokens':{k:{'page_id':v,'page_token':'test-only',**({'ig_id':'ig-main' if k=='meta' else 'ig-univers'} if k!='meta_pronos' else {})} for k,v in self.mod.PAGES.items()}}
        self.oldenv={k:os.environ.get(k) for k in ('RUNNER_TEMP','VM_AUTO_YOUTUBE')};os.environ['RUNNER_TEMP']=self.tmp.name;os.environ['VM_AUTO_YOUTUBE']='true'
    def tearDown(self):
        for k,v in self.oldmods.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v
        for k,v in self.oldenv.items():
            if v is None:os.environ.pop(k,None)
            else:os.environ[k]=v
        self.tmp.cleanup()
    def run_silently(self):
        with contextlib.redirect_stdout(io.StringIO()):self.mod.run()
    def test_routage_exact_et_reexecution_sans_doublon(self):
        self.run_silently()
        self.assertEqual(len([x for x in self.calls if x[0]=='facebook']),6)
        self.assertEqual([x[1] for x in self.calls if x[0]=='instagram'],['1384363904759072','1349998758205153'])
        self.assertEqual(len([x for x in self.calls if x[0]=='youtube']),1)
        before=list(self.calls);self.run_silently();self.assertEqual(self.calls,before)
    def test_destination_modifiee_non_contactee(self):
        FakeState.data['tokens']['meta_pronos']['page_id']='999999999'
        with self.assertRaises(SystemExit):self.run_silently()
        self.assertNotIn(('facebook','999999999'),self.calls)
    def test_demande_desactivee_aucun_envoi(self):
        (self.base/'diffusion.json').write_text('{"publish":false}')
        with self.assertRaises(Error):self.run_silently()
        self.assertEqual(self.calls,[])
if __name__=='__main__':unittest.main()
