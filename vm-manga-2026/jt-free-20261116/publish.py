"""Publish three reviewed editions to the five explicitly authorized Meta accounts.

Each upload and each container ID is checkpointed. Re-runs only resume reads or
publish a FINISHED Instagram container; an uncertain publish is never repeated.
No credentials are printed, copied into artifacts, or embedded in media URLs.
"""
import datetime as dt,hashlib,json,os,sys,time
from pathlib import Path
from zoneinfo import ZoneInfo
import requests
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.publier_meta import Graph,ensure_meta_targets
from tools.diffuser_jt import State,DeliveryError,git_save
BASE=Path(__file__).resolve().parent
TARGETS=[('meta','1384363904759072','veloce.mercato'),('meta_univers','1349998758205153','vmunivers.fr'),('meta_pronos','112294796981981',None)]

def run():
 req=json.loads((ROOT/'.github/vm-jt-manga-free-20261116.json').read_text())
 assert req['id']=='vm-jt-manga-free-20261116-v1' and req['publish'] is True
 assert req['edition_date']=='2026-11-16'
 age=(dt.datetime.now(ZoneInfo('Europe/Paris')).date()-dt.date.fromisoformat(req['edition_date'])).days
 assert 0<=age<=1,'Edition no longer current: requires editorial review'
 assert {x['slug'] for x in req['editions']}=={'actus','sport','gaming'}
 sp=Path(os.environ['RUNNER_TEMP'])/'vm-broadcast-state/state.enc'
 state=State(sp,os.environ.get('VM_DIFFUSION_STATE_KEY',''),lambda:git_save(sp))
 ensure_meta_targets(state);g=Graph()
 receipts=state.data.setdefault('manga_jt_publications',{}).setdefault(req['id'],{})
 def report():
  result=[{'destination':k,**v} for k,v in receipts.items()]
  (BASE/'publication-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 def save(k,**x):
  receipts[k]={**receipts.get(k,{}),**x,'at':dt.datetime.now(dt.timezone.utc).isoformat()}
  state.save();report();print('JT_RESULT '+json.dumps({'destination':k,**receipts[k]},ensure_ascii=False),flush=True)
 def verify(key):
  row=receipts[key]
  if row.get('status')=='published' or not row.get('id'):return
  edition,network,account=key.split('/');meta=state.data['tokens'][account]
  fields='id,permalink_url,status' if network=='facebook' else 'id,permalink,media_type'
  d=g.call('GET',row['id'],{'fields':fields,'access_token':meta['page_token']})
  url=d.get('permalink_url' if network=='facebook' else 'permalink','')
  if url.startswith('/'):url='https://www.facebook.com'+url
  ready=bool(url) and (network=='instagram' or d.get('status',{}).get('video_status')=='ready')
  if ready:save(key,status='published',url=url)
 for edition in req['editions']:
  slug=edition['slug'];url=edition['media_url']
  assert url.startswith(('https://resource2.heygen.ai/','https://files2.heygen.ai/'))
  assert 580<=edition['duration_seconds']<=620 and len(edition['caption'])<=2100
  r=requests.get(url,timeout=(30,180));r.raise_for_status()
  assert hashlib.sha256(r.content).hexdigest()==edition['sha256'],'Media hash mismatch'
  file=BASE/f'VM-JT-{slug}.mp4';file.write_bytes(r.content)
  for account,page,ig in TARGETS:
   meta=state.data.get('tokens',{}).get(account,{})
   for network in (['facebook','instagram'] if ig else ['facebook']):
    key=f'{slug}/{network}/{account}';old=receipts.get(key,{})
    if old and old.get('status')!='container_processing':continue
    try:
     assert str(meta.get('page_id'))==page and meta.get('page_token'),'Destination unavailable'
     ident=g.call('GET',page,{'fields':'id,name','access_token':meta['page_token']})
     assert str(ident.get('id'))==page,'Page mismatch'
     if network=='instagram':
      ident=g.call('GET',meta['ig_id'],{'fields':'id,username','access_token':meta['page_token']})
      assert ident.get('username')==ig,'Instagram mismatch'
     if network=='facebook':
      save(key,status='sending',media_sha256=edition['sha256'])
      with file.open('rb') as f:
       response=requests.post('https://graph-video.facebook.com/'+page+'/videos',data={'description':edition['caption'],'published':'true','access_token':meta['page_token']},files={'source':(file.name,f,'video/mp4')},timeout=(30,600),allow_redirects=False)
      data=response.json()
      if response.status_code>=300 or data.get('error'):raise DeliveryError('Facebook upload rejected: HTTP '+str(response.status_code)+' code '+str(data.get('error',{}).get('code','unknown')))
      mediaid=data.get('id')
     else:
      container=old.get('container_id')
      if not container:
       save(key,status='creating_container',media_sha256=edition['sha256'])
       data=g.call('POST',meta['ig_id']+'/media',{'media_type':'REELS','video_url':url,'caption':edition['caption'],'share_to_feed':'true','access_token':meta['page_token']})
       container=data.get('id');assert container,'Missing Instagram container'
       save(key,status='container_processing',container_id=str(container))
      finished=False
      for _ in range(40):
       data=g.call('GET',container,{'fields':'status_code,status','access_token':meta['page_token']})
       status=data.get('status_code')
       if status=='FINISHED':finished=True;break
       if status in ('ERROR','EXPIRED'):raise DeliveryError('Instagram container '+status)
       time.sleep(15)
      if not finished:continue
      save(key,status='publishing_container')
      mediaid=g.call('POST',meta['ig_id']+'/media_publish',{'creation_id':container,'access_token':meta['page_token']}).get('id')
     assert mediaid,'Missing publication id'
     save(key,status='processing',id=str(mediaid));verify(key)
    except Exception as e:
     safe=str(e)[:200] if isinstance(e,(DeliveryError,AssertionError)) else type(e).__name__
     status=receipts.get(key,{}).get('status')
     save(key,status='verification_required' if status in ('sending','publishing_container','creating_container') else 'failed',error=safe)
  file.unlink(missing_ok=True)
 # Read-only final verification; no duplicate uploads.
 for attempt in range(15):
  pending=False
  for key,row in list(receipts.items()):
   if row.get('status')=='published' or not row.get('id'):continue
   pending=True
   try:verify(key)
   except Exception:pass
  if not pending:break
  if attempt<14:time.sleep(20)
 report()
 for key,row in receipts.items():print('JT_RESULT '+json.dumps({'destination':key,**row},ensure_ascii=False),flush=True)
 if len(receipts)!=15 or any(r.get('status')!='published' for r in receipts.values()):raise SystemExit(1)
if __name__=='__main__':run()
