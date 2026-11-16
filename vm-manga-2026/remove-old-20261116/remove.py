"""Remove only the twelve verified rejected 3D publications, on user request."""
import json,os,sys,datetime as dt
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));BASE=Path(__file__).resolve().parent
from tools.publier_meta import Graph
from tools.diffuser_jt import State,DeliveryError,git_save,HTTP,YouTube,access_token
PAGES={'meta':'1384363904759072','meta_univers':'1349998758205153','meta_pronos':'112294796981981'}
IG={'meta':'veloce.mercato','meta_univers':'vmunivers.fr'}
def meta_call(method,ident,token,fields=None):
 assert ident.isdigit()
 r=requests.request(method,'https://graph.facebook.com/v27.0/'+ident,headers={'Authorization':'Bearer '+token},params={'fields':fields} if fields else None,timeout=90,allow_redirects=False)
 try:d=r.json()
 except ValueError:d={}
 return r.status_code,d
def run():
 req=json.loads((BASE/'request.json').read_text());assert req['id']=='remove-rejected-studio3d-20261116-v1'
 assert req['old_edition']=='vm-jt3d-2026-11-16-v1' and len(req['targets'])==12
 protected=set()
 for p in [ROOT/'vm-manga-2026/free-release/publication-results.json',ROOT/'vm-manga-2026/jt-free-20261116/publication-results.json']:
  protected.update(str(r['id']) for r in json.loads(p.read_text()))
 assert len(protected)==20 and not protected.intersection(str(r['id']) for r in req['targets'])
 sp=Path(os.environ['RUNNER_TEMP'])/'vm-broadcast-state/state.enc';state=State(sp,os.environ['VM_DIFFUSION_STATE_KEY'],lambda:git_save(sp))
 old=state.data.get('studio3d_publications',{}).get(req['old_edition'],{})
 receipts=state.data.setdefault('removed_rejected_publications',{}).setdefault(req['id'],{})
 def save(key,**data):
  receipts[key]={**receipts.get(key,{}),**data,'at':dt.datetime.now(dt.timezone.utc).isoformat()};state.save()
  (BASE/'results.json').write_text(json.dumps([{'destination':k,**v} for k,v in receipts.items()],ensure_ascii=False,indent=2))
  print('REMOVAL_RESULT '+json.dumps({'destination':key,**receipts[key]},ensure_ascii=False),flush=True)
 for row in req['targets']:
  key=row['destination'];ident=str(row['id']);prior=old.get(key,{})
  if receipts.get(key,{}).get('status')=='deleted':continue
  try:
   assert str(prior.get('id') or prior.get('video_id') or '')==ident,'Original receipt mismatch'
   assert prior.get('url')==row['url'],'Original URL mismatch'
   if key=='jt/youtube':
    assert ident=='sVj2FBxXmuw'
    http=HTTP();token=access_token('youtube',state,http);channel=YouTube(http,state,token).verify_channel()
    url='https://www.googleapis.com/youtube/v3/videos?part=snippet&id='+ident
    items=http.json('GET',url,token).get('items',[])
    assert len(items)==1 and items[0]['snippet']['channelId']==channel['id'],'YouTube owner mismatch'
    assert items[0]['snippet']['title'].startswith('Le nouveau JT VM en 3D'),'Not the rejected 3D version'
    save(key,status='deleting',id=ident,url=row['url'])
    status,_,_=http.request('DELETE','https://www.googleapis.com/youtube/v3/videos?id='+ident,headers={'Authorization':'Bearer '+token})
    assert status==204,'YouTube did not confirm deletion'
    absent=not http.json('GET',url,token).get('items',[])
    assert absent,'YouTube video still returned after deletion'
   else:
    fmt,network,account=key.split('/');assert fmt in ('reel','pastille','jt') and network in ('facebook','instagram')
    meta=state.data['tokens'][account];assert str(meta.get('page_id'))==PAGES[account]
    g=Graph();owner=g.call('GET',PAGES[account],{'fields':'id,name','access_token':meta['page_token']});assert str(owner['id'])==PAGES[account]
    if network=='instagram':
     owner=g.call('GET',meta['ig_id'],{'fields':'id,username','access_token':meta['page_token']});assert owner['username']==IG[account]
    fields='id,description,permalink_url' if network=='facebook' else 'id,caption,permalink'
    status,data=meta_call('GET',ident,meta['page_token'],fields)
    assert status==200 and str(data.get('id'))==ident,'Live media identity unavailable'
    caption=data.get('description' if network=='facebook' else 'caption','')
    assert 'plateau 3D originaux' in caption and 'Voix Piper' in caption,'Not the rejected 3D version'
    live_url=data.get('permalink_url' if network=='facebook' else 'permalink','')
    if live_url.startswith('/'):live_url='https://www.facebook.com'+live_url
    assert live_url.rstrip('/')==row['url'].rstrip('/'),'Live permalink mismatch'
    save(key,status='deleting',id=ident,url=row['url'])
    tokens=[meta['page_token']]
    user=os.getenv('META_USER_TOKEN','').strip()
    if network=='instagram' and user and user not in tokens:tokens.insert(0,user)
    success=False;error={}
    for t in tokens:
     status,data=meta_call('DELETE',ident,t)
     if status==200 and data.get('success') is True:success=True;break
     error={'http':status,'code':data.get('error',{}).get('code'),'subcode':data.get('error',{}).get('error_subcode')}
    if not success:
     save(key,status='blocked',error=error);continue
    # API success is the deletion receipt; read back using the previously valid token.
    status,data=meta_call('GET',ident,meta['page_token'],'id')
    if status==200 and data.get('id'):save(key,status='deletion_accepted_pending_visibility');continue
   prior['removed_by_user']=True;prior['removed_at']=dt.datetime.now(dt.timezone.utc).isoformat()
   save(key,status='deleted',id=ident,url=row['url'])
  except Exception as e:
   safe=str(e)[:180] if isinstance(e,(AssertionError,DeliveryError)) else type(e).__name__
   save(key,status='verification_required',id=ident,url=row['url'],error=safe)
 for k,v in receipts.items():print('REMOVAL_RESULT '+json.dumps({'destination':k,**v},ensure_ascii=False),flush=True)
 if len(receipts)!=12 or any(x['status']!='deleted' for x in receipts.values()):raise SystemExit(1)
if __name__=='__main__':run()
