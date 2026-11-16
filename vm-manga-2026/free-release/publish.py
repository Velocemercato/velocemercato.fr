"""One reviewed free manga bulletin; no re-upload after an uncertain write."""
import datetime as dt,hashlib,json,os,sys,time
from pathlib import Path
from zoneinfo import ZoneInfo
import requests
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.publier_meta import Graph,instagram_reel,ensure_meta_targets
from tools.diffuser_jt import State,DeliveryError,git_save
BASE=Path(__file__).resolve().parent
TARGETS=[('meta','1384363904759072','veloce.mercato'),('meta_univers','1349998758205153','vmunivers.fr'),('meta_pronos','112294796981981',None)]
def run():
 req=json.loads((ROOT/'.github/vm-manga-free-release.json').read_text())
 assert req['id']=='vm-manga-free-20261116-v1' and req['publish'] is True
 assert dt.datetime.now(ZoneInfo('Europe/Paris')).date().isoformat()==req['edition_date']=='2026-11-16'
 assert req['media_url'].startswith(('https://resource2.heygen.ai/','https://files2.heygen.ai/','https://cdn.jsdelivr.net/gh/Velocemercato/velocemercato.fr@'))
 assert req['download_url']==req['media_url']
 data=requests.get(req['download_url'],timeout=120);data.raise_for_status()
 assert hashlib.sha256(data.content).hexdigest()==req['sha256']
 file=BASE/'VM-Minute-Manga.mp4';file.write_bytes(data.content)
 sp=Path(os.environ['RUNNER_TEMP'])/'vm-broadcast-state/state.enc'
 state=State(sp,os.environ.get('VM_DIFFUSION_STATE_KEY',''),lambda:git_save(sp))
 ensure_meta_targets(state);g=Graph()
 receipts=state.data.setdefault('manga_free_publications',{}).setdefault(req['id'],{})
 results=[]
 def save(k,**x):
  receipts[k]={**receipts.get(k,{}),**x,'at':dt.datetime.now(dt.timezone.utc).isoformat()};state.save()
 for account,page,ig in TARGETS:
  meta=state.data.get('tokens',{}).get(account,{})
  for network in (['facebook','instagram'] if ig else ['facebook']):
   key=f'{network}/{account}'
   if key in receipts:continue
   try:
    assert str(meta.get('page_id'))==page and meta.get('page_token'),'Destination unavailable'
    ident=g.call('GET',page,{'fields':'id,name','access_token':meta['page_token']})
    assert str(ident.get('id'))==page,'Page mismatch'
    if network=='instagram':
     ident=g.call('GET',meta['ig_id'],{'fields':'id,username','access_token':meta['page_token']})
     assert ident.get('username')==ig,'Instagram mismatch'
    save(key,status='sending',media_sha256=req['sha256'])
    if network=='facebook':
     with file.open('rb') as f:
      r=requests.post('https://graph-video.facebook.com/'+page+'/videos',data={'description':req['caption'],'published':'true','access_token':meta['page_token']},files={'source':(file.name,f,'video/mp4')},timeout=(30,600),allow_redirects=False)
     result=r.json()
     if r.status_code>=300 or result.get('error'):raise DeliveryError('Facebook upload rejected: HTTP '+str(r.status_code)+' code '+str(result.get('error',{}).get('code','unknown')))
     mediaid=result.get('id')
    else:mediaid=instagram_reel(g,meta,{'verticale':req['media_url'],'texte_vertical':req['caption']},wait=300)
    if not mediaid:raise DeliveryError('Missing publication id')
    save(key,status='processing',id=str(mediaid))
   except Exception as e:
    safe=str(e)[:200] if isinstance(e,(DeliveryError,AssertionError)) else type(e).__name__
    save(key,status='verification_required' if receipts.get(key,{}).get('status')=='sending' else 'failed',error=safe)
 # Only read publication status; never resend an uncertain upload.
 for attempt in range(6):
  pending=False
  for key,row in list(receipts.items()):
   if row.get('status')=='published' or not row.get('id'):continue
   network,account=key.split('/');meta=state.data['tokens'][account]
   try:
    fields='id,permalink_url,status' if network=='facebook' else 'id,permalink,media_type'
    d=g.call('GET',row['id'],{'fields':fields,'access_token':meta['page_token']})
    url=d.get('permalink_url' if network=='facebook' else 'permalink','')
    if url.startswith('/'):url='https://www.facebook.com'+url
    ready=bool(url) and (network=='instagram' or d.get('status',{}).get('video_status')=='ready')
    if ready:save(key,status='published',url=url)
    else:pending=True
   except Exception:pending=True
  if not pending:break
  if attempt<5:time.sleep(20)
 for key,row in receipts.items():
  item={'destination':key,**row};results.append(item);print('MANGA_RESULT '+json.dumps(item,ensure_ascii=False),flush=True)
 (BASE/'publication-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
 if not len(results)==5 or any(r.get('status')!='published' for r in results):raise SystemExit(1)
if __name__=='__main__':run()
